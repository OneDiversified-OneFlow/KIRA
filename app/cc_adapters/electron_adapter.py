"""
Electron Adapter

Maps Electron desktop app message format to KIRA's Slack schema format.
"""

import logging
from typing import Dict, Any, Tuple, Optional

from app.cc_adapters import ChatAdapter


class ElectronAdapter(ChatAdapter):
    """
    Adapter for Electron desktop app messages.
    
    Maps Electron message format to Slack schema format so that Electron
    messages can be processed by KIRA's existing agent pipeline.
    """
    
    def adapt(
        self,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Adapt Electron message to Slack schema format.
        
        Expected Electron message format:
        {
            "text": str,              # Message text
            "userId": str,             # User ID
            "userName": str,          # User display name
            "channelId": str,         # Channel/conversation ID
            "timestamp": str,         # ISO timestamp
            "threadId": Optional[str] # Thread ID (optional)
        }
        
        Args:
            message: Electron message data
            context: Optional context data (unused for Electron)
            
        Returns:
            Tuple of (slack_data, message_data) in Slack schema format
            
        Raises:
            ValueError: If required fields are missing
        """
        # Validate required fields
        required_fields = ["text", "userId", "userName", "channelId"]
        for field in required_fields:
            if field not in message:
                raise ValueError(f"Missing required field in Electron message: {field}")
        
        # Extract Electron message fields
        electron_text = message.get("text", "")
        electron_user_id = message.get("userId")
        electron_user_name = message.get("userName")
        electron_channel_id = message.get("channelId")
        electron_timestamp = message.get("timestamp", "")
        electron_thread_id = message.get("threadId")
        
        # Map to Slack message_data format
        message_data = {
            "user": electron_user_id,
            "user_id": electron_user_id,
            "user_name": electron_user_name,
            "user_text": electron_text,
            "text": electron_text,
            "channel": electron_channel_id,
            "channel_id": electron_channel_id,
            "ts": electron_timestamp,
            "message_ts": electron_timestamp,
            "thread_ts": electron_thread_id if electron_thread_id else None,
            "files": message.get("files", []),
            "source": "electron"  # Mark source for debugging
        }
        
        # Map to Slack slack_data format
        # Electron doesn't have rich channel/member context, so we create minimal structure
        slack_data = {
            "channel": {
                "channel_id": electron_channel_id,
                "channel_name": electron_channel_id,  # Use ID as name if not provided
                "channel_type": "dm",  # Default to DM for Electron
                "members": [electron_user_id]  # Single user in conversation
            },
            "members": [
                {
                    "user_id": electron_user_id,
                    "user_name": electron_user_name,
                    "display_name": electron_user_name
                }
            ],
            "recent_messages": [],  # Electron doesn't provide recent messages
            "source": "electron"  # Mark source for debugging
        }
        
        logging.debug(f"[ELECTRON_ADAPTER] Adapted message from user {electron_user_name} ({electron_user_id})")
        
        return (slack_data, message_data)
    
    def get_interface_name(self) -> str:
        """Get the name of the chat interface this adapter handles."""
        return "electron"
    
    def validate_message(self, message: Dict[str, Any]) -> bool:
        """
        Validate that Electron message has required fields.
        
        Args:
            message: Message to validate
            
        Returns:
            bool: True if message is valid, False otherwise
        """
        required_fields = ["text", "userId", "userName", "channelId"]
        return all(field in message for field in required_fields)
