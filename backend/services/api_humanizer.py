"""
External API Humanizers
Handles all third-party API calls for humanization
"""

import requests
import logging
import time
from typing import Optional, Dict, Any, List
from datetime import datetime

from backend.config import config

logger = logging.getLogger(__name__)


class APIHumanizer:
    """
    Handles all external API calls for humanization
    
    Supported APIs:
    - RewriteAI (Primary)
    - Gemini (Fallback 1)
    - Groq (Fallback 2)
    - OpenAI (Optional)
    
    Features:
    - Automatic retry on failure
    - Timeout handling
    - Error logging
    - Response validation
    """
    
    def __init__(self):
        """Initialize API humanizer"""
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
        # API status tracking
        self.api_status = {
            "rewriteai": {"available": False, "last_used": None, "success_count": 0, "fail_count": 0},
            "gemini": {"available": False, "last_used": None, "success_count": 0, "fail_count": 0},
            "groq": {"available": False, "last_used": None, "success_count": 0, "fail_count": 0},
            "openai": {"available": False, "last_used": None, "success_count": 0, "fail_count": 0},
        }
        
        logger.info("✅ APIHumanizer initialized")
    
    # ============================================================
    # REWRITE AI API
    # ============================================================
    
    def rewriteai(self, text: str, tone: str) -> Optional[str]:
        """
        Humanize using RewriteAI API
        
        Args:
            text: Text to humanize
            tone: Tone to apply
            
        Returns:
            Humanized text or None if failed
        """
        
        if not config.is_rewriteai_enabled:
            logger.warning("RewriteAI API key not configured")
            return None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"📡 Calling RewriteAI API (attempt {attempt + 1})...")
                
                response = requests.post(
                    config.REWRITE_API_URL,
                    headers={
                        "Authorization": f"Bearer {config.REWRITE_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": text,
                        "tone": tone
                    },
                    timeout=config.API_TIMEOUT
                )
                
                # Check response
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate response structure
                    if "results" in data and len(data["results"]) > 0:
                        result = data["results"][0].get("text", "")
                        if result:
                            logger.info(f"✅ RewriteAI: {len(result)} chars")
                            self._update_api_status("rewriteai", True)
                            return result
                
                # Handle rate limiting
                if response.status_code == 429:
                    logger.warning(f"Rate limited by RewriteAI (attempt {attempt + 1})")
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                
                # Handle other errors
                logger.warning(f"RewriteAI API error: {response.status_code}")
                self._update_api_status("rewriteai", False)
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.Timeout:
                logger.error(f"RewriteAI API timeout (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                logger.error(f"RewriteAI API exception: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        return None
    
    # ============================================================
    # GEMINI API
    # ============================================================
    
    def gemini(self, text: str, tone: str) -> Optional[str]:
        """
        Humanize using Gemini API
        
        Args:
            text: Text to humanize
            tone: Tone to apply
            
        Returns:
            Humanized text or None if failed
        """
        
        if not config.is_gemini_enabled:
            logger.warning("Gemini API key not configured")
            return None
        
        # Build prompt
        prompt = (
            f"Rewrite the following text to sound {tone} and more human-like. "
            f"Keep all technical terms and scientific language. "
            f"Make it flow naturally and vary sentence structure. "
            f"Return only the rewritten text, nothing else.\n\n"
            f"Text: {text}"
        )
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"📡 Calling Gemini API (attempt {attempt + 1})...")
                
                response = requests.post(
                    f"{config.GEMINI_API_URL}?key={config.GEMINI_API_KEY}",
                    json={
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }],
                        "generationConfig": {
                            "temperature": 0.7,
                            "topK": 40,
                            "topP": 0.95,
                            "maxOutputTokens": 1024,
                        }
                    },
                    timeout=config.API_TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "candidates" in data and len(data["candidates"]) > 0:
                        result = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        if result:
                            logger.info(f"✅ Gemini: {len(result)} chars")
                            self._update_api_status("gemini", True)
                            return result
                
                # Handle rate limiting
                if response.status_code == 429:
                    logger.warning(f"Rate limited by Gemini (attempt {attempt + 1})")
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                
                logger.warning(f"Gemini API error: {response.status_code}")
                self._update_api_status("gemini", False)
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.Timeout:
                logger.error(f"Gemini API timeout (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                logger.error(f"Gemini API exception: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        return None
    
    # ============================================================
    # GROQ API
    # ============================================================
    
    def groq(self, text: str, tone: str) -> Optional[str]:
        """
        Humanize using Groq API
        
        Args:
            text: Text to humanize
            tone: Tone to apply
            
        Returns:
            Humanized text or None if failed
        """
        
        if not config.is_groq_enabled:
            logger.warning("Groq API key not configured")
            return None
        
        system_prompt = (
            f"You are a text humanizer. Rewrite the given text to sound {tone} and human-like. "
            f"Keep all technical terms and scientific language. "
            f"Use varied sentence structures. "
            f"Return ONLY the rewritten text, no explanations."
        )
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"📡 Calling Groq API (attempt {attempt + 1})...")
                
                response = requests.post(
                    config.GROQ_API_URL,
                    headers={
                        "Authorization": f"Bearer {config.GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": config.GROQ_MODEL,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": text}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 1024,
                        "top_p": 0.9,
                    },
                    timeout=config.API_TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "choices" in data and len(data["choices"]) > 0:
                        result = data["choices"][0]["message"]["content"].strip()
                        if result:
                            logger.info(f"✅ Groq: {len(result)} chars")
                            self._update_api_status("groq", True)
                            return result
                
                # Handle rate limiting
                if response.status_code == 429:
                    logger.warning(f"Rate limited by Groq (attempt {attempt + 1})")
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                
                logger.warning(f"Groq API error: {response.status_code}")
                self._update_api_status("groq", False)
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.Timeout:
                logger.error(f"Groq API timeout (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                logger.error(f"Groq API exception: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        return None
    
    # ============================================================
    # OPENAI API (Optional)
    # ============================================================
    
    def openai(self, text: str, tone: str) -> Optional[str]:
        """
        Humanize using OpenAI API (Optional)
        
        Args:
            text: Text to humanize
            tone: Tone to apply
            
        Returns:
            Humanized text or None if failed
        """
        
        if not config.is_openai_enabled:
            logger.warning("OpenAI API key not configured")
            return None
        
        system_prompt = (
            f"Rewrite this text to sound {tone} and natural. "
            f"Keep technical terms. Return only the rewritten text:"
        )
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"📡 Calling OpenAI API (attempt {attempt + 1})...")
                
                response = requests.post(
                    config.OPENAI_API_URL,
                    headers={
                        "Authorization": f"Bearer {config.OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": config.OPENAI_MODEL,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": text}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 1024,
                    },
                    timeout=config.API_TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "choices" in data and len(data["choices"]) > 0:
                        result = data["choices"][0]["message"]["content"].strip()
                        if result:
                            logger.info(f"✅ OpenAI: {len(result)} chars")
                            self._update_api_status("openai", True)
                            return result
                
                logger.warning(f"OpenAI API error: {response.status_code}")
                self._update_api_status("openai", False)
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.Timeout:
                logger.error(f"OpenAI API timeout (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                logger.error(f"OpenAI API exception: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        return None
    
    # ============================================================
    # UTILITY METHODS
    # ============================================================
    
    def _update_api_status(self, api_name: str, success: bool):
        """Update API status tracking"""
        if api_name in self.api_status:
            self.api_status[api_name]["last_used"] = datetime.now()
            self.api_status[api_name]["available"] = success
            if success:
                self.api_status[api_name]["success_count"] += 1
            else:
                self.api_status[api_name]["fail_count"] += 1
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get status of all APIs"""
        status = {}
        for api, data in self.api_status.items():
            status[api] = {
                "available": data["available"],
                "success_count": data["success_count"],
                "fail_count": data["fail_count"],
                "last_used": data["last_used"].isoformat() if data["last_used"] else None,
                "success_rate": round(
                    data["success_count"] / (data["success_count"] + data["fail_count"]) * 100
                    if (data["success_count"] + data["fail_count"]) > 0 else 0,
                    2
                )
            }
        return status
    
    def get_best_method(self) -> str:
        """Get the best available API method"""
        # Priority order: RewriteAI > Gemini > Groq > OpenAI
        if config.is_rewriteai_enabled and self.api_status["rewriteai"]["available"]:
            return "rewriteai"
        elif config.is_gemini_enabled and self.api_status["gemini"]["available"]:
            return "gemini"
        elif config.is_groq_enabled and self.api_status["groq"]["available"]:
            return "groq"
        elif config.is_openai_enabled and self.api_status["openai"]["available"]:
            return "openai"
        else:
            return "local"  # Fallback to local
    
    def reset_api_status(self):
        """Reset all API status tracking"""
        for api in self.api_status:
            self.api_status[api] = {
                "available": False,
                "last_used": None,
                "success_count": 0,
                "fail_count": 0,
            }
        logger.info("🔄 API status reset")


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_api_humanizer = None

def get_api_humanizer() -> APIHumanizer:
    """
    Get singleton instance of APIHumanizer
    
    Returns:
        APIHumanizer instance
    """
    global _api_humanizer
    if _api_humanizer is None:
        _api_humanizer = APIHumanizer()
    return _api_humanizer


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "APIHumanizer",
    "get_api_humanizer",
]