"""
AI Humanizer API - Main Entry Point
FastAPI application with all routes and middleware
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import time
import os
from datetime import datetime
from typing import Dict, Any

# ============================================================
# CONFIGURATION
# ============================================================

from backend.config import config
from backend.models import HealthResponse, ErrorResponse

# ============================================================
# LOGGING SETUP
# ============================================================

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ============================================================
# CREATE FASTAPI APP
# ============================================================

app = FastAPI(
    title="AI Humanizer API",
    description="Humanize AI-generated text with advanced NLP and intelligent rewriting",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ============================================================
# CORS MIDDLEWARE
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ALLOW_ORIGINS,
    allow_credentials=config.CORS_ALLOW_CREDENTIALS,
    allow_methods=config.CORS_ALLOW_METHODS,
    allow_headers=config.CORS_ALLOW_HEADERS,
)

# ============================================================
# REQUEST LOGGING MIDDLEWARE
# ============================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    
    start_time = time.time()
    
    # Get request details
    method = request.method
    url = str(request.url)
    client_host = request.client.host if request.client else "unknown"
    
    # Log request
    logger.info(f"📥 {method} {url} from {client_host}")
    
    try:
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"📤 {method} {url} → {response.status_code} "
            f"({process_time:.3f}s)"
        )
        
        # Add custom header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        logger.error(f"❌ {method} {url} → Error: {str(e)}")
        raise

# ============================================================
# EXCEPTION HANDLERS
# ============================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(f"Validation error: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error. Please try again later.",
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )

# ============================================================
# HEALTH CHECK
# ============================================================

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health Check",
    description="Check if the API is running and all dependencies are available"
)
async def health_check():
    """
    Health check endpoint
    
    Returns:
        HealthResponse with service status
    """
    
    from backend.services import get_humanizer
    from backend.config import config
    
    humanizer = get_humanizer()
    
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        timestamp=datetime.now(),
        methods_available=config.available_methods,
        uptime_seconds=humanizer.get_uptime(),
        dependencies=config.api_status
    )

# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get(
    "/",
    tags=["System"],
    summary="API Information",
    description="Get basic information about the API"
)
async def root():
    """
    Root endpoint with API information
    
    Returns:
        API information with available endpoints
    """
    
    return {
        "name": "AI Humanizer API",
        "version": "2.0.0",
        "description": "Humanize AI-generated text with advanced NLP",
        "endpoints": {
            "/": "This information",
            "/docs": "Swagger UI documentation",
            "/redoc": "ReDoc documentation",
            "/health": "Health check",
            "/api/humanize": "Humanize a single text (POST)",
            "/api/humanize/batch": "Humanize multiple texts (POST)",
            "/api/analyze": "Analyze text metrics (POST)",
            "/api/compare": "Compare tones (POST)",
            "/api/stats": "Service statistics (GET)",
        },
        "methods_available": config.available_methods,
        "defaults": {
            "tone": config.DEFAULT_TONE,
            "style": config.DEFAULT_STYLE,
            "preserve_technical": config.DEFAULT_PRESERVE_TECHNICAL
        },
        "limits": {
            "max_text_length": config.MAX_TEXT_LENGTH,
            "min_text_length": config.MIN_TEXT_LENGTH,
            "max_batch_size": config.MAX_BATCH_SIZE
        },
        "timestamp": datetime.now().isoformat()
    }

# ============================================================
# STATISTICS ENDPOINT
# ============================================================

@app.get(
    "/api/stats",
    tags=["System"],
    summary="Service Statistics",
    description="Get detailed statistics about the service"
)
async def get_stats():
    """
    Get service statistics
    
    Returns:
        Dictionary with service statistics
    """
    
    from backend.services import get_humanizer
    
    humanizer = get_humanizer()
    stats = humanizer.get_stats()
    
    return {
        "service": "AI Humanizer API",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "stats": stats,
        "api_status": config.api_status,
        "settings": {
            "cache_enabled": config.CACHE_ENABLED,
            "cache_ttl": config.CACHE_TTL,
            "rate_limit": f"{config.RATE_LIMIT_REQUESTS} per {config.RATE_LIMIT_PERIOD}s",
            "max_text_length": config.MAX_TEXT_LENGTH,
        }
    }

# ============================================================
# CLEAR CACHE ENDPOINT
# ============================================================

@app.post(
    "/api/cache/clear",
    tags=["System"],
    summary="Clear Cache",
    description="Clear the service cache"
)
async def clear_cache():
    """
    Clear the service cache
    
    Returns:
        Success message
    """
    
    from backend.services import get_humanize_service
    
    service = get_humanize_service()
    service.clear_cache()
    
    return {
        "status": "success",
        "message": "Cache cleared successfully",
        "timestamp": datetime.now().isoformat()
    }

# ============================================================
# RESET STATS ENDPOINT
# ============================================================

@app.post(
    "/api/stats/reset",
    tags=["System"],
    summary="Reset Statistics",
    description="Reset all service statistics"
)
async def reset_stats():
    """
    Reset service statistics
    
    Returns:
        Success message
    """
    
    from backend.services import get_humanizer
    
    humanizer = get_humanizer()
    humanizer.reset_stats()
    
    return {
        "status": "success",
        "message": "Statistics reset successfully",
        "timestamp": datetime.now().isoformat()
    }

# ============================================================
# IMPORT AND INCLUDE ROUTES
# ============================================================

from backend.routes import humanize_router

app.include_router(humanize_router)

# ============================================================
# STARTUP EVENT
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    
    logger.info("=" * 60)
    logger.info("🚀 AI Humanizer API Starting...")
    logger.info("=" * 60)
    logger.info(f"📚 Version: 2.0.0")
    logger.info(f"🌐 Host: {config.HOST}:{config.PORT}")
    logger.info(f"📖 Docs: http://{config.HOST}:{config.PORT}/docs")
    logger.info(f"🔧 Debug Mode: {config.DEBUG}")
    logger.info(f"📡 Available Methods: {config.available_methods}")
    logger.info(f"💾 Cache: {'Enabled' if config.CACHE_ENABLED else 'Disabled'}")
    logger.info("=" * 60)
    
    # Log API status
    for api, enabled in config.api_status.items():
        status = "✅" if enabled else "❌"
        logger.info(f"   {status} {api.upper()}: {'Configured' if enabled else 'Not configured'}")
    
    logger.info("=" * 60)
    logger.info("✅ API is ready to serve requests!")

# ============================================================
# SHUTDOWN EVENT
# ============================================================

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    
    logger.info("🛑 AI Humanizer API shutting down...")
    logger.info("👋 Goodbye!")

# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting server...")
    
    uvicorn.run(
        "backend.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD,
        log_level=config.LOG_LEVEL.lower(),
        access_log=True,
    )

# ============================================================
# EXPORTS
# ============================================================

__all__ = ["app"]