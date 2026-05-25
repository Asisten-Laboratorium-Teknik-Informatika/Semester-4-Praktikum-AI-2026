import os
import traceback
import asyncio
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.services.prediction import predict_burnout
from app.services.safety import check_crisis
from app.services.supabase_client import check_supabase_connection
from app.api.chat import router as chat_router
from app.api.dashboard import router as dashboard_router
from app.api.voice import router as voice_router


load_dotenv()


class MessageRequest(BaseModel):
    message: str = Field(..., min_length=1)


class PredictionRequest(BaseModel):
    features: dict[str, Any]


def _allowed_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,http://localhost:5000")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app = FastAPI(title="LifeLens API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_warmup_voice_clone():
    if os.getenv("LIFELENS_TTS_WARMUP", "1") == "0":
        return

    async def _warmup():
        try:
            from app.services.tts import warmup_voice_clone
            await warmup_voice_clone()
        except Exception as exc:
            print(f"[TTS warmup] skipped: {exc}")

    asyncio.create_task(_warmup())


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    print("Unhandled error:", repr(exc))
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "Server mengalami kesalahan. Tim backend dapat melihat detailnya di log.",
            "path": str(request.url.path),
        },
    )


# ─── Routers ─────────────────────────────────────────────────────────────────
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(voice_router, prefix="/api/voice", tags=["Voice"])


# ─── Standalone endpoints ────────────────────────────────────────────────────

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "1.0.0"}


@app.get("/health/supabase")
def supabase_health() -> dict[str, Any]:
    return check_supabase_connection()


@app.post("/safety/check")
def safety_check(payload: MessageRequest) -> dict[str, Any]:
    result = check_crisis(payload.message)
    return {"safe": result is None, "result": result}


@app.post("/predict")
def predict(payload: PredictionRequest) -> dict[str, Any]:
    return predict_burnout(payload.features)


# ─── Consent & History endpoints (spec 02_system_architecture.md) ────────────

class ConsentRequest(BaseModel):
    user_id: str
    consent_given: bool


@app.post("/api/consent")
def set_consent(payload: ConsentRequest) -> dict[str, Any]:
    """Simpan pilihan consent user."""
    # Untuk MVP: simpan di memory, nanti migrate ke Supabase
    from datetime import datetime
    return {
        "status": "ok",
        "user_id": payload.user_id,
        "consent_given": payload.consent_given,
        "timestamp": datetime.now().isoformat(),
        "note": "Jika consent=true, teks percakapan akan disimpan terenkripsi. "
                "Jika consent=false, hanya data statistik yang disimpan.",
    }


@app.get("/api/history/{user_id}")
def get_history(user_id: str) -> dict[str, Any]:
    """Ambil riwayat sesi dan risk timeline user."""
    from app.services.features import get_7day_features

    features = get_7day_features(user_id)
    days = features.get("days", 0)

    if days == 0:
        return {
            "status": "no_data",
            "sessions": [],
            "risk_timeline": [],
        }

    return {
        "status": "ok",
        "sessions": [{
            "date": "today",
            "days_tracked": days,
            "averages": features.get("averages", {}),
        }],
        "risk_timeline": [],
        "note": "Timeline akan berisi data risk level per hari setelah data cukup.",
    }

