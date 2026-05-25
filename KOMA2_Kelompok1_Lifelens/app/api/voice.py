"""
Voice API v2 — TTS + STT endpoints.

Endpoints:
  POST /tts         — Generate speech from text (multi-language)
  POST /stt         — Speech-to-text via faster-whisper (jika tersedia)
  GET  /voices      — List available voice options
"""

import asyncio
import io
import time
import uuid
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

from app.services.tts import generate_speech, get_audio_media_type, get_voice_options, warmup_voice_clone

router = APIRouter()

# ─── TTS ─────────────────────────────────────────────────────────────────────

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    emotion: str = Field(default="neutral")
    voice_lang: str = Field(default="id", description="id | ja | en | ko")
    require_clone: bool = Field(default=True)
    client_trace_id: str | None = Field(default=None, max_length=80)


@router.post("/tts")
async def text_to_speech(payload: TTSRequest):
    """Generate audio dari teks RINA. Support multi-language via voice_lang."""
    trace_id = payload.client_trace_id or uuid.uuid4().hex[:10]
    started = time.perf_counter()
    metrics: dict = {}

    audio_bytes = await generate_speech(
        payload.text,
        payload.emotion,
        payload.voice_lang,
        require_clone=payload.require_clone,
        debug_id=trace_id,
        metrics=metrics,
    )

    elapsed_ms = int((time.perf_counter() - started) * 1000)

    if audio_bytes is None:
        return JSONResponse(
            status_code=503,
            content={
                "error": "Gagal generate audio clone",
                "voice_lang": payload.voice_lang,
                "trace_id": trace_id,
                "metrics": metrics,
                "elapsed_ms": elapsed_ms,
            },
            headers={
                "X-TTS-Trace-Id": trace_id,
                "X-TTS-Elapsed-Ms": str(elapsed_ms),
                "X-TTS-Engine": str(metrics.get("engine", "unknown")),
                "X-TTS-Clone": str(metrics.get("clone", "failed")),
                "X-TTS-Cache": str(metrics.get("cache", "unknown")),
                "X-TTS-Source-Voice": str(metrics.get("source_voice", "")),
            },
        )

    content_type = get_audio_media_type(audio_bytes)
    ext = "wav" if content_type == "audio/wav" else "mp3"

    return Response(
        content=audio_bytes,
        media_type=content_type,
        headers={
            "Content-Disposition": f'inline; filename="rina.{ext}"',
            "X-TTS-Trace-Id": trace_id,
            "X-TTS-Elapsed-Ms": str(elapsed_ms),
            "X-TTS-Engine": str(metrics.get("engine", "unknown")),
            "X-TTS-Clone": str(metrics.get("clone", "unknown")),
            "X-TTS-Cache": str(metrics.get("cache", "unknown")),
            "X-TTS-Source-Voice": str(metrics.get("source_voice", "")),
        },
    )


# ─── VOICE OPTIONS ───────────────────────────────────────────────────────────

@router.get("/voices")
async def get_voices():
    """Return available voice options for frontend voice selector."""
    return {"voices": get_voice_options()}


@router.post("/warmup")
async def warmup_voices():
    """Preload clone model and cache tiny samples."""
    return {"status": "ok", "result": await warmup_voice_clone()}


# ─── STT (faster-whisper, optional) ─────────────────────────────────────────

_whisper_model = None


def _get_whisper_model():
    """Lazy-load faster-whisper model."""
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model

    try:
        from faster_whisper import WhisperModel
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"

        # small model — good balance of speed and accuracy
        _whisper_model = WhisperModel("small", device=device, compute_type=compute_type)
        print(f"[STT] faster-whisper loaded on {device}")
        return _whisper_model
    except ImportError:
        print("[STT] faster-whisper not available — use Web Speech API instead")
        return None
    except Exception as e:
        print(f"[STT] Error loading whisper: {e}")
        return None


@router.post("/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    """
    Transcribe audio ke teks Bahasa Indonesia.
    Gunakan faster-whisper jika tersedia, 404 jika tidak.
    """
    model = _get_whisper_model()
    if model is None:
        return {
            "error": "STT tidak tersedia di server. Gunakan Web Speech API di browser.",
            "fallback": "web_speech_api",
        }

    try:
        audio_bytes = await audio.read()

        # Save to temp file (faster-whisper needs file path)
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            segments, info = model.transcribe(
                tmp_path,
                language="id",
                beam_size=5,
            )
            transcript = " ".join([segment.text for segment in segments])
        finally:
            os.unlink(tmp_path)

        return {
            "transcript": transcript.strip(),
            "language": info.language if hasattr(info, 'language') else "id",
            "source": "faster_whisper",
        }

    except Exception as e:
        return {"error": f"Transcription gagal: {str(e)}"}


# ─── STT STATUS ──────────────────────────────────────────────────────────────

@router.get("/stt/status")
async def stt_status():
    """Cek apakah server-side STT tersedia."""
    model = _get_whisper_model()
    return {
        "available": model is not None,
        "engine": "faster_whisper" if model else "web_speech_api",
        "note": "Gunakan Web Speech API di browser jika server STT tidak tersedia",
    }
