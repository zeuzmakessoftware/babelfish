from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
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
    if services.get('stt'):
        await services['stt'].close()
    if services.get('rime'):
        await services['rime'].close()

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
        # Check if voice service is properly configured
        if not services.get('rime') or not services['rime'].api_key or services['rime'].api_key == "your_rime_api_key_here":
            raise HTTPException(
                status_code=503, 
                detail="Voice synthesis not configured. Please set RIME_API_KEY in your .env file."
            )
        
        text = request.get('text')
        voice_style = request.get('voice_style', 'professional_female')
        speed = request.get('speed', 1.0)
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Generate speech using Rime
        audio_stream = services['rime'].synthesize_speech(
            text=text,
            voice_style=voice_style,
            speed=speed,
            output_format='mp3'
        )
        
        # Collect all audio data into a single response
        audio_data = b""
        async for chunk in audio_stream:
            audio_data += chunk
        
        if not audio_data:
            raise HTTPException(status_code=500, detail="No audio data generated")
        
        # Determine media type based on audio data
        if audio_data.startswith(b'RIFF'):
            media_type = "audio/wav"
            filename = "speech.wav"
        else:
            media_type = "audio/mpeg"
            filename = "speech.mp3"
        
        return Response(
            content=audio_data,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(audio_data))
            }
        )
        
    except Exception as e:
        logger.error(f"Speech synthesis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")

@app.post("/api/voice/transcribe")
async def transcribe_audio(request: Dict[str, Any]):
    """
    Transcribe audio to text using AWS Transcribe
    """
    try:
        audio_data = request.get('audio_data')
        language_code = request.get('language_code', 'en-US')
        media_format = request.get('media_format', 'mp3')
        
        if not audio_data:
            raise HTTPException(status_code=400, detail="Audio data is required")
        
        # Convert base64 audio data to bytes
        import base64
        audio_bytes = base64.b64decode(audio_data)
        
        # Create async generator for audio stream
        async def audio_stream():
            yield audio_bytes
        
        # Transcribe audio
        result = await services['stt'].transcribe_audio_stream(
            audio_stream(),
            language_code=language_code,
            media_format=media_format
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.post("/api/voice/transcribe-file")
async def transcribe_audio_file(file: UploadFile):
    """
    Transcribe uploaded audio file to text
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="File is required")
        
        # Read file content
        content = await file.read()
        
        # Create async generator for audio stream
        async def audio_stream():
            yield content
        
        # Transcribe audio
        result = await services['stt'].transcribe_audio_stream(
            audio_stream(),
            language_code='en-US',
            media_format=file.filename.split('.')[-1] if '.' in file.filename else 'mp3'
        )
        
        return result
        
    except Exception as e:
        logger.error(f"File transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File transcription failed: {str(e)}")

@app.get("/api/voice/available-voices")
async def get_available_voices():
    """
    Get list of available voices for synthesis
    """
    try:
        voices = await services['rime'].get_available_voices()
        return voices
    except Exception as e:
        logger.error(f"Voice list error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get voices: {str(e)}")

@app.post("/api/voice/streaming-transcribe")
async def start_streaming_transcription(request: Dict[str, Any]):
    """
    Start real-time streaming transcription
    """
    try:
        language_code = request.get('language_code', 'en-US')
        
        # This would be implemented with WebSocket for real-time streaming
        # For now, return a placeholder response
        return {
            "message": "Streaming transcription endpoint",
            "session_id": str(uuid.uuid4()),
            "language_code": language_code,
            "status": "ready"
        }
        
    except Exception as e:
        logger.error(f"Streaming transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Streaming transcription failed: {str(e)}")

@app.post("/api/voice/test")
async def test_voice_synthesis():
    """
    Simple test endpoint for voice synthesis
    """
    try:
        # Check if voice service is properly configured
        if not services.get('rime') or not services['rime'].api_key or services['rime'].api_key == "your_rime_api_key_here":
            return {
                "message": "Voice synthesis not configured",
                "status": "disabled",
                "reason": "Rime API key not configured. Please set RIME_API_KEY in your .env file."
            }
        
        text = "Hello, this is a test of the voice synthesis system. If you can hear this, the audio is working correctly!"
        
        # Use the voice service
        audio_stream = services['rime'].synthesize_speech(
            text=text,
            voice_style='professional_female',
            speed=1.0,
            output_format='mp3'
        )
        
        # Collect all audio data
        audio_data = b""
        async for chunk in audio_stream:
            audio_data += chunk
        
        if not audio_data:
            raise HTTPException(status_code=500, detail="No audio data generated")
        
        # Determine media type based on audio data
        if audio_data.startswith(b'RIFF'):
            media_type = "audio/wav"
            filename = "test.wav"
        else:
            media_type = "audio/mpeg"
            filename = "test.mp3"
        
        return Response(
            content=audio_data,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(audio_data))
            }
        )
        
    except Exception as e:
        logger.error(f"Test voice synthesis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

@app.get("/api/voice/transcription-jobs")
async def list_transcription_jobs(max_results: int = 10):
    """
    List recent transcription jobs
    """
    try:
        jobs = await services['stt'].list_transcription_jobs(max_results)
        return jobs
    except Exception as e:
        logger.error(f"List transcription jobs error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")

@app.get("/api/voice/transcription-job/{job_name}")
async def get_transcription_job_status(job_name: str):
    """
    Get status of a specific transcription job
    """
    try:
        status = await services['stt'].get_transcription_job_status(job_name)
        return status
    except Exception as e:
        logger.error(f"Get job status error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

@app.delete("/api/voice/transcription-job/{job_name}")
async def delete_transcription_job(job_name: str):
    """
    Delete a transcription job
    """
    try:
        result = await services['stt'].delete_transcription_job(job_name)
        return result
    except Exception as e:
        logger.error(f"Delete job error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete job: {str(e)}")

@app.get("/api/voice/transcription-sessions")
async def get_active_transcription_sessions():
    """
    Get active transcription sessions
    """
    try:
        sessions = services['websocket'].get_active_transcription_sessions()
        return {
            "active_sessions": sessions,
            "total_active": len(sessions)
        }
    except Exception as e:
        logger.error(f"Get transcription sessions error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get sessions: {str(e)}")

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
            elif message['type'] == 'start_transcription':
                # Start real-time transcription
                asyncio.create_task(
                    process_streaming_transcription(websocket, session_id, message['data'])
                )
            elif message['type'] == 'audio_chunk':
                # Process audio chunk for real-time transcription
                asyncio.create_task(
                    process_audio_chunk(websocket, session_id, message['data'])
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
        # Send processing status
        await websocket.send_text(json.dumps({
            'type': 'status',
            'status': 'processing_voice',
            'message': 'Processing voice input...'
        }))
        
        # Transcribe audio if provided
        if data.get('audio_data'):
            import base64
            audio_bytes = base64.b64decode(data['audio_data'])
            
            async def audio_stream():
                yield audio_bytes
            
            transcription = await services['stt'].transcribe_audio_stream(
                audio_stream(),
                language_code=data.get('language_code', 'en-US')
            )
            
            if transcription.get('error'):
                await websocket.send_text(json.dumps({
                    'type': 'error',
                    'message': f'Transcription failed: {transcription["error"]}'
                }))
                return
            
            # Use transcribed text for translation
            data['text'] = transcription['text']
            
            # Send transcription result
            await websocket.send_text(json.dumps({
                'type': 'transcription_complete',
                'text': transcription['text'],
                'confidence': transcription['confidence']
            }))
        
        # Process the translation
        await process_realtime_translation(websocket, session_id, data)
        
        # Generate voice response if requested
        if data.get('synthesize_response'):
            await websocket.send_text(json.dumps({
                'type': 'status',
                'status': 'synthesizing',
                'message': 'Generating voice response...'
            }))
            
            # Generate speech for the response
            # This would be implemented with the actual response text
            
    except Exception as e:
        await websocket.send_text(json.dumps({
            'type': 'error',
            'message': f'Voice processing failed: {str(e)}'
        }))

async def process_streaming_transcription(websocket: WebSocket, session_id: str, data: Dict):
    """Start real-time streaming transcription"""
    try:
        language_code = data.get('language_code', 'en-US')
        
        await websocket.send_text(json.dumps({
            'type': 'transcription_started',
            'session_id': session_id,
            'language_code': language_code,
            'message': 'Real-time transcription started'
        }))
        
        # Store transcription session info
        services['websocket'].transcription_sessions[session_id] = {
            'websocket': websocket,
            'language_code': language_code,
            'buffer': b"",
            'active': True
        }
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            'type': 'error',
            'message': f'Failed to start transcription: {str(e)}'
        }))

async def process_audio_chunk(websocket: WebSocket, session_id: str, data: Dict):
    """Process audio chunk for real-time transcription"""
    try:
        session_info = services['websocket'].transcription_sessions.get(session_id)
        if not session_info or not session_info['active']:
            return
        
        # Decode audio chunk
        import base64
        audio_chunk = base64.b64decode(data['audio_chunk'])
        
        # Add to buffer
        session_info['buffer'] += audio_chunk
        
        # Process buffer if it's large enough
        if len(session_info['buffer']) > 4096:  # 4KB chunks
            async def audio_stream():
                yield session_info['buffer']
            
            # Get partial transcription
            result = await services['stt'].transcribe_audio_stream(
                audio_stream(),
                language_code=session_info['language_code']
            )
            
            if result.get('text'):
                await websocket.send_text(json.dumps({
                    'type': 'partial_transcription',
                    'text': result['text'],
                    'confidence': result['confidence'],
                    'is_final': False
                }))
            
            # Clear buffer
            session_info['buffer'] = b""
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            'type': 'error',
            'message': f'Audio chunk processing failed: {str(e)}'
        }))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)