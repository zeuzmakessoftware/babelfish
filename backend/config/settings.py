from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    rime_api_key: str = ""
    aws_access_key: str = ""
    aws_secret_key: str = ""
    aws_region: str = "us-east-1"
    tavily_api_key: str = ""
    
    # Database Configuration
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "babelfish"
    
    # ClickHouse Configuration  
    clickhouse_host: str = "localhost"
    clickhouse_port: int = 8123
    clickhouse_user: str = "default"
    clickhouse_password: str = ""
    clickhouse_database: str = "babelfish_analytics"
    
    # Application Configuration
    app_name: str = "Babelfish Enterprise AI"
    debug: bool = False
    log_level: str = "INFO"
    
    # Voice Configuration
    default_voice_style: str = "professional_female"
    max_text_length: int = 5000
    
    # AI Configuration
    bedrock_model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"
    embedding_model: str = "amazon.titan-embed-text-v2:0"
    max_tokens: int = 4000
    temperature: float = 0.7
    
    # Vector Search Configuration
    vector_dimension: int = 1024
    similarity_threshold: float = 0.7
    max_search_results: int = 10
    
    # Rate Limiting
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 1000
    
    # Security
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    allow_credentials: bool = True
    
    # Performance Settings
    worker_processes: int = 1
    max_concurrent_requests: int = 100
    
    # Monitoring & Analytics
    enable_analytics: bool = True
    analytics_retention_days: int = 30
    enable_performance_tracking: bool = True
    
    # Development Settings
    enable_debug_endpoints: bool = False
    enable_swagger_ui: bool = True
    enable_redoc: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields instead of rejecting them

_settings = None

def get_settings() -> Settings:
    """Get cached settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings 