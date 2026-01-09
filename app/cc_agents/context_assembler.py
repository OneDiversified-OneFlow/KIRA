"""
Context Assembler

Assembles context from multiple sources (filesystem, OneFlow, persona, etc.)
into a unified context string for injection into agent prompts.
"""

import logging
from typing import List, Optional, Dict, Any

from app.cc_agents.context_sources import ContextSource, ContextSourceError


class ContextAssembler:
    """
    Assembles context from multiple sources into a unified string.
    
    Takes a list of context sources and assembles their outputs into a single
    context string. Handles source failures gracefully (continues with available sources).
    """
    
    def __init__(self, sources: Optional[List[ContextSource]] = None):
        """
        Initialize context assembler.
        
        Args:
            sources: List of context sources to use. If None, uses default sources.
        """
        self._sources = sources or []
        self._logger = logging.getLogger(__name__)
    
    def add_source(self, source: ContextSource) -> None:
        """
        Add a context source to the assembler.
        
        Args:
            source: Context source to add
        """
        if not isinstance(source, ContextSource):
            raise TypeError(f"Source must be an instance of ContextSource, got {type(source)}")
        
        self._sources.append(source)
        self._logger.debug(f"[CONTEXT_ASSEMBLER] Added source: {source.get_source_name()}")
    
    def remove_source(self, source_name: str) -> None:
        """
        Remove a context source by name.
        
        Args:
            source_name: Name of the source to remove
        """
        self._sources = [s for s in self._sources if s.get_source_name() != source_name]
        self._logger.debug(f"[CONTEXT_ASSEMBLER] Removed source: {source_name}")
    
    async def assemble_context(
        self,
        search_query: str,
        slack_data: Optional[Dict[str, Any]] = None,
        message_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Assemble context from all sources.
        
        Retrieves context from each source and combines them into a unified string.
        Handles source failures gracefully (continues with available sources).
        
        Args:
            search_query: The search query or user message
            slack_data: Slack context data (channel, user, etc.)
            message_data: Current message data
            **kwargs: Additional parameters to pass to sources
            
        Returns:
            str: Unified context string from all sources. Empty string if no context available.
        """
        if not self._sources:
            self._logger.warning("[CONTEXT_ASSEMBLER] No sources configured")
            return ""
        
        context_parts = []
        successful_sources = []
        failed_sources = []
        
        # Retrieve context from each source
        for source in self._sources:
            source_name = source.get_source_name()
            
            # Check if source is available
            if not source.is_available():
                self._logger.debug(f"[CONTEXT_ASSEMBLER] Source {source_name} is not available, skipping")
                continue
            
            try:
                # Get context from source
                context = await source.get_context(
                    search_query=search_query,
                    slack_data=slack_data,
                    message_data=message_data,
                    **kwargs
                )
                
                if context and context.strip():
                    # Add source header for clarity
                    context_parts.append(f"## Context from {source_name.title()}")
                    context_parts.append(context)
                    successful_sources.append(source_name)
                else:
                    self._logger.debug(f"[CONTEXT_ASSEMBLER] Source {source_name} returned empty context")
                    
            except ContextSourceError as e:
                # Context source specific error (log but continue)
                self._logger.warning(f"[CONTEXT_ASSEMBLER] Source {source_name} error: {e}")
                failed_sources.append(source_name)
            except Exception as e:
                # Unexpected error (log but continue with other sources)
                self._logger.error(f"[CONTEXT_ASSEMBLER] Unexpected error from source {source_name}: {e}")
                failed_sources.append(source_name)
        
        # Log assembly results
        if successful_sources:
            self._logger.info(
                f"[CONTEXT_ASSEMBLER] Assembled context from {len(successful_sources)} source(s): "
                f"{', '.join(successful_sources)}"
            )
        
        if failed_sources:
            self._logger.warning(
                f"[CONTEXT_ASSEMBLER] Failed to retrieve context from {len(failed_sources)} source(s): "
                f"{', '.join(failed_sources)}"
            )
        
        # Combine all context parts
        if not context_parts:
            self._logger.debug("[CONTEXT_ASSEMBLER] No context assembled from any source")
            return ""
        
        assembled_context = "\n\n".join(context_parts)
        self._logger.debug(f"[CONTEXT_ASSEMBLER] Assembled {len(assembled_context)} characters of context")
        
        return assembled_context
    
    def get_source_count(self) -> int:
        """Get the number of configured sources."""
        return len(self._sources)
    
    def get_source_names(self) -> List[str]:
        """Get names of all configured sources."""
        return [source.get_source_name() for source in self._sources]
