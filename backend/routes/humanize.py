"""
Humanize Service - Core humanization logic
Handles all humanization methods with intelligent fallback
"""

import time
import logging
import re
import random
from typing import Optional, Dict, Any, List
from datetime import datetime

from backend.models import HumanizeResponse
from backend.services.local_humanizer import LocalHumanizer
from backend.services.api_humanizer import APIHumanizer
from backend.config import config
from backend.vocabulary import (
    ROBOTIC_PHRASES,
    SYNONYMS,
    TRANSITIONS,
    TONE_SETTINGS,
    DOMAIN_TERMS,
)

logger = logging.getLogger(__name__)


class HumanizeService:
    """
    Core humanization service with multiple strategies
    
    Features:
    - Multiple humanization methods (API + Local)
    - Intelligent fallback mechanism
    - Text analysis and metrics
    - Performance tracking
    - Caching support
    """
    
    def __init__(self):
        """Initialize humanization service"""
        self.local_humanizer = LocalHumanizer()
        self.api_humanizer = APIHumanizer()
        self.start_time = time.time()
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_processing_time": 0.0,
            "total_words_processed": 0,
            "methods_used": {},
            "tones_used": {},
            "cache_hits": 0,
            "cache_misses": 0,
        }
        
        # Simple cache
        self.cache = {}
        self.cache_max_size = config.CACHE_MAX_SIZE
        self.cache_enabled = config.CACHE_ENABLED
        
        logger.info("✅ HumanizeService initialized")
        logger.info(f"   Cache: {'Enabled' if self.cache_enabled else 'Disabled'}")
        logger.info(f"   Available methods: {config.available_methods}")
    
    # ============================================================
    # MAIN HUMANIZATION METHOD
    # ============================================================
    
    def humanize(
        self,
        text: str,
        tone: str = "academic",
        style: str = "balanced",
        preserve_technical: bool = True,
        use_cache: bool = True
    ) -> HumanizeResponse:
        """
        Humanize text using best available method
        
        Args:
            text: Text to humanize
            tone: academic, natural, blog, professional, conversational
            style: conservative, balanced, creative
            preserve_technical: Keep technical terms unchanged
            use_cache: Use cached result if available
            
        Returns:
            HumanizeResponse with humanized text
        """
        
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        # ===== CHECK CACHE =====
        cache_key = self._get_cache_key(text, tone, style, preserve_technical)
        
        if use_cache and self.cache_enabled and cache_key in self.cache:
            logger.info("✅ Cache hit!")
            self.stats["cache_hits"] += 1
            cached_result = self.cache[cache_key]
            cached_result.processing_time = time.time() - start_time
            return cached_result
        
        self.stats["cache_misses"] += 1
        
        # ===== HUMANIZE =====
        humanized = None
        method_used = "local"
        
        # Try API methods in priority order
        humanized = self._try_api_methods(text, tone)
        
        # Fallback to local
        if not humanized:
            logger.info("🔄 Falling back to local humanizer...")
            humanized = self.local_humanizer.humanize(
                text=text,
                tone=tone,
                style=style,
                preserve_technical=preserve_technical
            )
            method_used = "local"
        
        # ===== UPDATE STATS =====
        processing_time = time.time() - start_time
        self._update_stats(method_used, tone, len(humanized.split()), processing_time)
        
        # ===== CREATE RESPONSE =====
        response = HumanizeResponse(
            original_text=text,
            humanized_text=humanized,
            tone=tone,
            style=style,
            word_count=len(humanized.split()),
            processing_time=round(processing_time, 3),
            method_used=method_used,
            timestamp=datetime.now()
        )
        
        # ===== CACHE RESULT =====
        if self.cache_enabled and len(self.cache) < self.cache_max_size:
            self.cache[cache_key] = response
        
        logger.info(f"✅ Humanization complete: {response.word_count} words, {method_used}")
        return response
    
    # ============================================================
    # API METHODS
    # ============================================================
    
    def _try_api_methods(self, text: str, tone: str) -> Optional[str]:
        """Try all available API methods in priority order"""
        
        # 1. RewriteAI
        if config.is_rewriteai_enabled:
            logger.info("📡 Trying RewriteAI API...")
            result = self.api_humanizer.rewriteai(text, tone)
            if result:
                self.stats["methods_used"]["rewriteai_api"] = self.stats["methods_used"].get("rewriteai_api", 0) + 1
                return result
            logger.warning("RewriteAI API failed, trying next...")
        
        # 2. Gemini
        if config.is_gemini_enabled:
            logger.info("📡 Trying Gemini API...")
            result = self.api_humanizer.gemini(text, tone)
            if result:
                self.stats["methods_used"]["gemini_api"] = self.stats["methods_used"].get("gemini_api", 0) + 1
                return result
            logger.warning("Gemini API failed, trying next...")
        
        # 3. Groq
        if config.is_groq_enabled:
            logger.info("📡 Trying Groq API...")
            result = self.api_humanizer.groq(text, tone)
            if result:
                self.stats["methods_used"]["groq_api"] = self.stats["methods_used"].get("groq_api", 0) + 1
                return result
            logger.warning("Groq API failed, using local...")
        
        return None
    
    # ============================================================
    # ANALYSIS METHODS
    # ============================================================
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for various metrics
        
        Returns:
            Dictionary with analysis results
        """
        return self.local_humanizer.analyze(text)
    
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
        results = {}
        for tone in tones:
            results[tone] = self.humanize(
                text=text,
                tone=tone,
                style=style,
                preserve_technical=preserve_technical
            )
        return results
    
    def batch_humanize(
        self,
        texts: List[str],
        tone: str = "academic",
        style: str = "balanced",
        preserve_technical: bool = True
    ) -> List[HumanizeResponse]:
        """
        Humanize multiple texts
        
        Args:
            texts: List of texts to humanize
            tone: Tone for all texts
            style: Style for all texts
            preserve_technical: Keep technical terms
            
        Returns:
            List of HumanizeResponse objects
        """
        results = []
        for text in texts:
            result = self.humanize(
                text=text,
                tone=tone,
                style=style,
                preserve_technical=preserve_technical
            )
            results.append(result)
        return results
    
    # ============================================================
    # UTILITY METHODS
    # ============================================================
    
    def _get_cache_key(self, text: str, tone: str, style: str, preserve_technical: bool) -> str:
        """Generate cache key from parameters"""
        return f"{text[:100]}_{tone}_{style}_{preserve_technical}"
    
    def _update_stats(self, method: str, tone: str, words: int, processing_time: float):
        """Update service statistics"""
        self.stats["successful_requests"] += 1
        self.stats["total_processing_time"] += processing_time
        self.stats["total_words_processed"] += words
        
        self.stats["methods_used"][method] = self.stats["methods_used"].get(method, 0) + 1
        self.stats["tones_used"][tone] = self.stats["tones_used"].get(tone, 0) + 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        total_requests = self.stats["total_requests"]
        avg_time = self.stats["total_processing_time"] / total_requests if total_requests > 0 else 0
        
        return {
            "total_requests": self.stats["total_requests"],
            "successful_requests": self.stats["successful_requests"],
            "failed_requests": self.stats["failed_requests"],
            "success_rate": round(
                self.stats["successful_requests"] / total_requests * 100 if total_requests > 0 else 0,
                2
            ),
            "average_processing_time": round(avg_time, 3),
            "total_words_processed": self.stats["total_words_processed"],
            "methods_used": self.stats["methods_used"],
            "tones_used": self.stats["tones_used"],
            "cache_hits": self.stats["cache_hits"],
            "cache_misses": self.stats["cache_misses"],
            "cache_hit_rate": round(
                self.stats["cache_hits"] / (self.stats["cache_hits"] + self.stats["cache_misses"]) * 100
                if (self.stats["cache_hits"] + self.stats["cache_misses"]) > 0 else 0,
                2
            ),
            "uptime": round(time.time() - self.start_time, 2),
            "cache_size": len(self.cache),
            "available_methods": config.available_methods,
        }
    
    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
        logger.info("🗑️ Cache cleared")
    
    def get_uptime(self) -> float:
        """Get service uptime in seconds"""
        return time.time() - self.start_time


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_humanize_service = None

def get_humanize_service() -> HumanizeService:
    """Get singleton instance of HumanizeService"""
    global _humanize_service
    if _humanize_service is None:
        _humanize_service = HumanizeService()
    return _humanize_service


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "HumanizeService",
    "get_humanize_service",
]