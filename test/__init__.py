"""
Test Package for AI Humanizer
Contains all unit tests for the application

This package includes tests for:
- Configuration
- Data Models
- Humanizer Services
- API Endpoints
- Vocabulary
"""

# ============================================================
# VERSION
# ============================================================

__version__ = "2.0.0"

# ============================================================
# PACKAGE INFO
# ============================================================

def get_test_info() -> dict:
    """
    Get information about the test package
    
    Returns:
        Dictionary with test information
    """
    
    return {
        "package": "tests",
        "version": __version__,
        "description": "Unit tests for AI Humanizer",
        "test_files": [
            "test_config.py",
            "test_models.py",
            "test_humanizer.py",
            "test_api.py",
            "test_vocabulary.py",
        ],
        "frameworks": ["pytest"],
    }


# ============================================================
# INITIALIZATION LOG
# ============================================================

import logging
logger = logging.getLogger(__name__)

logger.info("🧪 Test package initialized")
logger.info(f"   Version: {__version__}")

# ============================================================
# END OF FILE
# ============================================================