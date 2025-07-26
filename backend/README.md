# Babelfish Enterprise AI - Backend

A powerful Python backend for the Babelfish technical translation platform, featuring enterprise-grade AI services for intelligent technical jargon translation.

## Architecture

### Core Services Integration

- **Rime Voice AI** - High-quality, realistic speech synthesis
- **AWS Bedrock** - Advanced AI analysis using Claude and Titan models
- **MongoDB Atlas** - Vector search for semantic term matching
- **Tavily MCP** - Real-time web search for current technical definitions
- **ClickHouse** - High-performance analytics and conversation tracking

### Technology Stack

- **FastAPI** - Modern, fast web framework
- **Python 3.11+** - Async/await support
- **WebSockets** - Real-time communication
- **Vector Embeddings** - Semantic search capabilities
- **Event Streaming** - Real-time analytics

## Features

### 🧠 Intelligent Translation
- AI-powered technical term analysis
- Context-aware business explanations
- Confidence scoring and validation
- Multi-source knowledge synthesis

### 🗣️ Enterprise Voice AI
- Professional voice synthesis with Rime
- Multiple voice styles and languages
- High-quality audio streaming
- Batch processing capabilities

### 🔍 Semantic Search
- Vector-based term matching
- MongoDB Atlas Vector Search
- Similarity scoring and ranking
- Term suggestion engine

### 📊 Real-time Analytics
- ClickHouse-powered metrics
- Session tracking and analysis
- Performance monitoring
- Usage pattern insights

### 🌐 Web Integration
- Real-time web search with Tavily
- Current technical definitions
- Source validation and ranking
- Accuracy verification

## Quick Start

### Prerequisites

1. **Python 3.11+**
2. **MongoDB Atlas** (with Vector Search enabled)
3. **ClickHouse** instance
4. **API Keys** for:
   - Rime Voice AI
   - AWS Bedrock
   - Tavily MCP

### Installation

1. **Clone and setup**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp config.template .env
# Edit .env with your API keys and database configuration
```

3. **Start the server**:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Required API Keys
RIME_API_KEY=your_rime_api_key
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
TAVILY_API_KEY=your_tavily_api_key

# Database URLs
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net
CLICKHOUSE_HOST=your_clickhouse_host

# AI Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
EMBEDDING_MODEL=amazon.titan-embed-text-v2:0
```

### Service Setup

#### MongoDB Atlas Vector Search
1. Create MongoDB Atlas cluster
2. Enable Vector Search
3. Configure vector index for embeddings

#### ClickHouse
1. Deploy ClickHouse instance
2. Configure network access
3. Create analytics database

#### AWS Bedrock
1. Enable Bedrock in your AWS region
2. Request access to Claude and Titan models
3. Configure IAM permissions

## API Endpoints

### Core Translation
- `POST /api/translate` - Translate technical terms
- `GET /api/terms/suggest/{partial}` - Get term suggestions

### Voice Synthesis
- `POST /api/voice/synthesize` - Generate speech audio

### Analytics
- `GET /api/analytics/dashboard` - Real-time metrics
- `GET /api/analytics/session/{id}` - Session details

### WebSocket
- `WS /ws/{session_id}` - Real-time communication

## Development

### Project Structure

```
backend/
├── main.py                 # FastAPI application
├── config/
│   └── settings.py        # Configuration management
├── models/
│   └── conversation.py    # Pydantic models
├── services/
│   ├── rime_voice.py     # Voice AI integration
│   ├── aws_ai.py         # Bedrock AI service
│   ├── mongodb_vector.py # Vector search
│   ├── tavily_search.py  # Web search
│   ├── clickhouse_analytics.py # Analytics
│   └── websocket_manager.py    # WebSocket handling
└── requirements.txt       # Python dependencies
```

### Running Tests

```bash
pytest tests/ -v
```

### Development Server

```bash
uvicorn main:app --reload --port 8000
```

## Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Considerations

- Set `DEBUG=False` in production
- Configure proper CORS origins
- Enable rate limiting
- Set up monitoring and logging
- Use environment-specific API keys

### Scaling

- Use multiple worker processes
- Implement load balancing
- Configure database connection pooling
- Set up caching for frequent queries

## Monitoring

### Health Checks

- `GET /` - Service health status
- Database connectivity checks
- Service integration status

### Metrics

- Request/response times
- Error rates
- Service availability
- Usage patterns

### Logging

- Structured logging with levels
- Request/response logging
- Error tracking
- Performance metrics

## Security

- API key management
- CORS configuration
- Rate limiting
- Input validation
- Error handling

## Support

For issues and questions:
1. Check the logs for error details
2. Verify all services are accessible
3. Confirm API keys are valid
4. Review configuration settings

## License

Enterprise License - See LICENSE file for details. 