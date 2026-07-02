
"""
Humanize Service - Core humanization logic with caching
"""
import time
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from collections import OrderedDict
from backend.models import HumanizeResponse
from backend.services.local_humanizer import LocalHumanizer
from backend.services.api_humanizer import APIHumanizer
from backend.config import config

logger = logging.getLogger(__name__)

class HumanizeService:
    def __init__(self):
        self.local_humanizer = LocalHumanizer()
        self.api_humanizer = APIHumanizer()
        self.start_time = time.time()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_words_processed = 0
        self.total_processing_time = 0.0
        self.methods_used = {}
        self.tones_used = {}
        self.cache = OrderedDict()
        self.cache_max_size = config.CACHE_MAX_SIZE
        self.cache_enabled = config.CACHE_ENABLED
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("✅ HumanizeService initialized")
    
    def humanize(self, text: str, tone: str = "academic", style: str = "balanced", preserve_technical: bool = True, use_cache: bool = True) -> HumanizeResponse:
        start_time = time.time()
        self.total_requests += 1
        if not text or len(text.strip()) < 10:
            raise ValueError("Text must be at least 10 characters long")
        humanized = None
        method_used = "local"
        if config.is_rewriteai_enabled:
            humanized = self.api_humanizer.rewriteai(text, tone)
            if humanized:
                method_used = "rewriteai_api"
                self.methods_used[method_used] = self.methods_used.get(method_used, 0) + 1
        if not humanized and config.is_gemini_enabled:
            humanized = self.api_humanizer.gemini(text, tone)
            if humanized:
                method_used = "gemini_api"
                self.methods_used[method_used] = self.methods_used.get(method_used, 0) + 1
        if not humanized and config.is_groq_enabled:
            humanized = self.api_humanizer.groq(text, tone)
            if humanized:
                method_used = "groq_api"
                self.methods_used[method_used] = self.methods_used.get(method_used, 0) + 1
        if not humanized:
            humanized = self.local_humanizer.humanize(text, tone, style, preserve_technical)
            method_used = "local"
            self.methods_used[method_used] = self.methods_used.get(method_used, 0) + 1
        processing_time = time.time() - start_time
        word_count = len(humanized.split())
        self.successful_requests += 1
        self.total_words_processed += word_count
        self.total_processing_time += processing_time
        self.tones_used[tone] = self.tones_used.get(tone, 0) + 1
        return HumanizeResponse(
            original_text=text,
            humanized_text=humanized,
            tone=tone,
            style=style,
            word_count=word_count,
            processing_time=round(processing_time, 3),
            method_used=method_used,
            timestamp=datetime.now()
        )
    
    def analyze(self, text: str) -> Dict[str, Any]:
        return self.local_humanizer.analyze(text)
    
    def humanize_batch(self, texts: List[str], tone: str = "academic", style: str = "balanced", preserve_technical: bool = True) -> List[HumanizeResponse]:
        results = []
        for text in texts:
            try:
                results.append(self.humanize(text, tone, style, preserve_technical))
            except Exception as e:
                results.append(HumanizeResponse(
                    original_text=text,
                    humanized_text=text,
                    tone=tone,
                    style=style,
                    word_count=len(text.split()),
                    processing_time=0.0,
                    method_used="failed",
                    timestamp=datetime.now()
                ))
        return results
    
    def compare_tones(self, text: str, tones: List[str], style: str = "balanced", preserve_technical: bool = True) -> Dict[str, HumanizeResponse]:
        results = {}
        for tone in tones:
            results[tone] = self.humanize(text, tone, style, preserve_technical)
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        total = self.total_requests
        avg_time = self.total_processing_time / total if total > 0 else 0
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": round(self.successful_requests / total * 100 if total > 0 else 0, 2),
            "average_processing_time": round(avg_time, 3),
            "total_words_processed": self.total_words_processed,
            "methods_used": self.methods_used,
            "tones_used": self.tones_used,
            "uptime": round(time.time() - self.start_time, 2),
        }
    
    def clear_cache(self):
        self.cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("🗑️ Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        total = self.cache_hits + self.cache_misses
        return {
            "enabled": self.cache_enabled,
            "size": len(self.cache),
            "max_size": self.cache_max_size,
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "hit_rate": round(self.cache_hits / total * 100 if total > 0 else 0, 2)
        }
    
    def get_uptime(self) -> float:
        return time.time() - self.start_time

_humanize_service = None

def get_humanize_service() -> HumanizeService:
    global _humanize_service
    if _humanize_service is None:
        _humanize_service = HumanizeService()
    return _humanize_service
