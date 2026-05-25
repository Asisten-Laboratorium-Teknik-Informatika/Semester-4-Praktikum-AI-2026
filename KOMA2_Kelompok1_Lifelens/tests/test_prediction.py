from app.services.prediction import predict_burnout, rule_based_predict


def test_rule_based_high_risk():
    result = rule_based_predict(
        {
            "sleep_hours": 4,
            "workload_score": 9,
            "sentiment_slope_7d": -0.6,
            "recovery_score": 2,
            "social_withdrawal": True,
        }
    )

    assert result["risk_level"] == "HIGH"
    assert result["source"] == "rule_based"
    assert result["score"] >= 8


def test_predict_falls_back_when_ml_features_are_missing():
    result = predict_burnout(
        {
            "sleep_hours": 4,
            "workload_score": 9,
            "sentiment_slope_7d": -0.6,
            "recovery_score": 2,
            "social_withdrawal": True,
        }
    )

    assert result["risk_level"] == "HIGH"
    assert result["source"] == "rule_based"
