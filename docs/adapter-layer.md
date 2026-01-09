# Adapter Layer

**Last Updated**: 2025-01-27  
**Status**: Implemented

## Overview

The Adapter Layer enables KIRA to work with multiple chat interfaces by mapping interface-specific message formats to KIRA's internal Slack schema format. This allows the agent pipeline to work with any chat interface without modification.

## Architecture

### ChatAdapter Interface

All adapters implement the `ChatAdapter` abstract base class:

```python
from app.cc_adapters import ChatAdapter

class MyAdapter(ChatAdapter):
    def adapt(self, message, context=None):
        # Convert interface-specific message to Slack schema
        slack_data, message_data = self._convert(message)
        return (slack_data, message_data)
    
    def get_interface_name(self):
        return "my_interface"
    
    def validate_message(self, message):
        # Validate message format
        return required_fields_present(message)
```

### Adapter Router

The `AdapterRouter` automatically detects message source and routes to the appropriate adapter:

```python
from app.cc_adapters.adapter_router import get_adapter_router

router = get_adapter_router()
slack_data, message_data = router.adapt_message(
    message,
    source="electron"  # Optional: auto-detected if not provided
)
```

## Built-in Adapters

### Slack Adapter

The Slack adapter is a pass-through that preserves existing Slack integration:

```python
from app.cc_adapters.slack_adapter import SlackAdapter

adapter = SlackAdapter()
slack_data, message_data = adapter.adapt(
    slack_message,
    context={"slack_data": existing_slack_data}
)
```

**Features**:
- Preserves existing Slack behavior
- No changes to existing functionality
- Backward compatible

### Electron Adapter

The Electron adapter maps Electron desktop app messages to Slack schema:

```python
from app.cc_adapters.electron_adapter import ElectronAdapter

adapter = ElectronAdapter()
slack_data, message_data = adapter.adapt({
    "text": "Hello, KIRA!",
    "userId": "user-123",
    "userName": "Test User",
    "channelId": "channel-456",
    "timestamp": "2025-01-27T10:00:00Z"
})
```

**Mapping**:
- `userId` → `user_id`
- `userName` → `user_name`
- `channelId` → `channel_id`
- `text` → `text`
- `timestamp` → `ts` / `message_ts`
- `threadId` → `thread_ts` (optional)

## Creating Custom Adapters

### Step 1: Implement ChatAdapter

```python
from app.cc_adapters import ChatAdapter
from typing import Dict, Any, Tuple, Optional

class WebAdapter(ChatAdapter):
    def adapt(
        self,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        # Extract web message fields
        web_text = message.get("content")
        web_user_id = message.get("author", {}).get("id")
        web_user_name = message.get("author", {}).get("name")
        web_conversation_id = message.get("conversationId")
        
        # Map to Slack schema
        message_data = {
            "user_id": web_user_id,
            "user_name": web_user_name,
            "user_text": web_text,
            "text": web_text,
            "channel_id": web_conversation_id,
            "channel": web_conversation_id,
            "ts": message.get("timestamp"),
            "message_ts": message.get("timestamp"),
            "source": "web"
        }
        
        slack_data = {
            "channel": {
                "channel_id": web_conversation_id,
                "channel_name": web_conversation_id,
                "channel_type": "dm",
                "members": [web_user_id]
            },
            "members": [{"user_id": web_user_id, "user_name": web_user_name}],
            "recent_messages": [],
            "source": "web"
        }
        
        return (slack_data, message_data)
    
    def get_interface_name(self) -> str:
        return "web"
    
    def validate_message(self, message: Dict[str, Any]) -> bool:
        return "content" in message and "author" in message
```

### Step 2: Register Adapter

```python
from app.cc_adapters.adapter_router import get_adapter_router
from app.cc_adapters.web_adapter import WebAdapter

router = get_adapter_router()
router.register_adapter("web", WebAdapter())
```

### Step 3: Use Adapter

```python
# Adapter router will automatically detect and use your adapter
slack_data, message_data = router.adapt_message(web_message)
```

## Integration

### Slack Handlers

Slack handlers automatically use the adapter router:

```python
# In app/cc_slack_handlers.py
from app.cc_adapters.adapter_router import get_adapter_router

router = get_adapter_router()
slack_data, message_data = router.adapt_message(
    message,
    context={"slack_data": get_slack_context_data(channel_id)},
    source="slack"
)
```

### Electron Handler

Electron messages are handled via the Electron handler:

```python
from app.cc_adapters.electron_handler import handle_electron_message

await handle_electron_message({
    "text": "Hello, KIRA!",
    "userId": "user-123",
    "userName": "Test User",
    "channelId": "channel-456"
})
```

## Slack Schema Format

All adapters must map to this schema:

### message_data

```python
{
    "user_id": str,           # User identifier
    "user_name": str,         # User display name
    "user_text": str,         # Message text
    "text": str,              # Message text (alias)
    "channel_id": str,        # Channel/conversation identifier
    "channel": str,           # Channel (alias)
    "ts": str,                # Message timestamp
    "message_ts": str,        # Message timestamp (alias)
    "thread_ts": str,         # Thread identifier (optional)
    "files": list,            # File attachments (optional)
    "source": str             # Source identifier (for debugging)
}
```

### slack_data

```python
{
    "channel": {
        "channel_id": str,
        "channel_name": str,
        "channel_type": str,  # "public_channel", "private_channel", "dm", "group_dm"
        "members": list
    },
    "members": [
        {
            "user_id": str,
            "user_name": str,
            "display_name": str
        }
    ],
    "recent_messages": list,
    "source": str             # Source identifier (for debugging)
}
```

## Error Handling

Adapters should handle errors gracefully:

```python
def adapt(self, message, context=None):
    try:
        # Validate message
        if not self.validate_message(message):
            raise ValueError("Invalid message format")
        
        # Convert message
        return self._convert(message)
    except Exception as e:
        logging.error(f"[{self.get_interface_name()}_ADAPTER] Error: {e}")
        raise
```

## Best Practices

1. **Validate Early**: Check message format before processing
2. **Provide Defaults**: Use sensible defaults for missing optional fields
3. **Log Source**: Include `"source"` field in output for debugging
4. **Handle Errors**: Gracefully handle malformed messages
5. **Document Mapping**: Document field mappings in adapter docstring

## Troubleshooting

### Adapter Not Found

If an adapter is not found, the router will raise `ValueError`:

```python
try:
    router.adapt_message(message, source="unknown")
except ValueError as e:
    print(f"Adapter not found: {e}")
```

### Invalid Message Format

Adapters should validate messages:

```python
if not adapter.validate_message(message):
    raise ValueError("Invalid message format")
```

### Schema Mismatch

Ensure your adapter outputs match the Slack schema format exactly. Check:
- Required fields are present
- Field names match schema
- Data types are correct
