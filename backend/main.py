from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import re
import random
import requests
import logging
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# ========== LOGGING SETUP ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== FASTAPI APP ==========
app = FastAPI(
    title="AI Humanizer API",
    description="Humanize AI-generated text with advanced NLP",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ========== CORS SETUP ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== MODELS ==========
class HumanizeRequest(BaseModel):
    text: str
    tone: Optional[str] = "academic"
    style: Optional[str] = "balanced"  # conservative, balanced, creative
    preserve_technical: Optional[bool] = True

class HumanizeResponse(BaseModel):
    original_text: str
    humanized_text: str
    tone: str
    word_count: int
    processing_time: float
    method_used: str  # "api" or "local"

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    methods_available: List[str]

# ========== CONFIGURATION ==========
REWRITE_API_KEY = os.getenv("REWRITE_API_KEY", "")
MAX_TEXT_LENGTH = 5000
DEFAULT_TONE = "academic"

logger.info(f"RewriteAI API Key present: {bool(REWRITE_API_KEY)}")

# ========== VOCABULARY DATABASE ==========

# Robotic phrases to replace
ROBOTIC_PHRASES = [
    ("was carried out", "was performed"),
    ("was carried out", "was conducted"),
    ("was placed", "was positioned"),
    ("was placed", "was mounted"),
    ("were recorded", "were documented"),
    ("were recorded", "were noted"),
    ("was identified by", "was recognized by"),
    ("was identified by", "was characterized by"),
    ("was utilized", "was used"),
    ("was utilized", "was employed"),
    ("in order to", "to"),
    ("prior to", "before"),
    ("subsequently", "then"),
    ("subsequently", "afterward"),
    ("thereafter", "after that"),
    ("exhibited", "showed"),
    ("exhibited", "displayed"),
    ("a significant amount of", "substantial"),
    ("a large number of", "many"),
    ("it is important to note that", ""),
    ("it should be mentioned that", ""),
]

# Rich synonym database
SYNONYMS = {
    "use": ["utilize", "employ", "apply", "leverage", "deploy"],
    "show": ["demonstrate", "reveal", "indicate", "suggest", "illustrate"],
    "get": ["obtain", "acquire", "secure", "gain", "attain"],
    "make": ["create", "produce", "generate", "construct", "establish"],
    "change": ["modify", "alter", "adjust", "transform", "adapt"],
    "identify": ["detect", "recognize", "distinguish", "characterize", "discern"],
    "observe": ["notice", "examine", "inspect", "study", "scrutinize"],
    "record": ["document", "note", "log", "capture", "chronicle"],
    "analyze": ["examine", "study", "investigate", "assess", "evaluate"],
    "place": ["position", "mount", "deposit", "set", "arrange"],
    "add": ["introduce", "supplement", "apply", "administer", "incorporate"],
    "avoid": ["prevent", "eliminate", "circumvent", "bypass", "avert"],
    "prepare": ["ready", "organize", "arrange", "set up", "establish"],
    "confirm": ["verify", "validate", "corroborate", "substantiate", "affirm"],
    "demonstrate": ["show", "prove", "exhibit", "display", "manifest"],
    "indicate": ["suggest", "point to", "imply", "signify", "denote"],
    "reveal": ["disclose", "uncover", "expose", "divulge", "unveil"],
    "discover": ["find", "unearth", "uncover", "detect", "identify"],
    "examine": ["inspect", "study", "scrutinize", "analyze", "review"],
    "investigate": ["probe", "explore", "examine", "scrutinize", "research"],
    "study": ["examine", "analyze", "investigate", "review", "scrutinize"],
    "review": ["examine", "study", "analyze", "assess", "evaluate"],
    "assess": ["evaluate", "appraise", "estimate", "judge", "measure"],
    "evaluate": ["assess", "appraise", "estimate", "judge", "determine"],
    "measure": ["calculate", "determine", "evaluate", "quantify", "assess"],
    "calculate": ["compute", "determine", "estimate", "quantify", "figure"],
    "determine": ["establish", "ascertain", "identify", "define", "pinpoint"],
    "establish": ["create", "found", "set up", "institute", "form"],
    "develop": ["create", "formulate", "devise", "design", "generate"],
    "create": ["develop", "produce", "generate", "formulate", "devise"],
    "design": ["plan", "devise", "create", "formulate", "conceive"],
    "implement": ["apply", "employ", "execute", "carry out", "realize"],
    "apply": ["use", "employ", "utilize", "implement", "administer"],
    "employ": ["use", "utilize", "apply", "engage", "deploy"],
    "leverage": ["use", "employ", "utilize", "capitalize on", "exploit"],
    "generate": ["produce", "create", "develop", "make", "yield"],
    "produce": ["generate", "create", "develop", "make", "yield"],
    "construct": ["build", "create", "develop", "form", "establish"],
    "form": ["create", "develop", "establish", "generate", "produce"],
}

# Advanced transitions
TRANSITIONS = {
    "addition": ["Moreover, ", "Additionally, ", "Furthermore, ", "In addition, ", "Not only that, "],
    "contrast": ["However, ", "In contrast, ", "On the other hand, ", "Conversely, ", "Nevertheless, "],
    "example": ["For instance, ", "For example, ", "Specifically, ", "In particular, ", "Notably, "],
    "result": ["Consequently, ", "As a result, ", "Therefore, ", "Thus, ", "Hence, "],
    "emphasis": ["Indeed, ", "In fact, ", "Actually, ", "Importantly, ", "Significantly, "],
    "conclusion": ["In summary, ", "Overall, ", "In conclusion, ", "To summarize, ", "Ultimately, "],
    "similarity": ["Similarly, ", "Likewise, ", "In the same way, ", "Correspondingly, "],
}

# Tone-specific adjustments
TONE_SETTINGS = {
    "academic": {
        "contractions": False,
        "formality": "high",
        "intro_words": ["Indeed, ", "Notably, ", "Significantly, ", "Importantly, "],
        "vocabulary": "formal"
    },
    "natural": {
        "contractions": True,
        "formality": "medium",
        "intro_words": ["So, ", "Well, ", "You see, ", "Now, "],
        "vocabulary": "balanced"
    },
    "blog": {
        "contractions": True,
        "formality": "low",
        "intro_words": ["Look, ", "Honestly, ", "Real talk, ", "Here's the thing, "],
        "vocabulary": "casual",
        "add_emoji": True
    },
    "professional": {
        "contractions": False,
        "formality": "high",
        "intro_words": ["Certainly, ", "Undoubtedly, ", "Clearly, ", "Evidently, "],
        "vocabulary": "formal"
    },
    "conversational": {
        "contractions": True,
        "formality": "very_low",
        "intro_words": ["So basically, ", "Alright, so ", "Okay, ", "You know, "],
        "vocabulary": "casual",
        "slang": True
    }
}

# Domain-specific terms (academic/biotech)
DOMAIN_TERMS = {
    "biotech": [
        "mycelium", "hyphae", "conidiophore", "phialide", "septate",
        "globose", "penicillus", "spore", "morphology", "consortium",
        "degradation", "polymer", "fungal", "isolates", "macroscopic"
    ],
    "academic": [
        "identification", "characterization", "analysis", "evaluation",
        "assessment", "investigation", "demonstration", "validation"
    ]
}

# ========== CORE HUMANIZATION ENGINE ==========

def humanize_locally(text: str, tone: str = "academic", style: str = "balanced", preserve_technical: bool = True) -> str:
    """Advanced local humanization without API calls"""
    
    logger.info(f"Humanizing text: {len(text)} chars, tone: {tone}, style: {style}")
    
    original_text = text
    
    # ===== STEP 1: Pre-processing =====
    # Remove extra spaces
    text = " ".join(text.split())
    
    # ===== STEP 2: Replace robotic phrases =====
    for old, new in ROBOTIC_PHRASES:
        if old in text.lower():
            # Randomly choose replacement if multiple options exist
            replacements = [p[1] for p in ROBOTIC_PHRASES if p[0] == old]
            if replacements:
                new = random.choice(replacements)
            text = text.replace(old, new)
    
    # ===== STEP 3: Intelligent synonym replacement =====
    words = text.split()
    modified_words = []
    
    for i, word in enumerate(words):
        # Clean word for lookup
        clean = re.sub(r'[^\w\s]', '', word).lower()
        
        # Check if word should be preserved (technical term)
        should_preserve = False
        if preserve_technical:
            for domain, terms in DOMAIN_TERMS.items():
                if clean in terms:
                    should_preserve = True
                    break
        
        # Replace with synonym if appropriate
        if clean in SYNONYMS and len(clean) > 3 and not should_preserve:
            # Vary replacement rate based on style
            if style == "conservative":
                replacement_rate = 0.3
            elif style == "creative":
                replacement_rate = 0.7
            else:  # balanced
                replacement_rate = 0.5
            
            if random.random() < replacement_rate:
                new_word = random.choice(SYNONYMS[clean])
                # Preserve capitalization and punctuation
                if word[0].isupper():
                    new_word = new_word.capitalize()
                if word[-1] in '.!?,;:':
                    new_word += word[-1]
                modified_words.append(new_word)
                continue
        
        modified_words.append(word)
    
    text = " ".join(modified_words)
    
    # ===== STEP 4: Sentence restructuring =====
    sentences = text.split(". ")
    
    # Merge short sentences
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
    
    # Add transitions
    if len(sentences) > 2:
        # Add transition at random position
        idx = random.randint(1, len(sentences) - 1)
        category = random.choice(list(TRANSITIONS.keys()))
        transition = random.choice(TRANSITIONS[category])
        sentences[idx] = transition + sentences[idx][0].lower() + sentences[idx][1:]
    
    text = ". ".join(sentences)
    
    # ===== STEP 5: Voice variation (active/passive) =====
    # Simple pattern-based voice change
    if "by" in text and random.random() < 0.2:
        # Passive → Active (simplified)
        parts = text.split(" by ")
        if len(parts) == 2:
            text = f"{parts[1]} {parts[0]}".strip()
    
    # ===== STEP 6: Tone application =====
    tone_settings = TONE_SETTINGS.get(tone, TONE_SETTINGS["natural"])
    
    # Add intro words
    if random.random() < 0.3 and tone_settings["intro_words"]:
        intro = random.choice(tone_settings["intro_words"])
        text = intro + text[0].lower() + text[1:]
    
    # Apply contractions
    if tone_settings.get("contractions", False):
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
        }
        for old, new in contraction_map.items():
            if random.random() < 0.5:  # 50% chance per contraction
                text = text.replace(old, new)
    
    # Add emojis for blog style
    if tone_settings.get("add_emoji", False) and random.random() < 0.3:
        emojis = ["🔬", "🧪", "💡", "🤔", "✨", "📝", "🎯", "🚀"]
        text = random.choice(emojis) + " " + text
    
    # ===== STEP 7: Quality assurance =====
    # Ensure minimum length preservation
    if len(text) < len(original_text) * 0.5:
        logger.warning("Text too short after humanization, using original")
        return original_text
    
    logger.info(f"Humanization complete: {len(text)} chars")
    return text

# ========== API CALLS ==========

def call_rewriteai_api(text: str, tone: str) -> Optional[str]:
    """Call RewriteAI API for humanization"""
    if not REWRITE_API_KEY:
        return None
    
    try:
        url = "https://rewriteai.com/api/v1/humanize"
        headers = {
            "Authorization": f"Bearer {REWRITE_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "tone": tone
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                return data["results"][0]["text"]
        
        logger.warning(f"RewriteAI API returned: {response.status_code}")
        return None
        
    except Exception as e:
        logger.error(f"RewriteAI API error: {e}")
        return None

# ========== API ENDPOINTS ==========

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API info"""
    return {
        "name": "AI Humanizer API",
        "version": "2.0.0",
        "description": "Humanize AI-generated text",
        "endpoints": {
            "/docs": "Swagger documentation",
            "/health": "Health check",
            "/api/humanize": "Main humanization endpoint (POST)"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    methods = []
    if REWRITE_API_KEY:
        methods.append("rewriteai")
    methods.append("local")
    
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        timestamp=datetime.now().isoformat(),
        methods_available=methods
    )

@app.post("/api/humanize", response_model=HumanizeResponse)
async def humanize_text(request: HumanizeRequest):
    """
    Humanize AI-generated text
    
    - **text**: The text to humanize (min 10 chars)
    - **tone**: academic, natural, blog, professional, conversational
    - **style**: conservative, balanced, creative
    - **preserve_technical**: Keep technical terms unchanged
    """
    import time
    start_time = time.time()
    
    # Validate input
    if len(request.text.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Text must be at least 10 characters long"
        )
    
    if len(request.text) > MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Text exceeds maximum length of {MAX_TEXT_LENGTH} characters"
        )
    
    # Validate tone
    valid_tones = ["academic", "natural", "blog", "professional", "conversational"]
    if request.tone not in valid_tones:
        raise HTTPException(
            status_code=400,
            detail=f"Tone must be one of: {', '.join(valid_tones)}"
        )
    
    # Validate style
    valid_styles = ["conservative", "balanced", "creative"]
    if request.style not in valid_styles:
        raise HTTPException(
            status_code=400,
            detail=f"Style must be one of: {', '.join(valid_styles)}"
        )
    
    logger.info(f"Received humanization request: tone={request.tone}, style={request.style}")
    
    # ===== STEP 1: Try RewriteAI API =====
    humanized = None
    method_used = "local"
    
    if REWRITE_API_KEY:
        humanized = call_rewriteai_api(request.text, request.tone)
        if humanized:
            method_used = "api"
            logger.info("Used RewriteAI API")
    
    # ===== STEP 2: Fallback to local =====
    if not humanized:
        humanized = humanize_locally(
            request.text,
            request.tone,
            request.style,
            request.preserve_technical
        )
        logger.info("Used local humanization")
    
    processing_time = time.time() - start_time
    
    return HumanizeResponse(
        original_text=request.text,
        humanized_text=humanized,
        tone=request.tone,
        word_count=len(humanized.split()),
        processing_time=round(processing_time, 3),
        method_used=method_used
    )

# ========== ERROR HANDLERS ==========

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again."}
    )

# ========== MAIN ENTRY POINT ==========

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting AI Humanizer API...")
    logger.info(f"📊 RewriteAI API: {'Enabled' if REWRITE_API_KEY else 'Disabled (fallback to local)'}")
    logger.info(f"📍 Server: http://0.0.0.0:8000")
    logger.info(f"📖 Docs: http://0.0.0.0:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )