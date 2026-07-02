
import re
import random
import requests
import json
import logging
from typing import Optional, Dict, Any, List
from transformers import pipeline

logger = logging.getLogger(__name__)

class IntelligentHumanizer:
    """Context-aware humanizer using LLM + rules"""
    
    def __init__(self):
        self.use_llm = True
        try:
            # Try to use local model (fast)
            self.paraphraser = pipeline(
                "text2text-generation",
                model="tuner007/pegasus_paraphrase",
                max_length=256,
                device=-1
            )
            logger.info("✅ Local paraphraser loaded")
        except:
            self.use_llm = False
            logger.warning("⚠️ Local model failed, using fallback")
        
        # Synonyms for intelligent replacement
        self.synonyms = {
            "carried out": ["performed", "conducted", "executed", "implemented"],
            "placed": ["positioned", "mounted", "deposited", "set"],
            "avoid": ["prevent", "eliminate", "circumvent", "bypass"],
            "recorded": ["documented", "noted", "logged", "captured"],
            "identified": ["recognized", "detected", "distinguished", "characterized"],
            "showed": ["demonstrated", "revealed", "exhibited", "displayed"],
            "exhibited": ["showed", "displayed", "demonstrated", "presented"],
            "prior to": ["before", "preceding", "in advance of"],
            "used": ["utilized", "employed", "applied", "leveraged"],
            "confirm": ["verify", "validate", "corroborate", "substantiate"],
        }
        
        self.transitions = [
            "Moreover, ", "Furthermore, ", "Additionally, ",
            "In contrast, ", "Conversely, ", "On the other hand, ",
            "Consequently, ", "As a result, ", "Therefore, ",
            "Notably, ", "Importantly, ", "Significantly, "
        ]
    
    def humanize(self, text: str, tone: str = "academic") -> str:
        """Humanize text with context awareness"""
        
        # Step 1: LLM paraphrase (if available)
        if self.use_llm:
            try:
                prompt = f"Paraphrase this text in {tone} tone, keeping all technical terms: {text}"
                result = self.paraphraser(prompt, max_length=512, num_return_sequences=1)
                text = result[0]['generated_text']
                logger.info("✅ LLM paraphrase completed")
            except Exception as e:
                logger.warning(f"LLM failed: {e}")
        
        # Step 2: Intelligent synonym replacement
        for old, new_list in self.synonyms.items():
            if old in text.lower():
                new = random.choice(new_list)
                text = text.replace(old, new)
        
        # Step 3: Add transitions
        sentences = text.split(". ")
        if len(sentences) > 2:
            idx = random.randint(1, len(sentences) - 1)
            transition = random.choice(self.transitions)
            sentences[idx] = transition + sentences[idx][0].lower() + sentences[idx][1:]
            text = ". ".join(sentences)
        
        # Step 4: Tone adjustments
        if tone == "academic":
            text = text.replace("don't", "do not")
            text = text.replace("can't", "cannot")
        
        return text
    
    def humanize_batch(self, texts: List[str], tone: str = "academic") -> List[str]:
        return [self.humanize(t, tone) for t in texts]

# Singleton
_intelligent_humanizer = None
def get_intelligent_humanizer():
    global _intelligent_humanizer
    if _intelligent_humanizer is None:
        _intelligent_humanizer = IntelligentHumanizer()
    return _intelligent_humanizer
