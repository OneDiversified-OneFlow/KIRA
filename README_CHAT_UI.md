# KIRA Chat UI - Testing Interface

A simple web-based chat interface for testing the enhanced context injection system, persona system, and adapter layer.

## Quick Start

### Option 1: Standalone Test Server (Recommended for Testing)

```bash
cd /tmp/KIRA
python3 start_chat_server.py
```

Then open your browser to: **http://127.0.0.1:8000/chat**

### Option 2: Full KIRA Web Interface

If you have the full KIRA environment running:

```bash
# Set environment variable to enable web interface
export WEB_INTERFACE_ENABLED=true

# Start KIRA (which includes the web interface)
python3 -m app.main
```

Then access: **http://localhost:8000/chat** (or https://localhost:8000 if SSL is configured)

## Features

### ✅ Enhanced Context Injection
- Automatically uses KIRA's filesystem memories
- Integrates OneFlow data (mocked initially)
- Supports persona overlays

### ✅ Persona System
- Select personas from dropdown menu
- Test different communication styles
- See persona overlays in action

### ✅ Adapter Layer
- Web messages automatically adapted to Slack schema
- Uses Electron adapter for web interface
- Seamless integration with KIRA's agent pipeline

## API Endpoints

### POST `/api/chat/message`
Send a chat message.

**Request:**
```json
{
  "text": "What is the project status?",
  "userId": "web-user-001",
  "userName": "Web User",
  "channelId": "web-channel-001",
  "persona": "direct_professional"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Response text...",
  "timestamp": "2025-01-27T10:00:00Z",
  "persona_used": "direct_professional"
}
```

### GET `/api/chat/personas`
List available personas.

**Response:**
```json
{
  "success": true,
  "personas": [
    {
      "name": "direct_professional",
      "display_name": "Direct Professional",
      "communication_style": "direct",
      "tone": "professional",
      "traits": ["concise", "factual", "action-oriented"]
    }
  ]
}
```

## Testing Without Full KIRA Environment

The standalone test server (`start_chat_server.py`) works without requiring:
- Claude SDK
- Slack tokens
- Full KIRA configuration

It will:
- ✅ Load and display personas
- ✅ Test adapter layer (Electron adapter)
- ✅ Test context assembler (filesystem + OneFlow sources)
- ⚠️ Return simplified responses (full agent pipeline requires KIRA environment)

## Architecture

```
Web Browser
    ↓
Chat UI (chat.html)
    ↓
FastAPI Server (/api/chat/message)
    ↓
Adapter Router (Electron Adapter)
    ↓
Enhanced Context Injection
    ├─ Filesystem Source (KIRA memories)
    ├─ OneFlow Source (OneFlow data)
    └─ Persona Source (Persona overlays)
    ↓
Context Assembler
    ↓
Memory Retriever (if available)
    ↓
Agent Pipeline (if full KIRA environment)
    ↓
Response
```

## Troubleshooting

### Server won't start
- Check if port 8000 is available: `lsof -i :8000`
- Install dependencies: `pip install fastapi uvicorn`

### Personas not loading
- Check that persona files exist in `app/config/personas/`
- Run `python3 test_persona_simple.py` to verify persona system

### Messages return echo only
- This is expected if full KIRA environment is not set up
- The adapter layer and context injection are still being tested
- Full responses require Claude SDK and KIRA configuration

### CORS errors
- The test server includes CORS middleware
- If accessing from different origin, check CORS settings

## Next Steps

1. **Full KIRA Integration**: Connect to actual KIRA agent pipeline
2. **OneFlow API**: Replace mocked OneFlow source with real API calls
3. **Authentication**: Add user authentication for production use
4. **WebSocket**: Add real-time message streaming
5. **History**: Add conversation history and context
