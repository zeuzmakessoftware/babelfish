from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class ConversationRequest(BaseModel):
    """Request model for technical translation"""
    input_text: str = Field(..., description="Technical term or phrase to translate")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    business_context: Optional[str] = Field(default=None, description="Additional business context")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    
    class Config:
        json_schema_extra = {
            "example": {
                "input_text": "microservices architecture",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "business_context": "enterprise application modernization",
                "user_agent": "Mozilla/5.0..."
            }
        }

class ConversationResponse(BaseModel):
    """Response model for technical translation"""
    session_id: str = Field(..., description="Session identifier")
    term: str = Field(..., description="Original technical term")
    explanation: str = Field(..., description="Enterprise-ready explanation")
    category: str = Field(..., description="Technical category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    business_impact: str = Field(..., description="Business impact assessment")
    related_terms: List[str] = Field(default=[], description="Related technical terms")
    sources: List[str] = Field(default=[], description="Information sources")
    processing_time: float = Field(..., description="Processing time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "term": "microservices",
                "explanation": "Distributed architecture pattern decomposing applications into independently deployable services...",
                "category": "Architecture",
                "confidence": 0.95,
                "business_impact": "Enables scalability and technology diversity for enterprise applications",
                "related_terms": ["containerization", "API gateway", "service mesh"],
                "sources": ["internal_kb", "web_search"],
                "processing_time": 1250.5
            }
        }

class TranslationEntry(BaseModel):
    """Database model for storing translations"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    term: str = Field(..., description="Technical term")
    explanation: str = Field(..., description="Explanation")
    category: str = Field(..., description="Category")
    embedding: List[float] = Field(..., description="Vector embedding")
    confidence: float = Field(..., ge=0.0, le=1.0)
    session_id: str = Field(..., description="Session identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    metadata: Dict[str, Any] = Field(default={})

class VoiceRequest(BaseModel):
    """Request model for voice synthesis"""
    text: str = Field(..., max_length=5000, description="Text to synthesize")
    voice_style: str = Field(default="professional_female", description="Voice style")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed")
    output_format: str = Field(default="mp3", description="Audio output format")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "DevOps represents the convergence of development and operations teams...",
                "voice_style": "professional_female",
                "speed": 1.0,
                "output_format": "mp3"
            }
        }

class AnalyticsEvent(BaseModel):
    """Model for analytics events"""
    session_id: str = Field(..., description="Session identifier")
    event_type: str = Field(..., description="Type of event")
    term: Optional[str] = Field(default=None, description="Technical term")
    category: Optional[str] = Field(default=None, description="Term category")
    confidence: Optional[float] = Field(default=None, description="Confidence score")
    processing_time: Optional[float] = Field(default=None, description="Processing time")
    user_agent: Optional[str] = Field(default=None, description="User agent")
    metadata: Dict[str, Any] = Field(default={})
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SessionMetrics(BaseModel):
    """Model for session analytics"""
    session_id: str
    total_translations: int
    average_confidence: float
    average_processing_time: float
    categories_used: List[str]
    success_rate: float
    duration_minutes: float
    first_activity: datetime
    last_activity: datetime

class DashboardMetrics(BaseModel):
    """Model for dashboard metrics"""
    total_sessions: int
    total_translations: int
    average_confidence: float
    average_processing_time: float
    top_categories: List[Dict[str, Any]]
    top_terms: List[Dict[str, Any]]
    success_rate: float
    active_sessions: int
    translation_volume_24h: List[Dict[str, Any]]
    
class TermSuggestion(BaseModel):
    """Model for term suggestions"""
    term: str = Field(..., description="Suggested term")
    category: str = Field(..., description="Term category")
    confidence: float = Field(..., description="Suggestion confidence")
    usage_count: int = Field(default=0, description="Usage frequency")

class WebSearchResult(BaseModel):
    """Model for web search results"""
    title: str = Field(..., description="Result title")
    url: str = Field(..., description="Source URL")
    snippet: str = Field(..., description="Content snippet")
    relevance_score: float = Field(..., description="Relevance score")
    source_type: str = Field(..., description="Source type (documentation, blog, etc.)")

class VectorSearchResult(BaseModel):
    """Model for vector search results"""
    term: str = Field(..., description="Found term")
    explanation: str = Field(..., description="Term explanation")
    category: str = Field(..., description="Term category")
    similarity_score: float = Field(..., description="Similarity score")
    metadata: Dict[str, Any] = Field(default={}) 