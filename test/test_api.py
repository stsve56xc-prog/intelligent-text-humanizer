"""
API Tests for AI Humanizer
Tests all API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models import ToneEnum, StyleEnum


class TestAPI:
    """Test all API endpoints"""
    
    def setup_method(self):
        """Setup before each test"""
        self.client = TestClient(app)
    
    # ============================================================
    # SYSTEM ENDPOINTS
    # ============================================================
    
    def test_root_endpoint(self):
        """Test root endpoint returns API info"""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["name"] == "AI Humanizer API"
    
    def test_health_endpoint(self):
        """Test health endpoint returns healthy status"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "methods_available" in data
        assert "local" in data["methods_available"]
    
    def test_docs_endpoint(self):
        """Test docs endpoint exists"""
        response = self.client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_endpoint(self):
        """Test redoc endpoint exists"""
        response = self.client.get("/redoc")
        assert response.status_code == 200
    
    # ============================================================
    # HUMANIZE ENDPOINT
    # ============================================================
    
    def test_humanize_endpoint_valid(self):
        """Test humanize endpoint with valid request"""
        response = self.client.post(
            "/api/humanize",
            json={
                "text": "Microscopic identification was carried out to confirm morphological characteristics.",
                "tone": "academic",
                "style": "balanced",
                "preserve_technical": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "original_text" in data
        assert "humanized_text" in data
        assert "word_count" in data
        assert "method_used" in data
        assert data["tone"] == "academic"
        assert data["style"] == "balanced"
    
    def test_humanize_endpoint_with_natural_tone(self):
        """Test humanize with natural tone"""
        response = self.client.post(
            "/api/humanize",
            json={
                "text": "The experiment was conducted successfully.",
                "tone": "natural",
                "style": "balanced"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["tone"] == "natural"
        assert "humanized_text" in data
    
    def test_humanize_endpoint_with_conversational_tone(self):
        """Test humanize with conversational tone"""
        response = self.client.post(
            "/api/humanize",
            json={
                "text": "The results indicate a significant correlation.",
                "tone": "conversational",
                "style": "creative"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["tone"] == "conversational"
        assert data["style"] == "creative"
    
    def test_humanize_endpoint_invalid_tone(self):
        """Test humanize with invalid tone"""
        response = self.client.post(
            "/api/humanize",
            json={
                "text": "This is a test text.",
                "tone": "invalid_tone"
            }
        )
        assert response.status_code == 422 or response.status_code == 400
    
    def test_humanize_endpoint_text_too_short(self):
        """Test humanize with text too short"""
        response = self.client.post(
            "/api/humanize",
            json={
                "text": "Hi",
                "tone": "academic"
            }
        )
        assert response.status_code == 422 or response.status_code == 400
    
    def test_humanize_endpoint_empty_text(self):
        """Test humanize with empty text"""
        response = self.client.post(
            "/api/humanize",
            json={
                "text": "",
                "tone": "academic"
            }
        )
        assert response.status_code == 422 or response.status_code == 400
    
    def test_humanize_endpoint_long_text(self):
        """Test humanize with long text"""
        long_text = "This is a test sentence. " * 500  # 5000+ chars
        response = self.client.post(
            "/api/humanize",
            json={
                "text": long_text,
                "tone": "academic"
            }
        )
        # Should either succeed or return 422 (too long)
        assert response.status_code in [200, 422, 400]
    
    def test_humanize_endpoint_preserve_technical(self):
        """Test humanize with technical term preservation"""
        text = "Aspergillus niger was identified by septate hyphae."
        response = self.client.post(
            "/api/humanize",
            json={
                "text": text,
                "tone": "academic",
                "preserve_technical": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Technical terms should be preserved
        assert "Aspergillus" in data["humanized_text"] or "niger" in data["humanized_text"]
    
    def test_humanize_endpoint_no_preserve_technical(self):
        """Test humanize without technical term preservation"""
        text = "Aspergillus niger was identified by septate hyphae."
        response = self.client.post(
            "/api/humanize",
            json={
                "text": text,
                "tone": "academic",
                "preserve_technical": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Text should still be humanized
        assert "humanized_text" in data
    
    def test_humanize_endpoint_response_structure(self):
        """Test humanize response structure"""
        response = self.client.post(
            "/api/humanize",
            json={
                "text": "This is a test text for humanization.",
                "tone": "academic"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check all required fields
        required_fields = [
            "original_text",
            "humanized_text",
            "tone",
            "style",
            "word_count",
            "processing_time",
            "method_used",
            "timestamp"
        ]
        for field in required_fields:
            assert field in data
        
        # Check field types
        assert isinstance(data["original_text"], str)
        assert isinstance(data["humanized_text"], str)
        assert isinstance(data["word_count"], int)
        assert isinstance(data["processing_time"], float)
        assert isinstance(data["method_used"], str)
    
    # ============================================================
    # BATCH HUMANIZE ENDPOINT
    # ============================================================
    
    def test_batch_humanize_endpoint(self):
        """Test batch humanize endpoint"""
        response = self.client.post(
            "/api/humanize/batch",
            json={
                "texts": ["Text 1", "Text 2", "Text 3"],
                "tone": "academic",
                "style": "balanced"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total_processed" in data
        assert data["total_processed"] == 3
        assert len(data["results"]) == 3
    
    def test_batch_humanize_endpoint_empty_list(self):
        """Test batch humanize with empty list"""
        response = self.client.post(
            "/api/humanize/batch",
            json={
                "texts": [],
                "tone": "academic"
            }
        )
        assert response.status_code == 422 or response.status_code == 400
    
    def test_batch_humanize_endpoint_too_many(self):
        """Test batch humanize with too many texts"""
        texts = ["Text"] * 60  # 60 texts (limit is 50)
        response = self.client.post(
            "/api/humanize/batch",
            json={
                "texts": texts,
                "tone": "academic"
            }
        )
        assert response.status_code == 422 or response.status_code == 400
    
    # ============================================================
    # ANALYZE ENDPOINT
    # ============================================================
    
    def test_analyze_endpoint(self):
        """Test analyze endpoint"""
        text = "This is a test sentence. It has multiple sentences. Here is the third one."
        response = self.client.post(
            "/api/analyze",
            json={"text": text}
        )
        assert response.status_code == 200
        data = response.json()
        assert "sentence_count" in data
        assert "word_count" in data
        assert "char_count" in data
        assert "readability_score" in data
        assert "difficulty_level" in data
        assert "vocabulary_richness" in data
        assert data["sentence_count"] >= 3
    
    def test_analyze_endpoint_empty_text(self):
        """Test analyze with empty text"""
        response = self.client.post(
            "/api/analyze",
            json={"text": ""}
        )
        assert response.status_code == 422 or response.status_code == 400
    
    def test_analyze_endpoint_technical_terms(self):
        """Test analyze detects technical terms"""
        text = "Aspergillus niger mycelium hyphae conidiophore"
        response = self.client.post(
            "/api/analyze",
            json={"text": text}
        )
        assert response.status_code == 200
        data = response.json()
        assert "technical_terms" in data
        # Should detect at least one technical term
        assert len(data["technical_terms"]) > 0
    
    # ============================================================
    # COMPARE ENDPOINT
    # ============================================================
    
    def test_compare_endpoint(self):
        """Test compare endpoint"""
        response = self.client.post(
            "/api/compare",
            json={
                "text": "This is a test text for comparison.",
                "tones": ["academic", "natural", "conversational"],
                "style": "balanced"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "original_text" in data
        assert "variations" in data
        assert "best_match" in data
        assert len(data["variations"]) == 3
    
    def test_compare_endpoint_single_tone(self):
        """Test compare with single tone"""
        response = self.client.post(
            "/api/compare",
            json={
                "text": "Test text.",
                "tones": ["academic"],
                "style": "balanced"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["variations"]) == 1
    
    def test_compare_endpoint_empty_tones(self):
        """Test compare with empty tones list"""
        response = self.client.post(
            "/api/compare",
            json={
                "text": "Test text.",
                "tones": [],
                "style": "balanced"
            }
        )
        assert response.status_code == 422 or response.status_code == 400
    
    # ============================================================
    # STATS ENDPOINT
    # ============================================================
    
    def test_stats_endpoint(self):
        """Test stats endpoint"""
        response = self.client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        assert "api_status" in data
        assert "service" in data
        assert data["service"] == "AI Humanizer API"
    
    # ============================================================
    # CACHE ENDPOINT
    # ============================================================
    
    def test_clear_cache_endpoint(self):
        """Test clear cache endpoint"""
        response = self.client.post("/api/cache/clear")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "message" in data
    
    # ============================================================
    # CORS TESTS
    # ============================================================
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = self.client.options(
            "/api/humanize",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
    
    # ============================================================
    # EDGE CASES
    # ============================================================
    
    def test_humanize_with_special_characters(self):
        """Test humanize with special characters"""
        text = "Microscopic identification (using LPCB stain) was carried out @ 25°C!"
        response = self.client.post(
            "/api/humanize",
            json={
                "text": text,
                "tone": "academic"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "humanized_text" in data
    
    def test_humanize_with_numbers(self):
        """Test humanize with numbers"""
        text = "The experiment was repeated 5 times at 37°C."
        response = self.client.post(
            "/api/humanize",
            json={
                "text": text,
                "tone": "academic"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "humanized_text" in data
    
    def test_humanize_with_emojis(self):
        """Test humanize with emojis"""
        text = "🔬 The experiment was successful! 🧪"
        response = self.client.post(
            "/api/humanize",
            json={
                "text": text,
                "tone": "blog"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "humanized_text" in data
    
    # ============================================================
    # PERFORMANCE TESTS
    # ============================================================
    
    def test_humanize_response_time(self):
        """Test humanize response time is reasonable"""
        import time
        
        start = time.time()
        response = self.client.post(
            "/api/humanize",
            json={
                "text": "This is a test text for performance testing.",
                "tone": "academic"
            }
        )
        end = time.time()
        
        assert response.status_code == 200
        # Should complete within 10 seconds
        assert end - start < 10.0
    
    def test_batch_humanize_response_time(self):
        """Test batch humanize response time is reasonable"""
        import time
        
        texts = [f"Test text {i}" for i in range(10)]
        
        start = time.time()
        response = self.client.post(
            "/api/humanize/batch",
            json={
                "texts": texts,
                "tone": "academic"
            }
        )
        end = time.time()
        
        assert response.status_code == 200
        # Should complete within 30 seconds
        assert end - start < 30.0


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])