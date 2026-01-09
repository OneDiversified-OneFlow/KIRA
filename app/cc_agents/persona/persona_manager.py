"""
Persona Manager

Loads and manages persona configurations from filesystem.
Validates persona schema and provides persona lookup by name.
"""

import logging
import os
import yaml
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

from app.config.settings import get_settings


class Persona:
    """
    Represents a persona configuration.
    
    Attributes:
        name: Unique identifier for the persona
        display_name: Human-readable display name
        communication_style: Communication style (direct, friendly, formal, etc.)
        tone: Tone of communication (professional, casual, empathetic, etc.)
        traits: List of behavioral traits
        prompt_overlay: Instructions for how the persona should behave
        description: Optional description of when to use this persona
        tags: Optional tags for persona discovery
    """
    
    def __init__(
        self,
        name: str,
        display_name: str,
        communication_style: str,
        tone: str,
        prompt_overlay: str,
        traits: Optional[List[str]] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ):
        """Initialize persona."""
        self.name = name
        self.display_name = display_name
        self.communication_style = communication_style
        self.tone = tone
        self.prompt_overlay = prompt_overlay
        self.traits = traits or []
        self.description = description
        self.tags = tags or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert persona to dictionary."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "communication_style": self.communication_style,
            "tone": self.tone,
            "prompt_overlay": self.prompt_overlay,
            "traits": self.traits,
            "description": self.description,
            "tags": self.tags
        }


class PersonaManager:
    """
    Manages persona configurations.
    
    Loads persona configurations from filesystem, validates schema,
    and provides persona lookup by name.
    """
    
    def __init__(self, personas_dir: Optional[str] = None):
        """
        Initialize persona manager.
        
        Args:
            personas_dir: Directory containing persona configuration files.
                         If None, uses default from settings.
        """
        self._logger = logging.getLogger(__name__)
        self._personas: Dict[str, Persona] = {}
        
        # Determine personas directory
        if personas_dir:
            self._personas_dir = Path(personas_dir)
        else:
            settings = get_settings()
            # Default to app/config/personas/ relative to project root
            base_dir = settings.FILESYSTEM_BASE_DIR or os.getcwd()
            self._personas_dir = Path(base_dir) / "app" / "config" / "personas"
        
        # Load personas on initialization
        self._load_personas()
    
    def _load_personas(self) -> None:
        """Load all persona configurations from filesystem."""
        if not self._personas_dir.exists():
            self._logger.warning(f"[PERSONA_MANAGER] Personas directory not found: {self._personas_dir}")
            return
        
        # Load YAML files
        for yaml_file in self._personas_dir.glob("*.yaml"):
            try:
                persona = self._load_persona_from_file(yaml_file)
                if persona:
                    self._personas[persona.name] = persona
                    self._logger.debug(f"[PERSONA_MANAGER] Loaded persona: {persona.name}")
            except Exception as e:
                self._logger.error(f"[PERSONA_MANAGER] Error loading persona from {yaml_file}: {e}")
        
        # Load YML files
        for yml_file in self._personas_dir.glob("*.yml"):
            try:
                persona = self._load_persona_from_file(yml_file)
                if persona:
                    self._personas[persona.name] = persona
                    self._logger.debug(f"[PERSONA_MANAGER] Loaded persona: {persona.name}")
            except Exception as e:
                self._logger.error(f"[PERSONA_MANAGER] Error loading persona from {yml_file}: {e}")
        
        # Load JSON files
        for json_file in self._personas_dir.glob("*.json"):
            try:
                persona = self._load_persona_from_file(json_file)
                if persona:
                    self._personas[persona.name] = persona
                    self._logger.debug(f"[PERSONA_MANAGER] Loaded persona: {persona.name}")
            except Exception as e:
                self._logger.error(f"[PERSONA_MANAGER] Error loading persona from {json_file}: {e}")
        
        self._logger.info(f"[PERSONA_MANAGER] Loaded {len(self._personas)} persona(s)")
    
    def _load_persona_from_file(self, file_path: Path) -> Optional[Persona]:
        """
        Load persona configuration from a file.
        
        Args:
            file_path: Path to persona configuration file (YAML or JSON)
            
        Returns:
            Persona object if valid, None otherwise
            
        Raises:
            ValueError: If persona configuration is invalid
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif file_path.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        # Validate required fields
        required_fields = ['name', 'display_name', 'communication_style', 'tone', 'prompt_overlay']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Create persona object
        persona = Persona(
            name=data['name'],
            display_name=data['display_name'],
            communication_style=data['communication_style'],
            tone=data['tone'],
            prompt_overlay=data['prompt_overlay'],
            traits=data.get('traits', []),
            description=data.get('description'),
            tags=data.get('tags', [])
        )
        
        return persona
    
    def get_persona(self, name: str) -> Optional[Persona]:
        """
        Get persona by name.
        
        Args:
            name: Persona name
            
        Returns:
            Persona object if found, None otherwise
        """
        return self._personas.get(name)
    
    def list_personas(self) -> List[str]:
        """
        List all available persona names.
        
        Returns:
            List of persona names
        """
        return list(self._personas.keys())
    
    def reload(self) -> None:
        """Reload personas from filesystem."""
        self._personas.clear()
        self._load_personas()
