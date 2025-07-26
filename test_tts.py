#!/usr/bin/env python3
"""
Test script for the new text-to-speech functionality
"""

import requests
import json

def test_tts():
    """Test the text-to-speech endpoints"""
    
    # Test the main synthesis endpoint
    print("🧪 Testing main synthesis endpoint...")
    response = requests.post(
        "http://localhost:8000/api/voice/synthesize",
        headers={"Content-Type": "application/json"},
        json={
            "text": "Hello! This is a test of the new text to speech system. It should now speak actual words instead of just a beep.",
            "voice_style": "professional_female",
            "speed": 1.0
        }
    )
    
    if response.status_code == 200:
        print("✅ Main synthesis endpoint working!")
        print(f"   Audio size: {len(response.content)} bytes")
        
        # Save the audio file
        with open("test_main_tts.wav", "wb") as f:
            f.write(response.content)
        print("   Saved as: test_main_tts.wav")
    else:
        print(f"❌ Main synthesis failed: {response.status_code}")
        print(f"   Response: {response.text}")
    
    # Test the test endpoint
    print("\n🧪 Testing test endpoint...")
    response = requests.post(
        "http://localhost:8000/api/voice/test",
        headers={"Content-Type": "application/json"},
        json={
            "text": "This is the test endpoint. It should also speak actual words.",
            "voice_style": "professional_male"
        }
    )
    
    if response.status_code == 200:
        print("✅ Test endpoint working!")
        print(f"   Audio size: {len(response.content)} bytes")
        
        # Save the audio file
        with open("test_endpoint_tts.wav", "wb") as f:
            f.write(response.content)
        print("   Saved as: test_endpoint_tts.wav")
    else:
        print(f"❌ Test endpoint failed: {response.status_code}")
        print(f"   Response: {response.text}")
    
    # Test health endpoint
    print("\n🧪 Testing health endpoint...")
    response = requests.get("http://localhost:8000/")
    
    if response.status_code == 200:
        print("✅ Health endpoint working!")
        health_data = response.json()
        print(f"   Services: {health_data.get('services', [])}")
    else:
        print(f"❌ Health endpoint failed: {response.status_code}")

if __name__ == "__main__":
    print("🎤 Testing Text-to-Speech System")
    print("=" * 40)
    test_tts()
    print("\n🎉 Test completed!")
    print("\nTo test in browser:")
    print("1. Open http://localhost:3000")
    print("2. Open browser console (F12)")
    print("3. Run: testVoice()")
    print("4. Click the page to enable audio") 