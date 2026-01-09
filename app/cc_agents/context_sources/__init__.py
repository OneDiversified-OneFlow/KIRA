"""
Context Sources Abstraction

This module defines the abstraction interface for context sources in the enhanced
context injection system. Context sources provide context from various origins:
- Filesystem (KIRA memories)
- OneFlow data (tasks, projects, users)
- Persona overlays
- Future sources (database, API, etc.)

All context sources implement the ContextSource interface, which allows them to
be assembled into a unified context string for injection into agent prompts.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class ContextSource(ABC):
    """
    Abstract base class for context sources.
    
    Context sources provide context from various origins (filesystem, API, database, etc.)
    and can be assembled into a unified context string for injection into agent prompts.
    """
    
    @abstractmethod
    async def get_context(
        self,
        search_query: str,
        slack_data: Optional[Dict[str, Any]] = None,
        message_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Retrieve context from this source.
        
        Args:
            search_query: The search query or user message
            slack_data: Slack context data (channel, user, etc.)
            message_data: Current message data
            **kwargs: Additional context-specific parameters
            
        Returns:
            str: Context string from this source. Empty string if no context available.
        """
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """
        Get the name of this context source (for logging/debugging).
        
        Returns:
            str: Source name (e.g., "filesystem", "oneflow", "persona")
        """
        pass
    
    def is_available(self) -> bool:
        """
        Check if this context source is available.
        
        Override this method if the source has availability requirements
        (e.g., API connectivity, file existence).
        
        Returns:
            bool: True if source is available, False otherwise
        """
        return True


class ContextSourceError(Exception):
    """Base exception for context source errors."""
    pass


class ContextSourceUnavailableError(ContextSourceError):
    """Raised when a context source is unavailable."""
    pass


class ContextSourceTimeoutError(ContextSourceError):
    """Raised when a context source operation times out."""
    pass
