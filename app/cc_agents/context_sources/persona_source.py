"""
Persona Context Source

Provides persona overlay as a context source for enhanced context injection.
"""

import logging
from typing import Optional, Dict, Any

from app.cc_agents.context_sources import ContextSource
from app.cc_agents.persona.persona_manager import PersonaManager, Persona
from app.cc_agents.persona.persona_injector import get_persona_manager


class PersonaContextSource(ContextSource):
    """
    Context source that provides persona overlay.
    
    This source retrieves persona configuration and returns the prompt overlay
    as context. The persona overlay is then injected into system prompts.
    """
    
    def __init__(self, persona_name: Optional[str] = None, persona_manager: Optional[PersonaManager] = None):
        """
        Initialize persona context source.
        
        Args:
            persona_name: Name of persona to use (optional, can be set per request)
            persona_manager: PersonaManager instance (optional, uses global if not provided)
        """
        self._source_name = "persona"
        self._default_persona_name = persona_name
        self._persona_manager = persona_manager or get_persona_manager()
    
    async def get_context(
        self,
        search_query: str,
        slack_data: Optional[Dict[str, Any]] = None,
        message_data: Optional[Dict[str, Any]] = None,
        persona_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Retrieve persona overlay context.
        
        Args:
            search_query: The search query or user message
            slack_data: Slack context data (channel, user, etc.)
            message_data: Current message data
            persona_name: Name of persona to use (overrides default)
            **kwargs: Additional parameters
            
        Returns:
            str: Persona prompt overlay. Empty string if no persona configured.
        """
        # Determine which persona to use
        target_persona_name = persona_name or self._default_persona_name
        
        if not target_persona_name:
            # No persona specified
            logging.debug("[PERSONA_SOURCE] No persona specified, returning empty context")
            return ""
        
        try:
            # Get persona from manager
            persona = self._persona_manager.get_persona(target_persona_name)
            
            if not persona:
                logging.warning(f"[PERSONA_SOURCE] Persona not found: {target_persona_name}")
                return ""
            
            # Return persona prompt overlay
            overlay = persona.prompt_overlay.strip()
            logging.debug(f"[PERSONA_SOURCE] Retrieved persona overlay for: {persona.name}")
            return overlay
            
        except Exception as e:
            logging.error(f"[PERSONA_SOURCE] Error retrieving persona context: {e}")
            return ""
    
    def get_source_name(self) -> str:
        """Get the name of this context source."""
        return self._source_name
    
    def is_available(self) -> bool:
        """
        Check if persona context source is available.
        
        Returns:
            bool: True if persona manager has personas loaded, False otherwise
        """
        try:
            personas = self._persona_manager.list_personas()
            return len(personas) > 0
        except Exception:
            return False
