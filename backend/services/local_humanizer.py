"""
Local Humanizer - No API Required
All logic runs locally using vocabulary database
"""

import re
import random
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from backend.vocabulary import (
    ROBOTIC_PHRASES,
    SYNONYMS,
    TRANSITIONS,
    TONE_SETTINGS,
    DOMAIN_TERMS,
)

logger = logging.getLogger(__name__)


class LocalHumanizer:
    """
    Local text humanization without external APIs
    
    Features:
    - No internet connection required
    - Uses built-in vocabulary database
    - Multiple tones and styles
    - Technical term preservation
    - Text analysis capabilities
    """
    
    def __init__(self):
        """Initialize local humanizer with vocabulary"""
        self._load_vocabulary()
        self._load_stopwords()
    
    def _load_vocabulary(self):
        """Load vocabulary from files"""
        logger.info("📚 Loading local vocabulary...")
        
        self.robotic_phrases = ROBOTIC_PHRASES
        self.synonyms = SYNONYMS
        self.transitions = TRANSITIONS
        self.tone_settings = TONE_SETTINGS
        self.domain_terms = DOMAIN_TERMS
        
        logger.info(f"✅ Loaded: {len(self.synonyms)} synonym groups")
        logger.info(f"✅ Loaded: {len(self.transitions)} transition types")
        logger.info(f"✅ Loaded: {len(self.domain_terms)} domain terms")
    
    def _load_stopwords(self):
        """Load common stopwords to skip"""
        self.stopwords = {
            "a", "an", "the", "and", "or", "but", "for", "nor", "on", "at", 
            "to", "by", "with", "without", "of", "in", "from", "up", "down",
            "off", "over", "under", "above", "below", "between", "among",
            "through", "during", "within", "upon", "toward", "until"
        }
    
    # ============================================================
    # MAIN HUMANIZATION METHOD
    # ============================================================
    
    def humanize(
        self,
        text: str,
        tone: str = "academic",
        style: str = "balanced",
        preserve_technical: bool = True
    ) -> str:
        """
        Humanize text using local vocabulary and rules
        
        Args:
            text: Text to humanize
            tone: academic, natural, blog, professional, conversational
            style: conservative, balanced, creative
            preserve_technical: Keep technical terms unchanged
            
        Returns:
            Humanized text
        """
        
        logger.info(f"Local humanization: {len(text)} chars, tone={tone}, style={style}")
        
        original_text = text
        
        # ===== STEP 1: Pre-process =====
        text = " ".join(text.split())
        
        # ===== STEP 2: Replace robotic phrases =====
        text = self._replace_robotic_phrases(text)
        
        # ===== STEP 3: Intelligent synonym replacement =====
        text = self._replace_with_synonyms(text, style, preserve_technical)
        
        # ===== STEP 4: Sentence restructuring =====
        text = self._restructure_sentences(text)
        
        # ===== STEP 5: Voice variation =====
        text = self._vary_voice(text)
        
        # ===== STEP 6: Apply tone =====
        text = self._apply_tone(text, tone)
        
        # ===== STEP 7: Quality check =====
        if len(text) < len(original_text) * 0.4:
            logger.warning("Text too short after humanization, returning original")
            return original_text
        
        logger.info(f"✅ Local humanization complete: {len(text)} chars")
        return text
    
    # ============================================================
    # STEP 2: REPLACE ROBOTIC PHRASES
    # ============================================================
    
    def _replace_robotic_phrases(self, text: str) -> str:
        """Replace robotic phrases with natural alternatives"""
        for old, new in self.robotic_phrases:
            if old in text.lower():
                # If there are multiple replacements, pick random
                if isinstance(new, list):
                    new = random.choice(new)
                text = text.replace(old, new)
        return text
    
    # ============================================================
    # STEP 3: SYNONYM REPLACEMENT
    # ============================================================
    
    def _replace_with_synonyms(
        self,
        text: str,
        style: str,
        preserve_technical: bool
    ) -> str:
        """Replace words with intelligent synonyms"""
        
        words = text.split()
        modified_words = []
        
        # Vary replacement rate based on style
        rates = {"conservative": 0.3, "balanced": 0.5, "creative": 0.7}
        rate = rates.get(style, 0.5)
        
        for i, word in enumerate(words):
            # Clean word for lookup
            clean = re.sub(r'[^\w\s]', '', word).lower()
            
            # Skip short words and stopwords
            if len(clean) < 4 or clean in self.stopwords:
                modified_words.append(word)
                continue
            
            # Check if technical term to preserve
            should_preserve = False
            if preserve_technical:
                for domain, terms in self.domain_terms.items():
                    if clean in terms:
                        should_preserve = True
                        break
            
            if should_preserve:
                modified_words.append(word)
                continue
            
            # Replace with synonym if available
            if clean in self.synonyms and random.random() < rate:
                new_word = random.choice(self.synonyms[clean])
                
                # Preserve formatting
                if word[0].isupper():
                    new_word = new_word.capitalize()
                if word[-1] in '.!?,;:':
                    new_word += word[-1]
                if word.isupper():
                    new_word = new_word.upper()
                
                modified_words.append(new_word)
                continue
            
            modified_words.append(word)
        
        return " ".join(modified_words)
    
    # ============================================================
    # STEP 4: SENTENCE RESTRUCTURING
    # ============================================================
    
    def _restructure_sentences(self, text: str) -> str:
        """Restructure sentences for better flow"""
        
        sentences = text.split(". ")
        
        # ===== Merge short sentences =====
        merged = []
        i = 0
        while i < len(sentences):
            if i < len(sentences) - 1 and len(sentences[i].split()) < 8:
                merged.append(sentences[i] + ". " + sentences[i+1])
                i += 2
            else:
                merged.append(sentences[i])
                i += 1
        sentences = merged
        
        # ===== Add transitions =====
        if len(sentences) > 2:
            # Don't add transition to first sentence
            idx = random.randint(1, len(sentences) - 1)
            category = random.choice(list(self.transitions.keys()))
            transition = random.choice(self.transitions[category])
            sentences[idx] = transition + sentences[idx][0].lower() + sentences[idx][1:]
        
        # ===== Vary sentence length =====
        for i, sent in enumerate(sentences):
            if len(sent.split()) > 25 and random.random() < 0.3:
                # Split long sentence
                parts = sent.split(", ")
                if len(parts) > 1:
                    mid = len(parts) // 2
                    sentences[i] = ". ".join([
                        ", ".join(parts[:mid]),
                        ", ".join(parts[mid:])
                    ])
        
        return ". ".join(sentences)
    
    # ============================================================
    # STEP 5: VOICE VARIATION
    # ============================================================
    
    def _vary_voice(self, text: str) -> str:
        """Vary between active and passive voice"""
        
        # Simple pattern-based voice change
        if " by " in text and random.random() < 0.2:
            parts = text.split(" by ")
            if len(parts) == 2:
                # Passive → Active (simplified)
                before = parts[0].strip()
                after = parts[1].strip()
                if "was" in before:
                    before = before.replace("was ", "")
                text = f"{after} {before}"
        
        return text
    
    # ============================================================
    # STEP 6: APPLY TONE
    # ============================================================
    
    def _apply_tone(self, text: str, tone: str) -> str:
        """Apply tone-specific adjustments"""
        
        # Get tone settings
        tone_settings = self.tone_settings.get(tone, self.tone_settings["natural"])
        
        # ===== Add intro words =====
        if random.random() < 0.3 and tone_settings.get("intro_words"):
            intro = random.choice(tone_settings["intro_words"])
            text = intro + text[0].lower() + text[1:]
        
        # ===== Apply contractions =====
        if tone_settings.get("contractions", False):
            text = self._apply_contractions(text)
        
        # ===== Add emojis for blog =====
        if tone == "blog" and random.random() < 0.3:
            emojis = ["🔬", "🧪", "💡", "🤔", "✨", "📝", "🎯", "🚀", "💎"]
            text = random.choice(emojis) + " " + text
        
        # ===== Add slang for conversational =====
        if tone == "conversational" and random.random() < 0.2:
            slang = {
                "because": "cuz",
                "going to": "gonna",
                "want to": "wanna",
                "got to": "gotta",
                "kind of": "kinda",
                "sort of": "sorta",
                "a lot of": "lots of",
            }
            for old, new in slang.items():
                if random.random() < 0.3:
                    text = text.replace(old, new)
        
        # ===== Add emphasis for professional =====
        if tone == "professional" and random.random() < 0.2:
            emphasis = ["clearly ", "undoubtedly ", "certainly ", "definitely "]
            sentences = text.split(". ")
            if len(sentences) > 1:
                idx = random.randint(1, len(sentences) - 1)
                sentences[idx] = random.choice(emphasis) + sentences[idx]
                text = ". ".join(sentences)
        
        return text
    
    # ============================================================
    # CONTRACTIONS
    # ============================================================
    
    def _apply_contractions(self, text: str) -> str:
        """Apply contractions to make text more natural"""
        
        contraction_map = {
            " are not ": " aren't ",
            " is not ": " isn't ",
            " cannot ": " can't ",
            " will not ": " won't ",
            " I am ": " I'm ",
            " you are ": " you're ",
            " it is ": " it's ",
            " do not ": " don't ",
            " does not ": " doesn't ",
            " did not ": " didn't ",
            " would not ": " wouldn't ",
            " should not ": " shouldn't ",
            " could not ": " couldn't ",
            " have not ": " haven't ",
            " has not ": " hasn't ",
            " had not ": " hadn't ",
            " will not ": " won't ",
            " shall not ": " shan't ",
            " must not ": " mustn't ",
        }
        
        for old, new in contraction_map.items():
            if random.random() < 0.4:
                text = text.replace(old, new)
        
        return text
    
    # ============================================================
    # TEXT ANALYSIS
    # ============================================================
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for various metrics
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with analysis results
        """
        
        # Basic metrics
        sentences = [s for s in text.split(". ") if s.strip()]
        words = [w for w in text.split() if w.strip()]
        
        if not words:
            return self._empty_analysis()
        
        sentence_count = len(sentences)
        word_count = len(words)
        char_count = len(text.replace(" ", ""))
        
        # Average word length
        avg_word_length = sum(len(w) for w in words) / word_count if word_count > 0 else 0
        
        # Readability (Flesch Reading Ease)
        readability = self._calculate_readability(text, words, sentences)
        
        # Difficulty level
        if readability > 60:
            difficulty = "Easy"
        elif readability > 40:
            difficulty = "Medium"
        else:
            difficulty = "Hard"
        
        # Vocabulary richness
        unique_words = len(set(w.lower() for w in words))
        vocabulary_richness = unique_words / word_count if word_count > 0 else 0
        
        # Find technical terms
        technical_terms = self._find_technical_terms(words)
        
        # Sentiment (basic)
        sentiment = self._basic_sentiment(words)
        
        # Sentence length variation (burstiness)
        burstiness = self._calculate_burstiness(sentences)
        
        return {
            "sentence_count": sentence_count,
            "word_count": word_count,
            "char_count": char_count,
            "avg_word_length": round(avg_word_length, 2),
            "readability_score": round(readability, 2),
            "difficulty_level": difficulty,
            "vocabulary_richness": round(vocabulary_richness, 3),
            "technical_terms": technical_terms[:20],
            "sentiment": sentiment,
            "burstiness": round(burstiness, 3),
        }
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis for empty text"""
        return {
            "sentence_count": 0,
            "word_count": 0,
            "char_count": 0,
            "avg_word_length": 0.0,
            "readability_score": 0.0,
            "difficulty_level": "Easy",
            "vocabulary_richness": 0.0,
            "technical_terms": [],
            "sentiment": {"polarity": 0.0, "subjectivity": 0.0},
            "burstiness": 0.0,
        }
    
    def _calculate_readability(self, text: str, words: List[str], sentences: List[str]) -> float:
        """Calculate Flesch Reading Ease score"""
        if not sentences or not words:
            return 0
        
        avg_words_per_sentence = len(words) / len(sentences)
        long_words = len([w for w in words if len(w) > 6])
        long_word_ratio = long_words / len(words) if len(words) > 0 else 0
        
        # Flesch Reading Ease formula
        score = 206.835 - 1.015 * avg_words_per_sentence - 84.6 * long_word_ratio
        return max(0, min(100, score))
    
    def _calculate_burstiness(self, sentences: List[str]) -> float:
        """Calculate sentence length variation (burstiness)"""
        if len(sentences) < 2:
            return 0.5
        
        lengths = [len(s.split()) for s in sentences]
        mean = sum(lengths) / len(lengths)
        
        if mean == 0:
            return 0.5
        
        variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
        std_dev = variance ** 0.5
        
        # Normalize to 0-1 range
        return min(1.0, std_dev / mean)
    
    def _find_technical_terms(self, words: List[str]) -> List[str]:
        """Find technical terms in text"""
        technical_terms = []
        seen = set()
        
        for word in words:
            clean = re.sub(r'[^\w\s]', '', word).lower()
            for domain, terms in self.domain_terms.items():
                if clean in terms and clean not in seen:
                    technical_terms.append(clean)
                    seen.add(clean)
                    break
        
        return technical_terms
    
    def _basic_sentiment(self, words: List[str]) -> Dict[str, float]:
        """Basic sentiment analysis using word lists"""
        
        positive_words = {
            "good", "great", "excellent", "amazing", "wonderful",
            "beautiful", "happy", "love", "nice", "perfect",
            "fantastic", "awesome", "brilliant", "outstanding",
            "superb", "terrific", "magnificent", "exceptional"
        }
        
        negative_words = {
            "bad", "terrible", "awful", "horrible", "poor",
            "sad", "angry", "ugly", "hate", "disappointing",
            "worst", "disgusting", "dreadful", "unpleasant",
            "awful", "atrocious", "deplorable", "wretched"
        }
        
        positive_count = sum(1 for w in words if w.lower() in positive_words)
        negative_count = sum(1 for w in words if w.lower() in negative_words)
        
        total = len(words)
        if total == 0:
            return {"polarity": 0.0, "subjectivity": 0.0}
        
        polarity = (positive_count - negative_count) / total
        subjectivity = (positive_count + negative_count) / total
        
        return {
            "polarity": round(polarity, 3),
            "subjectivity": round(subjectivity, 3)
        }


# ============================================================
# EXPORTS
# ============================================================

__all__ = ["LocalHumanizer"]