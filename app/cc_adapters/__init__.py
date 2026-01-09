"""
Chat Adapters

This module provides adapters for different chat interfaces (Slack, Electron, Web, etc.)
to convert interface-specific message formats to KIRA's internal Slack schema format.

The adapter pattern allows KIRA's agent pipeline to work with any chat interface
by mapping interface-specific data structures to the common Slack schema.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional


class ChatAdapter(ABC):
    """
    Abstract base class for chat interface adapters.
    
    Adapters convert interface-specific message formats (Electron, Web, etc.)
    to KIRA's internal Slack schema format (`slack_data` and `message_data`).
    
    This allows the agent pipeline to work with any chat interface without
    modification, as long as an adapter exists to map the interface format
    to the Slack schema.
    """
    
    @abstractmethod
    def adapt(
        self,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Adapt interface-specific message to Slack schema format.
        
        Args:
            message: Interface-specific message data (format depends on adapter)
            context: Optional context data (interface-specific)
            
        Returns:
            Tuple of (slack_data, message_data) in Slack schema format:
            - slack_data: Channel, members, recent messages, etc.
            - message_data: Current message (user_id, text, channel_id, etc.)
            
        Raises:
            ValueError: If message format is invalid or required fields are missing
        """
        pass
    
    @abstractmethod
    def get_interface_name(self) -> str:
        """
        Get the name of the chat interface this adapter handles.
        
        Returns:
            str: Interface name (e.g., "slack", "electron", "web")
        """
        pass
    
    def validate_message(self, message: Dict[str, Any]) -> bool:
        """
        Validate that message has required fields for this adapter.
        
        Override this method to provide adapter-specific validation.
        
        Args:
            message: Message to validate
            
        Returns:
            bool: True if message is valid, False otherwise
        """
        return True
