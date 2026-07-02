
import random
import re
import numpy as np
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Global embeddings (loaded once)
_embeddings = {}

def load_glove_embeddings():
    """Load GloVe embeddings"""
    global _embeddings
    if _embeddings:
        return _embeddings
    
    glove_path = "backend/word_data/glove/glove.6B.100d.txt"
    try:
        with open(glove_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 50000:
                    break
                parts = line.split()
                if len(parts) >= 101:
                    word = parts[0]
                    vec = np.array([float(x) for x in parts[1:]])
                    _embeddings[word] = vec
        logger.info(f"✅ Loaded {len(_embeddings)} GloVe embeddings")
    except Exception as e:
        logger.error(f"❌ Failed to load GloVe: {e}")
    return _embeddings

def find_synonyms(word, top_n=8):
    """Find semantic synonyms using GloVe"""
    embeddings = load_glove_embeddings()
    if word not in embeddings:
        return []
    
    word_vec = embeddings[word]
    similarities = []
    
    for w, vec in embeddings.items():
        if w == word or len(w) < 3:
            continue
        sim = np.dot(word_vec, vec) / (np.linalg.norm(word_vec) * np.linalg.norm(vec))
        similarities.append((w, sim))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    return [w for w, _ in similarities[:top_n]]

class GloveHumanizer:
    """Stealth Writer style humanizer using GloVe embeddings (400k words)"""
    
    def __init__(self):
        load_glove_embeddings()
        self.transitions = [
            "Indeed, ", "Notably, ", "Importantly, ",
            "In particular, ", "Specifically, ",
            "Furthermore, ", "Moreover, ",
            "In contrast, ", "Conversely, ",
            "Consequently, ", "As a result, ",
            "Interestingly, ", "Remarkably, "
        ]
        logger.info("✅ GloveHumanizer initialized")
    
    def humanize(self, text: str, tone: str = "academic") -> str:
        """Humanize text using GloVe embeddings"""
        
        # Step 1: Replace words with GloVe synonyms
        words = text.split()
        replaced = []
        for word in words:
            clean = re.sub(r'[^\w\s]', '', word).lower()
            if len(clean) > 3 and clean in load_glove_embeddings():
                syns = find_synonyms(clean, 5)
                if syns and random.random() < 0.4:
                    new_word = random.choice(syns)
                    # Preserve capitalization
                    if word[0].isupper():
                        new_word = new_word.capitalize()
                    if word[-1] in '.!?,;:':
                        new_word += word[-1]
                    replaced.append(new_word)
                    continue
            replaced.append(word)
        
        text = " ".join(replaced)
        
        # Step 2: Sentence restructuring
        sentences = text.split(". ")
        restructured = []
        for sent in sentences:
            if " by " in sent and random.random() < 0.2:
                parts = sent.split(" by ")
                if len(parts) == 2:
                    sent = f"{parts[1].strip()} {parts[0].strip()}"
            restructured.append(sent)
        
        text = ". ".join(restructured)
        
        # Step 3: Add transitions
        if len(sentences) > 2:
            idx = random.randint(1, len(sentences) - 1)
            transition = random.choice(self.transitions)
            sentences[idx] = transition + sentences[idx][0].lower() + sentences[idx][1:]
            text = ". ".join(sentences)
        
        return text

_glove_humanizer = None

def get_glove_humanizer():
    global _glove_humanizer
    if _glove_humanizer is None:
        _glove_humanizer = GloveHumanizer()
    return _glove_humanizer
