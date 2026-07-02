"""
Humanize Route Handler
Contains all API endpoints for humanization
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from backend.models import (
    HumanizeRequest,
    HumanizeResponse,
    BatchHumanizeRequest,
    BatchHumanizeResponse,
    AnalyzeRequest,
    AnalysisResult,
    CompareRequest,
    CompareResult,
    ErrorResponse,
)
from backend.services.humanize import get_humanize_service
from backend.services.humanizer import get_humanizer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["humanize"])


# ============================================================
# DEPENDENCIES
# ============================================================

def get_humanize_service_dep():
    """Get humanize service instance"""
    return get_humanize_service()


def get_humanizer_dep():
    """Get humanizer service instance"""
    return get_humanizer()


# ============================================================
# ENDPOINTS
# ============================================================

@router.post(
    "/humanize",
    response_model=HumanizeResponse,
    summary="Humanize a single text",
    description="Humanize AI-generated text using available methods"
)
async def humanize_text(
    request: HumanizeRequest,
    service = Depends(get_humanize_service_dep)
):
    """
    Humanize a single text
    
    **Request Body:**
    - **text**: The text to humanize (min 10 chars, max 5000 chars)
    - **tone**: academic, natural, blog, professional, conversational
    - **style**: conservative, balanced, creative
    - **preserve_technical**: Keep technical terms unchanged
    
    **Response:**
    - **original_text**: Original input text
    - **humanized_text**: Humanized output text
    - **method_used**: Which method was used (local/api)
    - **processing_time**: Time taken in seconds
    """
    try:
        logger.info(f"Humanize request: tone={request.tone}, style={request.style}")
        
        result = service.humanize(
            text=request.text,
            tone=request.tone.value,
            style=request.style.value,
            preserve_technical=request.preserve_technical
        )
        
        return result
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Humanize error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/humanize/batch",
    response_model=BatchHumanizeResponse,
    summary="Humanize multiple texts",
    description="Humanize up to 50 texts in a single request"
)
async def humanize_batch(
    request: BatchHumanizeRequest,
    service = Depends(get_humanize_service_dep)
):
    """
    Humanize multiple texts in batch
    
    **Request Body:**
    - **texts**: List of texts to humanize (1-50 items)
    - **tone**: Tone for all texts
    - **style**: Style for all texts
    - **preserve_technical**: Keep technical terms unchanged
    
    **Response:**
    - **results**: List of humanized results
    - **total_processed**: Number of texts processed
    - **total_time**: Total processing time
    - **failed_count**: Number of failed texts
    """
    try:
        logger.info(f"Batch humanize: {len(request.texts)} texts")
        
        results = service.humanize_batch(
            texts=request.texts,
            tone=request.tone.value,
            style=request.style.value,
            preserve_technical=request.preserve_technical
        )
        
        total_time = sum(r.processing_time for r in results)
        failed_count = sum(1 for r in results if r.method_used == "failed")
        
        return BatchHumanizeResponse(
            results=results,
            total_processed=len(request.texts),
            total_time=round(total_time, 3),
            failed_count=failed_count
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Batch humanize error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/analyze",
    response_model=AnalysisResult,
    summary="Analyze text",
    description="Get detailed analysis of text including readability, complexity"
)
async def analyze_text(
    request: AnalyzeRequest,
    service = Depends(get_humanize_service_dep)
):
    """
    Analyze a text for various metrics
    
    **Request Body:**
    - **text**: The text to analyze
    
    **Response:**
    - **sentence_count**: Number of sentences
    - **word_count**: Number of words
    - **readability_score**: Flesch Reading Ease score
    - **difficulty_level**: Easy, Medium, or Hard
    - **vocabulary_richness**: Unique words / total words
    - **technical_terms**: Technical terms found
    """
    try:
        logger.info(f"Analyze request: {len(request.text)} chars")
        
        result = service.analyze(request.text)
        return result
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analyze error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/compare",
    response_model=CompareResult,
    summary="Compare tones",
    description="Compare multiple tones for the same text"
)
async def compare_tones(
    request: CompareRequest,
    service = Depends(get_humanize_service_dep)
):
    """
    Compare different tones for the same text
    
    **Request Body:**
    - **text**: Text to humanize
    - **tones**: List of tones to compare
    - **style**: Style for all variations
    - **preserve_technical**: Keep technical terms unchanged
    
    **Response:**
    - **original_text**: Original text
    - **variations**: Humanized versions for each tone
    - **best_match**: Recommended best variation
    """
    try:
        logger.info(f"Compare tones: {len(request.tones)} tones")
        
        tones = [t.value for t in request.tones]
        
        variations = service.compare_tones(
            text=request.text,
            tones=tones,
            style=request.style.value,
            preserve_technical=request.preserve_technical
        )
        
        # Find best match (highest word count variation)
        best = max(variations.items(), key=lambda x: x[1].word_count)
        
        return CompareResult(
            original_text=request.text,
            variations=variations,
            best_match=best[0]
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Compare error: {e}")
        raise HTTPException(status_code=500, detail=str(e))