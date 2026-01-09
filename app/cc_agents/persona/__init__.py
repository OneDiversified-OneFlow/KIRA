"""
Persona System

This module provides persona management and injection capabilities for KIRA.
Personas allow agents to adopt different communication styles, tones, and
behavioral traits based on configuration.
"""

from app.cc_agents.persona.persona_manager import PersonaManager
from app.cc_agents.persona.persona_injector import inject_persona_overlay

__all__ = ["PersonaManager", "inject_persona_overlay"]
