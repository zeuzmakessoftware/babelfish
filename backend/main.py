from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import json
import uuid
import datetime
import logging
from contextlib import asynccontextmanager

# Service integrations
from services.rime_voice import RimeVoiceService
from services.speech_to_text import SpeechToTextService
from services.aws_ai import AWSBedrockService  
from services.mongodb_vector import MongoVectorService
from services.tavily_search import TavilySearchService
from services.clickhouse_analytics import ClickHouseService
from services.websocket_manager import WebSocketManager
from models.conversation import ConversationRequest, ConversationResponse, TranslationEntry
from config.settings import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instances
services = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    settings = get_settings()
    
    logger.info("Initializing Babelfish Enterprise AI Backend...")
    
    # Initialize all services
    services['rime'] = RimeVoiceService(settings.rime_api_key)
    services['stt'] = SpeechToTextService(settings.aws_access_key, settings.aws_secret_key, settings.aws_region)
    services['aws'] = AWSBedrockService(settings.aws_access_key, settings.aws_secret_key, settings.aws_region)
    services['mongodb'] = MongoVectorService(settings.mongodb_uri, settings.mongodb_database)
    services['tavily'] = TavilySearchService(settings.tavily_api_key)
    services['clickhouse'] = ClickHouseService(settings.clickhouse_host, settings.clickhouse_user, settings.clickhouse_password)
    services['websocket'] = WebSocketManager()
    
    # Initialize database connections
    await services['mongodb'].initialize()
    
    # Initialize ClickHouse if available (optional)
    try:
        await services['clickhouse'].initialize()
        logger.info("ClickHouse analytics service initialized successfully")
    except Exception as e:
        logger.warning(f"ClickHouse initialization failed, analytics will be disabled: {str(e)}")
        services['clickhouse'] = None
    
    logger.info("All services initialized successfully")
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down services...")
    await services['mongodb'].close()
    if services.get('clickhouse'):
        await services['clickhouse'].close()

app = FastAPI(
    title="Babelfish Enterprise AI Backend",
    description="Advanced technical translation platform with voice AI, semantic search, and real-time analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
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

@app.post("/api/translate", response_model=ConversationResponse)
async def translate_technical_term(request: ConversationRequest):
    """
    Main translation endpoint that processes technical jargon
    and returns enterprise-ready explanations
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        # Step 1: Search existing knowledge base using vector similarity
        logger.info(f"Processing translation request: {request.input_text}")
        vector_results = await services['mongodb'].search_similar_terms(
            request.input_text, 
            limit=3,
            threshold=0.7
        )
        
        # Step 2: If no good match, search web for current definitions
        web_results = None
        if not vector_results or vector_results[0]['score'] < 0.8:
            logger.info("Searching web for additional context")
            web_results = await services['tavily'].search_technical_term(
                request.input_text,
                search_depth="advanced"
            )
        
        # Step 3: Generate intelligent analysis using AWS Bedrock
        ai_analysis = await services['aws'].analyze_technical_term(
            term=request.input_text,
            existing_definitions=vector_results,
            web_context=web_results,
            business_context=request.business_context
        )
        
        # Step 4: Create comprehensive response
        response = ConversationResponse(
            session_id=session_id,
            term=request.input_text,
            explanation=ai_analysis['explanation'],
            category=ai_analysis['category'],
            confidence=ai_analysis['confidence'],
            business_impact=ai_analysis['business_impact'],
            related_terms=ai_analysis['related_terms'],
            sources=ai_analysis['sources'],
            processing_time=ai_analysis['processing_time']
        )
        
        # Step 5: Store in vector database for future searches
        await services['mongodb'].store_translation(
            term=request.input_text,
            explanation=response.explanation,
            category=response.category,
            embedding=ai_analysis['embedding'],
            metadata={
                'confidence': response.confidence,
                'session_id': session_id,
                'timestamp': datetime.datetime.utcnow()
            }
        )
        
        # Step 6: Log analytics event (if ClickHouse is available)
        if services.get('clickhouse'):
            try:
                await services['clickhouse'].log_translation_event({
                    'session_id': session_id,
                    'term': request.input_text,
                    'category': response.category,
                    'confidence': response.confidence,
                    'processing_time': response.processing_time,
                    'user_agent': request.user_agent,
                    'timestamp': datetime.datetime.utcnow()
                })
            except Exception as e:
                logger.warning(f"Failed to log analytics event: {str(e)}")
        
        return response
        
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@app.post("/api/voice/synthesize")
async def synthesize_speech(request: Dict[str, Any]):
    """
    Generate high-quality speech using Rime voice AI
    """
    try:
        text = request.get('text')
        voice_style = request.get('voice_style', 'professional_female')
        speed = request.get('speed', 1.0)
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Generate speech using Rime
        audio_stream = await services['rime'].synthesize_speech(
            text=text,
            voice_style=voice_style,
            speed=speed,
            output_format='mp3'
        )
        
        return StreamingResponse(
            audio_stream,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )
        
    except Exception as e:
        logger.error(f"Speech synthesis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")

@app.get("/api/analytics/session/{session_id}")
async def get_session_analytics(session_id: str):
    """
    Get detailed analytics for a specific session
    """
    if not services.get('clickhouse'):
        return {
            "session_id": session_id,
            "message": "Analytics service not available",
            "total_translations": 0,
            "avg_confidence": 0.0,
            "categories_used": [],
            "success_rate": 0.0
        }
    
    try:
        analytics = await services['clickhouse'].get_session_analytics(session_id)
        return analytics
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analytics retrieval failed: {str(e)}")

@app.get("/api/analytics/dashboard")
async def get_dashboard_metrics():
    """
    Get real-time dashboard metrics
    """
    if not services.get('clickhouse'):
        return {
            "total_translations": 0,
            "average_confidence": 0.0,
            "top_categories": [],
            "recent_activity": [],
            "message": "Analytics service not available"
        }
    
    try:
        metrics = await services['clickhouse'].get_dashboard_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Dashboard metrics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Dashboard metrics failed: {str(e)}")

@app.get("/api/terms/suggest/{partial_term}")
async def suggest_terms(partial_term: str, limit: int = 5):
    """
    Get term suggestions based on partial input using vector search
    """
    try:
        suggestions = await services['mongodb'].get_term_suggestions(partial_term, limit)
        return {"suggestions": suggestions}
    except Exception as e:
        logger.error(f"Term suggestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Term suggestions failed: {str(e)}")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time communication
    """
    await services['websocket'].connect(websocket, session_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message['type'] == 'translate':
                # Process translation in background
                asyncio.create_task(
                    process_realtime_translation(websocket, session_id, message['data'])
                )
            elif message['type'] == 'voice_input':
                # Process voice input
                asyncio.create_task(
                    process_voice_input(websocket, session_id, message['data'])
                )
            
    except WebSocketDisconnect:
        await services['websocket'].disconnect(websocket, session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await services['websocket'].disconnect(websocket, session_id)

async def process_realtime_translation(websocket: WebSocket, session_id: str, data: Dict):
    """Process translation and send real-time updates"""
    try:
        # Send processing status
        await websocket.send_text(json.dumps({
            'type': 'status',
            'status': 'processing',
            'message': 'Analyzing technical terminology...'
        }))
        
        # Create translation request
        request = ConversationRequest(
            input_text=data['text'],
            session_id=session_id,
            business_context=data.get('context')
        )
        
        # Process translation
        response = await translate_technical_term(request)
        
        # Send completed translation
        await websocket.send_text(json.dumps({
            'type': 'translation_complete',
            'data': response.dict()
        }))
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            'type': 'error',
            'message': f'Translation failed: {str(e)}'
        }))

async def process_voice_input(websocket: WebSocket, session_id: str, data: Dict):
    """Process voice input and return synthesized response"""
    try:
        # Process the translation first
        await process_realtime_translation(websocket, session_id, data)
        
        # Generate voice response if requested
        if data.get('synthesize_response'):
            await websocket.send_text(json.dumps({
                'type': 'status',
                'status': 'synthesizing',
                'message': 'Generating voice response...'
            }))
            
            # This would be handled by the /api/voice/synthesize endpoint
            # in a real implementation
            
    except Exception as e:
        await websocket.send_text(json.dumps({
            'type': 'error',
            'message': f'Voice processing failed: {str(e)}'
        }))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)