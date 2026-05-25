import re
from typing import Dict


BURNOUT_DOMAIN_KEYWORDS = {
    "work_stress": [
        "deadline", "lembur", "overtime", "meeting", "atasan", "bos",
        "target", "kpi", "presentasi", "laporan", "proyek", "klien",
        "kerja", "kantor", "tugas", "beban", "tekanan",
    ],
    "exhaustion": [
        "capek", "lelah", "kelelahan", "exhausted", "tired", "burnout",
        "drain", "habis", "energi", "loyo", "lemas",
    ],
    "sleep_problems": [
        "insomnia", "susah tidur", "kurang tidur", "begadang",
        "tidak bisa tidur", "tidur sebentar", "ngantuk",
    ],
    "social_withdrawal": [
        "sendirian", "menyendiri", "tidak mau ketemu", "males keluar",
        "isolasi", "menghindar", "tidak mood",
    ],
    "motivation_loss": [
        "tidak semangat", "males", "tidak bergairah", "bosan",
        "jenuh", "apatis", "tidak peduli", "percuma",
    ],
}

ABSOLUTIST_WORDS = [
    "selalu", "tidak pernah", "semua orang", "tidak ada yang",
    "semuanya", "tidak ada satupun", "pasti", "mustahil",
]

HELPLESSNESS_PHRASES = [
    "mau apa lagi", "percuma", "tidak bisa", "tidak mungkin",
    "sudah useless", "tidak ada gunanya", "untuk apa",
]

POSITIVE_WORDS = [
    "senang", "lega", "baik", "bagus", "semangat", "tenang",
    "terbantu", "bersyukur", "happy", "great",
]

NEGATIVE_WORDS = [
    "lelah", "capek", "stres", "stress", "sedih", "cemas",
    "takut", "marah", "pusing", "berat", "burnout", "susah",
]

_HF_API_URL = "https://api-inference.huggingface.co/models/mdhugol/indonesia-bert-sentiment-classification"
_hf_api_available = None  # None = belum dicoba, True/False = hasil


def _indobert_via_api(text: str) -> Dict:
    """
    Jalankan IndoBERT sentiment analysis via HF Inference API.
    Gratis untuk model publik. Ga perlu torch lokal.
    """
    global _hf_api_available
    
    import os
    import urllib.request
    import json as _json

    headers = {"Content-Type": "application/json"}
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"

    payload = _json.dumps({"inputs": text[:512]}).encode("utf-8")
    req = urllib.request.Request(_HF_API_URL, data=payload, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = _json.loads(resp.read().decode("utf-8"))
        
        # HF API returns [[{"label": "...", "score": ...}, ...]]
        if isinstance(result, list) and len(result) > 0:
            if isinstance(result[0], list):
                result = result[0]
            # Ambil label dengan score tertinggi
            top = max(result, key=lambda x: x.get("score", 0))
            
            raw_label = top["label"].upper()
            label_translation = {"LABEL_0": "positive", "LABEL_1": "neutral", "LABEL_2": "negative"}
            final_label = label_translation.get(raw_label, raw_label.lower())

            label_map = {"positive": 1.0, "neutral": 0.0, "negative": -1.0}
            base_score = label_map.get(final_label, 0.0)
            weighted_score = base_score * top["score"]

            _hf_api_available = True
            return {
                "sentiment_score": weighted_score,
                "sentiment_label": final_label,
                "confidence": top["score"],
                "source": "indobert_api",
            }
    except Exception as e:
        print(f"[NLP] IndoBERT API error: {e}")
        _hf_api_available = False

    return None


def _lexical_sentiment(text: str) -> Dict:
    """Fallback sentiment analysis menggunakan keyword matching."""
    text_lower = text.lower()
    positive_count = sum(1 for word in POSITIVE_WORDS if word in text_lower)
    negative_count = sum(1 for word in NEGATIVE_WORDS if word in text_lower)
    total = positive_count + negative_count

    if positive_count > negative_count:
        label = "positive"
        score = positive_count / total
    elif negative_count > positive_count:
        label = "negative"
        score = -(negative_count / total)
    else:
        label = "neutral"
        score = 0.0

    return {
        "sentiment_score": score,
        "sentiment_label": label,
        "confidence": abs(score) if total else 0.5,
        "source": "lexical_fallback",
    }


def analyze_sentiment(text: str) -> Dict:
    """
    Analisis sentimen: IndoBERT via HF Inference API → lexical fallback.
    """
    # Coba IndoBERT API (skip jika sudah gagal sebelumnya)
    if _hf_api_available is not False:
        result = _indobert_via_api(text)
        if result:
            return result

    # Fallback ke lexical
    return _lexical_sentiment(text)


def extract_domain_keywords(text: str) -> Dict:
    """
    Deteksi kata kunci yang berkaitan dengan dimensi burnout.
    """
    text_lower = text.lower()

    found = {}
    total_keywords = 0

    for domain, keywords in BURNOUT_DOMAIN_KEYWORDS.items():
        matches = [kw for kw in keywords if kw in text_lower]
        found[domain] = matches
        total_keywords += len(matches)

    return {
        "domain_keywords": found,
        "keyword_count": total_keywords,
        "dominant_domain": max(found, key=lambda k: len(found[k])) if total_keywords > 0 else None,
    }


def detect_cognitive_patterns(text: str) -> Dict:
    """
    Deteksi pola bahasa yang mengindikasikan distorsi kognitif.
    """
    text_lower = text.lower()

    absolutist_count = sum(1 for word in ABSOLUTIST_WORDS if word in text_lower)
    helplessness_count = sum(1 for phrase in HELPLESSNESS_PHRASES if phrase in text_lower)

    return {
        "absolutist_language_count": absolutist_count,
        "helplessness_phrases_count": helplessness_count,
        "cognitive_distortion_score": min((absolutist_count + helplessness_count * 1.5) / 5, 1.0),
    }


def compute_message_features(text: str) -> Dict:
    """
    Fitur dari karakteristik pesan itu sendiri.
    """
    words = text.split()
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    return {
        "message_length": len(words),
        "avg_sentence_length": len(words) / max(len(sentences), 1) if sentences else len(words),
        "question_count": text.count("?"),
        "exclamation_count": text.count("!"),
        "is_very_short": len(words) < 5,
        "is_long_disclosure": len(words) > 50,
    }


# ─── ADAPTIVE LANGUAGE MATCHING ──────────────────────────────────────────────

GAUL_MARKERS = [
    "gw", "gue", "lu", "lo", "bgt", "banget", "bro", "sis", "bestie",
    "literally", "ngl", "tbh", "wkwk", "haha", "dong", "sih", "mah",
    "anjir", "anjay", "cuy", "guys", "ygy", "ngab", "bet",
]

FORMAL_MARKERS = [
    "saya", "anda", "bapak", "ibu", "terima kasih", "mohon", "kiranya",
    "sekiranya", "dengan hormat", "berkenan",
]

ENGLISH_MARKERS = [
    "i'm", "i am", "feeling", "work", "deadline", "overwhelmed",
    "stress", "burned out", "can't", "don't", "really", "actually",
    "honestly", "basically", "literally", "productive",
]

SINGKAT_PATTERN = re.compile(r"^.{1,25}$")  # Pesan sangat pendek


def detect_language_style(text: str) -> Dict:
    """
    Deteksi gaya bahasa user: formal, santai, gaul, campur_inggris, atau singkat.
    Digunakan supaya respons RINA bisa menyesuaikan.
    """
    text_lower = text.lower()
    words = text_lower.split()

    gaul_count = sum(1 for w in words if w in GAUL_MARKERS)
    formal_count = sum(1 for m in FORMAL_MARKERS if m in text_lower)
    english_count = sum(1 for m in ENGLISH_MARKERS if m in text_lower)

    total_words = len(words) or 1

    # Scoring
    gaul_ratio = gaul_count / total_words
    english_ratio = english_count / total_words

    if len(text.strip()) <= 25 and total_words <= 6:
        style = "singkat"
    elif formal_count >= 2 or (formal_count >= 1 and "saya" in text_lower):
        style = "formal"
    elif gaul_ratio >= 0.15 or gaul_count >= 3:
        style = "gaul"
    elif english_ratio >= 0.2 or english_count >= 3:
        style = "campur_inggris"
    else:
        style = "santai"

    return {
        "language_style": style,
        "gaul_markers_found": gaul_count,
        "formal_markers_found": formal_count,
        "english_markers_found": english_count,
    }


async def extract_nlp_features(text: str) -> Dict:
    """
    Main function: ekstrak semua fitur NLP dari satu pesan.
    Dipanggil dari chat endpoint setelah terima pesan user.
    """
    sentiment = analyze_sentiment(text)
    keywords = extract_domain_keywords(text)
    cognitive = detect_cognitive_patterns(text)
    message_feat = compute_message_features(text)
    language = detect_language_style(text)

    return {
        **sentiment,
        **keywords,
        **cognitive,
        **message_feat,
        **language,
        "raw_text": text,
    }

