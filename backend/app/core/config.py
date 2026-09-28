import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "InternReach AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Mocking
    ENVIRONMENT: str = "development"
    MOCK_MODE: bool = True
    DEBUG: bool = True
    
    # Security
    JWT_SECRET: str = "super-secret-jwt-key-internreach-ai-development-token-32char"
    SESSION_SECRET: str = "super-secret-session-key-development"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    # Default to SQLite for seamless zero-config local run, easily overridden by postgres url
    DATABASE_URL: str = "sqlite+aiosqlite:///./internreach.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # LLM Providers
    PRIMARY_LLM_PROVIDER: str = "claude"  # "claude" or "gemini" or "mock"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-pro"
    
    # Search Providers
    SEARCH_PROVIDER: str = "tavily"  # "tavily", "serp", or "mock"
    SEARCH_PROVIDER_API_KEY: Optional[str] = None
    
    # Upload limits
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_MIME_TYPES: List[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword"
    ]
    UPLOAD_DIR: str = "./uploads"

    # Default Target Student Profile Constraints
    DEFAULT_GRADUATION_YEAR: int = 2028
    
    # Email / SMTP
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "notifications@internreach.ai"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
