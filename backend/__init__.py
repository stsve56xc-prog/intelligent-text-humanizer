"""
AI Humanizer Backend Package
Intelligent text humanization using NLP and vocabulary databases

This package provides:
- FastAPI application with RESTful API
- Multiple humanization methods (API + Local)
- Text analysis and metrics
- Vocabulary database for intelligent replacement
- Caching and statistics

Version: 2.0.0
"""

from backend.config import config
from backend.models import (
    HumanizeRequest,
    HumanizeResponse,
    BatchHumanizeRequest,
    BatchHumanizeResponse,
    HealthResponse,
    ErrorResponse,
)
from backend.main import app

# ============================================================
# VERSION
# ============================================================

__version__ = "2.0.0"
__title__ = "AI Humanizer API"
__description__ = "Humanize AI-generated text with advanced NLP"

# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    # Main app
    "app",
    
    # Config
    "config",
    
    # Models
    "HumanizeRequest",
    "HumanizeResponse",
    "BatchHumanizeRequest",
    "BatchHumanizeResponse",
    "HealthResponse",
    "ErrorResponse",
    
    # Version info
    "__version__",
    "__title__",
    "__description__",
]

# ============================================================
# PACKAGE INFO
# ============================================================

def get_package_info() -> dict:
    """
    Get comprehensive package information
    
    Returns:
        Dictionary with package details
    """
    
    return {
        "name": __title__,
        "version": __version__,
        "description": __description__,
        "author": "AI Humanizer Team",
        "license": "MIT",
        "python_version": "3.9+",
        "framework": "FastAPI",
        "available_methods": config.available_methods,
        "api_status": config.api_status,
        "features": [
            "Text humanization",
            "Batch processing",
            "Text analysis",
            "Tone comparison",
            "Caching",
            "Statistics tracking",
        ],
        "limits": {
            "max_text_length": config.MAX_TEXT_LENGTH,
            "min_text_length": config.MIN_TEXT_LENGTH,
            "max_batch_size": config.MAX_BATCH_SIZE,
        },
        "defaults": {
            "tone": config.DEFAULT_TONE,
            "style": config.DEFAULT_STYLE,
            "preserve_technical": config.DEFAULT_PRESERVE_TECHNICAL,
        },
    }


# ============================================================
# INITIALIZATION LOG
# ============================================================

import logging
logger = logging.getLogger(__name__)

logger.info("=" * 60)
logger.info(f"📦 {__title__} v{__version__}")
logger.info(f"📝 {__description__}")
logger.info("=" * 60)
logger.info(f"🔧 Available methods: {config.available_methods}")
logger.info(f"💾 Cache: {'Enabled' if config.CACHE_ENABLED else 'Disabled'}")
logger.info(f"📊 Environment: {config.ENVIRONMENT if hasattr(config, 'ENVIRONMENT') else 'development'}")
logger.info("=" * 60)

# ============================================================
# END OF FILE
# ============================================================