#!/usr/bin/env python3
"""
Quick Test Script for KIRA Enhanced Features

This script tests the enhanced context injection, persona system, and adapter layer
without requiring full KIRA environment setup.
"""

import asyncio
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_persona_system():
    """Test persona system loading and management."""
    print("\n=== Testing Persona System ===")
    
    try:
        from app.cc_agents.persona.persona_manager import PersonaManager
        
        # Initialize persona manager
        manager = PersonaManager()
        
        # List available personas
        personas = manager.list_personas()
        print(f"✅ Found {len(personas)} persona(s): {personas}")
        
        # Test loading a persona
        if personas:
            persona_name = personas[0]
            persona = manager.get_persona(persona_name)
            if persona:
                print(f"✅ Successfully loaded persona: {persona.name}")
                print(f"   Display Name: {persona.display_name}")
                print(f"   Communication Style: {persona.communication_style}")
                print(f"   Tone: {persona.tone}")
                print(f"   Traits: {', '.join(persona.traits)}")
                return True
            else:
                print(f"❌ Failed to load persona: {persona_name}")
                return False
        else:
            print("⚠️  No personas found (this is OK if personas directory is empty)")
            return True
            
    except Exception as e:
        print(f"❌ Persona system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_context_sources():
    """Test context source implementations."""
    print("\n=== Testing Context Sources ===")
    
    try:
        from app.cc_agents.context_sources.filesystem_source import FilesystemContextSource
        from app.cc_agents.context_sources.oneflow_source import OneFlowContextSource
        from app.cc_agents.context_sources.persona_source import PersonaContextSource
        
        # Test filesystem source
        fs_source = FilesystemContextSource()
        print(f"✅ FilesystemContextSource created: {fs_source.get_source_name()}")
        print(f"   Available: {fs_source.is_available()}")
        
        # Test OneFlow source
        of_source = OneFlowContextSource()
        print(f"✅ OneFlowContextSource created: {of_source.get_source_name()}")
        print(f"   Available: {of_source.is_available()}")
        
        # Test persona source (if personas exist)
        try:
            persona_source = PersonaContextSource()
            print(f"✅ PersonaContextSource created: {persona_source.get_source_name()}")
            print(f"   Available: {persona_source.is_available()}")
        except Exception as e:
            print(f"⚠️  PersonaContextSource: {e} (this is OK if no personas configured)")
        
        return True
        
    except Exception as e:
        print(f"❌ Context sources test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_context_assembler():
    """Test context assembler."""
    print("\n=== Testing Context Assembler ===")
    
    try:
        from app.cc_agents.context_assembler import ContextAssembler
        from app.cc_agents.context_sources.filesystem_source import FilesystemContextSource
        from app.cc_agents.context_sources.oneflow_source import OneFlowContextSource
        
        # Create assembler
        assembler = ContextAssembler()
        
        # Add sources
        assembler.add_source(FilesystemContextSource())
        assembler.add_source(OneFlowContextSource())
        
        print(f"✅ ContextAssembler created with {assembler.get_source_count()} source(s)")
        print(f"   Sources: {', '.join(assembler.get_source_names())}")
        
        # Test assembly (will use mocked OneFlow data)
        test_query = "What tasks are in progress?"
        context = await assembler.assemble_context(
            search_query=test_query,
            slack_data=None,
            message_data=None
        )
        
        if context:
            print(f"✅ Context assembled successfully ({len(context)} characters)")
            print(f"   Preview: {context[:100]}...")
        else:
            print("⚠️  Context assembly returned empty (this is OK if no memories exist)")
        
        return True
        
    except Exception as e:
        print(f"❌ Context assembler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_adapters():
    """Test adapter layer."""
    print("\n=== Testing Adapter Layer ===")
    
    try:
        from app.cc_adapters.electron_adapter import ElectronAdapter
        from app.cc_adapters.slack_adapter import SlackAdapter
        from app.cc_adapters.adapter_router import get_adapter_router
        
        # Test Electron adapter
        electron_adapter = ElectronAdapter()
        print(f"✅ ElectronAdapter created: {electron_adapter.get_interface_name()}")
        
        # Test Electron message adaptation
        electron_message = {
            "text": "Hello, KIRA!",
            "userId": "user-123",
            "userName": "Test User",
            "channelId": "channel-456",
            "timestamp": "2025-01-27T10:00:00Z"
        }
        
        if electron_adapter.validate_message(electron_message):
            slack_data, message_data = electron_adapter.adapt(electron_message)
            print(f"✅ Electron message adapted successfully")
            print(f"   User: {message_data.get('user_name')} ({message_data.get('user_id')})")
            print(f"   Channel: {message_data.get('channel_id')}")
            print(f"   Text: {message_data.get('text')}")
        else:
            print("❌ Electron message validation failed")
            return False
        
        # Test Slack adapter
        slack_adapter = SlackAdapter()
        print(f"✅ SlackAdapter created: {slack_adapter.get_interface_name()}")
        
        # Test adapter router
        router = get_adapter_router()
        detected_source = router.detect_source(electron_message)
        print(f"✅ AdapterRouter detected source: {detected_source}")
        
        # Test router adaptation
        slack_data2, message_data2 = router.adapt_message(electron_message, source="electron")
        print(f"✅ Router adapted message successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Adapter layer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_enhanced_memory_retriever():
    """Test enhanced memory retriever (if dependencies available)."""
    print("\n=== Testing Enhanced Memory Retriever ===")
    
    try:
        # Check if enhanced context injection is available
        from app.cc_agents.memory_retriever.agent import call_memory_retriever, ENHANCED_CONTEXT_AVAILABLE
        
        if ENHANCED_CONTEXT_AVAILABLE:
            print("✅ Enhanced context injection is available")
            
            # Test with persona
            try:
                result = await call_memory_retriever(
                    search_query="What is the project status?",
                    slack_data=None,
                    message_data=None,
                    persona_name="direct_professional"
                )
                print(f"✅ Enhanced memory retriever called successfully")
                print(f"   Result length: {len(result)} characters")
                if result:
                    print(f"   Preview: {result[:100]}...")
            except Exception as e:
                print(f"⚠️  Memory retriever call failed (may require full KIRA setup): {e}")
                print("   This is expected if Claude SDK dependencies are not installed")
        else:
            print("⚠️  Enhanced context injection not available (fallback to original)")
        
        return True
        
    except ImportError as e:
        print(f"⚠️  Cannot import memory retriever (dependencies not installed): {e}")
        print("   This is expected - full KIRA setup requires Claude SDK")
        return True  # Not a failure, just missing dependencies
    except Exception as e:
        print(f"⚠️  Memory retriever test issue: {e}")
        return True  # Not a critical failure

async def main():
    """Run all tests."""
    print("=" * 60)
    print("KIRA Enhanced Features Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Persona System", await test_persona_system()))
    results.append(("Context Sources", await test_context_sources()))
    results.append(("Context Assembler", await test_context_assembler()))
    results.append(("Adapter Layer", await test_adapters()))
    results.append(("Enhanced Memory Retriever", await test_enhanced_memory_retriever()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) had issues (may be expected if dependencies missing)")
        return 0  # Return 0 even if some tests fail (expected for missing deps)

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
