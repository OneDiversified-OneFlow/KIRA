#!/usr/bin/env python3
"""
Simple Chat Server for Testing

Starts a minimal FastAPI server for testing the chat interface
without requiring full KIRA environment setup.
"""

import os
import sys
import logging
import socket
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

# Import chat router directly (avoiding routes/__init__.py which imports other routes requiring slack_sdk)
try:
    import importlib.util
    import sys
    from pathlib import Path
    
    # Load chat.py directly without triggering __init__.py
    chat_path = Path(__file__).parent / "app" / "cc_web_interface" / "routes" / "chat.py"
    spec = importlib.util.spec_from_file_location("chat_router", chat_path)
    chat_module = importlib.util.module_from_spec(spec)
    sys.modules["chat_router"] = chat_module
    spec.loader.exec_module(chat_module)
    
    app.include_router(chat_module.router)
    print("✅ Chat router loaded")
except Exception as e:
    print(f"❌ Could not load chat router: {e}")
    import traceback
    traceback.print_exc()
    print("   Server will not function properly without chat router")
    raise


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


def find_free_port(start_port=8000, max_attempts=100):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"Could not find an available port after {max_attempts} attempts")


if __name__ == "__main__":
    # Try to use PORT env var, otherwise find a free port
    if os.environ.get("PORT"):
        port = int(os.environ.get("PORT"))
    else:
        # Find a random available port
        port = find_free_port()
    
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
