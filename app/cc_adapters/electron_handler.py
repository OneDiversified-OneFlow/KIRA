"""
Electron Message Handler

Handles messages from Electron desktop app and routes them through
the adapter layer to the existing agent pipeline.
"""

import logging
from typing import Dict, Any, Optional

from app.cc_adapters.adapter_router import get_adapter_router
from app.cc_slack_handlers import _process_message_logic


async def handle_electron_message(
    electron_message: Dict[str, Any],
    client: Optional[Any] = None
) -> None:
    """
    Handle message from Electron desktop app.
    
    This function adapts Electron messages to Slack schema format and
    routes them through the existing agent pipeline.
    
    Args:
        electron_message: Electron message data
        client: Optional Slack client (not used for Electron, but kept for compatibility)
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Get adapter router
        router = get_adapter_router()
        
        # Adapt Electron message to Slack schema
        slack_data, message_data = router.adapt_message(
            electron_message,
            source="electron"
        )
        
        logger.info(f"[ELECTRON_HANDLER] Processing Electron message from {message_data.get('user_name')}")
        
        # Create a mock Slack message object for compatibility with _process_message_logic
        # The adapter has already converted everything to the right format
        slack_message = {
            "channel": message_data.get("channel_id"),
            "user": message_data.get("user_id"),
            "text": message_data.get("text", ""),
            "ts": message_data.get("message_ts"),
            "thread_ts": message_data.get("thread_ts"),
            "files": message_data.get("files", [])
        }
        
        # Process through existing message handler
        # Note: _process_message_logic expects a Slack client, but for Electron
        # we can pass None or a mock client since we've already adapted the data
        await _process_message_logic(slack_message, client)
        
    except Exception as e:
        logger.error(f"[ELECTRON_HANDLER] Error processing Electron message: {e}")
        raise
