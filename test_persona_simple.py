#!/usr/bin/env python3
"""
Simple Persona System Test

Tests persona system without requiring full KIRA dependencies.
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_persona_loading():
    """Test persona loading and configuration."""
    print("=" * 60)
    print("Persona System Test")
    print("=" * 60)
    
    try:
        from app.cc_agents.persona.persona_manager import PersonaManager
        
        # Initialize persona manager
        print("\n1. Initializing PersonaManager...")
        manager = PersonaManager()
        print("   ✅ PersonaManager initialized")
        
        # List available personas
        print("\n2. Listing available personas...")
        personas = manager.list_personas()
        print(f"   ✅ Found {len(personas)} persona(s): {personas}")
        
        if not personas:
            print("\n   ⚠️  No personas found. Creating test persona...")
            # Create a test persona file
            import yaml
            test_persona = {
                "name": "test_persona",
                "display_name": "Test Persona",
                "communication_style": "test",
                "tone": "test",
                "prompt_overlay": "You are a test persona."
            }
            os.makedirs("app/config/personas", exist_ok=True)
            with open("app/config/personas/test_persona.yaml", "w") as f:
                yaml.dump(test_persona, f)
            manager.reload()
            personas = manager.list_personas()
            print(f"   ✅ Created test persona. Now have {len(personas)} persona(s)")
        
        # Test loading each persona
        print("\n3. Testing persona loading...")
        for persona_name in personas:
            persona = manager.get_persona(persona_name)
            if persona:
                print(f"   ✅ Loaded: {persona.name}")
                print(f"      Display Name: {persona.display_name}")
                print(f"      Style: {persona.communication_style}")
                print(f"      Tone: {persona.tone}")
                print(f"      Traits: {', '.join(persona.traits) if persona.traits else 'None'}")
                print(f"      Overlay Length: {len(persona.prompt_overlay)} characters")
            else:
                print(f"   ❌ Failed to load: {persona_name}")
                return False
        
        # Test persona injector
        print("\n4. Testing persona injector...")
        from app.cc_agents.persona.persona_injector import inject_persona_overlay
        
        base_prompt = "You are an AI assistant."
        if personas:
            test_persona_name = personas[0]
            enhanced_prompt = inject_persona_overlay(base_prompt, persona_name=test_persona_name)
            
            if enhanced_prompt != base_prompt:
                print(f"   ✅ Persona overlay injected for: {test_persona_name}")
                print(f"      Original length: {len(base_prompt)}")
                print(f"      Enhanced length: {len(enhanced_prompt)}")
                print(f"      Preview: {enhanced_prompt[:150]}...")
            else:
                print(f"   ⚠️  Persona overlay not applied (may be expected)")
        else:
            print("   ⚠️  No personas to test injection")
        
        print("\n" + "=" * 60)
        print("✅ Persona System Test Complete!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_persona_loading()
    sys.exit(0 if success else 1)
