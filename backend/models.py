"""
Data Models for AI Humanizer API
All request/response models with validation
"""

from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# ========== ENUMS ==========

class ToneEnum(str, Enum):
    """Available tones for humanization"""
    ACADEMIC = "academic"
    NATURAL = "natural"
    BLOG = "blog"
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"

class StyleEnum(str, Enum):
    """Available styles for humanization"""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    CREATIVE = "creative"

class MethodEnum(str, Enum):
    """Available humanization methods"""
    REWRITEAI = "rewriteai_api"
    GEMINI = "gemini_api"
    GROQ = "groq_api"
    LOCAL = "local"

# ========== REQUEST MODELS ==========

class HumanizeRequest(BaseModel):
    """
    Request model for text humanization
    
    Example:
    ```json
    {
        "text": "Microscopic identification was carried out...",
        "tone": "academic",
        "style": "balanced",
        "preserve_technical": true
    }
    ```
    """
    
    text: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Text to humanize (min 10 chars, max 5000 chars)"
    )
    
    tone: ToneEnum = Field(
        ToneEnum.ACADEMIC,
        description="Tone of the humanized text"
    )
    
    style: StyleEnum = Field(
        StyleEnum.BALANCED,
        description="Style intensity (conservative, balanced, creative)"
    )
    
    preserve_technical: bool = Field(
        True,
        description="Whether to preserve technical/scientific terms"
    )
    
    # Custom validators
    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate and clean text"""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        
        # Remove extra whitespace
        cleaned = ' '.join(v.split())
        
        if len(cleaned) < 10:
            raise ValueError("Text must be at least 10 characters long")
        
        return cleaned
    
    @field_validator('tone')
    @classmethod
    def validate_tone(cls, v: ToneEnum) -> ToneEnum:
        """Validate tone is valid"""
        valid_tones = [t.value for t in ToneEnum]
        if v.value not in valid_tones:
            raise ValueError(f"Tone must be one of: {', '.join(valid_tones)}")
        return v
    
    @field_validator('style')
    @classmethod
    def validate_style(cls, v: StyleEnum) -> StyleEnum:
        """Validate style is valid"""
        valid_styles = [s.value for s in StyleEnum]
        if v.value not in valid_styles:
            raise ValueError(f"Style must be one of: {', '.join(valid_styles)}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Microscopic identification was carried out to confirm morphological characteristics of purified fungal isolates.",
                "tone": "academic",
                "style": "balanced",
                "preserve_technical": True
            }
        }


class BatchHumanizeRequest(BaseModel):
    """
    Request model for batch text humanization
    
    Example:
    ```json
    {
        "texts": ["Text 1", "Text 2", "Text 3"],
        "tone": "academic",
        "style": "balanced",
        "preserve_technical": true
    }
    ```
    """
    
    texts: List[str] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of texts to humanize (1-50 items)"
    )
    
    tone: ToneEnum = Field(
        ToneEnum.ACADEMIC,
        description="Tone for all texts"
    )
    
    style: StyleEnum = Field(
        StyleEnum.BALANCED,
        description="Style for all texts"
    )
    
    preserve_technical: bool = Field(
        True,
        description="Preserve technical terms"
    )
    
    @field_validator('texts')
    @classmethod
    def validate_texts(cls, v: List[str]) -> List[str]:
        """Validate all texts"""
        if not v:
            raise ValueError("At least one text is required")
        
        if len(v) > 50:
            raise ValueError("Maximum 50 texts allowed")
        
        for i, text in enumerate(v):
            if not text or not text.strip():
                raise ValueError(f"Text at index {i} is empty")
            
            cleaned = ' '.join(text.split())
            if len(cleaned) < 10:
                raise ValueError(f"Text at index {i} is too short (min 10 chars)")
            
            if len(cleaned) > 5000:
                raise ValueError(f"Text at index {i} is too long (max 5000 chars)")
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "texts": [
                    "Microscopic identification was carried out...",
                    "A small portion was placed on a glass slide..."
                ],
                "tone": "academic",
                "style": "balanced",
                "preserve_technical": True
            }
        }


class AnalyzeRequest(BaseModel):
    """
    Request model for text analysis
    
    Example:
    ```json
    {
        "text": "Microscopic identification was carried out..."
    }
    ```
    """
    
    text: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Text to analyze"
    )
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        return ' '.join(v.split())
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Microscopic identification was carried out to confirm morphological characteristics."
            }
        }


class CompareRequest(BaseModel):
    """
    Request model for comparing multiple humanization results
    
    Example:
    ```json
    {
        "text": "Microscopic identification was carried out...",
        "tones": ["academic", "natural", "conversational"]
    }
    ```
    """
    
    text: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Text to humanize"
    )
    
    tones: List[ToneEnum] = Field(
        [ToneEnum.ACADEMIC, ToneEnum.NATURAL, ToneEnum.CONVERSATIONAL],
        description="List of tones to compare"
    )
    
    style: StyleEnum = Field(
        StyleEnum.BALANCED,
        description="Style for all variations"
    )
    
    preserve_technical: bool = Field(
        True,
        description="Preserve technical terms"
    )
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        return ' '.join(v.split())
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Microscopic identification was carried out...",
                "tones": ["academic", "natural", "conversational"],
                "style": "balanced",
                "preserve_technical": True
            }
        }


# ========== RESPONSE MODELS ==========

class HumanizeResponse(BaseModel):
    """
    Response model for text humanization
    
    Example:
    ```json
    {
        "original_text": "Microscopic identification was carried out...",
        "humanized_text": "Microscopic identification was performed...",
        "tone": "academic",
        "style": "balanced",
        "word_count": 45,
        "processing_time": 0.234,
        "method_used": "local",
        "timestamp": "2026-07-02T09:08:15.123456"
    }
    ```
    """
    
    original_text: str = Field(
        ...,
        description="Original input text"
    )
    
    humanized_text: str = Field(
        ...,
        description="Humanized output text"
    )
    
    tone: str = Field(
        ...,
        description="Tone used for humanization"
    )
    
    style: str = Field(
        ...,
        description="Style used for humanization"
    )
    
    word_count: int = Field(
        ...,
        description="Number of words in humanized text",
        ge=1
    )
    
    processing_time: float = Field(
        ...,
        description="Processing time in seconds",
        ge=0
    )
    
    method_used: str = Field(
        ...,
        description="Method used (api/local)"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of response"
    )
    
    # Optional fields
    changes_made: Optional[int] = Field(
        None,
        description="Number of changes made"
    )
    
    original_word_count: Optional[int] = Field(
        None,
        description="Original word count"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "original_text": "Microscopic identification was carried out to confirm morphological characteristics.",
                "humanized_text": "Microscopic identification was performed to confirm morphological characteristics.",
                "tone": "academic",
                "style": "balanced",
                "word_count": 8,
                "processing_time": 0.234,
                "method_used": "local",
                "timestamp": "2026-07-02T09:08:15.123456",
                "changes_made": 3,
                "original_word_count": 10
            }
        }


class BatchHumanizeResponse(BaseModel):
    """
    Response model for batch text humanization
    
    Example:
    ```json
    {
        "results": [...],
        "total_processed": 3,
        "total_time": 0.456,
        "timestamp": "2026-07-02T09:08:15.123456"
    }
    ```
    """
    
    results: List[HumanizeResponse] = Field(
        ...,
        description="List of humanized results"
    )
    
    total_processed: int = Field(
        ...,
        description="Total number of texts processed",
        ge=0
    )
    
    total_time: float = Field(
        ...,
        description="Total processing time in seconds",
        ge=0
    )
    
    failed_count: int = Field(
        0,
        description="Number of failed texts"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of response"
    )
    
    @field_validator('results')
    @classmethod
    def validate_results(cls, v: List[HumanizeResponse]) -> List[HumanizeResponse]:
        if not v:
            raise ValueError("At least one result is required")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "original_text": "Text 1...",
                        "humanized_text": "Humanized 1...",
                        "tone": "academic",
                        "word_count": 10,
                        "processing_time": 0.2,
                        "method_used": "local"
                    }
                ],
                "total_processed": 3,
                "total_time": 0.456,
                "failed_count": 0
            }
        }


class AnalysisResult(BaseModel):
    """
    Text analysis result model
    """
    
    # Basic metrics
    sentence_count: int = Field(..., description="Number of sentences")
    word_count: int = Field(..., description="Number of words")
    char_count: int = Field(..., description="Number of characters")
    avg_word_length: float = Field(..., description="Average word length")
    
    # Complexity metrics
    readability_score: float = Field(..., description="Flesch Reading Ease score")
    difficulty_level: str = Field(..., description="Easy, Medium, Hard")
    vocabulary_richness: float = Field(..., description="Unique words / total words")
    
    # AI detection indicators
    perplexity: Optional[float] = Field(None, description="Perplexity score")
    burstiness: Optional[float] = Field(None, description="Sentence length variation")
    entropy: Optional[float] = Field(None, description="Information entropy")
    
    # Content analysis
    entities: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Named entities found"
    )
    topics: List[str] = Field(
        default_factory=list,
        description="Main topics detected"
    )
    sentiment: Dict[str, float] = Field(
        default_factory=dict,
        description="Sentiment analysis"
    )
    
    # Technical terms
    technical_terms: List[str] = Field(
        default_factory=list,
        description="Technical terms found"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "sentence_count": 5,
                "word_count": 120,
                "char_count": 600,
                "avg_word_length": 5.0,
                "readability_score": 45.2,
                "difficulty_level": "Hard",
                "vocabulary_richness": 0.65,
                "perplexity": 78.5,
                "burstiness": 0.82,
                "entropy": 0.78,
                "entities": {
                    "ORG": ["Aspergillus", "Trichoderma"],
                    "MISC": ["LPCB"]
                },
                "topics": ["Microscopy", "Fungal Identification"],
                "sentiment": {
                    "polarity": 0.0,
                    "subjectivity": 0.3
                },
                "technical_terms": ["mycelium", "hyphae", "conidiophore"]
            }
        }


class CompareResult(BaseModel):
    """
    Comparison result model
    """
    
    original_text: str = Field(..., description="Original text")
    
    variations: Dict[str, HumanizeResponse] = Field(
        ...,
        description="Variations by tone"
    )
    
    best_match: str = Field(
        ...,
        description="Recommended best variation"
    )
    
    comparison_metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Comparison metrics"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of response"
    )


# ========== HEALTH MODELS ==========

class HealthResponse(BaseModel):
    """
    Health check response model
    
    Example:
    ```json
    {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": "2026-07-02T09:08:15.123456",
        "methods_available": ["local", "rewriteai"],
        "uptime_seconds": 3600.5
    }
    ```
    """
    
    status: str = Field(
        ...,
        description="Service status (healthy/unhealthy)"
    )
    
    version: str = Field(
        ...,
        description="API version"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Health check timestamp"
    )
    
    methods_available: List[str] = Field(
        default_factory=list,
        description="Available humanization methods"
    )
    
    uptime_seconds: Optional[float] = Field(
        None,
        description="Service uptime in seconds"
    )
    
    dependencies: Dict[str, bool] = Field(
        default_factory=dict,
        description="Status of external dependencies"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "2.0.0",
                "timestamp": "2026-07-02T09:08:15.123456",
                "methods_available": ["local", "rewriteai"],
                "uptime_seconds": 3600.5,
                "dependencies": {
                    "rewriteai": True,
                    "gemini": False,
                    "groq": False
                }
            }
        }


# ========== ERROR MODELS ==========

class ErrorResponse(BaseModel):
    """
    Error response model
    
    Example:
    ```json
    {
        "detail": "Text must be at least 10 characters long",
        "status_code": 400,
        "error_type": "ValidationError",
        "timestamp": "2026-07-02T09:08:15.123456",
        "path": "/api/humanize"
    }
    ```
    """
    
    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    error_type: str = Field(..., description="Type of error")
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Error timestamp"
    )
    
    path: Optional[str] = Field(
        None,
        description="Request path that caused error"
    )
    
    suggestion: Optional[str] = Field(
        None,
        description="Suggested fix"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Text must be at least 10 characters long",
                "status_code": 400,
                "error_type": "ValidationError",
                "timestamp": "2026-07-02T09:08:15.123456",
                "path": "/api/humanize",
                "suggestion": "Please provide a longer text (minimum 10 characters)"
            }
        }


# ========== VOCABULARY MODELS ==========

class SynonymRequest(BaseModel):
    """
    Request model for getting synonyms
    """
    
    word: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Word to get synonyms for"
    )
    
    limit: int = Field(
        10,
        ge=1,
        le=50,
        description="Maximum number of synonyms to return"
    )
    
    context: Optional[str] = Field(
        None,
        description="Context to find relevant synonyms"
    )
    
    @field_validator('word')
    @classmethod
    def validate_word(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Word cannot be empty")
        if not v.isalpha():
            raise ValueError("Word must contain only alphabetic characters")
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "word": "identify",
                "limit": 10,
                "context": "scientific"
            }
        }


class SynonymResponse(BaseModel):
    """
    Response model for synonyms
    """
    
    word: str = Field(..., description="Original word")
    synonyms: List[str] = Field(..., description="List of synonyms")
    total_found: int = Field(..., description="Total number of synonyms found")
    
    class Config:
        json_schema_extra = {
            "example": {
                "word": "identify",
                "synonyms": ["detect", "recognize", "distinguish", "characterize"],
                "total_found": 4
            }
        }


# ========== STATISTICS MODELS ==========

class StatsResponse(BaseModel):
    """
    Statistics response model
    """
    
    total_requests: int = Field(0, description="Total number of requests")
    successful_requests: int = Field(0, description="Number of successful requests")
    failed_requests: int = Field(0, description="Number of failed requests")
    
    average_processing_time: float = Field(0.0, description="Average processing time")
    total_words_processed: int = Field(0, description="Total words processed")
    
    methods_used: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of each method used"
    )
    
    tones_used: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of each tone used"
    )
    
    uptime: float = Field(0.0, description="Uptime in seconds")
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Statistics timestamp"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_requests": 150,
                "successful_requests": 145,
                "failed_requests"
    @field_validator('texts')
    @classmethod
    def validate_texts(cls, v: List[str]) -> List[str]:
        """Validate all texts"""
        if not v:
            raise ValueError("At least one text is required")
        
        if len(v) > 50:
            raise ValueError("Maximum 50 texts allowed")
        
        for i, text in enumerate(v):
            if not text or not text.strip():
                raise ValueError(f"Text at index {i} is empty")
            
            cleaned = ' '.join(text.split())
            if len(cleaned) < 10:
                raise ValueError(f"Text at index {i} is too short (min 10 chars)")
            
            if len(cleaned) > 5000:
                raise ValueError(f"Text at index {i} is too long (max 5000 chars)")
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "texts": [
                    "Microscopic identification was carried out...",
                    "A small portion was placed on a glass slide..."
                ],
                "tone": "academic",
                "style": "balanced",
                "preserve_technical": True
            }
        }


class AnalyzeRequest(BaseModel):
    """
    Request model for text analysis
    
    Example:
    ```json
    {
        "text": "Microscopic identification was carried out..."
    }
    ```
    """
    
    text: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Text to analyze"
    )
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        return ' '.join(v.split())
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Microscopic identification was carried out to confirm morphological characteristics."
            }
        }


class CompareRequest(BaseModel):
    """
    Request model for comparing multiple humanization results
    
    Example:
    ```json
    {
        "text": "Microscopic identification was carried out...",
        "tones": ["academic", "natural", "conversational"]
    }
    ```
    """
    
    text: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Text to humanize"
    )
    
    tones: List[ToneEnum] = Field(
        [ToneEnum.ACADEMIC, ToneEnum.NATURAL, ToneEnum.CONVERSATIONAL],
        description="List of tones to compare"
    )
    
    style: StyleEnum = Field(
        StyleEnum.BALANCED,
        description="Style for all variations"
    )
    
    preserve_technical: bool = Field(
        True,
        description="Preserve technical terms"
    )
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        return ' '.join(v.split())
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Microscopic identification was carried out...",
                "tones": ["academic", "natural", "conversational"],
                "style": "balanced",
                "preserve_technical": True
            }
        }


# ========== RESPONSE MODELS ==========

class HumanizeResponse(BaseModel):
    """
    Response model for text humanization
    
    Example:
    ```json
    {
        "original_text": "Microscopic identification was carried out...",
        "humanized_text": "Microscopic identification was performed...",
        "tone": "academic",
        "style": "balanced",
        "word_count": 45,
        "processing_time": 0.234,
        "method_used": "local",
        "timestamp": "2026-07-02T09:08:15.123456"
    }
    ```
    """
    
    original_text: str = Field(
        ...,
        description="Original input text"
    )
    
    humanized_text: str = Field(
        ...,
        description="Humanized output text"
    )
    
    tone: str = Field(
        ...,
        description="Tone used for humanization"
    )
    
    style: str = Field(
        ...,
        description="Style used for humanization"
    )
    
    word_count: int = Field(
        ...,
        description="Number of words in humanized text",
        ge=1
    )
    
    processing_time: float = Field(
        ...,
        description="Processing time in seconds",
        ge=0
    )
    
    method_used: str = Field(
        ...,
        description="Method used (api/local)"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of response"
    )
    
    # Optional fields
    changes_made: Optional[int] = Field(
        None,
        description="Number of changes made"
    )
    
    original_word_count: Optional[int] = Field(
        None,
        description="Original word count"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "original_text": "Microscopic identification was carried out to confirm morphological characteristics.",
                "humanized_text": "Microscopic identification was performed to confirm morphological characteristics.",
                "tone": "academic",
                "style": "balanced",
                "word_count": 8,
                "processing_time": 0.234,
                "method_used": "local",
                "timestamp": "2026-07-02T09:08:15.123456",
                "changes_made": 3,
                "original_word_count": 10
            }
        }


class BatchHumanizeResponse(BaseModel):
    """
    Response model for batch text humanization
    
    Example:
    ```json
    {
        "results": [...],
        "total_processed": 3,
        "total_time": 0.456,
        "timestamp": "2026-07-02T09:08:15.123456"
    }
    ```
    """
    
    results: List[HumanizeResponse] = Field(
        ...,
        description="List of humanized results"
    )
    
    total_processed: int = Field(
        ...,
        description="Total number of texts processed",
        ge=0
    )
    
    total_time: float = Field(
        ...,
        description="Total processing time in seconds",
        ge=0
    )
    
    failed_count: int = Field(
        0,
        description="Number of failed texts"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of response"
    )
    
    @field_validator('results')
    @classmethod
    def validate_results(cls, v: List[HumanizeResponse]) -> List[HumanizeResponse]:
        if not v:
            raise ValueError("At least one result is required")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "original_text": "Text 1...",
                        "humanized_text": "Humanized 1...",
                        "tone": "academic",
                        "word_count": 10,
                        "processing_time": 0.2,
                        "method_used": "local"
                    }
                ],
                "total_processed": 3,
                "total_time": 0.456,
                "failed_count": 0
            }
        }


class AnalysisResult(BaseModel):
    """
    Text analysis result model
    """
    
    # Basic metrics
    sentence_count: int = Field(..., description="Number of sentences")
    word_count: int = Field(..., description="Number of words")
    char_count: int = Field(..., description="Number of characters")
    avg_word_length: float = Field(..., description="Average word length")
    
    # Complexity metrics
    readability_score: float = Field(..., description="Flesch Reading Ease score")
    difficulty_level: str = Field(..., description="Easy, Medium, Hard")
    vocabulary_richness: float = Field(..., description="Unique words / total words")
    
    # AI detection indicators
    perplexity: Optional[float] = Field(None, description="Perplexity score")
    burstiness: Optional[float] = Field(None, description="Sentence length variation")
    entropy: Optional[float] = Field(None, description="Information entropy")
    
    # Content analysis
    entities: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Named entities found"
    )
    topics: List[str] = Field(
        default_factory=list,
        description="Main topics detected"
    )
    sentiment: Dict[str, float] = Field(
        default_factory=dict,
        description="Sentiment analysis"
    )
    
    # Technical terms
    technical_terms: List[str] = Field(
        default_factory=list,
        description="Technical terms found"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "sentence_count": 5,
                "word_count": 120,
                "char_count": 600,
                "avg_word_length": 5.0,
                "readability_score": 45.2,
                "difficulty_level": "Hard",
                "vocabulary_richness": 0.65,
                "perplexity": 78.5,
                "burstiness": 0.82,
                "entropy": 0.78,
                "entities": {
                    "ORG": ["Aspergillus", "Trichoderma"],
                    "MISC": ["LPCB"]
                },
                "topics": ["Microscopy", "Fungal Identification"],
                "sentiment": {
                    "polarity": 0.0,
                    "subjectivity": 0.3
                },
                "technical_terms": ["mycelium", "hyphae", "conidiophore"]
            }
        }


class CompareResult(BaseModel):
    """
    Comparison result model
    """
    
    original_text: str = Field(..., description="Original text")
    
    variations: Dict[str, HumanizeResponse] = Field(
        ...,
        description="Variations by tone"
    )
    
    best_match: str = Field(
        ...,
        description="Recommended best variation"
    )
    
    comparison_metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Comparison metrics"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of response"
    )


# ========== HEALTH MODELS ==========

class HealthResponse(BaseModel):
    """
    Health check response model
    
    Example:
    ```json
    {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": "2026-07-02T09:08:15.123456",
        "methods_available": ["local", "rewriteai"],
        "uptime_seconds": 3600.5
    }
    ```
    """
    
    status: str = Field(
        ...,
        description="Service status (healthy/unhealthy)"
    )
    
    version: str = Field(
        ...,
        description="API version"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Health check timestamp"
    )
    
    methods_available: List[str] = Field(
        default_factory=list,
        description="Available humanization methods"
    )
    
    uptime_seconds: Optional[float] = Field(
        None,
        description="Service uptime in seconds"
    )
    
    dependencies: Dict[str, bool] = Field(
        default_factory=dict,
        description="Status of external dependencies"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "2.0.0",
                "timestamp": "2026-07-02T09:08:15.123456",
                "methods_available": ["local", "rewriteai"],
                "uptime_seconds": 3600.5,
                "dependencies": {
                    "rewriteai": True,
                    "gemini": False,
                    "groq": False
                }
            }
        }


# ========== ERROR MODELS ==========

class ErrorResponse(BaseModel):
    """
    Error response model
    
    Example:
    ```json
    {
        "detail": "Text must be at least 10 characters long",
        "status_code": 400,
        "error_type": "ValidationError",
        "timestamp": "2026-07-02T09:08:15.123456",
        "path": "/api/humanize"
    }
    ```
    """
    
    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    error_type: str = Field(..., description="Type of error")
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Error timestamp"
    )
    
    path: Optional[str] = Field(
        None,
        description="Request path that caused error"
    )
    
    suggestion: Optional[str] = Field(
        None,
        description="Suggested fix"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Text must be at least 10 characters long",
                "status_code": 400,
                "error_type": "ValidationError",
                "timestamp": "2026-07-02T09:08:15.123456",
                "path": "/api/humanize",
                "suggestion": "Please provide a longer text (minimum 10 characters)"
            }
        }


# ========== VOCABULARY MODELS ==========

class SynonymRequest(BaseModel):
    """
    Request model for getting synonyms
    """
    
    word: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Word to get synonyms for"
    )
    
    limit: int = Field(
        10,
        ge=1,
        le=50,
        description="Maximum number of synonyms to return"
    )
    
    context: Optional[str] = Field(
        None,
        description="Context to find relevant synonyms"
    )
    
    @field_validator('word')
    @classmethod
    def validate_word(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Word cannot be empty")
        if not v.isalpha():
            raise ValueError("Word must contain only alphabetic characters")
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "word": "identify",
                "limit": 10,
                "context": "scientific"
            }
        }


class SynonymResponse(BaseModel):
    """
    Response model for synonyms
    """
    
    word: str = Field(..., description="Original word")
    synonyms: List[str] = Field(..., description="List of synonyms")
    total_found: int = Field(..., description="Total number of synonyms found")
    
    class Config:
        json_schema_extra = {
            "example": {
                "word": "identify",
                "synonyms": ["detect", "recognize", "distinguish", "characterize"],
                "total_found": 4
            }
        }


# ========== STATISTICS MODELS ==========

class StatsResponse(BaseModel):
    """
    Statistics response model
    """
    
    total_requests: int = Field(0, description="Total number of requests")
    successful_requests: int = Field(0, description="Number of successful requests")
    failed_requests: int = Field(0, description="Number of failed requests")
    
    average_processing_time: float = Field(0.0, description="Average processing time")
    total_words_processed: int = Field(0, description="Total words processed")
    
    methods_used: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of each method used"
    )
    
    tones_used: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of each tone used"
    )
    
    uptime: float = Field(0.0, description="Uptime in seconds")
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Statistics timestamp"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_requests": 150,
                "successful_requests": 145,
                "failed_requests": 5,
                "average_processing_time": 0.345,
                "total_words_processed": 5000,
                "methods_used": {
                    "local": 100,
                    "rewriteai_api": 50
                },
                "tones_used": {
                    "academic": 80,
                    "natural": 40,
                    "conversational": 30
                },
                "uptime": 7200.5
            }
        }


# ========== EXPORTS ==========

__all__ = [
    # Enums
    "ToneEnum",
    "StyleEnum", 
    "MethodEnum",
    
    # Request Models
    "HumanizeRequest",
    "BatchHumanizeRequest",
    "AnalyzeRequest",
    "CompareRequest",
    "SynonymRequest",
    
    # Response Models
    "HumanizeResponse",
    "BatchHumanizeResponse",
    "AnalysisResult",
    "CompareResult",
    "HealthResponse",
    "ErrorResponse",
    "SynonymResponse",
    "StatsResponse",
]