# Persona System

**Last Updated**: 2025-01-27  
**Status**: Implemented

## Overview

The Persona System allows KIRA to adopt different communication styles, tones, and behavioral traits based on configuration. Personas are injected into agent prompts via the enhanced context injection system.

## Persona Configuration

### Schema

Personas are defined in YAML or JSON files in `app/config/personas/`:

```yaml
name: "direct_professional"
display_name: "Direct Professional"
communication_style: "direct"
tone: "professional"
traits:
  - "concise"
  - "factual"
  - "action-oriented"
prompt_overlay: |
  You are a direct, professional assistant. Be concise and factual.
  Focus on actionable information. Avoid unnecessary pleasantries.
  Get to the point quickly while remaining respectful.
description: "Best for work-related queries requiring quick, factual responses"
tags:
  - "work"
  - "professional"
  - "direct"
```

### Required Fields

- `name`: Unique identifier (used in code)
- `display_name`: Human-readable name
- `communication_style`: Style (e.g., "direct", "friendly", "formal")
- `tone`: Tone (e.g., "professional", "casual", "empathetic")
- `prompt_overlay`: Instructions for how the persona should behave

### Optional Fields

- `traits`: List of behavioral traits
- `description`: When to use this persona
- `tags`: Tags for discovery

## Example Personas

### Direct Professional

```yaml
name: "direct_professional"
display_name: "Direct Professional"
communication_style: "direct"
tone: "professional"
traits:
  - "concise"
  - "factual"
  - "action-oriented"
prompt_overlay: |
  You are a direct, professional assistant. Be concise and factual.
  Focus on actionable information. Avoid unnecessary pleasantries.
  Get to the point quickly while remaining respectful.
```

### Friendly Casual

```yaml
name: "friendly_casual"
display_name: "Friendly Casual"
communication_style: "friendly"
tone: "casual"
traits:
  - "warm"
  - "conversational"
  - "empathetic"
prompt_overlay: |
  You are a friendly, casual assistant. Be warm and conversational.
  Use a friendly tone and show empathy. It's okay to be more relaxed
  and personable in your responses.
```

## Usage

### Using Personas in Code

```python
from app.cc_agents.memory_retriever.agent import call_memory_retriever

# Use persona when retrieving memory
memory = await call_memory_retriever(
    search_query="Hello, how are you?",
    slack_data=slack_data,
    message_data=message_data,
    persona_name="friendly_casual"
)
```

### Loading Personas Programmatically

```python
from app.cc_agents.persona.persona_manager import PersonaManager

# Load persona manager
manager = PersonaManager()

# Get persona
persona = manager.get_persona("direct_professional")

# List all personas
persona_names = manager.list_personas()
```

### Injecting Persona Overlay

```python
from app.cc_agents.persona.persona_injector import inject_persona_overlay

# Inject persona into system prompt
system_prompt = "You are an AI assistant."
enhanced_prompt = inject_persona_overlay(
    system_prompt,
    persona_name="direct_professional"
)
```

## Creating Custom Personas

### Step 1: Create Persona File

Create a new YAML file in `app/config/personas/`:

```yaml
# app/config/personas/my_custom_persona.yaml
name: "my_custom_persona"
display_name: "My Custom Persona"
communication_style: "analytical"
tone: "technical"
traits:
  - "detailed"
  - "precise"
  - "systematic"
prompt_overlay: |
  You are an analytical, technical assistant. Provide detailed explanations
  with precision. Use technical terminology appropriately. Structure
  responses systematically with clear reasoning.
```

### Step 2: Reload Personas

```python
from app.cc_agents.persona.persona_manager import PersonaManager

manager = PersonaManager()
manager.reload()  # Reload from filesystem
```

### Step 3: Use Your Persona

```python
memory = await call_memory_retriever(
    search_query="Explain how this works",
    persona_name="my_custom_persona"
)
```

## Integration with Enhanced Context Injection

Personas are integrated via the `PersonaContextSource`:

```python
from app.cc_agents.context_sources.persona_source import PersonaContextSource
from app.cc_agents.context_assembler import ContextAssembler

assembler = ContextAssembler()
assembler.add_source(PersonaContextSource(persona_name="direct_professional"))

context = await assembler.assemble_context(
    search_query="What is the status?",
    persona_name="direct_professional"
)
```

## Best Practices

1. **Clear Instructions**: Write persona overlays with clear, actionable instructions
2. **Consistent Style**: Maintain consistent communication style throughout the overlay
3. **Test Personas**: Test personas with various query types to ensure they behave as expected
4. **Document Use Cases**: Add descriptions and tags to help users choose appropriate personas

## Troubleshooting

### Persona Not Found

If a persona is not found, the system falls back to no persona (original behavior):

```python
# This will log a warning but continue without persona
memory = await call_memory_retriever(
    search_query="Hello",
    persona_name="nonexistent_persona"  # Warning logged, no persona applied
)
```

### Persona Not Loading

Check:
1. File is in `app/config/personas/` directory
2. File has `.yaml` or `.json` extension
3. Required fields are present
4. YAML/JSON syntax is valid

### Persona Not Applied

Verify:
1. Persona name is correct (case-sensitive)
2. Persona manager has loaded the persona (`manager.list_personas()`)
3. Persona is passed to `call_memory_retriever()` or context assembler
