#!/usr/bin/env python3
"""
Test gTTS fallback synthesis
"""

import asyncio
import tempfile
import os

async def test_gtts():
    """Test gTTS synthesis"""
    try:
        from gtts import gTTS
        
        print("Testing gTTS synthesis...")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Generate speech using gTTS
            text = "Hello, this is a test of the Google Text-to-Speech system."
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_path)
            
            # Check file size
            file_size = os.path.getsize(temp_path)
            print(f"✅ gTTS test successful! Generated {file_size} bytes")
            
            # Read and check content
            with open(temp_path, 'rb') as audio_file:
                audio_data = audio_file.read()
                print(f"Audio data length: {len(audio_data)} bytes")
                
                # Check if it's a valid MP3 (should start with MP3 header)
                if audio_data.startswith(b'\xff\xfb') or audio_data.startswith(b'ID3'):
                    print("✅ Valid MP3 file generated")
                else:
                    print("⚠️  File may not be valid MP3")
                    
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except ImportError as e:
        print(f"❌ gTTS not available: {e}")
    except Exception as e:
        print(f"❌ gTTS test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_gtts()) 