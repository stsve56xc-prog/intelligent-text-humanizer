import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    """Application configuration"""
    
    # API Keys
    REWRITE_API_KEY: str = os.getenv("REWRITE_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # API URLs
    REWRITE_URL: str = "https://rewriteai.com/api/v1/humanize"
    GEMINI_URL: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    GROQ_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    
    # Limits
    MAX_TEXT_LENGTH: int = 5000
    DEFAULT_TONE: str = "academic"
    DEFAULT_STYLE: str = "balanced"
    
    # Timeouts
    API_TIMEOUT: int = 30
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @property
    def is_rewriteai_enabled(self) -> bool:
        return bool(self.REWRITE_API_KEY)
    
    @property
    def is_gemini_enabled(self) -> bool:
        return bool(self.GEMINI_API_KEY)
    
    @property
    def is_groq_enabled(self) -> bool:
        return bool(self.GROQ_API_KEY)

config = Config()