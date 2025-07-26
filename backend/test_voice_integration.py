#!/usr/bin/env python3
"""
Test script for voice integration functionality
"""

import asyncio
import json
import base64
import aiohttp
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_SESSION_ID = "test_voice_session_123"

async def test_voice_endpoints():
    """Test all voice-related endpoints"""
    
    async with aiohttp.ClientSession() as session:
        print("🧪 Testing Babelfish Voice Integration...")
        
        # Test 1: Health check
        print("\n1. Testing health check...")
        async with session.get(f"{BASE_URL}/") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Health check passed: {data['message']}")
                print(f"   Services: {list(data['services'].keys())}")
            else:
                print(f"❌ Health check failed: {response.status}")
                return
        
        # Test 2: Get available voices
        print("\n2. Testing available voices...")
        async with session.get(f"{BASE_URL}/api/voice/available-voices") as response:
            if response.status == 200:
                voices = await response.json()
                print(f"✅ Available voices: {len(voices.get('voices', []))} voices found")
            else:
                print(f"❌ Failed to get voices: {response.status}")
        
        # Test 3: Speech synthesis
        print("\n3. Testing speech synthesis...")
        synthesis_data = {
            "text": "Hello, this is a test of the Babelfish voice synthesis system.",
            "voice_style": "professional_female",
            "speed": 1.0
        }
        
        async with session.post(f"{BASE_URL}/api/voice/synthesize", json=synthesis_data) as response:
            if response.status == 200:
                audio_data = await response.read()
                print(f"✅ Speech synthesis successful: {len(audio_data)} bytes generated")
            else:
                print(f"❌ Speech synthesis failed: {response.status}")
        
        # Test 4: Mock transcription
        print("\n4. Testing transcription...")
        # Create mock audio data (base64 encoded)
        mock_audio = base64.b64encode(b"mock_audio_data_for_testing").decode('utf-8')
        
        transcription_data = {
            "audio_data": mock_audio,
            "language_code": "en-US",
            "media_format": "mp3"
        }
        
        async with session.post(f"{BASE_URL}/api/voice/transcribe", json=transcription_data) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Transcription successful: '{result.get('text', '')}'")
                print(f"   Confidence: {result.get('confidence', 0):.2f}")
            else:
                print(f"❌ Transcription failed: {response.status}")
        
        # Test 5: Transcription jobs
        print("\n5. Testing transcription jobs...")
        async with session.get(f"{BASE_URL}/api/voice/transcription-jobs") as response:
            if response.status == 200:
                jobs = await response.json()
                print(f"✅ Transcription jobs: {len(jobs.get('jobs', []))} jobs found")
            else:
                print(f"❌ Failed to get transcription jobs: {response.status}")
        
        # Test 6: Active transcription sessions
        print("\n6. Testing transcription sessions...")
        async with session.get(f"{BASE_URL}/api/voice/transcription-sessions") as response:
            if response.status == 200:
                sessions = await response.json()
                print(f"✅ Transcription sessions: {sessions.get('total_active', 0)} active sessions")
            else:
                print(f"❌ Failed to get transcription sessions: {response.status}")
        
        # Test 7: Translation with voice context
        print("\n7. Testing translation with voice context...")
        translation_data = {
            "input_text": "API Gateway",
            "session_id": TEST_SESSION_ID,
            "business_context": "Technical documentation review"
        }
        
        async with session.post(f"{BASE_URL}/api/translate", json=translation_data) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Translation successful: {result.get('term', '')}")
                print(f"   Category: {result.get('category', '')}")
                print(f"   Confidence: {result.get('confidence', 0):.2f}")
            else:
                print(f"❌ Translation failed: {response.status}")
        
        print("\n🎉 Voice integration test completed!")

async def test_websocket_voice():
    """Test WebSocket voice functionality"""
    print("\n🔌 Testing WebSocket voice functionality...")
    
    uri = f"ws://localhost:8000/ws/{TEST_SESSION_ID}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(uri) as websocket:
                print("✅ WebSocket connected")
                
                # Test voice input message
                voice_message = {
                    "type": "voice_input",
                    "data": {
                        "text": "What is a microservice?",
                        "synthesize_response": True,
                        "language_code": "en-US"
                    }
                }
                
                await websocket.send_str(json.dumps(voice_message))
                print("✅ Voice input message sent")
                
                # Wait for response
                async for msg in websocket:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        print(f"📨 Received: {data.get('type', 'unknown')}")
                        
                        if data.get('type') == 'translation_complete':
                            print(f"✅ Translation received: {data.get('data', {}).get('term', '')}")
                            break
                        elif data.get('type') == 'error':
                            print(f"❌ Error: {data.get('message', '')}")
                            break
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        print(f"❌ WebSocket error: {msg.data}")
                        break
                        
    except Exception as e:
        print(f"❌ WebSocket test failed: {str(e)}")

async def main():
    """Main test function"""
    print("🚀 Starting Babelfish Voice Integration Tests")
    print("=" * 50)
    
    try:
        # Test REST endpoints
        await test_voice_endpoints()
        
        # Test WebSocket functionality
        await test_websocket_voice()
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 Voice integration tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 