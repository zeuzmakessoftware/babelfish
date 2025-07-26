# Audio Troubleshooting Guide

If you can't hear anything from the Babelfish voice interface, follow these steps:

## 🔧 Quick Fix Steps

### 1. Start the Backend
Make sure your Python backend is running:

```bash
cd backend
python main.py
```

You should see:
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     All services initialized successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Check Backend Health
Open your browser and go to: `http://localhost:8000/`

You should see a JSON response like:
```json
{
  "message": "Babelfish Enterprise AI Backend",
  "status": "operational",
  "version": "1.0.0",
  "services": {
    "voice_ai": "Rime",
    "speech_to_text": "AWS Transcribe",
    "generative_ai": "AWS Bedrock",
    "vector_search": "MongoDB",
    "web_search": "Tavily",
    "analytics": "ClickHouse"
  }
}
```

### 3. Test Voice Synthesis
Open your browser console (F12) and run:
```javascript
testVoice()
```

This will test the voice synthesis and show you detailed logs.

### 4. Check Environment Variables
Make sure your `.env` file in the backend folder has:
```bash
RIME_API_KEY=your_actual_rime_api_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
```

## 🐛 Common Issues & Solutions

### Issue 1: "Backend not available"
**Symptoms:** Console shows "Backend health check failed"

**Solutions:**
- Make sure backend is running on port 8000
- Check if port 8000 is not used by another application
- Try: `lsof -i :8000` to see what's using the port

### Issue 2: "Voice synthesis failed: 500"
**Symptoms:** Backend error when trying to synthesize speech

**Solutions:**
- Check if RIME_API_KEY is set correctly
- Verify your Rime API key is valid
- Check backend logs for detailed error messages

### Issue 3: "Audio blob received: 0 bytes"
**Symptoms:** Audio blob is empty

**Solutions:**
- Check if Rime service is responding
- Verify network connectivity to Rime API
- Check backend logs for Rime API errors

### Issue 4: "Audio error" in browser
**Symptoms:** Audio fails to play in browser

**Solutions:**
- Check browser console for CORS errors
- Make sure browser allows autoplay
- Try clicking on the page before audio plays
- Check if browser supports audio playback

### Issue 5: No sound at all
**Symptoms:** Everything seems to work but no audio

**Solutions:**
- Check system volume
- Check browser volume
- Try different browser
- Check if audio is muted in browser tab
- Try refreshing the page

## 🔍 Debug Steps

### 1. Check Backend Logs
Look at the backend terminal for errors:
```
ERROR: Speech synthesis error: ...
ERROR: Rime API error: ...
```

### 2. Check Browser Console
Open Developer Tools (F12) and look for:
- Network errors
- JavaScript errors
- Audio-related errors

### 3. Test Individual Components

**Test Backend Voice API:**
```bash
curl -X POST http://localhost:8000/api/voice/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello world","voice_style":"professional_female"}'
```

**Test Frontend Connection:**
```javascript
fetch('/api/voice/synthesize', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({text: 'test', voice_style: 'professional_female'})
}).then(r => r.blob()).then(b => console.log('Blob size:', b.size))
```

## 🎯 Quick Test Commands

### Test Backend Voice Service
```bash
cd backend
python test_voice_integration.py
```

### Test Frontend Voice
1. Open browser console (F12)
2. Run: `testVoice()`
3. Check console output

### Test Manual Voice Synthesis
```javascript
// In browser console
fetch('/api/voice/synthesize', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    text: 'Hello, this is a test!',
    voice_style: 'professional_female'
  })
})
.then(r => r.blob())
.then(b => {
  const url = URL.createObjectURL(b);
  const audio = new Audio(url);
  audio.play();
});
```

## 🔧 Environment Setup

### Required Environment Variables
```bash
# Backend .env file
RIME_API_KEY=your_rime_api_key_here
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
```

### Install Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ..
npm install
```

## 🚀 Start Everything

1. **Start Backend:**
```bash
cd backend
python main.py
```

2. **Start Frontend:**
```bash
npm run dev
```

3. **Test Voice:**
- Open browser to `http://localhost:3000`
- Open console (F12)
- Run `testVoice()`

## 📞 Still Having Issues?

If you're still having problems:

1. Check the backend logs for specific error messages
2. Verify all environment variables are set
3. Test with a simple curl command to the backend
4. Try a different browser
5. Check if your system's audio is working with other applications

The most common issue is that the backend isn't running or the Rime API key isn't configured properly. 