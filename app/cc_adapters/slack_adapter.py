"""
Slack Adapter

Pass-through adapter for existing Slack integration.
Preserves existing behavior and ensures backward compatibility.
"""

import logging
from typing import Dict, Any, Tuple, Optional

from app.cc_adapters import ChatAdapter


class SlackAdapter(ChatAdapter):
    """
    Adapter for Slack messages (pass-through).
    
    This adapter preserves existing Slack integration behavior by
    passing Slack messages through unchanged. It ensures backward
    compatibility and maintains the existing agent pipeline.
    """
    
    def adapt(
        self,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Adapt Slack message (pass-through).
        
        Slack messages are already in the correct format, so this adapter
        simply extracts the existing slack_data and message_data from context
        or constructs them from the message.
        
        Args:
            message: Slack message data (from Slack API)
            context: Optional context data (should contain slack_data if available)
            
        Returns:
            Tuple of (slack_data, message_data) in Slack schema format
        """
        # If context provides slack_data, use it
        if context and "slack_data" in context:
            slack_data = context["slack_data"]
        else:
            # Construct minimal slack_data from message
            slack_data = {
                "channel": {
                    "channel_id": message.get("channel"),
                    "channel_name": message.get("channel"),
                    "channel_type": "public_channel",  # Default
                    "members": []
                },
                "members": [],
                "recent_messages": []
            }
        
        # Construct message_data from Slack message
        message_data = {
            "user": message.get("user"),
            "user_id": message.get("user"),
            "user_name": message.get("user_name"),  # May need to be fetched
            "user_text": message.get("text", ""),
            "text": message.get("text", ""),
            "channel": message.get("channel"),
            "channel_id": message.get("channel"),
            "ts": message.get("ts"),
            "message_ts": message.get("ts"),
            "thread_ts": message.get("thread_ts"),
            "files": message.get("files", []),
            "source": "slack"  # Mark source for debugging
        }
        
        logging.debug(f"[SLACK_ADAPTER] Passed through Slack message from user {message.get('user')}")
        
        return (slack_data, message_data)
    
    def get_interface_name(self) -> str:
        """Get the name of the chat interface this adapter handles."""
        return "slack"
    
    def validate_message(self, message: Dict[str, Any]) -> bool:
        """
        Validate that Slack message has required fields.
        
        Args:
            message: Message to validate
            
        Returns:
            bool: True if message is valid, False otherwise
        """
        # Slack messages should have at least channel and user
        return "channel" in message and "user" in message
