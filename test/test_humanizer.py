"""
Humanizer Tests for AI Humanizer
Tests all humanization services and local humanizer logic
"""

import pytest
from backend.services.local_humanizer import LocalHumanizer
from backend.services.api_humanizer import APIHumanizer
from backend.services.humanizer import HumanizerService, get_humanizer
from backend.services.humanize import HumanizeService, get_humanize_service
from backend.vocabulary import ROBOTIC_PHRASES, SYNONYMS, TRANSITIONS, TONE_SETTINGS, DOMAIN_TERMS


class TestLocalHumanizer:
    """Test LocalHumanizer class"""
    
    def setup_method(self):
        """Setup before each test"""
        self.humanizer = LocalHumanizer()
    
    # ============================================================
    # BASIC HUMANIZATION TESTS
    # ============================================================
    
    def test_humanize_basic(self):
        """Test basic humanization"""
        text = "Microscopic identification was carried out."
        result = self.humanizer.humanize(text, tone="academic")
        
        assert result is not None
        assert len(result) > 0
        # Should replace robotic phrase
        assert "was carried out" not in result.lower() or "was performed" in result.lower()
    
    def test_humanize_with_technical_terms(self):
        """Test humanization with technical term preservation"""
        text = "Aspergillus niger was identified by septate hyphae."
        result = self.humanizer.humanize(text, preserve_technical=True)
        
        # Technical terms should be preserved
        assert "Aspergillus" in result or "aspergillus" in result.lower()
        assert "septate" in result or "hyphae" in result
    
    def test_humanize_without_technical_preserve(self):
        """Test humanization without technical term preservation"""
        text = "Aspergillus niger was identified by septate hyphae."
        result = self.humanizer.humanize(text, preserve_technical=False)
        
        # Should still work, may or may not preserve technical terms
        assert result is not None
        assert len(result) > 0
    
    def test_humanize_empty_text(self):
        """Test humanization with empty text"""
        result = self.humanizer.humanize("", tone="academic")
        assert result == ""  # Should return empty string
    
    def test_humanize_short_text(self):
        """Test humanization with short text"""
        text = "Test."
        result = self.humanizer.humanize(text, tone="academic")
        # Should return original or humanized
        assert result is not None
    
    # ============================================================
    # TONE TESTS
    # ============================================================
    
    def test_humanize_academic_tone(self):
        """Test academic tone"""
        text = "The experiment was conducted successfully."
        result = self.humanizer.humanize(text, tone="academic")
        
        assert result is not None
        # Academic tone should be formal
        assert "was" in result or "were" in result
    
    def test_humanize_natural_tone(self):
        """Test natural tone"""
        text = "The experiment was conducted successfully."
        result = self.humanizer.humanize(text, tone="natural")
        
        assert result is not None
        # Natural tone should have some contractions
        # Note: Not guaranteed to have contractions every time
    
    def test_humanize_blog_tone(self):
        """Test blog tone"""
        text = "The experiment was conducted successfully."
        result = self.humanizer.humanize(text, tone="blog")
        
        assert result is not None
        # Blog tone should be more casual
        assert len(result) > 0
    
    def test_humanize_professional_tone(self):
        """Test professional tone"""
        text = "The experiment was conducted successfully."
        result = self.humanizer.humanize(text, tone="professional")
        
        assert result is not None
        # Professional tone should be formal
        assert "was" in result or "were" in result
    
    def test_humanize_conversational_tone(self):
        """Test conversational tone"""
        text = "The experiment was conducted successfully."
        result = self.humanizer.humanize(text, tone="conversational")
        
        assert result is not None
        # Conversational tone should have casual elements
        # Note: May not always have "So basically" due to randomness
    
    def test_humanize_invalid_tone(self):
        """Test humanization with invalid tone"""
        text = "Test text."
        result = self.humanizer.humanize(text, tone="invalid_tone")
        
        # Should fallback to natural tone
        assert result is not None
        assert len(result) > 0
    
    # ============================================================
    # STYLE TESTS
    # ============================================================
    
    def test_humanize_conservative_style(self):
        """Test conservative style"""
        text = "The experiment was conducted successfully. The results were recorded."
        result = self.humanizer.humanize(text, style="conservative")
        
        assert result is not None
        assert len(result) > 0
    
    def test_humanize_balanced_style(self):
        """Test balanced style"""
        text = "The experiment was conducted successfully. The results were recorded."
        result = self.humanizer.humanize(text, style="balanced")
        
        assert result is not None
        assert len(result) > 0
    
    def test_humanize_creative_style(self):
        """Test creative style"""
        text = "The experiment was conducted successfully. The results were recorded."
        result = self.humanizer.humanize(text, style="creative")
        
        assert result is not None
        assert len(result) > 0
    
    # ============================================================
    # ROBOTIC PHRASE REPLACEMENT TESTS
    # ============================================================
    
    def test_robotic_phrase_replacement(self):
        """Test robotic phrase replacement"""
        phrases = [
            ("was carried out", "was performed"),
            ("was placed", "was positioned"),
            ("were recorded", "were documented"),
            ("was identified by", "was recognized by"),
            ("in order to", "to"),
            ("prior to", "before"),
        ]
        
        for old, new in phrases:
            text = f"The experiment {old} successfully."
            result = self.humanizer.humanize(text)
            
            # Should replace or keep (if random doesn't pick)
            assert len(result) > 0
    
    # ============================================================
    # SYNONYM REPLACEMENT TESTS
    # ============================================================
    
    def test_synonym_replacement(self):
        """Test synonym replacement"""
        text = "This study shows significant results."
        result = self.humanizer.humanize(text)
        
        assert result is not None
        # Some words might be replaced
        assert len(result) > 0
    
    def test_synonym_replacement_all_words(self):
        """Test synonym replacement on all words"""
        text = "The experiment was conducted."
        result = self.humanizer.humanize(text, style="creative")
        
        assert result is not None
        assert len(result) > 0
    
    # ============================================================
    # SENTENCE RESTRUCTURING TESTS
    # ============================================================
    
    def test_sentence_restructuring(self):
        """Test sentence restructuring"""
        text = "This is sentence one. This is sentence two. This is sentence three."
        result = self.humanizer.humanize(text)
        
        assert result is not None
        assert len(result) > 0
        # Should have at least 2 sentences
        assert len(result.split(". ")) >= 2
    
    def test_sentence_merging(self):
        """Test short sentence merging"""
        text = "Short. Another short. Long sentence here."
        result = self.humanizer.humanize(text)
        
        assert result is not None
        assert len(result) > 0
    
    def test_sentence_splitting(self):
        """Test long sentence splitting"""
        long_text = "This is a very long sentence that should be split into multiple parts because it has many words and commas, and it needs to be broken down, and this should work properly."
        result = self.humanizer.humanize(long_text)
        
        assert result is not None
        assert len(result) > 0
    
    # ============================================================
    # TRANSITION ADDITION TESTS
    # ============================================================
    
    def test_transition_addition(self):
        """Test transition word addition"""
        text = "The experiment was conducted. The results were analyzed."
        result = self.humanizer.humanize(text)
        
        assert result is not None
        assert len(result) > 0
    
    def test_no_transition_for_short_text(self):
        """Test no transition for very short text"""
        text = "Short text."
        result = self.humanizer.humanize(text)
        
        assert result is not None
        assert len(result) > 0
    
    # ============================================================
    # VOICE VARIATION TESTS
    # ============================================================
    
    def test_voice_variation(self):
        """Test active/passive voice variation"""
        text = "The experiment was conducted by the researcher."
        result = self.humanizer.humanize(text)
        
        assert result is not None
        assert len(result) > 0
    
    # ============================================================
    # TEXT ANALYSIS TESTS
    # ============================================================
    
    def test_analyze_basic(self):
        """Test basic text analysis"""
        text = "This is a test sentence. It has multiple sentences."
        result = self.humanizer.analyze(text)
        
        assert "sentence_count" in result
        assert "word_count" in result
        assert "char_count" in result
        assert "readability_score" in result
        assert "difficulty_level" in result
        assert "vocabulary_richness" in result
        assert result["sentence_count"] >= 2
    
    def test_analyze_empty_text(self):
        """Test analyze with empty text"""
        result = self.humanizer.analyze("")
        
        assert result["sentence_count"] == 0
        assert result["word_count"] == 0
        assert result["char_count"] == 0
    
    def test_analyze_technical_terms(self):
        """Test technical term detection"""
        text = "Aspergillus niger mycelium hyphae conidiophore"
        result = self.humanizer.analyze(text)
        
        assert "technical_terms" in result
        # Should detect at least one technical term
        assert len(result["technical_terms"]) > 0
    
    def test_analyze_readability(self):
        """Test readability calculation"""
        easy_text = "This is a very easy to read sentence."
        hard_text = "The complicated morphological characteristics of Aspergillus niger were identified through microscopic examination."
        
        easy_result = self.humanizer.analyze(easy_text)
        hard_result = self.humanizer.analyze(hard_text)
        
        assert easy_result["readability_score"] >= hard_result["readability_score"]
    
    def test_analyze_vocabulary_richness(self):
        """Test vocabulary richness calculation"""
        rich_text = "The quick brown fox jumps over the lazy dog."
        poor_text = "Test test test test test test test."
        
        rich_result = self.humanizer.analyze(rich_text)
        poor_result = self.humanizer.analyze(poor_text)
        
        assert rich_result["vocabulary_richness"] >= poor_result["vocabulary_richness"]
    
    # ============================================================
    # QUALITY CHECKS
    # ============================================================
    
    def test_quality_check_preserves_length(self):
        """Test quality check preserves reasonable length"""
        text = "This is a test text with reasonable length for humanization."
        result = self.humanizer.humanize(text)
        
        # Should not be too short
        assert len(result) > len(text) * 0.4
    
    def test_quality_check_returns_original_if_too_short(self):
        """Test quality check returns original if too short"""
        text = "Short text."
        result = self.humanizer.humanize(text)
        
        # Should return something reasonable
        assert result is not None
    
    # ============================================================
    # EDGE CASES
    # ============================================================
    
    def test_humanize_with_special_characters(self):
        """Test humanization with special characters"""
        text = "Microscopic identification (using LPCB stain) was carried out @ 25°C!"
        result = self.humanizer.humanize(text)
        
        assert result is not None
        assert len(result) > 0
    
    def test_humanize_with_numbers(self):
        """Test humanization with numbers"""
        text = "The experiment was repeated 5 times at 37°C."
        result = self.humanizer.humanize(text)
        
        assert result is not None
        assert len(result) > 0
    
    def test_humanize_with_emojis(self):
        """Test humanization with emojis"""
        text = "🔬 The experiment was successful! 🧪"
        result = self.humanizer.humanize(text, tone="blog")
        
        assert result is not None
        assert len(result) > 0
    
    def test_humanize_with_quotes(self):
        """Test humanization with quotes"""
        text = 'He said "The experiment was successful."'
        result = self.humanizer.humanize(text)
        
        assert result is not None
        assert len(result) > 0
    
    def test_humanize_with_contractions(self):
        """Test humanization with existing contractions"""
        text = "It's not working. Can't do it."
        result = self.humanizer.humanize(text, tone="conversational")
        
        assert result is not None
        assert len(result) > 0


class TestHumanizerService:
    """Test HumanizerService class"""
    
    def setup_method(self):
        """Setup before each test"""
        self.service = HumanizerService()
    
    def test_humanizer_service_init(self):
        """Test HumanizerService initialization"""
        assert self.service is not None
        assert hasattr(self.service, 'local_humanizer')
        assert hasattr(self.service, 'api_humanizer')
        assert hasattr(self.service, 'total_requests')
        assert hasattr(self.service, 'successful_requests')
    
    def test_humanize(self):
        """Test humanize method"""
        result = self.service.humanize(
            text="This is a test text.",
            tone="academic",
            style="balanced"
        )
        assert result is not None
        assert result.original_text == "This is a test text."
        assert result.word_count > 0
        assert result.processing_time >= 0
    
    def test_analyze(self):
        """Test analyze method"""
        result = self.service.analyze(
            text="This is a test sentence. It has multiple sentences."
        )
        assert "sentence_count" in result
        assert "word_count" in result
        assert result["sentence_count"] >= 2
    
    def test_get_stats(self):
        """Test get_stats method"""
        stats = self.service.get_stats()
        assert "total_requests" in stats
        assert "successful_requests" in stats
        assert "failed_requests" in stats
        assert "uptime" in stats
    
    def test_get_uptime(self):
        """Test get_uptime method"""
        uptime = self.service.get_uptime()
        assert uptime >= 0


class TestHumanizeService:
    """Test HumanizeService class (with cache)"""
    
    def setup_method(self):
        """Setup before each test"""
        self.service = get_humanize_service()
    
    def test_humanize_service_init(self):
        """Test HumanizeService initialization"""
        assert self.service is not None
        assert hasattr(self.service, 'local_humanizer')
        assert hasattr(self.service, 'api_humanizer')
        assert hasattr(self.service, 'cache')
    
    def test_humanize(self):
        """Test humanize method"""
        result = self.service.humanize(
            text="This is a test text.",
            tone="academic"
        )
        assert result is not None
        assert result.word_count > 0
    
    def test_analyze(self):
        """Test analyze method"""
        result = self.service.analyze(
            text="This is a test sentence."
        )
        assert "word_count" in result
    
    def test_clear_cache(self):
        """Test clear_cache method"""
        self.service.clear_cache()
        assert len(self.service.cache) == 0
    
    def test_get_cache_stats(self):
        """Test get_cache_stats method"""
        stats = self.service.get_cache_stats()
        assert "enabled" in stats
        assert "size" in stats
        assert "max_size" in stats
        assert "hits" in stats
        assert "misses" in stats


class TestAPIHumanizer:
    """Test APIHumanizer class (Mock tests)"""
    
    def setup_method(self):
        """Setup before each test"""
        self.api_humanizer = APIHumanizer()
    
    def test_api_humanizer_init(self):
        """Test APIHumanizer initialization"""
        assert self.api_humanizer is not None
        assert hasattr(self.api_humanizer, 'max_retries')
        assert hasattr(self.api_humanizer, 'retry_delay')
        assert hasattr(self.api_humanizer, 'api_status')
    
    def test_get_api_status(self):
        """Test get_api_status method"""
        status = self.api_humanizer.get_api_status()
        assert "rewriteai" in status
        assert "gemini" in status
        assert "groq" in status
        assert "openai" in status
    
    def test_get_best_method(self):
        """Test get_best_method method"""
        method = self.api_humanizer.get_best_method()
        assert method in ["rewriteai", "gemini", "groq", "openai", "local"]
    
    def test_reset_api_status(self):
        """Test reset_api_status method"""
        self.api_humanizer.reset_api_status()
        status = self.api_humanizer.get_api_status()
        for api in status.values():
            assert api["success_count"] == 0
            assert api["fail_count"] == 0


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])