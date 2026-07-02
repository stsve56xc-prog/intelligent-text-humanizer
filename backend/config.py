"""
Configuration Module for AI Humanizer API
All environment variables and settings
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# ========== BASE CONFIG ==========

class Config:
    """
    Main configuration class for AI Humanizer API
    Loads all settings from environment variables with defaults
    """
    
    # ========== API KEYS ==========
    
    # RewriteAI API
    REWRITE_API_KEY: str = os.getenv("REWRITE_API_KEY", "")
    REWRITE_API_URL: str = os.getenv("REWRITE_API_URL", "https://rewriteai.com/api/v1/humanize")
    
    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_API_URL: str = os.getenv(
        "GEMINI_API_URL",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    )
    
    # Groq API
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_API_URL: str = os.getenv(
        "GROQ_API_URL",
        "https://api.groq.com/openai/v1/chat/completions"
    )
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
    
    # OpenAI API (Optional)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_URL: str = os.getenv(
        "OPENAI_API_URL",
        "https://api.openai.com/v1/chat/completions"
    )
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # ========== API SETTINGS ==========
    
    # Timeouts (in seconds)
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    API_CONNECT_TIMEOUT: int = int(os.getenv("API_CONNECT_TIMEOUT", "10"))
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # seconds
    
    # ========== TEXT LIMITS ==========
    
    MAX_TEXT_LENGTH: int = int(os.getenv("MAX_TEXT_LENGTH", "5000"))
    MIN_TEXT_LENGTH: int = int(os.getenv("MIN_TEXT_LENGTH", "10"))
    MAX_BATCH_SIZE: int = int(os.getenv("MAX_BATCH_SIZE", "50"))
    
    # ========== DEFAULT SETTINGS ==========
    
    DEFAULT_TONE: str = os.getenv("DEFAULT_TONE", "academic")
    DEFAULT_STYLE: str = os.getenv("DEFAULT_STYLE", "balanced")
    DEFAULT_PRESERVE_TECHNICAL: bool = os.getenv("DEFAULT_PRESERVE_TECHNICAL", "true").lower() == "true"
    
    # ========== SERVER SETTINGS ==========
    
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    RELOAD: bool = os.getenv("RELOAD", "true").lower() == "true"
    
    # ========== LOGGING ==========
    
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", "logs/app.log")
    
    # ========== CORS SETTINGS ==========
    
    CORS_ALLOW_ORIGINS: list = os.getenv(
        "CORS_ALLOW_ORIGINS",
        "*"
    ).split(",")
    
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    CORS_ALLOW_METHODS: list = os.getenv(
        "CORS_ALLOW_METHODS",
        "*"
    ).split(",")
    
    CORS_ALLOW_HEADERS: list = os.getenv(
        "CORS_ALLOW_HEADERS",
        "*"
    ).split(",")
    
    # ========== CACHE SETTINGS ==========
    
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "1000"))
    
    # ========== FILE PATHS ==========
    
    BASE_DIR: Path = Path(__file__).parent.parent
    WORD_DATA_DIR: Path = BASE_DIR / "word_data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    MODELS_DIR: Path = BASE_DIR / "models"
    VOCABULARY_DIR: Path = BASE_DIR / "vocabulary"
    
    # Create directories if they don't exist
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        for dir_path in [cls.LOGS_DIR, cls.WORD_DATA_DIR, cls.MODELS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    # ========== PROPERTIES ==========
    
    @property
    def is_rewriteai_enabled(self) -> bool:
        """Check if RewriteAI API is configured"""
        return bool(self.REWRITE_API_KEY)
    
    @property
    def is_gemini_enabled(self) -> bool:
        """Check if Gemini API is configured"""
        return bool(self.GEMINI_API_KEY)
    
    @property
    def is_groq_enabled(self) -> bool:
        """Check if Groq API is configured"""
        return bool(self.GROQ_API_KEY)
    
    @property
    def is_openai_enabled(self) -> bool:
        """Check if OpenAI API is configured"""
        return bool(self.OPENAI_API_KEY)
    
    @property
    def available_methods(self) -> list:
        """Get list of available humanization methods"""
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
    
    @property
    def api_status(self) -> Dict[str, bool]:
        """Get status of all APIs"""
        return {
            "rewriteai": self.is_rewriteai_enabled,
            "gemini": self.is_gemini_enabled,
            "groq": self.is_groq_enabled,
            "openai": self.is_openai_enabled
        }
    
    # ========== VALIDATION ==========
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        valid = True
        
        # Validate tone
        valid_tones = ["academic", "natural", "blog", "professional", "conversational"]
        if cls.DEFAULT_TONE not in valid_tones:
            print(f"⚠️ Invalid DEFAULT_TONE: {cls.DEFAULT_TONE}")
            valid = False
        
        # Validate style
        valid_styles = ["conservative", "balanced", "creative"]
        if cls.DEFAULT_STYLE not in valid_styles:
            print(f"⚠️ Invalid DEFAULT_STYLE: {cls.DEFAULT_STYLE}")
            valid = False
        
        # Validate limits
        if cls.MAX_TEXT_LENGTH < cls.MIN_TEXT_LENGTH:
            print(f"⚠️ MAX_TEXT_LENGTH ({cls.MAX_TEXT_LENGTH}) < MIN_TEXT_LENGTH ({cls.MIN_TEXT_LENGTH})")
            valid = False
        
        return valid
    
    # ========== DISPLAY ==========
    
    @classmethod
    def display(cls):
        """Display all configuration settings"""
        print("\n" + "=" * 60)
        print("🔧 AI HUMANIZER CONFIGURATION")
        print("=" * 60)
        
        print("\n📡 APIs:")
        print(f"  RewriteAI: {'✅ Enabled' if cls.is_rewriteai_enabled else '❌ Disabled'}")
        print(f"  Gemini:    {'✅ Enabled' if cls.is_gemini_enabled else '❌ Disabled'}")
        print(f"  Groq:      {'✅ Enabled' if cls.is_groq_enabled else '❌ Disabled'}")
        print(f"  OpenAI:    {'✅ Enabled' if cls.is_openai_enabled else '❌ Disabled'}")
        print(f"  Available Methods: {', '.join(cls.available_methods)}")
        
        print("\n📝 Limits:")
        print(f"  Max Text Length: {cls.MAX_TEXT_LENGTH}")
        print(f"  Min Text Length: {cls.MIN_TEXT_LENGTH}")
        print(f"  Max Batch Size:  {cls.MAX_BATCH_SIZE}")
        
        print("\n🎨 Defaults:")
        print(f"  Default Tone:    {cls.DEFAULT_TONE}")
        print(f"  Default Style:   {cls.DEFAULT_STYLE}")
        print(f"  Preserve Tech:   {cls.DEFAULT_PRESERVE_TECHNICAL}")
        
        print("\n🌐 Server:")
        print(f"  Host: {cls.HOST}")
        print(f"  Port: {cls.PORT}")
        print(f"  Debug: {cls.DEBUG}")
        print(f"  Reload: {cls.RELOAD}")
        
        print("\n⚡ Performance:")
        print(f"  API Timeout:     {cls.API_TIMEOUT}s")
        print(f"  Cache Enabled:   {cls.CACHE_ENABLED}")
        print(f"  Cache TTL:       {cls.CACHE_TTL}s")
        print(f"  Rate Limit:      {cls.RATE_LIMIT_REQUESTS} per {cls.RATE_LIMIT_PERIOD}s")
        
        print("\n📁 Paths:")
        print(f"  Base Directory:  {cls.BASE_DIR}")
        print(f"  Word Data:       {cls.WORD_DATA_DIR}")
        print(f"  Logs Directory:  {cls.LOGS_DIR}")
        print(f"  Models:          {cls.MODELS_DIR}")
        
        print("\n" + "=" * 60)
        print("✅ Configuration loaded successfully!")
        print("=" * 60 + "\n")


# ========== ENVIRONMENT DETECTION ==========

class Environment:
    """Detect and manage environment settings"""
    
    @staticmethod
    def is_production() -> bool:
        """Check if running in production"""
        return os.getenv("ENVIRONMENT", "").lower() == "production"
    
    @staticmethod
    def is_development() -> bool:
        """Check if running in development"""
        return os.getenv("ENVIRONMENT", "").lower() == "development" or Config.DEBUG
    
    @staticmethod
    def is_testing() -> bool:
        """Check if running in testing"""
        return os.getenv("ENVIRONMENT", "").lower() == "testing"
    
    @staticmethod
    def get_environment() -> str:
        """Get current environment name"""
        env = os.getenv("ENVIRONMENT", "development")
        if Config.DEBUG and env == "production":
            return "production_with_debug"
        return env
    
    @staticmethod
    def is_cloud() -> bool:
        """Check if running in cloud environment"""
        return bool(os.getenv("CLOUD_PROVIDER", ""))

env = Environment()


# ========== DEVELOPMENT ==========

class DevelopmentConfig(Config):
    """Development-specific configuration"""
    
    DEBUG = True
    RELOAD = True
    LOG_LEVEL = "DEBUG"
    CACHE_ENABLED = False


class ProductionConfig(Config):
    """Production-specific configuration"""
    
    DEBUG = False
    RELOAD = False
    LOG_LEVEL = "WARNING"
    CACHE_ENABLED = True


class TestingConfig(Config):
    """Testing-specific configuration"""
    
    DEBUG = True
    RELOAD = False
    LOG_LEVEL = "DEBUG"
    CACHE_ENABLED = False
    MAX_TEXT_LENGTH = 1000
    RATE_LIMIT_REQUESTS = 9999  # No rate limiting in tests


# ========== CONFIG SELECTOR ==========

def get_config() -> Config:
    """Get the appropriate config based on environment"""
    
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig
    elif env == "testing":
        return TestingConfig
    else:
        return DevelopmentConfig


# ========== SINGLETON ==========

config = get_config()

# Create directories on import
config.create_directories()

# Validate config on import
if not config.validate():
    print("⚠️ Configuration validation failed! Please check your settings.")


# ========== EXPORTS ==========

__all__ = [
    "Config",
    "DevelopmentConfig",
    "ProductionConfig",
    "TestingConfig",
    "Environment",
    "config",
    "env",
    "get_config",
]