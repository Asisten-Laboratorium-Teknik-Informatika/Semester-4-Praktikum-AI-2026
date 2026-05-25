import pytest
from app.services.gemini import _extract_json, _detect_response_emotion

def test_extract_json():
    text = "Halo, saya RINA. [DATA:{\"sleep_hours\": 6, \"mood_score\": -0.5, \"emotion_tone\": \"neutral\"}:DATA]"
    data = _extract_json(text)
    assert data["sleep_hours"] == 6
    assert data["mood_score"] == -0.5

def test_extract_json_no_data():
    text = "Halo, saya RINA. Tidak ada data."
    data = _extract_json(text)
    assert data["sleep_hours"] is None
    assert data["mood_score"] is None

def test_detect_response_emotion():
    assert _detect_response_emotion("Wah seru banget!", {}) == "happy"
    assert _detect_response_emotion("Hmm, kedengarannya berat ya.", {}) == "concerned"
    assert _detect_response_emotion("Kamu hebat sekali bisa bertahan.", {}) == "encouraging"
    assert _detect_response_emotion("Oke, saya mengerti.", {}) == "neutral"
