"""
Chat API Routes

Simple chat interface for testing enhanced context injection, persona system, and adapter layer.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.cc_adapters.electron_handler import handle_electron_message
from app.cc_adapters.adapter_router import get_adapter_router

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """Chat message request model."""
    text: str
    userId: Optional[str] = "web-user-001"
    userName: Optional[str] = "Web User"
    channelId: Optional[str] = "web-channel-001"
    timestamp: Optional[str] = None
    threadId: Optional[str] = None
    persona: Optional[str] = None  # Optional persona name


class ChatResponse(BaseModel):
    """Chat response model."""
    success: bool
    message: str
    timestamp: str
    persona_used: Optional[str] = None


@router.post("/message", response_model=ChatResponse)
async def send_message(message: ChatMessage):
    """
    Send a chat message through KIRA's enhanced context injection system.
    
    This endpoint:
    1. Adapts the web message to Slack schema via Electron adapter
    2. Routes through enhanced context injection (KIRA memories + OneFlow data + persona)
    3. Processes through KIRA's agent pipeline
    4. Returns the response
    """
    try:
        # Generate timestamp if not provided
        if not message.timestamp:
            message.timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Create Electron-compatible message
        electron_message = {
            "text": message.text,
            "userId": message.userId,
            "userName": message.userName,
            "channelId": message.channelId,
            "timestamp": message.timestamp,
            "threadId": message.threadId,
            "source": "web"  # Mark as web source
        }
        
        logger.info(f"[CHAT_API] Received message from {message.userName}: {message.text[:50]}...")
        
        # Use adapter router to adapt message
        router_adapter = get_adapter_router()
        slack_data, message_data = router_adapter.adapt_message(
            electron_message,
            source="electron"  # Use electron adapter for web messages
        )
        
        # Process through enhanced context injection system
        # Try to use enhanced memory retriever if available
        try:
            from app.cc_agents.memory_retriever.agent import call_memory_retriever
            
            memory_query = f"User {message.userName} asked: {message.text}"
            retrieved_memory = await call_memory_retriever(
                search_query=memory_query,
                slack_data=slack_data,
                message_data=message_data,
                persona_name=message.persona
            )
            
            # Use retrieved memory as response
            response_text = retrieved_memory if retrieved_memory else "I received your message, but I need the full KIRA environment to generate a complete response."
        except ImportError:
            # Fallback: Use context assembler directly if memory retriever not available
            try:
                from app.cc_agents.context_assembler import ContextAssembler
                from app.cc_agents.context_sources.filesystem_source import FilesystemContextSource
                from app.cc_agents.context_sources.oneflow_source import OneFlowContextSource
                from app.cc_agents.context_sources.persona_source import PersonaContextSource
                from app.cc_agents.persona.persona_manager import PersonaManager
                
                assembler = ContextAssembler()
                assembler.add_source(FilesystemContextSource())
                assembler.add_source(OneFlowContextSource())
                
                if message.persona:
                    persona_manager = PersonaManager()
                    persona = persona_manager.get_persona(message.persona)
                    if persona:
                        persona_source = PersonaContextSource(persona)
                        assembler.add_source(persona_source)
                
                context = await assembler.assemble_context(
                    search_query=message.text,
                    slack_data=slack_data,
                    message_data=message_data,
                    persona_name=message.persona
                )
                
                if context:
                    response_text = f"Enhanced Context Retrieved:\n\n{context}\n\n[Note: This is context assembly only. Full agent pipeline requires KIRA environment.]"
                else:
                    response_text = f"Message received: '{message.text}'\n\n[Note: Enhanced context injection is working, but no context was found. Full agent pipeline requires KIRA environment.]"
            except Exception as e:
                logger.warning(f"[CHAT_API] Could not use enhanced context injection: {e}")
                response_text = f"Message received: '{message.text}'\n\n[Note: Enhanced context injection requires full KIRA environment setup. This is a test response.]"
        
        logger.info(f"[CHAT_API] Response generated ({len(response_text)} characters)")
        
        return ChatResponse(
            success=True,
            message=response_text,
            timestamp=datetime.utcnow().isoformat() + "Z",
            persona_used=message.persona
        )
        
    except Exception as e:
        logger.error(f"[CHAT_API] Error processing message: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.get("/personas")
async def list_personas():
    """List available personas."""
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
        
        return {
            "success": True,
            "personas": personas
        }
    except Exception as e:
        logger.error(f"[CHAT_API] Error listing personas: {e}")
        return {
            "success": False,
            "personas": [],
            "error": str(e)
        }
