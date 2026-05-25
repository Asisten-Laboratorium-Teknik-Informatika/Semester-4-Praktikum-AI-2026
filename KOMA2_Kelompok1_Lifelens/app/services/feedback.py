from __future__ import annotations

from typing import Any
from app.services.supabase_client import get_supabase_client

def record_feedback(message_id: str, score: int) -> dict[str, Any]:
    """
    Merekam feedback user terhadap pesan RINA.
    score: 1 (thumbs up), -1 (thumbs down), 0 (clear).
    """
    if score not in (1, -1, 0):
        raise ValueError("Score feedback harus berupa 1, -1, atau 0")
        
    client = get_supabase_client()
    
    try:
        response = client.table("conversation_texts").update(
            {"feedback_score": score}
        ).eq("id", message_id).execute()
        
        if not response.data:
            return {"success": False, "error": "Pesan tidak ditemukan"}
            
        return {"success": True, "data": response.data[0]}
    except Exception as exc:
        return {"success": False, "error": str(exc)}
