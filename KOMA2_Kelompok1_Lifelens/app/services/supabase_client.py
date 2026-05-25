from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv


load_dotenv()


def get_supabase_client() -> Any:
    try:
        from supabase import create_client
    except ImportError as exc:
        raise RuntimeError("Package supabase belum terinstall.") from exc

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL atau SUPABASE_SERVICE_KEY belum diatur.")
    return create_client(url, key)


def check_supabase_connection() -> dict[str, Any]:
    try:
        client = get_supabase_client()
        # Lightweight request. It validates credentials without assuming project tables exist.
        client.auth.get_session()
        return {"status": "ok", "configured": True}
    except Exception as exc:
        return {"status": "error", "configured": False, "detail": str(exc)}
