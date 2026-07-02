from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
import re
import random
import json
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

# ========== CONFIG ==========
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== MODELS ==========
class HumanizeRequest(BaseModel):
    text: str
    tone: Optional[str] = "academic"

class HumanizeResponse(BaseModel):
    original_text: str
    humanized_text: str
    tone: str
    word_count: int

# ========== VOCABULARY ==========
ROBOTIC_PHRASES = [
    ("was carried out", "was done"),
    ("was placed", "was put"),
    ("were recorded", "were noted"),
    ("was identified by", "showed"),
    ("was utilized", "was used"),
    ("in order to", "to"),
    ("prior to", "before"),
    ("subsequently", "then"),
    ("thereafter", "after that"),
    ("exhibited", "showed"),
]

SYNONYMS = {
    "use": ["utilize", "employ", "apply", "leverage"],
    "show": ["demonstrate", "reveal", "indicate", "suggest"],
    "get": ["obtain", "acquire", "secure", "gain"],
    "make": ["create", "produce", "generate", "construct"],
    "change": ["modify", "alter", "adjust", "transform"],
    "identify": ["detect", "recognize", "distinguish", "characterize"],
    "observe": ["notice", "examine", "inspect", "study"],
    "record": ["document", "note", "log", "capture"],
    "analyze": ["examine", "study", "investigate", "assess"],
    "place": ["position", "mount", "deposit", "set"],
    "add": ["introduce", "supplement", "apply", "administer"],
    "avoid": ["prevent", "eliminate", "circumvent", "bypass"],
    "prepare": ["ready", "set up", "organize", "arrange"],
    "confirm": ["verify", "validate", "corroborate", "substantiate"],
}

TRANSITIONS = {
    "addition": ["Moreover, ", "Additionally, ", "Furthermore, "],
    "contrast": ["However, ", "In contrast, ", "On the other hand, "],
    "example": ["For instance, ", "For example, ", "Specifically, "],
    "result": ["Consequently, ", "As a result, ", "Therefore, "],
    "emphasis": ["Indeed, ", "In fact, ", "Notably, "],
}

# ========== LOCAL HUMANIZER ==========
def humanize_locally(text: str, tone: str = "academic") -> str:
    """Humanize text without any API"""
    
    # 1. Replace robotic phrases
    for old, new in ROBOTIC_PHRASES:
        text = text.replace(old, new)
    
    # 2. Replace words with synonyms (50% chance)
    words = text.split()
    for i, word in enumerate(words):
        clean = re.sub(r'[^\w\s]', '', word).lower()
        if clean in SYNONYMS and len(clean) > 3:
            if random.random() < 0.5:
                new_word = random.choice(SYNONYMS[clean])
                if word[0].isupper():
                    new_word = new_word.capitalize()
                words[i] = new_word
    
    text = " ".join(words)
    
    # 3. Add transition words
    sentences = text.split(". ")
    if len(sentences) > 2:
        idx = len(sentences) // 2
        category = random.choice(list(TRANSITIONS.keys()))
        transition = random.choice(TRANSITIONS[category])
        sentences[idx] = transition + sentences[idx][0].lower() + sentences[idx][1:]
    
    result = ". ".join(sentences)
    
    # 4. Tone adjustments
    if tone == "conversational":
        result = "So basically, " + result[0].lower() + result[1:]
        result = re.sub(r' are not ', " aren't ", result)
        result = re.sub(r' is not ', " isn't ", result)
        result = re.sub(r' cannot ', " can't ", result)
    
    elif tone == "blog":
        if random.random() < 0.3:
            result = "🔬 " + result + " 🧪"
    
    return result

# ========== API ROUTES ==========
@app.get("/")
def root():
    return {"message": "AI Humanizer API is running!"}

@app.post("/api/humanize", response_model=HumanizeResponse)
async def humanize(request: HumanizeRequest):
    try:
        # Try RewriteAI first (if key exists)
        REWRITE_KEY = os.getenv("REWRITE_API_KEY", "")
        
        if REWRITE_KEY:
            try:
                response = requests.post(
                    "https://rewriteai.com/api/v1/humanize",
                    headers={
                        "Authorization": f"Bearer {REWRITE_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={"text": request.text, "tone": request.tone},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    humanized = data["results"][0]["text"]
                    return HumanizeResponse(
                        original_text=request.text,
                        humanized_text=humanized,
                        tone=request.tone,
                        word_count=len(humanized.split())
                    )
            except:
                pass  # Fallback to local
        
        # Fallback: Local humanizer
        humanized = humanize_locally(request.text, request.tone)
        
        return HumanizeResponse(
            original_text=request.text,
            humanized_text=humanized,
            tone=request.tone,
            word_count=len(humanized.split())
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== RUN ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)