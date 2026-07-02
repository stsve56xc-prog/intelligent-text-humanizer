import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    
    REWRITE_API_KEY: str = os.getenv("REWRITE_API_KEY", "")
    REWRITE_API_URL: str = os.getenv("REWRITE_API_URL", "https://rewriteai.com/api/v1/humanize")
    
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_API_URL: str = os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent")
    
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_API_URL: str = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_URL: str = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    API_CONNECT_TIMEOUT: int = int(os.getenv("API_CONNECT_TIMEOUT", "10"))
    
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))
    
    MAX_TEXT_LENGTH: int = int(os.getenv("MAX_TEXT_LENGTH", "5000"))
    MIN_TEXT_LENGTH: int = int(os.getenv("MIN_TEXT_LENGTH", "10"))
    MAX_BATCH_SIZE: int = int(os.getenv("MAX_BATCH_SIZE", "50"))
    
    DEFAULT_TONE: str = os.getenv("DEFAULT_TONE", "academic")
    DEFAULT_STYLE: str = os.getenv("DEFAULT_STYLE", "balanced")
    DEFAULT_PRESERVE_TECHNICAL: bool = os.getenv("DEFAULT_PRESERVE_TECHNICAL", "true").lower() == "true"
    
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    RELOAD: bool = os.getenv("RELOAD", "true").lower() == "true"
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    CORS_ALLOW_ORIGINS: list = os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    CORS_ALLOW_METHODS: list = os.getenv("CORS_ALLOW_METHODS", "*").split(",")
    CORS_ALLOW_HEADERS: list = os.getenv("CORS_ALLOW_HEADERS", "*").split(",")
    
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "1000"))
    
    BASE_DIR: Path = Path(__file__).parent.parent
    WORD_DATA_DIR: Path = BASE_DIR / "word_data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    MODELS_DIR: Path = BASE_DIR / "models"
    VOCABULARY_DIR: Path = BASE_DIR / "vocabulary"
    
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    CLOUD_PROVIDER: str = os.getenv("CLOUD_PROVIDER", "")
    
    @classmethod
    def create_directories(cls):
        for dir_path in [cls.LOGS_DIR, cls.WORD_DATA_DIR, cls.MODELS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @property
    def is_rewriteai_enabled(self) -> bool:
        return bool(self.REWRITE_API_KEY)
    
    @property
    def is_gemini_enabled(self) -> bool:
        return bool(self.GEMINI_API_KEY)
    
    @property
    def is_groq_enabled(self) -> bool:
        return bool(self.GROQ_API_KEY)
    
    @property
    def is_openai_enabled(self) -> bool:
        return bool(self.OPENAI_API_KEY)
    
    @property
    def available_methods(self) -> list:
        methods = ["local"]
        if self.is_rewriteai_enabled:
            methods.append("rewriteai")
        if self.is_gemini_enabled:
            methods.append("gemini")
        if self.is_groq_enabled:
            methods.append("groq")
        if self.is_openai_enabled:
            methods.append("openai")
        return methods
    
    def get_api_status(self) -> dict:
        """Get status of all APIs"""
        return {
            "rewriteai": self.is_rewriteai_enabled,
            "gemini": self.is_gemini_enabled,
            "groq": self.is_groq_enabled,
            "openai": self.is_openai_enabled
        }
    
    @classmethod
    def validate(cls) -> bool:
        valid = True
        valid_tones = ["academic", "natural", "blog", "professional", "conversational"]
        if cls.DEFAULT_TONE not in valid_tones:
            print(f"⚠️ Invalid DEFAULT_TONE: {cls.DEFAULT_TONE}")
            valid = False
        valid_styles = ["conservative", "balanced", "creative"]
        if cls.DEFAULT_STYLE not in valid_styles:
            print(f"⚠️ Invalid DEFAULT_STYLE: {cls.DEFAULT_STYLE}")
            valid = False
        return valid
    
    @classmethod
    def display(cls):
        print("=" * 60)
        print("🔧 CONFIGURATION")
        print("=" * 60)
        print(f"RewriteAI: {'✅' if cls.is_rewriteai_enabled else '❌'}")
        print(f"Gemini: {'✅' if cls.is_gemini_enabled else '❌'}")
        print(f"Groq: {'✅' if cls.is_groq_enabled else '❌'}")
        print(f"OpenAI: {'✅' if cls.is_openai_enabled else '❌'}")
        print(f"Default Tone: {cls.DEFAULT_TONE}")
        print(f"Default Style: {cls.DEFAULT_STYLE}")
        print(f"Max Text Length: {cls.MAX_TEXT_LENGTH}")
        print("=" * 60)

config = Config()
config.create_directories()
config.validate()

__all__ = ["config"]
