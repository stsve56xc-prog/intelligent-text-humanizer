"""
Routes Package
Contains all API route handlers for the AI Humanizer

This package provides:
- humanize: Main humanization endpoints
- Additional routes can be added here
"""

from backend.routes.humanize import router as humanize_router

# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "humanize_router",
]

# ============================================================
# VERSION
# ============================================================

__version__ = "2.0.0"

# ============================================================
# PACKAGE INFO
# ============================================================

def get_routes_info() -> dict:
    """
    Get information about all available routes
    
    Returns:
        Dictionary with route information
    """
    
    return {
        "package": "backend.routes",
        "version": __version__,
        "routes": {
            "humanize": {
                "prefix": "/api",
                "tags": ["humanize"],
                "endpoints": [
                    "POST /api/humanize",
                    "POST /api/humanize/batch",
                    "POST /api/analyze",
                    "POST /api/compare",
                ]
            }
        }
    }


# ============================================================
# INITIALIZATION LOG
# ============================================================

import logging
logger = logging.getLogger(__name__)

logger.info("📦 Routes package initialized")
logger.info(f"   Version: {__version__}")
logger.info(f"   Routes loaded: humanize_router")

# ============================================================
# END OF FILE
# ============================================================