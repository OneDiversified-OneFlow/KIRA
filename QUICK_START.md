# Quick Start - KIRA Chat UI

## 🚀 Start the Chat Server

```bash
cd /tmp/KIRA
python3 start_chat_server.py
```

## 🌐 Open in Browser

**Chat Interface:** http://127.0.0.1:8000/chat

**Home Page:** http://127.0.0.1:8000/

**API Docs:** http://127.0.0.1:8000/docs

## ✨ Features to Test

1. **Persona Selection** - Choose from dropdown (friendly_casual, direct_professional)
2. **Enhanced Context Injection** - Messages use KIRA memories + OneFlow data + persona
3. **Adapter Layer** - Web messages automatically adapted to Slack schema
4. **Real-time Chat** - Send messages and see responses

## 📝 Example Messages

- "What is the project status?"
- "Tell me about the current tasks"
- "What are the recent updates?"

## 🔧 Troubleshooting

If the server doesn't start:
- Check port 8000: `lsof -i :8000`
- Install dependencies: `pip install fastapi uvicorn`

If personas don't load:
- Run: `python3 test_persona_simple.py`
