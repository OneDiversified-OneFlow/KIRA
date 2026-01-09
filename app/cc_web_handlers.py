"""
Web Message Handlers

Handles web chat messages through KIRA's agent pipeline,
capturing responses instead of posting to Slack.
"""

import logging
from typing import Optional, Dict, Any

from app.cc_utils.language_helper import detect_language
from app.cc_agents.bot_call_detector import call_bot_call_detector
from app.cc_agents.answer_aggregator import call_answer_aggregator
from app.cc_agents.memory_retriever import call_memory_retriever
from app.cc_agents.simple_chat import call_simple_chat
from app.cc_agents.proactive_confirm import call_proactive_confirm
from app.cc_agents.proactive_suggester import call_proactive_suggester
from app.cc_agents.operator.agent import call_operator
from app.config.settings import get_settings

logger = logging.getLogger(__name__)

# Global response storage for web messages
_web_responses: Dict[str, str] = {}


def _capture_web_response(channel_id: str, response_text: str):
    """Capture response text for web messages instead of posting to Slack."""
    _web_responses[channel_id] = response_text
    logger.info(f"[WEB_HANDLER] Captured response for {channel_id}: {response_text[:100]}...")


def get_web_response(channel_id: str) -> Optional[str]:
    """Get captured response for a web message."""
    return _web_responses.pop(channel_id, None)


async def process_web_message(
    message_text: str,
    user_id: str = "web-user-001",
    user_name: str = "Web User",
    channel_id: str = "web-channel-001",
    thread_id: Optional[str] = None,
    persona_name: Optional[str] = None,
    slack_data: Optional[Dict[str, Any]] = None,
    message_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Process a web message through KIRA's agent pipeline.
    
    This function follows the same logic as _process_message_logic but:
    1. Uses web-adapted message data
    2. Captures responses instead of posting to Slack
    3. Returns the response text directly
    
    Args:
        message_text: User's message text
        user_id: Web user ID
        user_name: Web user name
        channel_id: Web channel ID
        thread_id: Optional thread ID
        persona_name: Optional persona name for enhanced context injection
        slack_data: Pre-adapted slack_data (optional)
        message_data: Pre-adapted message_data (optional)
    
    Returns:
        str: Response text from KIRA
    """
    logger.info(f"[WEB_HANDLER] Processing web message from {user_name}: {message_text[:50]}...")
    
    # Create message_data if not provided
    if not message_data:
        message_data = {
            "user_id": user_id,
            "user_name": user_name,
            "user_text": message_text,
            "channel_id": channel_id,
            "thread_ts": thread_id,
            "message_ts": f"web-{channel_id}-{thread_id or 'main'}"
        }
    
    # Create slack_data if not provided (minimal structure for web)
    if not slack_data:
        slack_data = {
            "channel": {
                "channel_id": channel_id,
                "channel_type": "web",  # Web interface
                "channel_name": "Web Chat"
            },
            "messages": []
        }
    
    # Proactive Confirm check
    logger.info(f"[WEB_HANDLER] Checking for pending confirms")
    approved, original_message = await call_proactive_confirm(
        message_text, channel_id, user_id, thread_id
    )
    
    if approved and original_message:
        logger.info(f"[WEB_HANDLER] User approved pending confirm")
        # Process original message instead
        message_text = original_message.get("user_text", message_text)
        message_data = original_message
    
    # For web, we always treat it as a bot call (no need for bot_call_detector)
    # But we can still check if it's a simple question
    
    # Response aggregation check
    logger.info(f"[WEB_HANDLER] Checking answer aggregator")
    is_answer_completed = await call_answer_aggregator(message_text, message_data)
    if is_answer_completed:
        logger.info(f"[WEB_HANDLER] Answer aggregator handled the message")
        response = get_web_response(channel_id)
        if response:
            return response
        return "I've processed your request."
    
    # Memory retrieval with persona support
    logger.info(f"[WEB_HANDLER] Retrieving memory with persona: {persona_name}")
    memory_query = f"""Please gather and provide the memory needed to fulfill user {user_name}({user_id})'s request '{message_text}' in channel {channel_id}.
Be sure to include **guidelines** and information (channel_id, user_id, user_name) about this channel and requesting user."""
    
    retrieved_memory = await call_memory_retriever(
        memory_query,
        slack_data,
        message_data,
        persona_name=persona_name  # Pass persona to enhanced context injection
    )
    logger.info(f"[WEB_HANDLER] Memory retrieved: {retrieved_memory[:100] if retrieved_memory else 'None'}...")
    
    # Try simple_chat first
    logger.info(f"[WEB_HANDLER] Trying simple_chat")
    
    # For web, we need to modify simple_chat to capture responses
    # Since simple_chat uses Slack MCP tools, we'll need to either:
    # 1. Create a web-specific simple_chat that returns text
    # 2. Mock the Slack MCP server to capture responses
    # 3. Use operator directly for web messages
    
    # For now, let's try simple_chat and see if we can capture its response
    # If it doesn't work, we'll fall back to operator
    
    try:
        # Note: simple_chat will try to use Slack MCP tools, which won't work for web
        # We'll need to handle this differently
        is_simple_completed = await call_simple_chat(
            message_text,
            slack_data,
            message_data,
            retrieved_memory
        )
        
        if is_simple_completed:
            logger.info(f"[WEB_HANDLER] Simple chat handled the message")
            # Check if response was captured
            response = get_web_response(channel_id)
            if response:
                return response
            # If not captured, simple_chat might have posted to Slack (which we don't have)
            # Fall through to operator
    except Exception as e:
        logger.warning(f"[WEB_HANDLER] Simple chat failed (expected for web): {e}")
        # Fall through to operator
    
    # For web messages, use operator directly since simple_chat requires Slack
    logger.info(f"[WEB_HANDLER] Using operator for web message")
    
    try:
        # Call operator which should work better for web
        operator_response = await call_operator(
            message_text,
            slack_data,
            message_data,
            retrieved_memory
        )
        
        if operator_response:
            return operator_response
    except Exception as e:
        logger.error(f"[WEB_HANDLER] Operator failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Fallback response
    return f"I received your message: '{message_text}'. I'm processing it, but the full agent pipeline requires additional setup for web messages."
