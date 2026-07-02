"""
Services Package
Contains all business logic and service layer components

This package provides:
- HumanizerService: Main orchestrator for humanization
- LocalHumanizer: Local text humanization without APIs
- APIHumanizer: External API integrations
- HumanizeService: Core humanization with caching
"""

from backend.services.humanizer import HumanizerService, get_humanizer
from backend.services.local_humanizer import LocalHumanizer
from backend.services.api_humanizer import APIHumanizer, get_api_humanizer
from backend.services.humanize import HumanizeService, get_humanize_service

# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    # Humanizer Service (Main)
    "HumanizerService",
    "get_humanizer",
    
    # Local Humanizer
    "LocalHumanizer",
    
    # API Humanizer
    "APIHumanizer",
    "get_api_humanizer",
    
    # Humanize Service (with cache)
    "HumanizeService",
    "get_humanize_service",
]

# ============================================================
# VERSION
# ============================================================

__version__ = "2.0.0"

# ============================================================
# PACKAGE INFO
# ============================================================

def get_service_info() -> dict:
    """
    Get information about all available services
    
    Returns:
        Dictionary with service information
    """
    from backend.config import config
    
    return {
        "package": "backend.services",
        "version": __version__,
        "available_methods": config.available_methods,
        "services": {
            "humanizer": {
                "class": "HumanizerService",
                "description": "Main orchestrator with fallback",
                "available": True,
            },
            "local": {
                "class": "LocalHumanizer",
                "description": "No API required, pure local",
                "available": True,
            },
            "api": {
                "class": "APIHumanizer",
                "description": "External API integrations",
                "available": bool(config.available_methods),
            },
            "humanize": {
                "class": "HumanizeService",
                "description": "Core humanization with caching",
                "available": True,
            },
        },
        "api_status": config.api_status,
    }


# ============================================================
# INITIALIZATION LOG
# ============================================================

import logging
logger = logging.getLogger(__name__)

logger.info("📦 Services package initialized")
logger.info(f"   Version: {__version__}")
logger.info(f"   Available methods: {get_service_info()['available_methods']}")

# ============================================================
# END OF FILE
# ============================================================