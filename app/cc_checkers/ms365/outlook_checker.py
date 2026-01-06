"""
Email Checker for Microsoft 365 (Lokka MCP)
Module for periodically checking Outlook emails and processing them with LLM

Checker concept: Periodic task processing as an extension of configured MCP
- Operator: Uses Lokka MCP (user request processing)
- Checker: Uses Lokka MCP (background periodic tasks)
"""

import asyncio
import json
import logging
import os
from typing import List, Dict, Any

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, ResultMessage

from app.config.settings import get_settings

settings = get_settings()


async def fetch_new_emails() -> List[Dict[str, Any]]:
    """
    Query latest unread emails using Lokka MCP

    Returns:
        List of latest emails (max 10)
    """
    if not settings.MS365_ENABLED:
        logging.error("[EMAIL_CHECKER] MS365 MCP is not enabled")
        return []

    # MCP server settings (Lokka - cached version)
    mcp_servers = {
        "ms365": {
            "command": "npx",
            "args": ["mcp-cache", "npx", "-y", "@batteryho/lokka-cached"],
            "env": {
                "TENANT_ID": settings.MS365_TENANT_ID,
                "CLIENT_ID": settings.MS365_CLIENT_ID,
                "USE_INTERACTIVE": "true"
            }
        }
    }

    system_prompt = """You are an Outlook email collection expert.
Using Lokka MCP (Microsoft 365 MCP), query the list of unread emails and return structured JSON data.

**Task Instructions:**
1. Use `mcp__ms365__*` tools to query up to 10 unread emails from inbox in newest order
2. **Mark all queried emails as read**
3. Extract the following information for each email:
   - id: Email ID
   - subject: Subject
   - from: Sender object ({"emailAddress": {"name": "Name", "address": "email@address"}} format)
   - toRecipients: Recipients array
   - ccRecipients: CC recipients array
   - receivedDateTime: Received time
   - bodyPreview: Body preview (within 200 chars)
   - isRead: Read status
   - hasAttachments: Has attachments

**Output Format:**
Respond only in JSON array format as below. Do not include any other explanation or text:

```json
[
  {
    "id": "mailID",
    "subject": "Subject",
    "from": {
      "emailAddress": {
        "name": "Sender Name",
        "address": "sender@example.com"
      }
    },
    "toRecipients": [
      {
        "emailAddress": {
          "name": "Recipient1",
          "address": "recipient1@example.com"
        }
      }
    ],
    "ccRecipients": [],
    "receivedDateTime": "2024-01-15T10:30:00Z",
    "bodyPreview": "Body preview...",
    "isRead": false,
    "hasAttachments": true
  }
]
```

**Note:** Return empty array [] if no unread emails"""

    try:
        options = ClaudeAgentOptions(
            system_prompt=system_prompt,
            model=settings.MODEL_FOR_SIMPLE,
            permission_mode="bypassPermissions",
            allowed_tools=["*"],
            disallowed_tools=[
                "Bash(curl:*)",
                "Bash(rm:*)",
                "Bash(rm -r*)",
                "Bash(rm -rf*)",
                "Read(./.env)",
                "Read(./credential.json)",
                "WebFetch",
                "Write",
                "Edit",
                "NotebookEdit",
            ],
            setting_sources=["project"],
            cwd=os.getcwd(),
            mcp_servers=mcp_servers,
        )

        async with ClaudeSDKClient(options=options) as client:
            await client.query("Use mcp__ms365__* tools to query up to 10 unread emails from inbox and return as JSON.")

            async for message in client.receive_response():
                if isinstance(message, ResultMessage):
                    result_text = message.result.strip()

                    # Extract JSON (remove ```json ... ```)
                    if "```json" in result_text or "```" in result_text:
                        json_start = result_text.find("[")
                        json_end = result_text.rfind("]") + 1
                        if json_start != -1 and json_end > json_start:
                            result_text = result_text[json_start:json_end]

                    emails = json.loads(result_text)
                    logging.info(f"[EMAIL_CHECKER] Fetched {len(emails)} new emails via Lokka MCP")
                    return emails

        return []

    except json.JSONDecodeError as e:
        logging.error(f"[EMAIL_CHECKER] Failed to parse email JSON: {e}")
        return []
    except Exception as e:
        logging.error(f"[EMAIL_CHECKER] Error fetching emails via Lokka MCP: {e}")
        return []


async def process_emails_batch(emails: List[Dict[str, Any]]):
    """
    Process email batch with agent

    Args:
        emails: List of emails to process
    """
    from app.cc_checkers.ms365.outlook_agent import call_email_task_extractor
    from app.cc_utils.email_tasks_db import get_pending_tasks, complete_task
    from app.queueing_extended import enqueue_message

    if not emails:
        logging.info("[EMAIL_PROCESSOR] No emails to process")
        return

    logging.info(f"[EMAIL_PROCESSOR] Processing {len(emails)} emails...")

    # Log output
    for idx, email in enumerate(emails, 1):
        subject = email.get("subject", "(No subject)")
        from_addr = email.get("from", "")
        received_time = email.get("receivedDateTime", "")
        body_preview = email.get("bodyPreview", "")

        logging.info(f"[EMAIL_PROCESSOR] [{idx}/{len(emails)}] From: {from_addr}")
        logging.info(f"[EMAIL_PROCESSOR] [{idx}/{len(emails)}] Subject: {subject}")
        logging.info(f"[EMAIL_PROCESSOR] [{idx}/{len(emails)}] Received: {received_time}")
        logging.info(f"[EMAIL_PROCESSOR] [{idx}/{len(emails)}] Preview: {body_preview[:100]}...")

    # 1. Call agent to analyze emails and extract tasks (save to DB)
    # Agent also handles marking as read
    await call_email_task_extractor(emails)

    # 2. Get pending tasks from DB
    pending_tasks = get_pending_tasks()

    if not pending_tasks:
        logging.info("[EMAIL_PROCESSOR] No pending tasks found")
        return

    # 3. Add to Slack channel queue
    logging.info(f"[EMAIL_PROCESSOR] Found {len(pending_tasks)} pending tasks")

    for task in pending_tasks:
        task_id = task["id"]
        user_id = task.get("user")
        channel_id = task.get("channel")
        text = task.get("text")

        # Can only add to queue if user, channel, text all exist
        if not user_id or not channel_id or not text:
            logging.warning(f"[EMAIL_PROCESSOR] Task {task_id} missing user/channel/text, skipping")
            continue

        # Add to Slack queue (same pattern as web interface)
        await enqueue_message({
            "text": text,
            "channel": channel_id,
            "ts": "",
            "user": user_id,
            "thread_ts": None,
        })

        # Mark task as complete
        complete_task(task_id)
        logging.info(f"[EMAIL_PROCESSOR] Queued task {task_id} to user {user_id}")


async def check_email_updates():
    """
    Email check function called periodically (called by scheduler)
    """
    if not settings.MS365_ENABLED:
        logging.warning("[EMAIL_CHECKER] MS365 MCP is not enabled, skipping email check")
        return

    logging.info("[EMAIL_CHECKER] Checking for new emails...")

    try:
        # Query new emails
        emails = await fetch_new_emails()

        if emails:
            logging.info(f"[EMAIL_CHECKER] Found {len(emails)} new emails, starting background processing")
            # Process as background task
            asyncio.create_task(process_emails_batch(emails))
        else:
            logging.info("[EMAIL_CHECKER] No new emails found")

    except Exception as e:
        logging.error(f"[EMAIL_CHECKER] Error checking emails: {e}")
