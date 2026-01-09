#!/usr/bin/env python3
"""
Simple Chat Server for Testing

Starts a minimal FastAPI server for testing the chat interface
without requiring full KIRA environment setup.
"""

import os
import sys
import logging
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError:
    print("❌ FastAPI and uvicorn are required. Install with: pip install fastapi uvicorn")
    sys.exit(1)

# Create FastAPI app
app = FastAPI(title="KIRA Chat Test Server")

# Add CORS middleware for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
static_dir = Path(__file__).parent / "app" / "cc_web_interface" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Import chat router
try:
    from app.cc_web_interface.routes.chat import router as chat_router
    app.include_router(chat_router)
    print("✅ Chat router loaded")
except Exception as e:
    print(f"⚠️  Could not load chat router: {e}")
    print("   Creating minimal chat endpoint...")
    
    @app.post("/api/chat/message")
    async def simple_chat_message(message: dict):
        """Simple chat endpoint for testing."""
        return {
            "success": True,
            "message": f"Echo: {message.get('text', 'No text provided')}",
            "timestamp": "2025-01-27T10:00:00Z"
        }
    
    @app.get("/api/chat/personas")
    async def simple_personas():
        """Simple personas endpoint."""
        try:
            from app.cc_agents.persona.persona_manager import PersonaManager
            manager = PersonaManager()
            persona_names = manager.list_personas()
            personas = []
            for name in persona_names:
                persona = manager.get_persona(name)
                if persona:
                    personas.append({
                        "name": persona.name,
                        "display_name": persona.display_name,
                        "communication_style": persona.communication_style,
                        "tone": persona.tone,
                        "traits": persona.traits
                    })
            return {"success": True, "personas": personas}
        except Exception as e:
            return {"success": False, "personas": [], "error": str(e)}


@app.get("/chat")
async def chat_ui():
    """Chat interface page."""
    html_path = static_dir / "chat.html"
    if html_path.exists():
        with open(html_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(
            content="<h1>Chat Interface</h1><p>chat.html not found. Please ensure the file exists.</p>",
            status_code=404
        )


@app.get("/")
async def root():
    """Root page - redirect to chat."""
    return HTMLResponse(
        content="""
        <html>
            <head><title>KIRA Chat Test Server</title></head>
            <body style="font-family: sans-serif; padding: 40px; text-align: center;">
                <h1>🤖 KIRA Chat Test Server</h1>
                <p>Enhanced Context Injection & Persona System Testing</p>
                <p><a href="/chat" style="display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 8px; margin-top: 20px;">Open Chat Interface</a></p>
                <p style="margin-top: 40px; color: #666;">
                    <a href="/api/chat/personas">View Personas API</a> |
                    <a href="/docs">API Documentation</a>
                </p>
            </body>
        </html>
        """
    )


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy", "service": "KIRA Chat Test Server"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "127.0.0.1")
    
    print("=" * 60)
    print("KIRA Chat Test Server")
    print("=" * 60)
    print(f"\n🚀 Starting server on http://{host}:{port}")
    print(f"📱 Chat Interface: http://{host}:{port}/chat")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"🔍 Health Check: http://{host}:{port}/health")
    print("\nPress Ctrl+C to stop\n")
    
    uvicorn.run(app, host=host, port=port, log_level="info")
