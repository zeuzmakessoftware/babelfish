# Voice Synthesis Setup Guide

## The "Alien Noises" Issue

The "alien noises" you're hearing are caused by the voice synthesis system trying to generate audio without proper configuration. Here's how to fix it:

## Quick Fix (Disable Voice Synthesis)

1. **Remove the test script from your page** (already done):
   - The `test-voice.js` script has been removed from `app/page.tsx`
   - This prevents automatic voice testing when the page loads

2. **Create a `.env` file in the backend directory**:
   ```bash
   cd backend
   cp config.template .env
   ```

3. **Edit the `.env` file** to disable voice synthesis:
   ```env
   # Set empty API keys to disable external services
   RIME_API_KEY=
   AWS_ACCESS_KEY=
   AWS_SECRET_KEY=
   TAVILY_API_KEY=
   
   # Enable debug mode
   DEBUG=True
   ```

## Proper Voice Synthesis Setup

If you want to enable voice synthesis:

1. **Get a Rime API key**:
   - Sign up at https://rime.ai
   - Get your API key from the dashboard
   - The API uses the endpoint: `https://users.rime.ai/v1/rime-tts`

2. **Configure your `.env` file**:
   ```env
   RIME_API_KEY=your_actual_rime_api_key_here
   AWS_ACCESS_KEY=your_aws_key_if_using_aws_services
   AWS_SECRET_KEY=your_aws_secret_if_using_aws_services
   ```

3. **Test the API manually** (optional):
   ```bash
   curl --request POST \
     --url https://users.rime.ai/v1/rime-tts \
     --header 'Accept: audio/mp3' \
     --header 'Authorization: Bearer YOUR_API_KEY' \
     --header 'Content-Type: application/json' \
     --data '{
       "speaker": "aurora",
       "text": "Hello, this is a test.",
       "modelId": "arcana",
       "repetition_penalty": 1.5,
       "temperature": 0.5,
       "top_p": 1,
       "samplingRate": 24000,
       "max_tokens": 1200
     }'
   ```

3. **Install Python dependencies**:
   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Start the backend**:
   ```bash
   python main.py
   ```

## Testing Voice Synthesis

Once configured, you can test voice synthesis:

1. **Start your frontend**:
   ```bash
   npm run dev
   ```

2. **Test the voice endpoint**:
   ```bash
   curl -X POST http://localhost:8000/api/voice/test
   ```

3. **Or use the browser console**:
   ```javascript
   // Load the test script manually
   const script = document.createElement('script');
   script.src = '/test-voice.js';
   document.head.appendChild(script);
   
   // Run the test
   window.testVoice();
   ```

## Troubleshooting

- **"Alien noises"**: Usually means corrupted audio format or missing dependencies
- **"Voice synthesis not configured"**: API key not set in `.env` file
- **"Backend not available"**: Make sure the backend is running on port 8000

## Current Status

✅ **Fixed**: Removed automatic voice testing from page load
✅ **Fixed**: Added proper error handling for unconfigured voice services
⚠️ **Action needed**: Create `.env` file to disable voice synthesis or configure API keys 