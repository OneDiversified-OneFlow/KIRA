"""
Filesystem Context Source

Wraps KIRA's existing filesystem memory retrieval (slack-memory-retrieval skill)
to provide context from KIRA's memories directory.
"""

import logging
from typing import Optional, Dict, Any

from app.cc_agents.context_sources import ContextSource
from app.cc_agents.memory_retriever.agent import call_memory_retriever


class FilesystemContextSource(ContextSource):
    """
    Context source that retrieves context from KIRA's filesystem memories.
    
    This wraps the existing `call_memory_retriever()` function to provide
    context from KIRA's memories directory via the slack-memory-retrieval skill.
    """
    
    def __init__(self):
        """Initialize filesystem context source."""
        self._source_name = "filesystem"
    
    async def get_context(
        self,
        search_query: str,
        slack_data: Optional[Dict[str, Any]] = None,
        message_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Retrieve context from KIRA's filesystem memories.
        
        This wraps the existing `call_memory_retriever()` function to maintain
        backward compatibility with KIRA's existing memory retrieval mechanism.
        
        Args:
            search_query: The search query or user message
            slack_data: Slack context data (channel, user, etc.)
            message_data: Current message data
            **kwargs: Additional parameters (ignored for filesystem source)
            
        Returns:
            str: Context string from filesystem memories. Empty string if no memories found.
        """
        try:
            # Call existing memory retriever (preserves existing behavior)
            context = await call_memory_retriever(
                search_query=search_query,
                slack_data=slack_data,
                message_data=message_data
            )
            
            # Return empty string if no memories found (matches existing behavior)
            if context == "관련된 메모리가 없습니다.":
                logging.debug(f"[FILESYSTEM_SOURCE] No memories found for query: {search_query[:50]}...")
                return ""
            
            logging.debug(f"[FILESYSTEM_SOURCE] Retrieved {len(context)} characters from filesystem memories")
            return context
            
        except Exception as e:
            logging.error(f"[FILESYSTEM_SOURCE] Error retrieving filesystem context: {e}")
            # Return empty string on error (graceful degradation)
            return ""
    
    def get_source_name(self) -> str:
        """Get the name of this context source."""
        return self._source_name
    
    def is_available(self) -> bool:
        """
        Check if filesystem context source is available.
        
        The filesystem source is always available (it will handle missing
        memories directory gracefully in get_context()).
        
        Returns:
            bool: True (filesystem source is always available)
        """
        return True
