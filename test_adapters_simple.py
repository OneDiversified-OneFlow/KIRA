#!/usr/bin/env python3
"""
Simple Adapter Layer Test

Tests adapter layer without requiring full KIRA dependencies.
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_adapters():
    """Test adapter implementations."""
    print("=" * 60)
    print("Adapter Layer Test")
    print("=" * 60)
    
    try:
        from app.cc_adapters.electron_adapter import ElectronAdapter
        from app.cc_adapters.slack_adapter import SlackAdapter
        from app.cc_adapters.adapter_router import get_adapter_router
        
        # Test Electron Adapter
        print("\n1. Testing Electron Adapter...")
        electron_adapter = ElectronAdapter()
        print(f"   ✅ ElectronAdapter created: {electron_adapter.get_interface_name()}")
        
        electron_message = {
            "text": "Hello, KIRA! What is the project status?",
            "userId": "user-123",
            "userName": "Test User",
            "channelId": "channel-456",
            "timestamp": "2025-01-27T10:00:00Z",
            "threadId": "thread-789"
        }
        
        if electron_adapter.validate_message(electron_message):
            print("   ✅ Electron message validation passed")
            slack_data, message_data = electron_adapter.adapt(electron_message)
            print("   ✅ Electron message adapted successfully")
            print(f"      User: {message_data.get('user_name')} ({message_data.get('user_id')})")
            print(f"      Channel: {message_data.get('channel_id')}")
            print(f"      Text: {message_data.get('text')[:50]}...")
            print(f"      Thread: {message_data.get('thread_ts')}")
        else:
            print("   ❌ Electron message validation failed")
            return False
        
        # Test Slack Adapter
        print("\n2. Testing Slack Adapter...")
        slack_adapter = SlackAdapter()
        print(f"   ✅ SlackAdapter created: {slack_adapter.get_interface_name()}")
        
        slack_message = {
            "text": "Hello from Slack!",
            "user": "U123",
            "channel": "C456",
            "ts": "1234567890.123456",
            "thread_ts": "1234567890.000000"
        }
        
        if slack_adapter.validate_message(slack_message):
            print("   ✅ Slack message validation passed")
            slack_data2, message_data2 = slack_adapter.adapt(slack_message)
            print("   ✅ Slack message adapted successfully")
            print(f"      User: {message_data2.get('user_id')}")
            print(f"      Channel: {message_data2.get('channel_id')}")
            print(f"      Text: {message_data2.get('text')}")
        else:
            print("   ❌ Slack message validation failed")
            return False
        
        # Test Adapter Router
        print("\n3. Testing Adapter Router...")
        router = get_adapter_router()
        print("   ✅ AdapterRouter created")
        
        # Test source detection
        detected = router.detect_source(electron_message)
        print(f"   ✅ Detected source for Electron message: {detected}")
        
        detected2 = router.detect_source(slack_message)
        print(f"   ✅ Detected source for Slack message: {detected2}")
        
        # Test router adaptation
        slack_data3, message_data3 = router.adapt_message(electron_message, source="electron")
        print("   ✅ Router adapted Electron message")
        print(f"      Result user: {message_data3.get('user_name')}")
        
        slack_data4, message_data4 = router.adapt_message(slack_message, source="slack")
        print("   ✅ Router adapted Slack message")
        print(f"      Result user: {message_data4.get('user_id')}")
        
        # Test error handling
        print("\n4. Testing error handling...")
        try:
            invalid_message = {"invalid": "message"}
            router.adapt_message(invalid_message)
            print("   ⚠️  Should have raised error for invalid message")
        except (ValueError, Exception) as e:
            print(f"   ✅ Error handling works: {type(e).__name__}")
        
        print("\n" + "=" * 60)
        print("✅ Adapter Layer Test Complete!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_adapters()
    sys.exit(0 if success else 1)
