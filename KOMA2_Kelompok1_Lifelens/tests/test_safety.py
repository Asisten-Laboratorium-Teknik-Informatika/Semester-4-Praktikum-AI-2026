from app.services.safety import check_crisis


def test_crisis_detected():
    result = check_crisis("ingin mati rasanya")
    assert result is not None
    assert result["stop"] is True


def test_normal_message_is_safe():
    result = check_crisis("hari ini capek banget")
    assert result is None
