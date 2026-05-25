import pytest
from app.services.nlp import (
    analyze_sentiment,
    extract_domain_keywords,
    detect_cognitive_patterns,
    compute_message_features,
    extract_nlp_features
)
import asyncio

def test_analyze_sentiment():
    """Test sentiment analysis (requires model to be loaded)."""
    # Since loading the model takes time and resources, this is a basic test
    result = analyze_sentiment("Saya merasa sangat lelah dan stres dengan pekerjaan ini.")
    assert "sentiment_score" in result
    assert "sentiment_label" in result
    assert "confidence" in result
    assert result["sentiment_label"] in ["positive", "neutral", "negative"]

def test_extract_domain_keywords():
    """Test keyword extraction for burnout domains."""
    text = "Saya selalu lembur tiap malam dan merasa capek banget, sampai susah tidur."
    result = extract_domain_keywords(text)
    
    assert result["keyword_count"] > 0
    assert "lembur" in result["domain_keywords"]["work_stress"]
    assert "capek" in result["domain_keywords"]["exhaustion"]
    assert "susah tidur" in result["domain_keywords"]["sleep_problems"]

def test_detect_cognitive_patterns():
    """Test detection of cognitive distortions like absolutist language."""
    text = "Semua orang membenci saya, tidak ada satupun yang peduli. Saya tidak bisa apa-apa."
    result = detect_cognitive_patterns(text)
    
    assert result["absolutist_language_count"] > 0
    assert result["helplessness_phrases_count"] > 0
    assert result["cognitive_distortion_score"] > 0

def test_compute_message_features():
    """Test calculation of message features (length, sentences, punctuation)."""
    text = "Halo? Apakah ada orang di sana! Saya butuh bantuan."
    result = compute_message_features(text)
    
    assert result["message_length"] == 9
    assert result["question_count"] == 1
    assert result["exclamation_count"] == 1
    assert result["is_very_short"] is False
    assert result["is_long_disclosure"] is False

@pytest.mark.asyncio
async def test_extract_nlp_features_async():
    """Test the full async NLP pipeline."""
    text = "Kerjaan numpuk bikin pusing, mau apa lagi coba?"
    result = await extract_nlp_features(text)
    
    assert "sentiment_score" in result
    assert "keyword_count" in result
    assert "cognitive_distortion_score" in result
    assert "message_length" in result
    assert result["raw_text"] == text
