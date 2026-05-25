"""
Chat API — HTTP dan WebSocket endpoints untuk percakapan dengan RINA.

Flow:
  User message → Safety check → Gemini RINA → NLP extraction
  → Feature update → Prediction → Response ke user
"""

from __future__ import annotations

import asyncio
import json
import random
import traceback
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from app.services.safety import check_crisis
from app.services.gemini import get_rina_response
from app.services.nlp import extract_nlp_features
from app.services.features import update_daily_features, get_7day_features
from app.services.prediction import predict_burnout
from app.services.trend_analysis import generate_recommendations

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    user_id: str = Field(default="anonymous")


class ChatResponse(BaseModel):
    response: str
    emotion: str = "neutral"
    risk_level: str | None = None
    top_factors: list[str] = []
    recommendations: list[dict] = []
    extracted_data: dict = {}
    is_crisis: bool = False


async def _process_message(user_id: str, message: str) -> dict[str, Any]:
    """
    Pipeline utama: proses satu pesan user dan hasilkan respons lengkap.
    """
    # 1. SAFETY CHECK — PALING PERTAMA, tidak boleh dilewati
    crisis = check_crisis(message)
    if crisis and crisis.get("stop"):
        return {
            "response": crisis["response"],
            "emotion": "concerned",
            "is_crisis": True,
            "hotline": crisis.get("hotline", {}),
            "risk_level": "HIGH",
            "top_factors": [],
            "recommendations": [],
            "extracted_data": {},
        }

    # 2. Ambil risk level saat ini untuk tone adjustment RINA
    current_features = get_7day_features(user_id)
    current_risk = "LOW"
    if current_features.get("days", 0) >= 1:
        try:
            pred = predict_burnout(current_features.get("averages", {}), user_text=message)
            current_risk = pred.get("risk_level", "LOW")
        except Exception:
            pass

    # 3. Kirim ke Gemini RINA + dapatkan respons
    rina_text, extracted_json = await get_rina_response(
        user_id, message, risk_level=current_risk
    )

    # 4. NLP Feature Extraction dari pesan user
    nlp_features = await extract_nlp_features(message)

    # 5. Update feature store dengan data gabungan (NLP + Gemini extraction)
    combined_features: dict[str, float] = {}
    # NLP features
    for key in ["sentiment_score", "cognitive_distortion_score"]:
        if key in nlp_features:
            combined_features[key] = float(nlp_features[key])

    # NLP counts
    nlp_mappings = {
        "absolutist_language_count": "absolutist_count",
        "helplessness_phrases_count": "helplessness_count",
        "keyword_count": "keyword_count",
        "message_length": "message_avg_length",
    }
    for nlp_key, feat_key in nlp_mappings.items():
        if nlp_key in nlp_features:
            combined_features[feat_key] = float(nlp_features[nlp_key])

    # Tambahkan data dari Gemini extraction
    for key in ["sleep_hours", "sleep_quality", "workload_score", "mood_score", "social_score", "recovery_score"]:
        val = extracted_json.get(key)
        if val is not None:
            try:
                combined_features[key] = float(val)
            except (TypeError, ValueError):
                pass

    if combined_features:
        updated = update_daily_features(user_id, combined_features)
    else:
        updated = get_7day_features(user_id)

    # 6. Prediksi burnout (ML jika data cukup, rule-based jika tidak)
    risk_result = {"risk_level": "LOW", "factors": []}
    if updated.get("days", 0) >= 1:
        try:
            prediction_input = updated.get("averages", {})
            prediction_input["sentiment_slope_7d"] = updated.get("sentiment_slope_7d", 0)
            risk_result = predict_burnout(prediction_input, user_text=message)
        except Exception:
            pass

    # 7. Generate recommendations
    risk_level = risk_result.get("risk_level", "LOW")
    top_factors = risk_result.get("factors", [])
    recommendations = generate_recommendations(risk_level, top_factors)

    # 8. Jika crisis detected (medium level), tambahkan sebagai bubble terpisah
    is_crisis = False
    if crisis and not crisis.get("stop"):
        # Medium crisis — bubble terpisah, tone concerned
        rina_text += f" ||| {crisis['response']}"
        is_crisis = True
        # Override emotion ke concerned untuk medium crisis
        extracted_json["emotion_tone"] = "concerned"

    return {
        "response": rina_text,
        "emotion": extracted_json.get("emotion_tone", "neutral"),
        "risk_level": risk_level,
        "top_factors": top_factors,
        "recommendations": recommendations,
        "extracted_data": {
            "nlp": {
                "sentiment": nlp_features.get("sentiment_label"),
                "sentiment_score": nlp_features.get("sentiment_score"),
                "dominant_domain": nlp_features.get("dominant_domain"),
                "cognitive_distortion": nlp_features.get("cognitive_distortion_score"),
            },
            "gemini": {
                k: extracted_json.get(k)
                for k in ["sleep_hours", "mood_score", "workload_score", "emotion_tone", "keywords"]
            },
            "features_tracked_days": updated.get("days", 0),
        },
        "is_crisis": is_crisis,
    }


# ─── HTTP Endpoint ───────────────────────────────────────────────────────────

@router.post("/", response_model=ChatResponse)
async def chat_http(payload: ChatRequest) -> dict[str, Any]:
    """HTTP POST endpoint untuk chat. Cocok untuk demo dan testing."""
    result = await _process_message(payload.user_id, payload.message)
    return result


# ─── SSE Streaming Endpoint ──────────────────────────────────────────────────

def _split_sentences(text: str) -> list[str]:
    """Pecah teks menjadi kalimat-kalimat untuk streaming."""
    import re
    # Split by ||| delimiter first (RINA bubble separator)
    bubbles = [b.strip() for b in text.split("|||") if b.strip()]

    sentences = []
    for bubble in bubbles:
        # Split per kalimat dalam bubble
        parts = re.split(r'(?<=[.!?…])\s+', bubble)
        parts = [p.strip() for p in parts if p.strip()]
        if parts:
            sentences.extend(parts)
        else:
            sentences.append(bubble)
        # Add bubble separator marker
        sentences.append("|||")

    # Remove trailing separator
    if sentences and sentences[-1] == "|||":
        sentences.pop()

    return sentences


# ─── WebSocket Endpoint ──────────────────────────────────────────────────────

@router.websocket("/ws/{user_id}")
async def chat_websocket(websocket: WebSocket, user_id: str) -> None:
    """
    WebSocket endpoint untuk real-time chat dengan streaming.

    Client mengirim: {"message": "..."}
    Server mengirim secara berurutan:
      1. {"type": "stream_start"} — mulai streaming
      2. {"type": "chunk", "text": "...", "is_bubble_break": false} — per kalimat
      3. {"type": "stream_end", ...} — selesai, kirim metadata lengkap
    """
    await websocket.accept()
    print(f"WebSocket connected: {user_id}")

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Format JSON tidak valid"})
                continue

            message = data.get("message", "").strip()
            if not message:
                await websocket.send_json({"type": "error", "message": "Pesan kosong"})
                continue

            try:
                # Signal: mulai streaming
                await websocket.send_json({"type": "stream_start"})

                # Proses pesan
                result = await _process_message(user_id, message)
                full_text = result.get("response", "")
                emotion = result.get("emotion", "neutral")
                is_crisis = result.get("is_crisis", False)

                # Streaming: kirim per kata dengan delay natural
                sentences = _split_sentences(full_text)

                for sentence in sentences:
                    if sentence == "|||":
                        # Bubble break — jeda "thinking" lebih lama
                        await asyncio.sleep(0.6 + random.random() * 0.6)
                        await websocket.send_json({
                            "type": "chunk",
                            "text": "",
                            "is_bubble_break": True,
                            "emotion": emotion,
                        })
                        await asyncio.sleep(0.3 + random.random() * 0.3)
                    else:
                        # Kirim per kata dengan timing natural
                        words = sentence.split()
                        for i, word in enumerate(words):
                            # Tambah spasi kecuali kata pertama
                            text_chunk = word if i == 0 else " " + word
                            await websocket.send_json({
                                "type": "chunk",
                                "text": text_chunk,
                                "is_bubble_break": False,
                                "emotion": emotion,
                            })

                            # Delay natural per kata
                            base = 0.04 + random.random() * 0.04  # 40-80ms base
                            # Kata panjang = lebih lambat
                            if len(word) > 6:
                                base += 0.02
                            # Setelah koma = jeda mikir
                            if word.endswith(",") or word.endswith("..."):
                                base += 0.15 + random.random() * 0.15
                            # Setelah titik/tanya = jeda lebih panjang
                            elif word.endswith(".") or word.endswith("?") or word.endswith("!"):
                                base += 0.1 + random.random() * 0.1
                            # Filler words = sedikit lebih lambat (kayak mikir)
                            if word.lower().rstrip(".,!?") in ("hmm", "eh", "duh", "wah", "btw", "sih"):
                                base += 0.08

                            await asyncio.sleep(base)

                # Signal: streaming selesai + metadata
                msg_type = "crisis" if is_crisis else "message"
                await websocket.send_json({
                    "type": "stream_end",
                    "msg_type": msg_type,
                    "response": full_text,
                    "emotion": emotion,
                    "risk_level": result.get("risk_level"),
                    "top_factors": result.get("top_factors", []),
                    "recommendations": result.get("recommendations", []),
                    "extracted_data": result.get("extracted_data", {}),
                    "is_crisis": is_crisis,
                })

            except WebSocketDisconnect:
                raise  # Let outer handler catch it
            except Exception as exc:
                traceback.print_exc()
                try:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Terjadi kesalahan: {exc}",
                    })
                except Exception:
                    break  # WS sudah disconnect, keluar loop

    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {user_id}")

