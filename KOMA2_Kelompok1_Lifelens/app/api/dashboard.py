"""
Dashboard API — Endpoint untuk menampilkan data insight user.

Menyediakan: risk level, top factors, trend 7 hari, dan rekomendasi.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.services.features import get_7day_features
from app.services.prediction import predict_burnout
from app.services.trend_analysis import predict_next_week_trend, generate_recommendations

router = APIRouter()


@router.get("/{user_id}")
async def get_dashboard(user_id: str) -> dict[str, Any]:
    """
    Ambil data dashboard lengkap untuk satu user.
    
    Return:
      - risk_level: LOW / MEDIUM / HIGH
      - top_factors: alasan utama risiko
      - trend: prediksi tren minggu depan
      - recommendations: saran yang dipersonalisasi
      - features: data harian yang sudah dikumpulkan
    """
    features_summary = get_7day_features(user_id)
    days_tracked = features_summary.get("days", 0)

    if days_tracked == 0:
        return {
            "status": "no_data",
            "message": "Belum ada data percakapan. Mulai ngobrol dengan RINA dulu ya!",
            "risk_level": None,
            "top_factors": [],
            "trend": None,
            "recommendations": [],
            "days_tracked": 0,
        }

    # Prediksi risiko burnout
    averages = features_summary.get("averages", {})
    averages["sentiment_slope_7d"] = features_summary.get("sentiment_slope_7d", 0)
    risk_result = predict_burnout(averages)
    risk_level = risk_result.get("risk_level", "LOW")
    top_factors = risk_result.get("factors", [])

    # Trend analysis (butuh minimal 5 hari)
    trend = None
    if days_tracked >= 5:
        # Buat daily_features list dari averages (simplified)
        trend = {"prediction": "insufficient_data", "confidence": "low"}

    # Rekomendasi berdasarkan risiko
    recommendations = generate_recommendations(risk_level, top_factors)

    return {
        "status": "ok",
        "risk_level": risk_level,
        "score": risk_result.get("score"),
        "top_factors": top_factors,
        "trend": trend,
        "recommendations": recommendations,
        "days_tracked": days_tracked,
        "averages": averages,
        "disclaimer": "Ini adalah screening tool, BUKAN diagnosis medis resmi.",
    }
