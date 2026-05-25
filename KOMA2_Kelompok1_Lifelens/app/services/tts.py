"""
Voice TTS Service v2 — Hybrid Multi-Engine

Arsitektur:
  ID  → Chatterbox voice clone dari 6096144127445966044.oga
  JP  → Chatterbox voice clone dari Hu Tao Japanese OGG
  fallback → edge-tts / gTTS jika clone gagal

Translation: Argos Translate (offline) → fallback: skip (pakai teks asli)
Emotion: SSML prosody mapping per preset (Edge-TTS) / Punctuation (Chatterbox)
"""

import asyncio
import hashlib
import io
import os
import re
import threading
import time
from pathlib import Path
from typing import Optional

# gTTS — fallback TTS yang stabil
try:
    from gtts import gTTS
    _gtts_available = True
except ImportError:
    _gtts_available = False

import edge_tts

# ─── TRY IMPORT OPTIONAL DEPS ───────────────────────────────────────────────

_kokoro_available = False
_kokoro_pipeline = None
try:
    from kokoro import KPipeline
    _kokoro_available = True
except ImportError:
    pass

_argos_available = False
try:
    import argostranslate.translate
    import argostranslate.package
    _argos_available = True
except ImportError:
    pass

_chatterbox_available = False
_chatterbox_turbo_available = False
_chatterbox_import_attempted = False
_chatterbox_vc_available = False
_chatterbox_vc_import_attempted = False
_chatterbox_model = None
_chatterbox_vc_model = None
_chatterbox_is_turbo = False
_chatterbox_condition_ref = None
_chatterbox_vc_target_ref = None
_chatterbox_lock = threading.Lock()
torch = None
torchaudio = None
ChatterboxTTS = None
ChatterboxTurboTTS = None
ChatterboxVC = None


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = PROJECT_ROOT.parent
VOICE_REF_DIR = PROJECT_ROOT / "ml_models" / "voice_ref"
AUDIO_CACHE_DIR = PROJECT_ROOT / ".cache" / "tts"
LOG_DIR = PROJECT_ROOT / "logs"
TTS_LOG_FILE = LOG_DIR / "tts.log"
VOICE_CACHE_VERSION = "tts-v5"

VOICE_REFERENCE_SOURCES = {
    "id": (
        PROJECT_ROOT / "6096144127445966044.oga",
        WORKSPACE_ROOT / "6096144127445966044.oga",
    ),
    "ja": (
        PROJECT_ROOT / "Hu Tao-Voice-Overs-Japanese - Genshin Impact Wiki.ogg",
        WORKSPACE_ROOT / "Hu Tao-Voice-Overs-Japanese - Genshin Impact Wiki.ogg",
    ),
}

VOICE_REFERENCE_WAVS = {
    "id": VOICE_REF_DIR / "rina_voice_ref_indo_6096144127445966044.wav",
    "ja": VOICE_REF_DIR / "rina_voice_ref_jp_hu_tao.wav",
}


def _log_tts(trace_id: str, message: str):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} [TTS:{trace_id}] {message}"
    print(line, flush=True)
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with TTS_LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ─── VOICE ENGINES CONFIG ───────────────────────────────────────────────────

VOICE_ENGINES = {
    "id": {
        "label": "Indonesia",
        "engine": "chatterbox",
        "edge_voice": "id-ID-GadisNeural",  # Fallback
        "edge_voice_fallback": "id-ID-GadisNeural",
        "translate_first": False,
        "description": "Suara RINA Indonesia (clone realtime 6096144127445966044)",
    },
    "ja": {
        "label": "Japanese",
        "engine": "chatterbox",
        "edge_voice": "ja-JP-NanamiNeural",  # Fallback
        "edge_voice_fallback": "ja-JP-NanamiNeural",
        "translate_first": True,
        "description": "Suara RINA Jepang (clone realtime Hu Tao)",
    },
    # "en": { ... },
    # "ko": { ... },
}

# ─── EMOTION → SSML PROSODY MAPPING ─────────────────────────────────────────

EMOTION_PRESETS = {
    # RINA character: warm, caring, slightly playful (inspired by Hu Tao energy)
    "empati":       {"rate": "-8%",  "pitch": "-2Hz",  "volume": "-10%"},   # lembut, pelan
    "concerned":    {"rate": "-12%", "pitch": "-3Hz",  "volume": "-15%"},   # khawatir, hati-hati
    "encouraging":  {"rate": "+3%",  "pitch": "+4Hz",  "volume": "+5%"},    # semangat tapi gentle
    "happy":        {"rate": "+5%",  "pitch": "+6Hz",  "volume": "+5%"},    # senang, ceria
    "excited":      {"rate": "+8%",  "pitch": "+8Hz",  "volume": "+8%"},    # antusias!
    "thinking":     {"rate": "-5%",  "pitch": "+1Hz",  "volume": "-8%"},    # mikir, tenang
    "neutral":      {"rate": "-3%",  "pitch": "+2Hz",  "volume": "+0%"},    # default warm (bukan datar!)
    "listening":    {"rate": "-3%",  "pitch": "+2Hz",  "volume": "-8%"},    # dengerin, gentle
    "surprised":    {"rate": "+5%",  "pitch": "+10Hz", "volume": "+5%"},    # kaget, lucu
}

# ─── KOKORO PROBLEMATIC PATTERNS ────────────────────────────────────────────
# Fonem Bahasa Indonesia yang sering rusak di Kokoro

PROBLEMATIC_PATTERNS = [
    "ng",   # senang, dengan, jangan
    "ny",   # nyaman, menyesal, banyak
    "sy",   # syukur, syarat
    "kh",   # khusus, akhir
]


# ─── TEXT CLEANING ───────────────────────────────────────────────────────────

def _clean_text_for_tts(text: str) -> str:
    """Bersihkan teks dari karakter yang mengganggu TTS."""
    # Hapus bubble separator
    text = text.replace("|||", ". ")
    # Hapus markdown formatting
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'_+', '', text)

    # Normalize chat slang into spoken Indonesian. Avoid fake phonetic spelling:
    # it made the clone sound like a foreign accent.
    replacements = {
        r'\bRINA\b': 'Rina',
        r'\bLifeLens\b': 'Life Lens',
        r'\bga\b': 'nggak',
        r'\bgak\b': 'nggak',
        r'\bngga\b': 'nggak',
        r'\bnggk\b': 'nggak',
        r'\bklo\b': 'kalau',
        r'\bkalo\b': 'kalau',
        r'\budh\b': 'udah',
        r'\bbgt\b': 'banget',
        r'\bgtu\b': 'gitu',
        r'\bemg\b': 'emang',
        r'\byg\b': 'yang',
        r'\bdgn\b': 'dengan',
        r'\bdr\b': 'dari',
        r'\bkrn\b': 'karena',
        r'\btd\b': 'tadi',
        r'\bkm\b': 'kamu',
    }
    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)

    # Hapus emoji unicode
    text = re.sub(
        r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF'
        r'\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U0000FE00-\U0000FE0F'
        r'\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F]+', '', text
    )

    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([,.!?])', r'\1', text)
    text = re.sub(r'([,.!?])([^\s,.!?])', r'\1 \2', text)

    # Limit panjang (max 500 karakter)
    if len(text) > 500:
        text = text[:497] + '...'
    return text.strip()


# ─── TRANSLATION ─────────────────────────────────────────────────────────────

_argos_initialized = False

def _ensure_argos_packages():
    """Download paket bahasa Argos Translate jika belum ada."""
    global _argos_initialized
    if _argos_initialized or not _argos_available:
        return

    try:
        argostranslate.package.update_package_index()
        available = argostranslate.package.get_available_packages()

        for target in ["ja", "en", "ko"]:
            # Cek apakah sudah terinstall
            installed = argostranslate.package.get_installed_packages()
            already = any(p.from_code == "id" and p.to_code == target for p in installed)
            if already:
                continue

            # Cari dan install
            pkg = next(
                (p for p in available if p.from_code == "id" and p.to_code == target),
                None
            )
            if pkg:
                print(f"[Argos] Downloading id->{target} package...")
                argostranslate.package.install_from_path(pkg.download())

        _argos_initialized = True
    except Exception as e:
        print(f"[Argos] Setup error: {e}")


def translate_text(text: str, target_lang: str) -> str:
    """
    Translate teks Indonesia ke bahasa target.
    Hanya untuk input TTS — hasil tidak disimpan.
    """
    if not _argos_available:
        return text  # fallback: kirim teks asli

    _ensure_argos_packages()

    try:
        result = argostranslate.translate.translate(text, "id", target_lang)
        return result if result else text
    except Exception as e:
        print(f"[Translate] Error id->{target_lang}: {e}")
        return text


# ─── KOKORO TTS ──────────────────────────────────────────────────────────────

def _get_kokoro_pipeline(lang_code: str):
    """Lazy-load Kokoro pipeline."""
    global _kokoro_pipeline
    if not _kokoro_available:
        return None

    if _kokoro_pipeline is None:
        try:
            _kokoro_pipeline = KPipeline(lang_code=lang_code)
        except Exception as e:
            print(f"[Kokoro] Init error: {e}")
            return None

    return _kokoro_pipeline


def should_use_kokoro(text: str) -> bool:
    """
    Cek apakah teks aman untuk Kokoro.
    Kokoro bagus untuk kalimat pendek, tanpa fonem Indo bermasalah.
    """
    # Kalimat terlalu panjang
    if len(text.split()) > 8:
        return False

    # Ada fonem bermasalah
    text_lower = text.lower()
    for pattern in PROBLEMATIC_PATTERNS:
        if pattern in text_lower:
            return False

    # Kalimat tanya (intonasi Kokoro buruk)
    if text.strip().endswith("?"):
        return False

    # Kata terlalu panjang (>12 huruf)
    if any(len(w) > 12 for w in text.split()):
        return False

    return True


async def kokoro_tts(text: str, voice_id: str, lang_code: str) -> Optional[bytes]:
    """Generate audio via Kokoro TTS."""
    pipeline = _get_kokoro_pipeline(lang_code)
    if pipeline is None:
        return None

    try:
        # Kokoro generate audio
        audio_segments = list(pipeline(text, voice=voice_id))
        if not audio_segments:
            return None

        # Combine segments, convert to WAV bytes
        import numpy as np
        import struct

        all_audio = np.concatenate([seg[2] for seg in audio_segments])

        # Convert to 16-bit PCM WAV
        sample_rate = 24000
        audio_int16 = (all_audio * 32767).astype(np.int16)

        buf = io.BytesIO()
        # WAV header
        data_size = len(audio_int16) * 2
        buf.write(b'RIFF')
        buf.write(struct.pack('<I', 36 + data_size))
        buf.write(b'WAVE')
        buf.write(b'fmt ')
        buf.write(struct.pack('<IHHIIHH', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16))
        buf.write(b'data')
        buf.write(struct.pack('<I', data_size))
        buf.write(audio_int16.tobytes())

        return buf.getvalue()

    except Exception as e:
        print(f"[Kokoro] TTS error: {e}")
        return None


# ─── CHATTERBOX TTS (GPU VOICE CLONE) ────────────────────────────────────────

def _ensure_chatterbox_imports() -> bool:
    """Import Chatterbox only when TTS clone is actually requested."""
    global ChatterboxTTS, ChatterboxTurboTTS, ChatterboxVC, _chatterbox_available
    global _chatterbox_import_attempted, _chatterbox_turbo_available
    global torch, torchaudio

    if _chatterbox_available:
        return True
    if _chatterbox_import_attempted:
        return False

    _chatterbox_import_attempted = True
    t0 = time.perf_counter()
    try:
        _log_tts("chatterbox-import", "import torch start")
        import torch as _torch
        _log_tts("chatterbox-import", f"import torch done elapsed={(time.perf_counter() - t0) * 1000:.0f}ms")
        _log_tts("chatterbox-import", "import torchaudio start")
        import torchaudio as _torchaudio
        _log_tts("chatterbox-import", f"import torchaudio done elapsed={(time.perf_counter() - t0) * 1000:.0f}ms")
        _log_tts("chatterbox-import", "import ChatterboxTTS start")
        from chatterbox.tts import ChatterboxTTS as _ChatterboxTTS
        _log_tts("chatterbox-import", f"import ChatterboxTTS done elapsed={(time.perf_counter() - t0) * 1000:.0f}ms")
        _log_tts("chatterbox-import", "import ChatterboxVC start")
        from chatterbox.vc import ChatterboxVC as _ChatterboxVC
        _log_tts("chatterbox-import", f"import ChatterboxVC done elapsed={(time.perf_counter() - t0) * 1000:.0f}ms")

        torch = _torch
        torchaudio = _torchaudio
        ChatterboxTTS = _ChatterboxTTS
        ChatterboxVC = _ChatterboxVC
        _chatterbox_available = True

        try:
            _log_tts("chatterbox-import", "import ChatterboxTurboTTS start")
            from chatterbox.tts_turbo import ChatterboxTurboTTS as _ChatterboxTurboTTS
            ChatterboxTurboTTS = _ChatterboxTurboTTS
            _chatterbox_turbo_available = True
            _log_tts("chatterbox-import", f"import ChatterboxTurboTTS done elapsed={(time.perf_counter() - t0) * 1000:.0f}ms")
        except ImportError:
            _chatterbox_turbo_available = False

        _log_tts("chatterbox-import", f"all imports done elapsed={(time.perf_counter() - t0) * 1000:.0f}ms")
        return True
    except ImportError as e:
        _log_tts("chatterbox-import", f"import error: {e}")
        return False


def _ensure_chatterbox_vc_imports() -> bool:
    """Import only the voice-conversion path; avoids slow ChatterboxTTS import."""
    global ChatterboxVC, _chatterbox_vc_available, _chatterbox_vc_import_attempted
    global torch, torchaudio

    if _chatterbox_vc_available:
        return True
    if _chatterbox_vc_import_attempted:
        return False

    _chatterbox_vc_import_attempted = True
    t0 = time.perf_counter()
    try:
        if torch is None:
            _log_tts("chatterbox-vc-import", "import torch start")
            import torch as _torch
            torch = _torch
            _log_tts("chatterbox-vc-import", f"import torch done elapsed={(time.perf_counter() - t0) * 1000:.0f}ms")

        if torchaudio is None:
            _log_tts("chatterbox-vc-import", "import torchaudio start")
            import torchaudio as _torchaudio
            torchaudio = _torchaudio
            _log_tts("chatterbox-vc-import", f"import torchaudio done elapsed={(time.perf_counter() - t0) * 1000:.0f}ms")

        _log_tts("chatterbox-vc-import", "import ChatterboxVC start")
        from chatterbox.vc import ChatterboxVC as _ChatterboxVC
        ChatterboxVC = _ChatterboxVC
        _chatterbox_vc_available = True
        _log_tts("chatterbox-vc-import", f"import ChatterboxVC done elapsed={(time.perf_counter() - t0) * 1000:.0f}ms")
        return True
    except ImportError as e:
        _log_tts("chatterbox-vc-import", f"import error: {e}")
        return False


def _init_chatterbox():
    """Lazy-load Chatterbox model to GPU."""
    global _chatterbox_is_turbo, _chatterbox_model
    if not _ensure_chatterbox_imports():
        return None
    if _chatterbox_model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        use_turbo = (
            os.environ.get("LIFELENS_TTS_TURBO", "1") != "0"
            and _chatterbox_turbo_available
        )

        if use_turbo:
            try:
                print("[Chatterbox] Loading TURBO model into VRAM...")
                _chatterbox_model = ChatterboxTurboTTS.from_pretrained(device=device)
                _chatterbox_is_turbo = True
                print(f"[Chatterbox] Turbo model loaded successfully on {device}!")
                return _chatterbox_model
            except Exception as e:
                print(f"[Chatterbox] Turbo init error, falling back to standard: {e}")
                _chatterbox_model = None
                _chatterbox_is_turbo = False

        try:
            print("[Chatterbox] Loading model into VRAM...")
            _chatterbox_model = ChatterboxTTS.from_pretrained(device=device)
            if device == "cuda":
                try:
                    _chatterbox_model.half()
                    print("[Chatterbox] Enabled FP16 precision for faster inference.")
                except Exception as ex:
                    print(f"[Chatterbox] FP16 failed: {ex}")
            print(f"[Chatterbox] Model loaded successfully on {device}!")
        except Exception as e:
            print(f"[Chatterbox] Init error: {e}")
            return None
    return _chatterbox_model


def _init_chatterbox_vc():
    """Lazy-load Chatterbox voice conversion model."""
    global _chatterbox_vc_model
    t0 = time.perf_counter()
    if not _ensure_chatterbox_vc_imports():
        return None
    if _chatterbox_vc_model is None:
        try:
            _log_tts("vc-init", "loading voice conversion model")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            _chatterbox_vc_model = ChatterboxVC.from_pretrained(device=device)
            _log_tts("vc-init", f"voice conversion model loaded on {device}")
        except Exception as e:
            _log_tts("vc-init", f"init error: {e}")
            return None
    else:
        _log_tts("vc-init", "voice conversion model already loaded")
    _log_tts("vc-init", f"voice conversion init ready elapsed={(time.perf_counter() - t0) * 1000:.0f}ms")
    return _chatterbox_vc_model

# Setup pykakasi untuk merubah huruf Jepang jadi Romaji agar terbaca Chatterbox
_kks = None
def _get_kakasi():
    global _kks
    if _kks is None:
        try:
            import pykakasi
            _kks = pykakasi.kakasi()
        except ImportError:
            pass
    return _kks

def _to_romaji(text: str) -> str:
    kks = _get_kakasi()
    if not kks:
        return text
    result = kks.convert(text)
    return " ".join([item['hepburn'] for item in result])


CHATTERBOX_EMOTION_PRESETS = {
    "neutral": {
        "exaggeration": 0.48,
        "cfg_weight": 0.45,
        "temperature": 0.75,
        "repetition_penalty": 1.15,
        "min_p": 0.04,
        "top_p": 0.95,
    },
    "happy": {
        "exaggeration": 0.72,
        "cfg_weight": 0.35,
        "temperature": 0.88,
        "repetition_penalty": 1.12,
        "min_p": 0.04,
        "top_p": 0.98,
    },
    "excited": {
        "exaggeration": 0.78,
        "cfg_weight": 0.32,
        "temperature": 0.92,
        "repetition_penalty": 1.10,
        "min_p": 0.04,
        "top_p": 0.98,
    },
    "surprised": {
        "exaggeration": 0.76,
        "cfg_weight": 0.35,
        "temperature": 0.9,
        "repetition_penalty": 1.10,
        "min_p": 0.04,
        "top_p": 0.98,
    },
    "concerned": {
        "exaggeration": 0.36,
        "cfg_weight": 0.58,
        "temperature": 0.68,
        "repetition_penalty": 1.22,
        "min_p": 0.06,
        "top_p": 0.9,
    },
    "empati": {
        "exaggeration": 0.34,
        "cfg_weight": 0.6,
        "temperature": 0.66,
        "repetition_penalty": 1.22,
        "min_p": 0.06,
        "top_p": 0.9,
    },
    "thinking": {
        "exaggeration": 0.42,
        "cfg_weight": 0.55,
        "temperature": 0.7,
        "repetition_penalty": 1.2,
        "min_p": 0.05,
        "top_p": 0.92,
    },
    "listening": {
        "exaggeration": 0.38,
        "cfg_weight": 0.56,
        "temperature": 0.68,
        "repetition_penalty": 1.2,
        "min_p": 0.05,
        "top_p": 0.92,
    },
    "encouraging": {
        "exaggeration": 0.62,
        "cfg_weight": 0.42,
        "temperature": 0.82,
        "repetition_penalty": 1.14,
        "min_p": 0.04,
        "top_p": 0.96,
    },
}


def _chatterbox_params(emotion: str) -> dict:
    return CHATTERBOX_EMOTION_PRESETS.get(emotion, CHATTERBOX_EMOTION_PRESETS["neutral"])


def _style_text_for_chatterbox(text: str, emotion: str) -> str:
    """Add light delivery cues without changing Indonesian pronunciation."""
    text = text.strip()
    if not text:
        return text

    if emotion in {"happy", "excited", "encouraging"}:
        return text if text.endswith(("!", "?", ".")) else f"{text}!"
    if emotion == "surprised":
        return text if text.endswith(("?!", "?", "!")) else f"{text}?!"
    if emotion in {"thinking", "concerned", "empati", "listening"}:
        return text if text.endswith(("...", ".", "?")) else f"{text}..."
    return text if text.endswith((".", "?", "!")) else f"{text}."


def _looks_like_japanese_romaji(text: str) -> bool:
    text_lower = text.lower()
    markers = {
        "konnichiwa", "konbanwa", "ohayou", "arigatou", "desu", "watashi",
        "anata", "kyou", "ichinichi", "daijoubu", "hanashi", "kikasete",
        "ne", "yo", "suki", "genki",
    }
    return any(marker in text_lower for marker in markers)


def _ensure_voice_reference(voice_lang: str) -> Optional[str]:
    """Convert the requested source voice to a normalized WAV prompt."""
    source_candidates = VOICE_REFERENCE_SOURCES.get(voice_lang) or ()
    source = next((candidate for candidate in source_candidates if candidate.exists()), None)
    target = VOICE_REFERENCE_WAVS.get(voice_lang)
    if not target:
        return None
    if not source:
        if target.exists():
            return str(target)
        searched = ", ".join(str(candidate) for candidate in source_candidates)
        print(f"[VoiceRef] Missing source for {voice_lang}: {searched}")
        return None

    if target.exists() and target.stat().st_mtime_ns >= source.stat().st_mtime_ns:
        return str(target)

    try:
        from pydub import AudioSegment
        from pydub.effects import normalize

        VOICE_REF_DIR.mkdir(parents=True, exist_ok=True)
        audio = AudioSegment.from_file(str(source))
        clip_ms = 16000 if voice_lang == "id" else 18000
        clip = audio[:clip_ms].set_channels(1).set_frame_rate(24000)
        clip = normalize(clip)
        clip.export(str(target), format="wav")
        print(f"[VoiceRef] Prepared {voice_lang} reference: {target}")
        return str(target)
    except Exception as e:
        print(f"[VoiceRef] Convert failed for {voice_lang}: {e}")
        return str(source) if source.exists() else None


def _cache_path(text: str, emotion: str, voice_lang: str) -> Path:
    ref = _ensure_voice_reference(voice_lang) if voice_lang in VOICE_REFERENCE_SOURCES else ""
    mode = os.environ.get("LIFELENS_TTS_MODE", "vc")
    engine = "turbo" if os.environ.get("LIFELENS_TTS_TURBO", "1") != "0" else "standard"
    ref_stamp = ""
    if ref and Path(ref).exists():
        ref_stamp = str(Path(ref).stat().st_mtime_ns)
    payload = f"{VOICE_CACHE_VERSION}|{mode}|{engine}|{voice_lang}|{emotion}|{ref}|{ref_stamp}|{text}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return AUDIO_CACHE_DIR / f"{digest}.audio"


def _read_cache(path: Path) -> Optional[bytes]:
    try:
        if path.exists():
            return path.read_bytes()
    except Exception as e:
        print(f"[TTS cache] Read error: {e}")
    return None


def _write_cache(path: Path, audio: bytes) -> bytes:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(audio)
    except Exception as e:
        print(f"[TTS cache] Write error: {e}")
    return audio


async def _run_vc_with_timeout(
    source_audio: bytes,
    voice_lang: str,
    debug_id: str,
    timeout_s: Optional[float] = None,
) -> Optional[bytes]:
    timeout_s = timeout_s or float(os.environ.get("LIFELENS_VC_TIMEOUT_SECONDS", "45"))
    try:
        return await asyncio.wait_for(
            chatterbox_vc_generate(source_audio, voice_lang=voice_lang, debug_id=debug_id),
            timeout=timeout_s,
        )
    except asyncio.TimeoutError:
        _log_tts(debug_id, f"chatterbox_vc timeout after {timeout_s:.0f}s")
        return None


async def chatterbox_generate(text: str, emotion: str = "neutral", voice_lang: str = "id") -> Optional[bytes]:
    """Generate audio via Chatterbox TTS using GPU."""
    def _sync_generate() -> Optional[bytes]:
        global _chatterbox_condition_ref
        model = _init_chatterbox()
        if model is None:
            return None
        try:
            params = _chatterbox_params(emotion)
            text_mod = _style_text_for_chatterbox(text, emotion)
            ref_path = _ensure_voice_reference(voice_lang)

            # Convert to romaji jika bahasa jepang
            if voice_lang == "ja":
                text_mod = _to_romaji(text_mod)
                print(f"[Chatterbox] Converted to Romaji: {text_mod}")

            if not ref_path:
                print(f"[Chatterbox] No reference found for {voice_lang}")
                return None

            with _chatterbox_lock:
                if _chatterbox_condition_ref != ref_path:
                    model.prepare_conditionals(ref_path, exaggeration=params["exaggeration"])
                    _chatterbox_condition_ref = ref_path

                generate_kwargs = {
                    "temperature": params["temperature"],
                    "repetition_penalty": params["repetition_penalty"],
                    "top_p": params["top_p"],
                }
                if _chatterbox_is_turbo:
                    generate_kwargs.update({
                        "top_k": 1000,
                        "norm_loudness": True,
                    })
                else:
                    generate_kwargs.update({
                        "exaggeration": params["exaggeration"],
                        "cfg_weight": params["cfg_weight"],
                        "min_p": params["min_p"],
                    })

                wav = model.generate(text_mod, audio_prompt_path=None, **generate_kwargs)
            
            buf = io.BytesIO()
            torchaudio.save(buf, wav, model.sr, format="wav")
            audio_bytes = buf.getvalue()
            
            print(f"[Chatterbox] OK — {len(audio_bytes)} bytes")
            return audio_bytes
        except Exception as e:
            print(f"[Chatterbox] Generate error: {e}")
            return None

    try:
        return await asyncio.to_thread(_sync_generate)
    except Exception as e:
        print(f"[Chatterbox] Thread error: {e}")
        return None


async def chatterbox_vc_generate(
    source_audio: bytes,
    voice_lang: str = "id",
    debug_id: str = "-",
) -> Optional[bytes]:
    """Convert fast source speech into the configured RINA clone voice."""
    def _sync_generate() -> Optional[bytes]:
        global _chatterbox_vc_target_ref
        t0 = time.perf_counter()
        model = _init_chatterbox_vc()
        if model is None:
            _log_tts(debug_id, "chatterbox_vc init failed")
            return None

        ref_path = _ensure_voice_reference(voice_lang)
        if not ref_path:
            _log_tts(debug_id, f"chatterbox_vc no reference for lang={voice_lang}")
            return None

        import tempfile

        source_path = None
        try:
            from pydub import AudioSegment

            t_convert = time.perf_counter()
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                source_path = tmp.name

            source = AudioSegment.from_file(io.BytesIO(source_audio))
            source = source.set_channels(1).set_frame_rate(24000)
            source.export(source_path, format="wav")
            _log_tts(debug_id, f"vc source prepared in {(time.perf_counter() - t_convert) * 1000:.0f}ms")

            with _chatterbox_lock:
                if _chatterbox_vc_target_ref != ref_path:
                    t_ref = time.perf_counter()
                    model.set_target_voice(ref_path)
                    _chatterbox_vc_target_ref = ref_path
                    _log_tts(debug_id, f"vc target voice set in {(time.perf_counter() - t_ref) * 1000:.0f}ms")
                t_vc = time.perf_counter()
                wav = model.generate(source_path, target_voice_path=None)
                _log_tts(debug_id, f"vc conversion generated in {(time.perf_counter() - t_vc) * 1000:.0f}ms")

            buf = io.BytesIO()
            torchaudio.save(buf, wav, model.sr, format="wav")
            audio_bytes = buf.getvalue()
            _log_tts(debug_id, f"chatterbox_vc ok bytes={len(audio_bytes)} total={(time.perf_counter() - t0) * 1000:.0f}ms")
            return audio_bytes
        except Exception as e:
            _log_tts(debug_id, f"chatterbox_vc error: {e}")
            return None
        finally:
            if source_path:
                try:
                    Path(source_path).unlink(missing_ok=True)
                except Exception:
                    pass

    try:
        return await asyncio.to_thread(_sync_generate)
    except Exception as e:
        _log_tts(debug_id, f"chatterbox_vc thread error: {e}")
        return None



# ─── EDGE-TTS ────────────────────────────────────────────────────────────────

async def edge_tts_generate(
    text: str,
    voice: str,
    emotion: str = "neutral",
    debug_id: str = "-",
) -> Optional[bytes]:
    """Generate audio MP3 via edge-tts dengan prosody emotion.
    
    Dijalankan di thread terpisah untuk menghindari conflict
    dengan uvicorn event loop.
    """
    preset = EMOTION_PRESETS.get(emotion, EMOTION_PRESETS["neutral"])

    def _sync_generate() -> Optional[bytes]:
        """Sync wrapper — jalan di thread baru dengan event loop baru."""
        async def _inner():
            _log_tts(debug_id, f"edge_tts start voice={voice} emotion={emotion} chars={len(text)}")
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=preset["rate"],
                pitch=preset["pitch"],
                volume=preset["volume"],
            )
            audio_buffer = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_buffer.write(chunk["data"])
            return audio_buffer.getvalue()

        try:
            t0 = time.perf_counter()
            loop = asyncio.new_event_loop()
            try:
                audio_data = loop.run_until_complete(_inner())
            finally:
                loop.close()

            if len(audio_data) < 100:
                _log_tts(debug_id, "edge_tts returned tiny audio")
                return None
            _log_tts(debug_id, f"edge_tts ok bytes={len(audio_data)} elapsed={(time.perf_counter() - t0) * 1000:.0f}ms")
            return audio_data
        except Exception as e:
            _log_tts(debug_id, f"edge_tts error: {e}")
            return None

    try:
        return await asyncio.to_thread(_sync_generate)
    except Exception as e:
        _log_tts(debug_id, f"edge_tts thread error: {e}")
        return None


# ─── gTTS FALLBACK ───────────────────────────────────────────────────────────

def gtts_generate(text: str, lang: str = "id") -> Optional[bytes]:
    """Generate audio MP3 via gTTS (Google Translate TTS) — sync, reliable."""
    if not _gtts_available:
        print("[gTTS] Not installed. pip install gTTS")
        return None

    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        audio_data = buf.getvalue()

        if len(audio_data) < 100:
            return None

        print(f"[gTTS] OK — {len(audio_data)} bytes")
        return audio_data

    except Exception as e:
        print(f"[gTTS] Error: {e}")
        return None


# ─── VOICE ROUTER — MAIN ENTRY POINT ────────────────────────────────────────

async def generate_speech(
    text: str,
    emotion: str = "neutral",
    voice_lang: str = "id",
    require_clone: bool = True,
    debug_id: Optional[str] = None,
    metrics: Optional[dict] = None,
) -> Optional[bytes]:
    """
    Main TTS function — Voice Router.

    Flow:
      1. Clean teks
      2. Jika bahasa asing → translate dulu (Argos)
      3. Route ke engine yang sesuai:
         - ID: edge-tts id-ID-GadisNeural
         - JP/EN: Kokoro → fallback edge-tts
         - KR: edge-tts ko-KR-SunHiNeural
      4. Return audio bytes
    """
    trace_id = debug_id or f"{int(time.time() * 1000):x}"
    metrics = metrics if metrics is not None else {}
    started = time.perf_counter()

    _log_tts(trace_id, f"request start lang={voice_lang} emotion={emotion} require_clone={require_clone} raw_chars={len(text)}")

    clean = _clean_text_for_tts(text)
    if not clean:
        metrics["error"] = "empty_text"
        _log_tts(trace_id, "request stopped: empty text after clean")
        return None

    config = VOICE_ENGINES.get(voice_lang, VOICE_ENGINES["id"])
    metrics["voice_lang"] = voice_lang
    metrics["emotion"] = emotion

    # Step 1: Translate jika diperlukan
    tts_text = clean
    if config.get("translate_first") and voice_lang != "id":
        t_translate = time.perf_counter()
        tts_text = translate_text(clean, voice_lang)
        _log_tts(trace_id, f"translate done elapsed={(time.perf_counter() - t_translate) * 1000:.0f}ms chars={len(tts_text)}")

    cache_file = _cache_path(tts_text, emotion, voice_lang)
    cached = _read_cache(cache_file)
    if cached is not None:
        metrics.update({
            "cache": "hit",
            "engine": "cache",
            "clone": "yes",
            "elapsed_ms": int((time.perf_counter() - started) * 1000),
        })
        _log_tts(trace_id, f"cache hit bytes={len(cached)} elapsed={metrics['elapsed_ms']}ms")
        return cached
    metrics["cache"] = "miss"
    _log_tts(trace_id, f"cache miss clean_chars={len(tts_text)}")

    # Step 2: Route ke engine
    # Chatterbox (Hu Tao Clone) diprioritaskan untuk ID dan JA (Jepang)
    if voice_lang in ["id", "ja"]:
        mode = os.environ.get("LIFELENS_TTS_MODE", "vc").lower()
        metrics["mode"] = mode

        if mode in {"tts", "full"}:
            t_full = time.perf_counter()
            audio = await chatterbox_generate(tts_text, emotion, voice_lang=voice_lang)
            if audio is not None:
                metrics.update({
                    "engine": "chatterbox-tts",
                    "clone": "yes",
                    "elapsed_ms": int((time.perf_counter() - started) * 1000),
                })
                _log_tts(trace_id, f"full clone ok bytes={len(audio)} tts_elapsed={(time.perf_counter() - t_full) * 1000:.0f}ms total={metrics['elapsed_ms']}ms")
                return _write_cache(cache_file, audio)
            _log_tts(trace_id, "full clone failed; trying VC path")

        source_voice = config["edge_voice"]
        source_lang_for_gtts = {"ja": "ja"}.get(voice_lang, "id")
        if voice_lang == "ja" and not _looks_like_japanese_romaji(tts_text):
            # Chat text is normally Indonesian. Use an Indonesian source voice for
            # pronunciation, then convert timbre to the Hu Tao reference.
            source_voice = VOICE_ENGINES["id"]["edge_voice"]
            source_lang_for_gtts = "id"

        metrics["source_voice"] = source_voice
        audio = await edge_tts_generate(tts_text, source_voice, emotion, debug_id=trace_id)
        if audio is not None:
            if mode in {"vc", "convert", "voice_conversion"}:
                converted = await _run_vc_with_timeout(audio, voice_lang=voice_lang, debug_id=trace_id)
                if converted is not None:
                    metrics.update({
                        "engine": "edge-tts+chatterbox-vc",
                        "clone": "yes",
                        "elapsed_ms": int((time.perf_counter() - started) * 1000),
                    })
                    _log_tts(trace_id, f"request ok cloned bytes={len(converted)} total={metrics['elapsed_ms']}ms")
                    return _write_cache(cache_file, converted)

                metrics["clone"] = "failed"
                if require_clone:
                    metrics.update({
                        "engine": "edge-tts+chatterbox-vc",
                        "error": "clone_failed",
                        "elapsed_ms": int((time.perf_counter() - started) * 1000),
                    })
                    _log_tts(trace_id, f"request failed: clone_required but vc failed total={metrics['elapsed_ms']}ms")
                    return None

                _log_tts(trace_id, "vc failed; clone not required so returning edge source")
            metrics.update({
                "engine": "edge-tts",
                "clone": "no",
                "elapsed_ms": int((time.perf_counter() - started) * 1000),
            })
            _log_tts(trace_id, f"request ok edge_only bytes={len(audio)} total={metrics['elapsed_ms']}ms")
            return _write_cache(cache_file, audio)

        _log_tts(trace_id, "edge_tts failed; trying gTTS source")
        audio = gtts_generate(tts_text, source_lang_for_gtts)
        if audio is not None and mode in {"vc", "convert", "voice_conversion"}:
            converted = await _run_vc_with_timeout(audio, voice_lang=voice_lang, debug_id=trace_id)
            if converted is not None:
                metrics.update({
                    "engine": "gtts+chatterbox-vc",
                    "clone": "yes",
                    "elapsed_ms": int((time.perf_counter() - started) * 1000),
                })
                _log_tts(trace_id, f"request ok cloned_from_gtts bytes={len(converted)} total={metrics['elapsed_ms']}ms")
                return _write_cache(cache_file, converted)

        if audio is not None and not require_clone:
            metrics.update({
                "engine": "gtts",
                "clone": "no",
                "elapsed_ms": int((time.perf_counter() - started) * 1000),
            })
            _log_tts(trace_id, f"request ok gtts_edge_fallback bytes={len(audio)} total={metrics['elapsed_ms']}ms")
            return _write_cache(cache_file, audio)

        metrics.update({
            "error": "source_or_clone_failed",
            "clone": "failed",
            "elapsed_ms": int((time.perf_counter() - started) * 1000),
        })
        _log_tts(trace_id, f"request failed total={metrics['elapsed_ms']}ms")
        return None

    # JP/EN → coba Kokoro dulu, fallback edge-tts, fallback gTTS
    if config.get("engine") == "kokoro" and _kokoro_available:
        if should_use_kokoro(tts_text):
            kokoro_lang = "a" if voice_lang == "en" else "j"  # Kokoro lang codes
            audio = await kokoro_tts(tts_text, config["kokoro_voice"], kokoro_lang)
            if audio is not None:
                return _write_cache(cache_file, audio)
            # Kokoro gagal → fallback

    # Fallback / KR → edge-tts → gTTS
    audio = await edge_tts_generate(tts_text, config.get("edge_voice", "id-ID-GadisNeural"), emotion, debug_id=trace_id)
    if audio is not None:
        metrics.update({
            "engine": "edge-tts",
            "clone": "no",
            "elapsed_ms": int((time.perf_counter() - started) * 1000),
        })
        return _write_cache(cache_file, audio)
    # Final fallback → gTTS
    gtts_lang = {"ja": "ja", "en": "en", "ko": "ko"}.get(voice_lang, "id")
    audio = gtts_generate(tts_text, gtts_lang)
    return _write_cache(cache_file, audio) if audio is not None else None


async def warmup_voice_clone() -> dict:
    """Preload VC model and cache tiny clone samples so first chat audio is faster."""
    results = {}
    timeout_s = float(os.environ.get("LIFELENS_VC_WARMUP_TIMEOUT_SECONDS", "180"))
    samples = {
        "id": ("Hai, aku Rina.", "neutral"),
        "ja": ("Konnichiwa, Rina desu.", "neutral"),
    }

    for lang, (sample_text, emotion) in samples.items():
        trace_id = f"warmup-{lang}"
        started = time.perf_counter()
        try:
            _log_tts(trace_id, "warmup start")
            clean = _clean_text_for_tts(sample_text)
            config = VOICE_ENGINES.get(lang, VOICE_ENGINES["id"])
            source_voice = config["edge_voice"]
            audio = await edge_tts_generate(clean, source_voice, emotion, debug_id=trace_id)
            if audio is None:
                results[lang] = {"ok": False, "error": "edge_source_failed"}
                continue

            converted = await _run_vc_with_timeout(
                audio,
                voice_lang=lang,
                debug_id=trace_id,
                timeout_s=timeout_s,
            )
            if converted is None:
                results[lang] = {"ok": False, "error": "vc_failed_or_timeout"}
                continue

            cache_file = _cache_path(clean, emotion, lang)
            _write_cache(cache_file, converted)
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            results[lang] = {"ok": True, "elapsed_ms": elapsed_ms, "bytes": len(converted)}
            _log_tts(trace_id, f"warmup ok elapsed={elapsed_ms}ms bytes={len(converted)}")
        except Exception as e:
            results[lang] = {"ok": False, "error": str(e)}
            _log_tts(trace_id, f"warmup error: {e}")

    return results


# ─── UTILITY ─────────────────────────────────────────────────────────────────

async def list_voices(language: str = "id") -> list:
    """List available edge-tts voices untuk bahasa tertentu."""
    voices = await edge_tts.list_voices()
    return [
        {"name": v["Name"], "gender": v["Gender"], "locale": v["Locale"]}
        for v in voices
        if v["Locale"].startswith(language)
    ]


def get_voice_options() -> list[dict]:
    """Return daftar pilihan voice untuk frontend."""
    return [
        {
            "lang": lang,
            "label": cfg["label"],
            "description": cfg["description"],
            "engine": cfg["engine"],
            "kokoro_available": _kokoro_available if cfg["engine"] == "kokoro" else None,
            "translate_available": _argos_available if cfg.get("translate_first") else None,
        }
        for lang, cfg in VOICE_ENGINES.items()
    ]


def get_audio_media_type(audio_bytes: bytes) -> str:
    """Infer response media type from audio bytes."""
    if audio_bytes.startswith(b"RIFF") and audio_bytes[8:12] == b"WAVE":
        return "audio/wav"
    if audio_bytes.startswith(b"ID3") or audio_bytes[:1] == b"\xff":
        return "audio/mpeg"
    return "application/octet-stream"
