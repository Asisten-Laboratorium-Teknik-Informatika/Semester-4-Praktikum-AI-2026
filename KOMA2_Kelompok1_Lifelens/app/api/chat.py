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
import time
import traceback
from pathlib import Path
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from app.services.safety import check_crisis
from app.services.gemini import get_rina_response, stream_rina_response
from app.services.nlp import extract_nlp_features
from app.services.features import update_daily_features, get_7day_features
from app.services.prediction import predict_burnout
from app.services.trend_analysis import generate_recommendations

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHAT_LOG_DIR = PROJECT_ROOT / "logs"
CHAT_LOG_FILE = CHAT_LOG_DIR / "chat.log"


def _log_chat(trace_id: str, message: str):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} [CHAT:{trace_id}] {message}"
    print(line, flush=True)
    try:
        CHAT_LOG_DIR.mkdir(parents=True, exist_ok=True)
        with CHAT_LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


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


async def _process_message(user_id: str, message: str, trace_id: str | None = None) -> dict[str, Any]:
    """
    Pipeline utama: proses satu pesan user dan hasilkan respons lengkap.
    """
    trace_id = trace_id or f"chat-{int(time.time() * 1000):x}"
    started = time.perf_counter()
    _log_chat(trace_id, f"process start user={user_id} chars={len(message)}")

    # 1. SAFETY CHECK — PALING PERTAMA, tidak boleh dilewati
    t_step = time.perf_counter()
    crisis = check_crisis(message)
    _log_chat(trace_id, f"safety done elapsed={(time.perf_counter() - t_step) * 1000:.0f}ms crisis={bool(crisis)}")
    if crisis and crisis.get("stop"):
        _log_chat(trace_id, f"process stop crisis total={(time.perf_counter() - started) * 1000:.0f}ms")
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
    t_step = time.perf_counter()
    current_features = get_7day_features(user_id)
    current_risk = "LOW"
    if current_features.get("days", 0) >= 1:
        try:
            pred = predict_burnout(current_features.get("averages", {}), user_text=message)
            current_risk = pred.get("risk_level", "LOW")
        except Exception:
            pass
    _log_chat(trace_id, f"risk precheck done elapsed={(time.perf_counter() - t_step) * 1000:.0f}ms risk={current_risk}")

    # 3. Kirim ke Gemini RINA + dapatkan respons
    t_step = time.perf_counter()
    rina_text, extracted_json = await get_rina_response(
        user_id, message, risk_level=current_risk, trace_id=trace_id
    )
    _log_chat(trace_id, f"rina response ready elapsed={(time.perf_counter() - t_step) * 1000:.0f}ms chars={len(rina_text)} emotion={extracted_json.get('emotion_tone', 'neutral')}")

    # 4. NLP Feature Extraction dari pesan user
    t_step = time.perf_counter()
    nlp_features = await extract_nlp_features(message)
    _log_chat(trace_id, f"nlp done elapsed={(time.perf_counter() - t_step) * 1000:.0f}ms sentiment={nlp_features.get('sentiment_label')}")

    # 5. Update feature store dengan data gabungan (NLP + Gemini extraction)
    t_step = time.perf_counter()
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
    _log_chat(trace_id, f"features update done elapsed={(time.perf_counter() - t_step) * 1000:.0f}ms days={updated.get('days', 0)}")

    # 6. Prediksi burnout (ML jika data cukup, rule-based jika tidak)
    t_step = time.perf_counter()
    risk_result = {"risk_level": "LOW", "factors": []}
    if updated.get("days", 0) >= 1:
        try:
            prediction_input = updated.get("averages", {})
            prediction_input["sentiment_slope_7d"] = updated.get("sentiment_slope_7d", 0)
            risk_result = predict_burnout(prediction_input, user_text=message)
        except Exception:
            pass
    _log_chat(trace_id, f"prediction done elapsed={(time.perf_counter() - t_step) * 1000:.0f}ms risk={risk_result.get('risk_level', 'LOW')}")

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

    response_payload = {
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
    _log_chat(trace_id, f"process done total={(time.perf_counter() - started) * 1000:.0f}ms response_chars={len(rina_text)}")
    return response_payload


# ─── HTTP Endpoint ───────────────────────────────────────────────────────────

@router.post("/", response_model=ChatResponse)
async def chat_http(payload: ChatRequest) -> dict[str, Any]:
    """HTTP POST endpoint untuk chat. Cocok untuk demo dan testing."""
    trace_id = f"http-{int(time.time() * 1000):x}"
    result = await _process_message(payload.user_id, payload.message, trace_id=trace_id)
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


async def _send_stream_piece(websocket: WebSocket, state: dict[str, str], text: str, emotion: str) -> None:
    """Send real Gemini stream text while preserving ||| bubble breaks."""
    state["buffer"] = state.get("buffer", "") + text

    while "|||" in state["buffer"]:
        before, after = state["buffer"].split("|||", 1)
        if before:
            await websocket.send_json({
                "type": "chunk",
                "text": before,
                "is_bubble_break": False,
                "emotion": emotion,
            })
        await websocket.send_json({
            "type": "chunk",
            "text": "",
            "is_bubble_break": True,
            "emotion": emotion,
        })
        state["buffer"] = after

    # Keep two trailing chars so a delimiter split across chunks still works.
    if len(state["buffer"]) > 2:
        send_text = state["buffer"][:-2]
        state["buffer"] = state["buffer"][-2:]
        if send_text:
            await websocket.send_json({
                "type": "chunk",
                "text": send_text,
                "is_bubble_break": False,
                "emotion": emotion,
            })


async def _flush_stream_piece(websocket: WebSocket, state: dict[str, str], emotion: str) -> None:
    remaining = state.get("buffer", "")
    state["buffer"] = ""
    if remaining:
        await websocket.send_json({
            "type": "chunk",
            "text": remaining,
            "is_bubble_break": False,
            "emotion": emotion,
        })


async def _run_analysis_after_reply(
    user_id: str,
    message: str,
    rina_text: str,
    extracted_json: dict[str, Any],
    websocket: WebSocket,
    trace_id: str,
) -> None:
    """Run NLP/prediction after the visible RINA reply has already streamed."""
    started = time.perf_counter()
    try:
        t_step = time.perf_counter()
        nlp_features = await extract_nlp_features(message)
        _log_chat(trace_id, f"post-reply nlp done elapsed={(time.perf_counter() - t_step) * 1000:.0f}ms sentiment={nlp_features.get('sentiment_label')}")

        t_step = time.perf_counter()
        combined_features: dict[str, float] = {}
        for key in ["sentiment_score", "cognitive_distortion_score"]:
            if key in nlp_features:
                combined_features[key] = float(nlp_features[key])

        nlp_mappings = {
            "absolutist_language_count": "absolutist_count",
            "helplessness_phrases_count": "helplessness_count",
            "keyword_count": "keyword_count",
            "message_length": "message_avg_length",
        }
        for nlp_key, feat_key in nlp_mappings.items():
            if nlp_key in nlp_features:
                combined_features[feat_key] = float(nlp_features[nlp_key])

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
        _log_chat(trace_id, f"post-reply features update done elapsed={(time.perf_counter() - t_step) * 1000:.0f}ms days={updated.get('days', 0)}")

        t_step = time.perf_counter()
        risk_result = {"risk_level": "LOW", "factors": []}
        if updated.get("days", 0) >= 1:
            try:
                prediction_input = updated.get("averages", {})
                prediction_input["sentiment_slope_7d"] = updated.get("sentiment_slope_7d", 0)
                risk_result = predict_burnout(prediction_input, user_text=message)
            except Exception:
                pass
        _log_chat(trace_id, f"post-reply prediction done elapsed={(time.perf_counter() - t_step) * 1000:.0f}ms risk={risk_result.get('risk_level', 'LOW')}")

        risk_level = risk_result.get("risk_level", "LOW")
        top_factors = risk_result.get("factors", [])
        recommendations = generate_recommendations(risk_level, top_factors)

        await websocket.send_json({
            "type": "risk_update",
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
        })
        _log_chat(trace_id, f"post-reply risk_update sent total={(time.perf_counter() - started) * 1000:.0f}ms response_chars={len(rina_text)}")
    except Exception as exc:
        _log_chat(trace_id, f"post-reply analysis failed: {exc}")
        traceback.print_exc()


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
                trace_id = f"ws-{int(time.time() * 1000):x}"
                analysis_payload = None
                _log_chat(trace_id, f"ws message received user={user_id} chars={len(message)}")
                # Signal: mulai streaming
                await websocket.send_json({"type": "stream_start"})
                _log_chat(trace_id, "ws stream_start sent")

                fast_started = time.perf_counter()
                crisis = check_crisis(message)
                streamed_live = False
                if crisis and crisis.get("stop"):
                    full_text = crisis["response"]
                    emotion = "concerned"
                    is_crisis = True
                    _log_chat(trace_id, "ws fast crisis response ready")
                else:
                    _log_chat(trace_id, "ws real gemini stream start")
                    rina_text = ""
                    extracted_json = {}
                    emotion = "neutral"
                    stream_state = {"buffer": ""}
                    async for event in stream_rina_response(
                        user_id=user_id,
                        message=message,
                        risk_level="LOW",
                        trace_id=trace_id,
                    ):
                        if event.get("type") == "text":
                            await _send_stream_piece(websocket, stream_state, event.get("text", ""), emotion)
                        elif event.get("type") == "done":
                            rina_text = event.get("text", "")
                            extracted_json = event.get("data", {})

                    emotion = extracted_json.get("emotion_tone", "neutral")
                    await _flush_stream_piece(websocket, stream_state, emotion)
                    is_crisis = False
                    if crisis and not crisis.get("stop"):
                        rina_text += f" ||| {crisis['response']}"
                        await websocket.send_json({
                            "type": "chunk",
                            "text": "",
                            "is_bubble_break": True,
                            "emotion": "concerned",
                        })
                        await websocket.send_json({
                            "type": "chunk",
                            "text": crisis["response"],
                            "is_bubble_break": False,
                            "emotion": "concerned",
                        })
                        is_crisis = True
                        extracted_json["emotion_tone"] = "concerned"

                    full_text = rina_text
                    emotion = extracted_json.get("emotion_tone", emotion)
                    streamed_live = True
                    analysis_payload = {
                        "user_id": user_id,
                        "message": message,
                        "rina_text": rina_text,
                        "extracted_json": extracted_json,
                        "websocket": websocket,
                        "trace_id": trace_id,
                    }
                    _log_chat(trace_id, f"ws fast ai response ready elapsed={(time.perf_counter() - fast_started) * 1000:.0f}ms chars={len(full_text)} emotion={emotion}")

                # Streaming: kirim per kata dengan delay natural
                if not streamed_live:
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
                    "risk_level": None,
                    "top_factors": [],
                    "recommendations": [],
                    "extracted_data": {},
                    "is_crisis": is_crisis,
                })
                _log_chat(trace_id, "ws stream_end sent")
                if analysis_payload is not None:
                    asyncio.create_task(_run_analysis_after_reply(**analysis_payload))
                    _log_chat(trace_id, "ws post-reply analysis running")

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
