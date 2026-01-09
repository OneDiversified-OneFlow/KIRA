# Enhanced Context Injection System

**Last Updated**: 2025-01-27  
**Status**: Implemented

## Overview

The Enhanced Context Injection System allows KIRA to assemble context from multiple sources before injecting it into agent prompts. This system extends KIRA's existing memory retrieval mechanism to include:

- **KIRA Filesystem Memories**: Existing memory retrieval from filesystem (preserved)
- **OneFlow Data**: Context from OneFlow tasks, projects, and users (mocked initially, API later)
- **Persona Overlays**: Configurable agent personalities (optional)

## Architecture

### Context Sources

Context sources implement the `ContextSource` interface and provide context from various origins:

```python
from app.cc_agents.context_sources import ContextSource

class MyContextSource(ContextSource):
    async def get_context(self, search_query, slack_data=None, message_data=None, **kwargs) -> str:
        # Retrieve and return context string
        return context_string
    
    def get_source_name(self) -> str:
        return "my_source"
```

### Context Assembler

The `ContextAssembler` combines context from multiple sources:

```python
from app.cc_agents.context_assembler import ContextAssembler
from app.cc_agents.context_sources.filesystem_source import FilesystemContextSource
from app.cc_agents.context_sources.oneflow_source import OneFlowContextSource

# Create assembler
assembler = ContextAssembler()

# Add sources
assembler.add_source(FilesystemContextSource())
assembler.add_source(OneFlowContextSource())

# Assemble context
context = await assembler.assemble_context(
    search_query="What is the project status?",
    slack_data=slack_data,
    message_data=message_data
)
```

### Integration Point

The enhanced context injection system intercepts `call_memory_retriever()`:

```python
from app.cc_agents.memory_retriever.agent import call_memory_retriever

# Enhanced context injection is automatic
retrieved_memory = await call_memory_retriever(
    search_query="What is the project status?",
    slack_data=slack_data,
    message_data=message_data,
    persona_name="direct_professional"  # Optional
)
```

## Configuration

### Default Sources

By default, the system includes:
1. **FilesystemContextSource**: KIRA's existing memory retrieval
2. **OneFlowContextSource**: OneFlow data (mocked initially)

### Adding Custom Sources

To add a custom context source:

1. Create a new source class:
```python
from app.cc_agents.context_sources import ContextSource

class CustomContextSource(ContextSource):
    async def get_context(self, search_query, slack_data=None, message_data=None, **kwargs) -> str:
        # Your implementation
        return context_string
    
    def get_source_name(self) -> str:
        return "custom"
```

2. Add to context assembler:
```python
assembler.add_source(CustomContextSource())
```

## Examples

### Basic Usage

```python
# Enhanced context injection is automatic
memory = await call_memory_retriever(
    "What tasks are in progress?",
    slack_data=slack_data,
    message_data=message_data
)
```

### With Persona

```python
# Include persona in context
memory = await call_memory_retriever(
    "Hello, how are you?",
    slack_data=slack_data,
    message_data=message_data,
    persona_name="friendly_casual"
)
```

### Custom Assembler

```python
from app.cc_agents.context_assembler import ContextAssembler
from app.cc_agents.context_sources.filesystem_source import FilesystemContextSource

# Create custom assembler with only filesystem source
assembler = ContextAssembler()
assembler.add_source(FilesystemContextSource())

context = await assembler.assemble_context(
    search_query="What did we decide?",
    slack_data=slack_data,
    message_data=message_data
)
```

## Error Handling

The system handles source failures gracefully:

- If a source fails, other sources continue to provide context
- If all sources fail, the system falls back to original memory retrieval
- Sources can check availability with `is_available()`

## Backward Compatibility

The enhanced context injection system is **fully backward compatible**:

- Existing code continues to work without modification
- Falls back to original behavior if enhanced context unavailable
- All call sites receive the same function signature

## Future Enhancements

- **API Integration**: Replace mocked OneFlow data with real API calls
- **Database Sources**: Add database-backed context sources
- **Caching**: Add context caching for performance
- **Source Prioritization**: Allow sources to specify priority/order
