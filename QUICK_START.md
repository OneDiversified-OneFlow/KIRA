# Quick Start - KIRA Chat UI

## 🚀 Start the Chat Server

```bash
cd /tmp/KIRA
python3 start_chat_server.py
```

## 🌐 Open in Browser

The server will display the actual port when it starts (e.g., 8001, 8002, etc.)

**Chat Interface:** http://127.0.0.1:[PORT]/chat (check server output for actual port)

**Home Page:** http://127.0.0.1:[PORT]/

**API Docs:** http://127.0.0.1:[PORT]/docs

**Note:** You can set a specific port: `PORT=9000 python3 start_chat_server.py`

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
- The server automatically finds an available port
- To use a specific port: `PORT=9000 python3 start_chat_server.py`
- Install dependencies: `pip install fastapi uvicorn`

If personas don't load:
- Run: `python3 test_persona_simple.py`
