"""
Main Humanizer Service - Orchestrates all humanization methods
This is the main entry point for text humanization
"""

import time
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from backend.models import HumanizeResponse, AnalysisResult
from backend.services.local_humanizer import LocalHumanizer
from backend.services.api_humanizer import APIHumanizer
from backend.config import config

logger = logging.getLogger(__name__)


class HumanizerService:
    """
    Orchestrates humanization with fallback mechanisms
    
    Priority Order:
    1. RewriteAI API (if key exists)
    2. Gemini API (if key exists)
    3. Groq API (if key exists)
    4. Local humanizer (fallback - always available)
    
    Features:
    - Automatic fallback if API fails
    - Statistics tracking
    - Performance monitoring
    - Multi-tone support
    """
    
    def __init__(self):
        """Initialize humanizer service with all available methods"""
        
        # Initialize humanizers
        self.local_humanizer = LocalHumanizer()
        self.api_humanizer = APIHumanizer()
        
        # Service stats
        self.start_time = time.time()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_words_processed = 0
        self.total_processing_time = 0.0
        self.methods_used = {}
        self.tones_used = {}
        
        # Log available methods
        logger.info("🚀 HumanizerService initialized")
        logger.info(f"   Available methods: {config.available_methods}")
        logger.info(f"   Cache enabled: {config.CACHE_ENABLED}")
    
    # ============================================================
    # MAIN HUMANIZATION METHOD
    # ============================================================
    
    def humanize(
        self,
        text: str,
        tone: str = "academic",
        style: str = "balanced",
        preserve_technical: bool = True
    ) -> HumanizeResponse:
        """
        Humanize text using best available method
        
        Args:
            text: Text to humanize (min 10 chars)
            tone: academic, natural, blog, professional, conversational
            style: conservative, balanced, creative
            preserve_technical: Keep technical/scientific terms unchanged
            
        Returns:
            HumanizeResponse with original and humanized text
            
        Raises:
            ValueError: If text is invalid
            Exception: If humanization fails
        """
        
        start_time = time.time()
        self.total_requests += 1
        
        # ===== VALIDATE INPUT =====
        if not text or len(text.strip()) < 10:
            raise ValueError("Text must be at least 10 characters long")
        
        if len(text) > config.MAX_TEXT_LENGTH:
            raise ValueError(f"Text exceeds maximum length of {config.MAX_TEXT_LENGTH} characters")
        
        # ===== TRY API METHODS (in priority order) =====
        humanized = None
        method_used = "local"
        
        # 1. Try RewriteAI API
        if config.is_rewriteai_enabled:
            logger.info("📡 Attempting RewriteAI API...")
            humanized = self.api_humanizer.rewriteai(text, tone)
            if humanized:
                method_used = "rewriteai_api"
                logger.info("✅ RewriteAI API successful")
                self.methods_used[method_used] = self.methods_used.get(method_used, 0) + 1
        
        # 2. Try Gemini API (if RewriteAI failed)
        if not humanized and config.is_gemini_enabled:
            logger.info("📡 Attempting Gemini API...")
            humanized = self.api_humanizer.gemini(text, tone)
            if humanized:
                method_used = "gemini_api"
                logger.info("✅ Gemini API successful")
                self.methods_used[method_used] = self.methods_used.get(method_used, 0) + 1
        
        # 3. Try Groq API (if Gemini failed)
        if not humanized and config.is_groq_enabled:
            logger.info("📡 Attempting Groq API...")
            humanized = self.api_humanizer.groq(text, tone)
            if humanized:
                method_used = "groq_api"
                logger.info("✅ Groq API successful")
                self.methods_used[method_used] = self.methods_used.get(method_used, 0) + 1
        
        # 4. Fallback to Local (always available)
        if not humanized:
            logger.info("🔄 Using local humanizer (fallback)...")
            humanized = self.local_humanizer.humanize(
                text=text,
                tone=tone,
                style=style,
                preserve_technical=preserve_technical
            )
            method_used = "local"
            self.methods_used[method_used] = self.methods_used.get(method_used, 0) + 1
        
        # ===== UPDATE STATS =====
        processing_time = time.time() - start_time
        word_count = len(humanized.split())
        
        self.successful_requests += 1
        self.total_words_processed += word_count
        self.total_processing_time += processing_time
        self.tones_used[tone] = self.tones_used.get(tone, 0) + 1
        
        # ===== CREATE RESPONSE =====
        response = HumanizeResponse(
            original_text=text,
            humanized_text=humanized,
            tone=tone,
            style=style,
            word_count=word_count,
            processing_time=round(processing_time, 3),
            method_used=method_used,
            timestamp=datetime.now()
        )
        
        logger.info(f"✅ Humanization complete: {word_count} words, {method_used}, {processing_time:.3f}s")
        return response
    
    # ============================================================
    # BATCH HUMANIZATION
    # ============================================================
    
    def humanize_batch(
        self,
        texts: List[str],
        tone: str = "academic",
        style: str = "balanced",
        preserve_technical: bool = True
    ) -> List[HumanizeResponse]:
        """
        Humanize multiple texts in batch
        
        Args:
            texts: List of texts to humanize (max 50)
            tone: Tone for all texts
            style: Style for all texts
            preserve_technical: Keep technical terms
            
        Returns:
            List of HumanizeResponse objects
        """
        
        if not texts:
            raise ValueError("At least one text is required")
        
        if len(texts) > config.MAX_BATCH_SIZE:
            raise ValueError(f"Maximum {config.MAX_BATCH_SIZE} texts allowed")
        
        results = []
        for i, text in enumerate(texts):
            logger.info(f"Processing text {i+1}/{len(texts)}...")
            try:
                result = self.humanize(
                    text=text,
                    tone=tone,
                    style=style,
                    preserve_technical=preserve_technical
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to humanize text {i+1}: {e}")
                # Return original text if fails
                results.append(HumanizeResponse(
                    original_text=text,
                    humanized_text=text,  # Return original on failure
                    tone=tone,
                    style=style,
                    word_count=len(text.split()),
                    processing_time=0.0,
                    method_used="failed",
                    timestamp=datetime.now()
                ))
                self.failed_requests += 1
        
        return results
    
    # ============================================================
    # TEXT ANALYSIS
    # ============================================================
    
    def analyze(self, text: str) -> AnalysisResult:
        """
        Analyze text for various metrics
        
        Args:
            text: Text to analyze
            
        Returns:
            AnalysisResult with metrics
        """
        
        if not text or len(text.strip()) < 10:
            raise ValueError("Text must be at least 10 characters long")
        
        return self.local_humanizer.analyze(text)
    
    # ============================================================
    # TONE COMPARISON
    # ============================================================
    
    def compare_tones(
        self,
        text: str,
        tones: List[str],
        style: str = "balanced",
        preserve_technical: bool = True
    ) -> Dict[str, HumanizeResponse]:
        """
        Compare multiple tones for the same text
        
        Args:
            text: Text to humanize
            tones: List of tones to compare
            style: Style for all variations
            preserve_technical: Keep technical terms
            
        Returns:
            Dictionary of tone -> HumanizeResponse
        """
        
        if not tones:
            raise ValueError("At least one tone is required")
        
        results = {}
        for tone in tones:
            logger.info(f"Comparing tone: {tone}")
            results[tone] = self.humanize(
                text=text,
                tone=tone,
                style=style,
                preserve_technical=preserve_technical
            )
        
        return results
    
    # ============================================================
    # STATISTICS
    # ============================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get service statistics
        
        Returns:
            Dictionary with all statistics
        """
        
        total = self.total_requests
        avg_time = self.total_processing_time / total if total > 0 else 0
        
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": round(
                self.successful_requests / total * 100 if total > 0 else 0,
                2
            ),
            "average_processing_time": round(avg_time, 3),
            "total_words_processed": self.total_words_processed,
            "methods_used": self.methods_used,
            "tones_used": self.tones_used,
            "uptime": round(time.time() - self.start_time, 2),
            "available_methods": config.available_methods,
        }
    
    def reset_stats(self):
        """Reset all statistics"""
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_words_processed = 0
        self.total_processing_time = 0.0
        self.methods_used = {}
        self.tones_used = {}
        self.start_time = time.time()
        logger.info("🔄 Statistics reset")
    
    def get_uptime(self) -> float:
        """Get service uptime in seconds"""
        return time.time() - self.start_time
    
    # ============================================================
    # UTILITY METHODS
    # ============================================================
    
    def is_available(self) -> bool:
        """Check if service is available"""
        return True  # Always available (local fallback)
    
    def get_available_methods(self) -> List[str]:
        """Get list of available humanization methods"""
        return config.available_methods
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get comprehensive service information
        
        Returns:
            Dictionary with service details
        """
        return {
            "name": "AI Humanizer Service",
            "version": "2.0.0",
            "status": "healthy" if self.is_available() else "unhealthy",
            "uptime": self.get_uptime(),
            "methods": self.get_available_methods(),
            "api_status": config.api_status,
            "stats": self.get_stats(),
            "limits": {
                "max_text_length": config.MAX_TEXT_LENGTH,
                "min_text_length": config.MIN_TEXT_LENGTH,
                "max_batch_size": config.MAX_BATCH_SIZE,
                "rate_limit": f"{config.RATE_LIMIT_REQUESTS} per {config.RATE_LIMIT_PERIOD}s"
            },
            "defaults": {
                "tone": config.DEFAULT_TONE,
                "style": config.DEFAULT_STYLE,
                "preserve_technical": config.DEFAULT_PRESERVE_TECHNICAL
            },
            "cache": {
                "enabled": config.CACHE_ENABLED,
                "ttl": config.CACHE_TTL,
                "max_size": config.CACHE_MAX_SIZE
            }
        }


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_humanizer = None

def get_humanizer() -> HumanizerService:
    """
    Get singleton instance of HumanizerService
    
    Returns:
        HumanizerService instance
    """
    global _humanizer
    if _humanizer is None:
        _humanizer = HumanizerService()
    return _humanizer


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "HumanizerService",
    "get_humanizer",
]