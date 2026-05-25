from __future__ import annotations

import re
from typing import Any


# ─── HIGH RISK: STOP proses, tampilkan emergency UI ─────────────────────────
CRISIS_PHRASES_HIGH = [
    "ingin mati",
    "pengen mati",
    "mau mati",
    "bunuh diri",
    "mengakhiri hidup",
    "akhiri hidup",
    "tidak ingin hidup",
    "ga mau hidup",
    "gak mau hidup",
    "nggak mau hidup",
    "tidak kuat hidup",
    "lebih baik mati",
    "menyakiti diri",
    "melukai diri",
    "silet tangan",
    "minum racun",
    "overdosis",
    "loncat dari",
    "gantung diri",
    "hilang selamanya",
    "tidak ada gunanya hidup",
    "lebih baik tidak ada",
    "capek hidup",
    "tidak mau hidup",
    "self harm",
]

# ─── MEDIUM RISK: masih proses, tapi tambahkan empati + referral ─────────────
CRISIS_PHRASES_MEDIUM = [
    "sangat lelah sekali",
    "tidak bisa lanjut",
    "ga bisa lanjut",
    "gak bisa lanjut",
    "menyerah",
    "nyerah",
    "tidak ada harapan",
    "ga ada harapan",
    "tidak ada yang peduli",
    "ga ada yang peduli",
    "sudah tidak kuat",
    "udah ga kuat",
    "percuma",
    "sia-sia",
    "hampa",
    "kosong rasanya",
]

CRISIS_RESPONSE_HIGH = (
    "Aku dengar kamu. Ini terdengar sangat berat.\n\n"
    "Kamu tidak harus menanggung ini sendirian. "
    "Ada orang yang terlatih dan siap mendengarkan 24 jam:\n\n"
    "Into The Light Indonesia: 119 ext 8\n"
    "Sejiwa Foundation: 119 ext 8\n\n"
    "Kamu berarti. Tolong hubungi mereka ya."
)

CRISIS_RESPONSE_MEDIUM = (
    "Kedengarannya kamu sedang berat banget. Aku di sini.\n"
    "Kalau butuh bicara sama seseorang yang terlatih, "
    "hubungi Into The Light Indonesia: 119 ext 8."
)

HOTLINES = {
    "indonesia_emergency": "119",
    "sejiwa": "119 ext 8",
    "into_the_light": "Into The Light Indonesia: https://www.intothelightid.org",
}


def _normalize_text(text: str) -> str:
    lowered = text.lower()
    normalized = re.sub(r"\s+", " ", lowered).strip()
    return normalized


def check_crisis(message: str) -> dict[str, Any] | None:
    """
    Cek keyword krisis SEBELUM proses apapun.

    Return:
      - None jika aman
      - dict dengan stop=True jika HIGH (hentikan pipeline)
      - dict dengan stop=False jika MEDIUM (lanjut, tapi tambah empati)
    """
    if not message or not message.strip():
        return None

    normalized = _normalize_text(message)

    # HIGH RISK — cek pertama, STOP semua proses
    matched_high = next(
        (phrase for phrase in CRISIS_PHRASES_HIGH if phrase in normalized), None
    )
    if matched_high is not None:
        return {
            "response": CRISIS_RESPONSE_HIGH,
            "hotline": HOTLINES,
            "matched_phrase": matched_high,
            "level": "high",
            "stop": True,
        }

    # MEDIUM RISK — lanjut proses, tapi tambahkan catatan empati
    matched_medium = next(
        (phrase for phrase in CRISIS_PHRASES_MEDIUM if phrase in normalized), None
    )
    if matched_medium is not None:
        return {
            "response": CRISIS_RESPONSE_MEDIUM,
            "hotline": HOTLINES,
            "matched_phrase": matched_medium,
            "level": "medium",
            "stop": False,
        }

    return None  # Aman

