"""
Adapter Router

Routes messages to appropriate adapters based on message source.
"""

import logging
from typing import Dict, Any, Tuple, Optional

from app.cc_adapters import ChatAdapter
from app.cc_adapters.slack_adapter import SlackAdapter
from app.cc_adapters.electron_adapter import ElectronAdapter


class AdapterRouter:
    """
    Routes messages to appropriate adapters based on source detection.
    """
    
    def __init__(self):
        """Initialize adapter router with default adapters."""
        self._adapters: Dict[str, ChatAdapter] = {
            "slack": SlackAdapter(),
            "electron": ElectronAdapter()
        }
        self._logger = logging.getLogger(__name__)
    
    def detect_source(self, message: Dict[str, Any]) -> str:
        """
        Detect message source from message format.
        
        Args:
            message: Message data
            
        Returns:
            str: Source name ("slack", "electron", or "unknown")
        """
        # Check for explicit source marker
        if "source" in message:
            source = message["source"]
            if source in self._adapters:
                return source
        
        # Detect by field presence
        # Electron messages have "userId", "userName", "channelId"
        # Slack messages have "user", "channel", "ts"
        if "userId" in message and "userName" in message and "channelId" in message:
            return "electron"
        elif "user" in message and "channel" in message and "ts" in message:
            return "slack"
        else:
            # Default to Slack for backward compatibility
            self._logger.warning("[ADAPTER_ROUTER] Could not detect source, defaulting to Slack")
            return "slack"
    
    def adapt_message(
        self,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Adapt message to Slack schema format using appropriate adapter.
        
        Args:
            message: Interface-specific message data
            context: Optional context data
            source: Optional explicit source (if not provided, will be detected)
            
        Returns:
            Tuple of (slack_data, message_data) in Slack schema format
            
        Raises:
            ValueError: If source is unknown or message is invalid
        """
        # Detect source if not provided
        if not source:
            source = self.detect_source(message)
        
        # Get adapter
        adapter = self._adapters.get(source)
        if not adapter:
            raise ValueError(f"Unknown message source: {source}")
        
        # Validate message
        if not adapter.validate_message(message):
            raise ValueError(f"Invalid message format for {source} adapter")
        
        # Adapt message
        try:
            slack_data, message_data = adapter.adapt(message, context)
            self._logger.debug(f"[ADAPTER_ROUTER] Adapted {source} message successfully")
            return (slack_data, message_data)
        except Exception as e:
            self._logger.error(f"[ADAPTER_ROUTER] Error adapting {source} message: {e}")
            raise
    
    def register_adapter(self, source: str, adapter: ChatAdapter) -> None:
        """
        Register a custom adapter.
        
        Args:
            source: Source name
            adapter: Adapter instance
        """
        if not isinstance(adapter, ChatAdapter):
            raise TypeError(f"Adapter must be an instance of ChatAdapter, got {type(adapter)}")
        
        self._adapters[source] = adapter
        self._logger.debug(f"[ADAPTER_ROUTER] Registered adapter for source: {source}")


# Global adapter router instance
_adapter_router: Optional[AdapterRouter] = None


def get_adapter_router() -> AdapterRouter:
    """
    Get or create global adapter router instance.
    
    Returns:
        AdapterRouter instance
    """
    global _adapter_router
    if _adapter_router is None:
        _adapter_router = AdapterRouter()
    return _adapter_router
