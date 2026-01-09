"""
Persona Injector

Injects persona prompt overlay into system prompts.
Integrates with enhanced context injection system.
"""

import logging
from typing import Optional

from app.cc_agents.persona.persona_manager import PersonaManager, Persona


# Global persona manager instance (lazy initialization)
_persona_manager: Optional[PersonaManager] = None


def get_persona_manager() -> PersonaManager:
    """
    Get or create global persona manager instance.
    
    Returns:
        PersonaManager instance
    """
    global _persona_manager
    if _persona_manager is None:
        _persona_manager = PersonaManager()
    return _persona_manager


def inject_persona_overlay(
    system_prompt: str,
    persona_name: Optional[str] = None,
    persona: Optional[Persona] = None
) -> str:
    """
    Inject persona overlay into system prompt.
    
    If persona_name is provided, loads persona from manager.
    If persona object is provided, uses it directly.
    If neither is provided, returns original system prompt unchanged.
    
    Args:
        system_prompt: Base system prompt
        persona_name: Name of persona to inject (optional)
        persona: Persona object to inject (optional, overrides persona_name)
        
    Returns:
        System prompt with persona overlay injected
    """
    logger = logging.getLogger(__name__)
    
    # Determine which persona to use
    target_persona: Optional[Persona] = None
    
    if persona:
        # Use provided persona object
        target_persona = persona
    elif persona_name:
        # Load persona from manager
        manager = get_persona_manager()
        target_persona = manager.get_persona(persona_name)
        
        if not target_persona:
            logger.warning(f"[PERSONA_INJECTOR] Persona not found: {persona_name}, using original prompt")
            return system_prompt
    
    # If no persona, return original prompt
    if not target_persona:
        return system_prompt
    
    # Inject persona overlay
    persona_overlay = target_persona.prompt_overlay.strip()
    
    # Append persona overlay to system prompt
    # Format: Add persona instructions after base prompt
    enhanced_prompt = f"""{system_prompt}

## Persona Configuration
<persona>
{persona_overlay}
</persona>"""
    
    logger.debug(f"[PERSONA_INJECTOR] Injected persona: {target_persona.name}")
    return enhanced_prompt


def set_persona_manager(manager: PersonaManager) -> None:
    """
    Set custom persona manager instance (for testing).
    
    Args:
        manager: PersonaManager instance to use
    """
    global _persona_manager
    _persona_manager = manager
