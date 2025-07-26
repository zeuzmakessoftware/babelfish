# Babelfish Voice Integration

This document describes the voice integration features in the Babelfish Enterprise AI Backend.

## Overview

The voice integration provides comprehensive speech-to-text and text-to-speech capabilities using:

- **Speech-to-Text**: AWS Transcribe for converting audio to text
- **Text-to-Speech**: Rime Voice AI for high-quality speech synthesis
- **Real-time Processing**: WebSocket-based streaming for live voice interactions

## Services

### 1. Speech-to-Text Service (`speech_to_text.py`)

Converts audio input to text using AWS Transcribe.

**Features:**
- Audio file transcription
- Real-time streaming transcription
- Multiple language support
- Confidence scoring
- Job management

**Key Methods:**
```python
# Transcribe audio stream
await stt_service.transcribe_audio_stream(audio_stream, language_code="en-US")

# Transcribe audio file
await stt_service.transcribe_audio_file("audio.mp3", language_code="en-US")

# Start streaming transcription
async for result in stt_service.start_streaming_transcription(audio_stream):
    print(result["text"])
```

### 2. Voice Synthesis Service (`rime_voice.py`)

Generates high-quality speech using Rime Voice AI.

**Features:**
- Multiple voice styles (professional, conversational)
- Adjustable speed and pitch
- Streaming audio output
- Batch synthesis support

**Key Methods:**
```python
# Synthesize speech
audio_stream = rime_service.synthesize_speech(
    text="Hello world",
    voice_style="professional_female",
    speed=1.0
)

# Get available voices
voices = await rime_service.get_available_voices()
```

## API Endpoints

### Voice Synthesis

#### `POST /api/voice/synthesize`
Generate speech from text.

**Request:**
```json
{
    "text": "Hello, this is a test message",
    "voice_style": "professional_female",
    "speed": 1.0
}
```

**Response:** Audio stream (MP3)

#### `GET /api/voice/available-voices`
Get list of available voices.

**Response:**
```json
{
    "voices": [
        {
            "voice_id": "aurora",
            "style": "professional",
            "language": "en-US"
        }
    ]
}
```

### Speech-to-Text

#### `POST /api/voice/transcribe`
Transcribe audio data to text.

**Request:**
```json
{
    "audio_data": "base64_encoded_audio",
    "language_code": "en-US",
    "media_format": "mp3"
}
```

**Response:**
```json
{
    "text": "Transcribed text here",
    "confidence": 0.95,
    "language_code": "en-US",
    "status": "COMPLETED"
}
```

#### `POST /api/voice/transcribe-file`
Transcribe uploaded audio file.

**Request:** Multipart form with audio file

**Response:** Same as `/api/voice/transcribe`

#### `GET /api/voice/transcription-jobs`
List recent transcription jobs.

#### `GET /api/voice/transcription-job/{job_name}`
Get status of specific transcription job.

#### `DELETE /api/voice/transcription-job/{job_name}`
Delete a transcription job.

#### `GET /api/voice/transcription-sessions`
Get active transcription sessions.

## WebSocket Voice Integration

### Connection
```javascript
const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);
```

### Message Types

#### Voice Input
```json
{
    "type": "voice_input",
    "data": {
        "text": "What is a microservice?",
        "audio_data": "base64_audio_optional",
        "synthesize_response": true,
        "language_code": "en-US"
    }
}
```

#### Start Transcription
```json
{
    "type": "start_transcription",
    "data": {
        "language_code": "en-US"
    }
}
```

#### Audio Chunk
```json
{
    "type": "audio_chunk",
    "data": {
        "audio_chunk": "base64_audio_chunk"
    }
}
```

### Response Messages

#### Transcription Complete
```json
{
    "type": "transcription_complete",
    "text": "Transcribed text",
    "confidence": 0.95
}
```

#### Partial Transcription
```json
{
    "type": "partial_transcription",
    "text": "Partial text",
    "confidence": 0.85,
    "is_final": false
}
```

#### Translation Complete
```json
{
    "type": "translation_complete",
    "data": {
        "term": "API Gateway",
        "explanation": "A service that acts as an entry point...",
        "category": "architecture",
        "confidence": 0.92
    }
}
```

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Rime Voice AI
RIME_API_KEY=your_rime_api_key

# AWS Services (for transcription)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
```

### Voice Styles

Available voice styles in Rime:

- `professional_female`: Professional female voice (Aurora)
- `professional_male`: Professional male voice (Atlas)
- `conversational_female`: Conversational female voice (Bella)
- `conversational_male`: Conversational male voice (Caleb)

## Testing

Run the voice integration test:

```bash
cd backend
python test_voice_integration.py
```

This will test:
- Health check
- Available voices
- Speech synthesis
- Transcription
- Transcription jobs
- WebSocket voice functionality

## Usage Examples

### Frontend Integration

```javascript
// Speech synthesis
async function synthesizeSpeech(text) {
    const response = await fetch('/api/voice/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            text: text,
            voice_style: 'professional_female',
            speed: 1.0
        })
    });
    
    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    audio.play();
}

// Transcription
async function transcribeAudio(audioData) {
    const response = await fetch('/api/voice/transcribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            audio_data: audioData,
            language_code: 'en-US'
        })
    });
    
    return await response.json();
}
```

### WebSocket Voice Processing

```javascript
const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'transcription_complete':
            console.log('Transcribed:', data.text);
            break;
        case 'translation_complete':
            console.log('Translation:', data.data.explanation);
            break;
        case 'error':
            console.error('Error:', data.message);
            break;
    }
};

// Send voice input
ws.send(JSON.stringify({
    type: 'voice_input',
    data: {
        text: 'What is a microservice?',
        synthesize_response: true
    }
}));
```

## Error Handling

The voice services include comprehensive error handling:

- Network timeouts
- API rate limits
- Invalid audio formats
- Transcription failures
- Synthesis errors

All errors are logged and returned with appropriate HTTP status codes.

## Performance Considerations

- Audio chunks are processed in 4KB buffers for real-time transcription
- Speech synthesis streams audio data for immediate playback
- WebSocket connections are managed with automatic cleanup
- Transcription jobs are queued and processed asynchronously

## Security

- API keys are stored securely in environment variables
- Audio data is processed in memory and not persisted
- WebSocket connections are validated and rate-limited
- Transcription jobs are isolated per session

## Troubleshooting

### Common Issues

1. **Speech synthesis fails**
   - Check Rime API key configuration
   - Verify text length limits
   - Ensure proper audio format

2. **Transcription not working**
   - Verify AWS credentials
   - Check audio format compatibility
   - Ensure sufficient audio quality

3. **WebSocket connection issues**
   - Check CORS configuration
   - Verify session ID format
   - Monitor connection limits

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- Real-time voice translation
- Voice emotion detection
- Custom voice training
- Multi-language voice synthesis
- Advanced audio processing
- Voice biometrics integration 