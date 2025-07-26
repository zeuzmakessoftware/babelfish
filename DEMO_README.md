# 🐠 Babelfish Enterprise AI - Functional Demo

A real-time technical translation platform that converts complex technical jargon into clear, actionable business insights using advanced AI.

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)
```bash
./start-demo.sh
```

### Option 2: Manual Startup

#### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

#### Frontend Setup
```bash
# In a new terminal
pnpm install
pnpm dev
```

## 🌐 Access Points

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/

## 🎯 Demo Features

### Real-Time Translation
- **Voice Input**: Click the microphone button or use voice commands
- **Text Input**: Type technical terms directly
- **Instant Analysis**: Get enterprise-ready explanations with confidence scores

### Example Technical Terms to Try
- "microservices architecture"
- "technical debt"
- "DevOps pipeline"
- "serverless computing"
- "containerization"
- "CI/CD"
- "agile methodology"
- "cloud-native"

### Advanced Features
- **Real-time Processing**: WebSocket-based communication
- **Voice Synthesis**: AI-generated speech responses
- **Analytics Dashboard**: Session metrics and performance data
- **Term Suggestions**: Intelligent autocomplete
- **Fallback Mode**: Works offline with local translations

## 🏗️ Architecture

### Frontend (Next.js + TypeScript)
- **React 19** with modern hooks
- **Three.js** for 3D visualizations
- **Web Speech API** for voice interaction
- **WebSocket** for real-time communication
- **Tailwind CSS** for styling

### Backend (FastAPI + Python)
- **FastAPI** for high-performance API
- **WebSocket** for real-time communication
- **AWS Bedrock** for AI analysis
- **MongoDB** for vector search
- **ClickHouse** for analytics
- **Rime Voice** for speech synthesis

## 🔧 Configuration

### Environment Variables
Create a `.env.local` file in the root directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend Configuration
Copy `backend/config.template` to `backend/config.py` and configure:
- AWS credentials for Bedrock
- MongoDB connection string
- ClickHouse connection details
- Rime API key
- Tavily API key

## 🎮 Demo Scenarios

### Scenario 1: Voice Translation
1. Click the microphone button
2. Say "microservices architecture"
3. Watch real-time processing
4. Listen to AI-generated explanation

### Scenario 2: Technical Discussion
1. Type "technical debt reduction strategies"
2. View detailed business impact analysis
3. Explore related terms and categories

### Scenario 3: Enterprise Analytics
1. Check the conversation dashboard
2. Monitor confidence scores
3. View processing times and success rates

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version (3.8+ required)
- Verify virtual environment is activated
- Ensure all dependencies are installed

**Frontend won't connect:**
- Verify backend is running on port 8000
- Check browser console for CORS errors
- Ensure WebSocket connection is established

**Voice features not working:**
- Check microphone permissions
- Use HTTPS or localhost (required for Web Speech API)
- Try Chrome/Safari/Edge (best compatibility)

### Debug Mode
Enable debug logging by setting:
```bash
export LOG_LEVEL=DEBUG
```

## 📊 Performance Metrics

The demo includes real-time analytics:
- Translation confidence scores
- Processing times
- Success rates
- Category distribution
- Session metrics

## 🔒 Security Notes

- Demo uses local development settings
- No production credentials required
- All API keys are optional for demo
- Fallback to local translations when services unavailable

## 🎨 Customization

### Adding New Terms
Edit `app/utils/translations.ts` to add local fallback translations.

### Styling
Modify `app/globals.css` and component styles for custom theming.

### Backend Services
Configure additional AI services in `backend/services/`.

## 📞 Support

For demo issues:
1. Check the browser console for errors
2. Verify all services are running
3. Check network connectivity
4. Review the troubleshooting section above

## 🚀 Next Steps

After the demo:
- Explore the API documentation
- Try different technical terms
- Experiment with voice features
- Review the analytics dashboard
- Customize the configuration

---

**Enjoy the Babelfish Enterprise AI Demo! 🐠✨** 