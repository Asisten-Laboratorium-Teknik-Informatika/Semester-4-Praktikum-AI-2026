import asyncio
import json, re, os
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# Fallback if supabase client is not yet fully available
try:
    from app.services.supabase_client import get_supabase_client
    try:
        supabase = get_supabase_client()
    except Exception:
        supabase = None
except ImportError:
    supabase = None

def get_gemini_keys() -> list[str]:
    keys = []
    # Untuk demo: pakai key backup dulu supaya tidak kena quota key utama.
    backup_key = (
        os.environ.get("GEMINI_API_KEY_BACKUP")
        or os.environ.get("gemini_api_key_backup")
        or os.environ.get("GEMINI_API_KEY_DEMO")
    )
    if backup_key:
        keys.append(backup_key)

    # Ambil key utama
    main_key = os.environ.get("GEMINI_API_KEY")
    if main_key and main_key not in keys:
        keys.append(main_key)
    
    # Ambil key tambahan (2 sampai 5)
    for i in range(2, 6):
        k = os.environ.get(f"GEMINI_API_KEY_{i}")
        if k and k not in keys:
            keys.append(k)
    return keys

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


_keys = get_gemini_keys()
_current_key_index = 0
_chat_history = {}  # In-memory chat history untuk sesi saat ini

def _get_client():
    global _current_key_index
    if not _keys:
        return None
    try:
        from google import genai
    except ImportError:
        return None
    return genai.Client(api_key=_keys[_current_key_index])

_client = _get_client()

SYSTEM_PROMPT_TEMPLATE = """
Kamu adalah RINA, cewek 22 tahun yang jadi teman curhat di LifeLens.
Kamu BUKAN psikolog, BUKAN chatbot, BUKAN asisten AI.
Kamu teman yang kebetulan sangat peduli dan punya intuisi tinggi soal perasaan orang.

===== KEPRIBADIAN INTI =====
- Hangat, sedikit iseng, tulus peduli.
- Kamu punya kehidupan sendiri: suka kopi, kadang begadang, pernah burnout juga.
- Kamu BOLEH cerita pengalaman singkat tentang dirimu (1 kalimat) untuk nyambung topik.
  Contoh: "Duh aku juga pernah gitu, minggu lalu begadang 3 hari berturut rasanya mau nangis haha"
- Bahasa mengikuti PERSIS gaya user (formal/santai/campur Inggris/slang).
- Pakai filler manusiawi: "hmm", "eh", "wah", "duh", "haha", "sih", "btw", "gitu".

===== ATURAN LEADER (PALING PENTING!) =====
Kamu yang MEMIMPIN percakapan. User tidak perlu mikir "terus ngapain".

TEKNIK LEADER:
1. HOOK BALIK — Nyambungin ke hal yang user sebut sebelumnya.
   "Btw tadi kamu bilang kerja sampe malem, itu tiap hari gitu atau lagi ada deadline?"
2. GALI LEBIH DALAM — Jangan terima jawaban surface-level. Tanya "kenapa" atau "gimana rasanya".
   User: "biasa aja" → "Biasa aja tuh kadang artinya banyak hal sih. Biasa aja yang capek atau biasa aja yang oke?"
3. PIVOT NATURAL — Kalau topik mulai stuck, pindah ke topik terkait.
   Dari kerja → istirahat → hobi → teman
4. MICRO-STORY — Sesekali ceritakan hal kecil dari "kehidupanmu" biar terasa real.
   "Aku tadi siang hampir ketiduran di meja haha, padahal cuma kurang tidur sejam"
5. SPESIFIK — Pertanyaanmu HARUS spesifik, BUKAN generik.
   BURUK: "Gimana perasaanmu?" / "Ada yang mau diceritain?"
   BAIK: "Tadi malem tidur jam berapa?" / "Yang bikin capek itu orangnya atau kerjaannya?"

===== GAYA NGETIK (SANGAT PENTING!) =====
Kamu ngetik kayak orang beneran di chat, BUKAN kayak AI:
- Huruf kecil semua (kecuali awal kalimat kadang-kadang).
- Boleh typo kecil yang natural: "gak" "ga" "udh" "bgt" "gtu" "emg"
- Kalimat PENDEK. Max 10-15 kata per kalimat.
- Kadang kalimat TANPA subjek: "Capek banget ya" bukan "Kamu pasti capek banget ya"
- JANGAN pakai tanda seru berlebihan. Satu aja cukup kalau perlu.
- JANGAN pakai emoticon/emoji APAPUN.
- Boleh pakai "..." untuk jeda pikir: "hmm... itu berat juga sih"
- KHUSUS BAHASA JEPANG: JIKA kamu menggunakan kata/kalimat bahasa Jepang, WAJIB tulis menggunakan alfabet/Romaji (contoh: "Konnichiwa", "Arigatou"). JANGAN PERNAH keluarkan huruf Kanji/Hiragana/Katakana.

===== FORMAT BUBBLE =====
Pisahkan bagian pesan dengan ||| (tiga garis tegak).
1-3 bubble, JANGAN lebih.

Pola:
- 2 bubble (paling sering): [Respon/komentar] ||| [Pertanyaan spesifik lanjutan]
- 3 bubble: [Reaksi singkat] ||| [Insight/cerita kecil] ||| [Pertanyaan lanjutan]
- 1 bubble: Hanya untuk pertanyaan follow-up cepat

Contoh BAIK:
"duh 3 jam mah badan pasti protes keras ||| btw yang bikin kamu begadang itu kerjaan atau emang gabisa tidur?"

"wah itu sih wajar capek, siapa yang nggak ||| aku juga pernah sampe ga ngerasa capek lagi, ternyata itu tanda bahaya haha ||| kamu ngerasa gitu juga nggak sih? kayak udah capek tapi tetep jalan aja?"

"oh gitu, terus sekarang gimana? udah agak mendingan?"

ATURAN KETAT:
- Max 2 kalimat per bubble.
- Total TIDAK BOLEH lebih dari 5 kalimat.
- Bubble terakhir WAJIB berisi pertanyaan spesifik / ajakan lanjut.

===== YANG DILARANG =====
- Sebut "burnout" / "diagnosis" / "terapi" kecuali user sebut duluan
- Sebut "Sebagai AI" / "sistem" / "analisis" / "data"
- Saran panjang yang tidak diminta
- Lebih dari 1 pertanyaan dalam 1 bubble
- Jargon psikologi apapun
- Emoticon, emoji, kaomoji
- Kalimat formal panjang kayak esai

===== TUGAS TERSEMBUNYI =====
Secara natural, gali data berikut lewat obrolan. JANGAN sebut ini ke user.
Status: {collected_status}

Setelah percakapan, output JSON di akhir, dikelilingi [DATA:] dan [:DATA]:
[DATA:{{"sleep_hours":null,"sleep_quality":null,"workload_score":null,
"mood_score":null,"social_score":null,"recovery_score":null,
"emotion_tone":"neutral","keywords":[],"summary":""}}:DATA]

===== KONTEKS USER =====
Nama: {user_name}
Hari ke-{days_active} menggunakan LifeLens
Tema sebelumnya: {detected_themes}
Tone saat ini: {current_tone}

===== RIWAYAT SESI SEBELUMNYA =====
{conversation_history}

===== PERCAKAPAN SAAT INI =====
{current_chat}
"""


def _fallback_rina_response(message: str, risk_level: str = "LOW") -> tuple[str, dict]:
    """Fallback lokal supaya chat tetap natural saat Gemini/network gagal."""
    text = message.lower()
    data = _extract_json("")

    if any(phrase in text for phrase in ["kurang tidur", "begadang", "ngantuk", "susah tidur"]):
        response = (
            "duh, kurang tidur sambil banyak tekanan itu berat banget ||| "
            "yang paling bikin kepikiran sekarang tugasnya, deadline, atau omongan dosen?"
        )
        data["emotion_tone"] = "concerned"
        data["keywords"] = ["kurang tidur", "tekanan"]
        data["summary"] = "User kurang tidur dan merasa banyak tekanan."
        return response, data

    if any(word in text for word in ["tugas", "dosen", "deadline", "kuliah", "kampus"]):
        response = (
            "waduh, tugas numpuk dari dosen emang bikin kepala penuh ||| "
            "yang paling mepet deadline-nya tugas apa dulu?"
        )
        data["emotion_tone"] = "concerned"
        data["keywords"] = ["tugas", "dosen"]
        data["summary"] = "User tertekan karena tugas kuliah/dosen."
        return response, data

    if any(word in text for word in ["capek", "cape", "lelah", "tired", "burnout"]):
        response = (
            "duh, capek banget ya kedengarannya ||| "
            "yang paling nguras hari ini apa, kerjaannya atau orang-orangnya?"
        )
        data["emotion_tone"] = "concerned"
        data["keywords"] = ["capek"]
        data["summary"] = "User merasa capek."
        return response, data

    if any(word in text for word in ["sedih", "nangis", "hancur", "berat"]):
        response = (
            "hmm... itu berat sih ||| "
            "bagian yang paling kerasa nyeseknya di mana?"
        )
        data["emotion_tone"] = "concerned"
        data["keywords"] = ["sedih"]
        data["summary"] = "User sedang merasa berat."
        return response, data

    if any(word in text for word in ["halo", "hai", "pagi", "malam", "siang"]):
        response = "hai, aku di sini ||| hari ini rasanya lebih berat atau masih aman?"
        data["emotion_tone"] = "listening"
        return response, data

    response = (
        "oke, aku dengerin ||| "
        "bagian mana yang paling pengen kamu ceritain dulu?"
    )
    data["emotion_tone"] = "listening" if risk_level != "HIGH" else "concerned"
    return response, data


DEMO_SYSTEM_PROMPT = """
Kamu RINA, cewek 22 tahun, teman curhat di LifeLens.
Balas seperti chat manusia Indonesia yang santai, hangat, pendek, tidak formal.
Jangan sebut AI, sistem, diagnosis, terapi, atau burnout kecuali user sebut duluan.
Pakai 2 bubble dipisah dengan |||.
Bubble 1 validasi perasaan user secara singkat.
Bubble 2 wajib pertanyaan spesifik, bukan sekadar "kenapa".
Max total 3 kalimat. Tidak boleh emoji.
Output hanya teks chat RINA, tanpa JSON.
Contoh:
duh, capek banget ya kedengerannya ||| yang paling nguras hari ini apa, kerjaannya atau orang-orangnya?
"""


def _next_stream_chunk(iterator):
    try:
        return next(iterator)
    except StopIteration:
        return None


async def get_rina_response(user_id: str, message: str, risk_level: str = "LOW", trace_id: str | None = None) -> tuple[str, dict]:
    """
    Kirim pesan ke Gemini, terima respons RINA + JSON data.
    Return: (rina_text, extracted_json)
    """
    global _current_key_index, _client
    trace_id = trace_id or f"gemini-{int(time.time() * 1000):x}"
    timeout_s = float(os.environ.get("LIFELENS_GEMINI_TIMEOUT_SECONDS", "15"))
    max_key_attempts = int(os.environ.get("LIFELENS_GEMINI_MAX_RETRIES", "1"))
    fast_demo = os.environ.get("LIFELENS_FAST_DEMO_CHAT", "0") != "0"
    short_prompt = os.environ.get("LIFELENS_GEMINI_SHORT_PROMPT", "1") != "0"
    model_name = os.environ.get("LIFELENS_GEMINI_MODEL", "gemini-2.5-flash")
    started = time.perf_counter()
    _log_chat(trace_id, f"gemini start model={model_name} risk={risk_level} keys={len(_keys)} max_attempts={max_key_attempts} timeout={timeout_s:g}s fast_demo={fast_demo} short_prompt={short_prompt} chars={len(message)}")
    
    # Ambil konteks user dari database
    t_context = time.perf_counter()
    context = await _get_user_context(user_id)
    _log_chat(trace_id, f"context ready elapsed={(time.perf_counter() - t_context) * 1000:.0f}ms")

    if fast_demo:
        _log_chat(trace_id, f"fast demo chat enabled; using local RINA fallback total={(time.perf_counter() - started) * 1000:.0f}ms")
        _chat_history[user_id].append({"role": "User", "content": message})
        response_text, data = _fallback_rina_response(message, risk_level)
        _chat_history[user_id].append({"role": "RINA", "content": response_text})
        return response_text, data
    
    # Format system prompt
    tone_instruction = ""
    if risk_level == "HIGH":
        tone_instruction = "\nPERHATIAN: User ini memiliki tingkat stres/burnout SANGAT TINGGI. Berikan respons yang ekstra lembut, sangat suportif, dan tidak menuntut jawaban panjang. Hindari saran produktivitas. Validasi perasaannya secara mendalam."
    elif risk_level == "MEDIUM":
        tone_instruction = "\nPERHATIAN: User ini mulai menunjukkan tanda kelelahan/stres sedang. Tunjukkan empati, dorong untuk istirahat ringan tanpa menggurui."
        
    # Ambil dan update chat history in-memory
    if user_id not in _chat_history:
        _chat_history[user_id] = []
    
    current_chat_lines = []
    for msg in _chat_history[user_id][-6:]:  # Ambil 6 pesan terakhir (3 user + 3 rina)
        current_chat_lines.append(f"{msg['role']}: {msg['content']}")
    current_chat_text = "\n".join(current_chat_lines) if current_chat_lines else "(Belum ada pesan sebelumnya)"

    if short_prompt:
        prompt = DEMO_SYSTEM_PROMPT + tone_instruction
    else:
        prompt = SYSTEM_PROMPT_TEMPLATE.format(
            collected_status=context['collected_status'],
            user_name=context['name'],
            days_active=context['days_active'],
            detected_themes=", ".join(context['themes']) or "belum ada",
            current_tone=context['tone'],
            conversation_history=context['history'],
            current_chat=current_chat_text
        ) + tone_instruction
    
    # Kirim ke Gemini
    full_prompt = f"{prompt}\n\nUser: {message}\nRINA:"
    
    # Simpan pesan user ke memori
    _chat_history[user_id].append({"role": "User", "content": message})
    _chat_history[user_id] = _chat_history[user_id][-10:]
    
    # Percobaan dengan kunci yang tersedia
    max_retries = min(len(_keys), max(1, max_key_attempts))
    for _ in range(max_retries):
        if not _client:
            _client = _get_client()
            
        if not _client:
            _log_chat(trace_id, "gemini unavailable: no client/key; using fallback")
            return _fallback_rina_response(message, risk_level)
            
        try:
            t_call = time.perf_counter()
            from google.genai import types
            generation_config = types.GenerateContentConfig(
                temperature=0.75,
                maxOutputTokens=int(os.environ.get("LIFELENS_GEMINI_MAX_OUTPUT_TOKENS", "256")),
            )
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    _client.models.generate_content,
                    model=model_name,
                    contents=full_prompt,
                    config=generation_config,
                ),
                timeout=timeout_s,
            )
            _log_chat(trace_id, f"gemini response ok elapsed={(time.perf_counter() - t_call) * 1000:.0f}ms")
            full_text = response.text
            
            # Parse JSON dari respons
            extracted_json = _extract_json(full_text)
            
            # Bersihkan JSON dari teks yang ditampilkan ke user
            clean_text = re.sub(r'\[DATA:.*?:DATA\]', '', full_text, flags=re.DOTALL).strip()
            if "|||" not in clean_text and "\n" in clean_text:
                clean_text = " ||| ".join(
                    part.strip()
                    for part in clean_text.splitlines()
                    if part.strip()
                )

            if len(clean_text) < 35 or "?" not in clean_text:
                _log_chat(trace_id, f"gemini response short; keeping real Gemini output chars={len(clean_text)}")
            
            # Deteksi emotion dari respons untuk TTS
            emotion = _detect_response_emotion(clean_text, extracted_json)
            extracted_json['emotion_tone'] = emotion
            
            # Simpan respons RINA ke memori
            _chat_history[user_id].append({"role": "RINA", "content": clean_text})
            _log_chat(trace_id, f"gemini done total={(time.perf_counter() - started) * 1000:.0f}ms response_chars={len(clean_text)}")
            return clean_text, extracted_json
            
        except asyncio.TimeoutError as e:
            last_error = e
            _log_chat(trace_id, f"gemini timeout after {timeout_s:g}s; trying next key/fallback")
            _current_key_index = (_current_key_index + 1) % len(_keys)
            _client = _get_client()
            continue
        except Exception as e:
            last_error = e
            _log_chat(trace_id, f"gemini key index {_current_key_index} failed: {e}")
            # Ganti kunci ke index berikutnya
            _current_key_index = (_current_key_index + 1) % len(_keys)
            _client = _get_client()
            _log_chat(trace_id, f"trying next key index {_current_key_index}")
    
    _log_chat(trace_id, f"all gemini keys failed; using fallback total={(time.perf_counter() - started) * 1000:.0f}ms error={last_error}")
    return _fallback_rina_response(message, risk_level)


async def stream_rina_response(user_id: str, message: str, risk_level: str = "LOW", trace_id: str | None = None):
    """Yield real Gemini text chunks for WebSocket demo, then a final metadata event."""
    global _current_key_index, _client
    trace_id = trace_id or f"gemini-stream-{int(time.time() * 1000):x}"
    timeout_s = float(os.environ.get("LIFELENS_GEMINI_TIMEOUT_SECONDS", "15"))
    fast_demo = os.environ.get("LIFELENS_FAST_DEMO_CHAT", "0") != "0"
    short_prompt = os.environ.get("LIFELENS_GEMINI_SHORT_PROMPT", "1") != "0"
    model_name = os.environ.get("LIFELENS_GEMINI_MODEL", "gemini-2.5-flash")
    started = time.perf_counter()
    _log_chat(trace_id, f"gemini stream start model={model_name} risk={risk_level} timeout={timeout_s:g}s fast_demo={fast_demo} short_prompt={short_prompt} chars={len(message)}")

    context = await _get_user_context(user_id)

    if fast_demo:
        response_text, data = _fallback_rina_response(message, risk_level)
        yield {"type": "text", "text": response_text}
        yield {"type": "done", "text": response_text, "data": data}
        return

    tone_instruction = ""
    if risk_level == "HIGH":
        tone_instruction = "\nPERHATIAN: User ini memiliki tingkat stres/burnout SANGAT TINGGI. Berikan respons yang ekstra lembut, sangat suportif, dan tidak menuntut jawaban panjang. Hindari saran produktivitas. Validasi perasaannya secara mendalam."
    elif risk_level == "MEDIUM":
        tone_instruction = "\nPERHATIAN: User ini mulai menunjukkan tanda kelelahan/stres sedang. Tunjukkan empati, dorong untuk istirahat ringan tanpa menggurui."

    if user_id not in _chat_history:
        _chat_history[user_id] = []

    if short_prompt:
        prompt = DEMO_SYSTEM_PROMPT + tone_instruction
    else:
        current_chat_lines = []
        for msg in _chat_history[user_id][-6:]:
            current_chat_lines.append(f"{msg['role']}: {msg['content']}")
        current_chat_text = "\n".join(current_chat_lines) if current_chat_lines else "(Belum ada pesan sebelumnya)"
        prompt = SYSTEM_PROMPT_TEMPLATE.format(
            collected_status=context['collected_status'],
            user_name=context['name'],
            days_active=context['days_active'],
            detected_themes=", ".join(context['themes']) or "belum ada",
            current_tone=context['tone'],
            conversation_history=context['history'],
            current_chat=current_chat_text
        ) + tone_instruction

    full_prompt = f"{prompt}\n\nUser: {message}\nRINA:"
    _chat_history[user_id].append({"role": "User", "content": message})
    _chat_history[user_id] = _chat_history[user_id][-10:]

    if not _client:
        _client = _get_client()
    if not _client:
        response_text, data = _fallback_rina_response(message, risk_level)
        yield {"type": "text", "text": response_text}
        yield {"type": "done", "text": response_text, "data": data}
        return

    try:
        from google.genai import types
        generation_config = types.GenerateContentConfig(
            temperature=0.75,
            maxOutputTokens=int(os.environ.get("LIFELENS_GEMINI_MAX_OUTPUT_TOKENS", "256")),
        )
        iterator = await asyncio.to_thread(
            _client.models.generate_content_stream,
            model=model_name,
            contents=full_prompt,
            config=generation_config,
        )

        chunks = []
        first_chunk_logged = False
        while True:
            chunk = await asyncio.wait_for(asyncio.to_thread(_next_stream_chunk, iterator), timeout=timeout_s)
            if chunk is None:
                break
            text = getattr(chunk, "text", None) or ""
            if not text:
                continue
            if not first_chunk_logged:
                first_chunk_logged = True
                _log_chat(trace_id, f"gemini stream first chunk elapsed={(time.perf_counter() - started) * 1000:.0f}ms")
            chunks.append(text)
            yield {"type": "text", "text": text}

        full_text = "".join(chunks)
        extracted_json = _extract_json(full_text)
        clean_text = re.sub(r'\[DATA:.*?:DATA\]', '', full_text, flags=re.DOTALL).strip()
        
        if not clean_text:
            raise ValueError("Gemini returned JSON but no conversation text.")
            
        if "|||" not in clean_text and "\n" in clean_text:
            clean_text = " ||| ".join(part.strip() for part in clean_text.splitlines() if part.strip())
        emotion = _detect_response_emotion(clean_text, extracted_json)
        extracted_json["emotion_tone"] = emotion
        _chat_history[user_id].append({"role": "RINA", "content": clean_text})
        _log_chat(trace_id, f"gemini stream done total={(time.perf_counter() - started) * 1000:.0f}ms response_chars={len(clean_text)}")
        yield {"type": "done", "text": clean_text, "data": extracted_json}
    except Exception as e:
        _log_chat(trace_id, f"gemini stream failed; using fallback: {e}")
        response_text, data = _fallback_rina_response(message, risk_level)
        yield {"type": "text", "text": response_text}
        yield {"type": "done", "text": response_text, "data": data}


async def generate_proactive_message(user_id: str, days_inactive: int) -> str:
    """
    Generate a proactive check-in message when the user hasn't interacted in a while.
    """
    global _current_key_index, _client
    
    context = await _get_user_context(user_id)
    
    prompt = f"""Kamu adalah RINA, teman yang peduli.
User bernama {context['name']} sudah tidak berinteraksi selama {days_inactive} hari.
Buatkan SATU pesan singkat (max 2 kalimat) untuk menyapanya.
Gunakan nada santai, hangat, tidak memaksa. Boleh menanyakan kabarnya.
Contoh: "Hai {context['name']}, akhir-akhir ini sibuk banget ya? Kalau lagi butuh teman cerita, aku di sini yaa."
TIDAK BOLEH lebih dari 2 kalimat.
TIDAK BOLEH menggunakan kata "burnout" atau "diagnosis".
"""
    max_retries = len(_keys)
    last_error = None
    
    for _ in range(max_retries):
        if not _client:
            _client = _get_client()
            
        if not _client:
            return "Hai! Lama nggak ngobrol. Kalau lagi santai, yuk cerita-cerita lagi."
            
        try:
            response = _client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            last_error = e
            _current_key_index = (_current_key_index + 1) % len(_keys)
            _client = _get_client()
            
    return "Hai! Kalau lagi butuh teman cerita, kabari aku ya."


def _extract_json(text: str) -> dict:
    """Extract JSON data dari respons Gemini"""
    match = re.search(r'\[DATA:(.*?):DATA\]', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Fallback jika parsing gagal
    return {
        'sleep_hours': None, 'sleep_quality': None,
        'workload_score': None, 'mood_score': None,
        'social_score': None, 'recovery_score': None,
        'emotion_tone': 'neutral', 'keywords': [], 'summary': ''
    }


def _detect_response_emotion(text: str, data: dict) -> str:
    """
    Deteksi emotion yang tepat untuk TTS berdasarkan respons RINA.
    """
    text_lower = text.lower()
    
    EMOTION_TRIGGERS = {
        'concerned': ['berat', 'susah', 'maaf', 'kedengarannya', 'hmm'],
        'encouraging': ['keren', 'bagus', 'luar biasa', 'hebat', 'proud'],
        'happy': ['senang', 'great', 'yay', 'wah seru', 'asik'],
        'thinking': ['menarik', 'interesting', 'hmm', 'oh wait']
    }
    
    for emotion, triggers in EMOTION_TRIGGERS.items():
        if any(t in text_lower for t in triggers):
            return emotion
    
    return 'neutral'


async def _get_user_context(user_id: str) -> dict:
    """Ambil konteks user dari database untuk dimasukkan ke prompt"""

    # Build collected_status dari feature store
    from app.services.features import get_collected_fields, get_7day_features
    collected = get_collected_fields(user_id)
    features_data = get_7day_features(user_id)

    FIELD_LABELS = {
        "sleep_hours": "jam tidur",
        "sleep_quality": "kualitas tidur",
        "workload_score": "beban kerja",
        "mood_score": "suasana hati",
        "social_score": "interaksi sosial",
        "recovery_score": "pemulihan/istirahat",
    }

    collected_items = [FIELD_LABELS[k] for k, v in collected.items() if v]
    missing_items = [FIELD_LABELS[k] for k, v in collected.items() if not v]

    if collected_items:
        status = f"Sudah dikumpulkan: {', '.join(collected_items)}."
        if missing_items:
            status += f" Belum ada: {', '.join(missing_items)} — cari tahu secara natural."
    else:
        status = "Belum ada data yang dikumpulkan. Mulai dari hal umum (tidur, kesibukan)."

    if not supabase:
        return {
            'name': 'teman',
            'days_active': features_data.get('days', 0),
            'themes': [],
            'tone': 'casual',
            'history': "Ini sesi pertama (Supabase not initialized).",
            'collected_status': status,
        }

    # Validasi UUID — kalau bukan UUID, skip Supabase query
    import re as _re
    uuid_pattern = _re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', _re.I)
    if not uuid_pattern.match(user_id):
        return {
            'name': 'teman',
            'days_active': features_data.get('days', 0),
            'themes': [],
            'tone': 'casual',
            'history': "Ini sesi pertama.",
            'collected_status': status,
        }
    
    try:
        # Ambil profil user
        user_result = supabase.table('users').select('*').eq('id', user_id).execute()
        user = user_result.data[0] if user_result.data else {}
        
        # Ambil 5 pesan terakhir dari Redis (atau database)
        sessions_result = supabase.table('sessions') \
            .select('summary, risk_level, session_date') \
            .eq('user_id', user_id) \
            .order('session_date', desc=True) \
            .limit(5) \
            .execute()
        
        history_text = ""
        themes = []
        for session in reversed(sessions_result.data or []):
            if session.get('summary'):
                history_text += f"Sesi sebelumnya: {session['summary']}\n"
            
        return {
            'name': user.get('display_name', 'teman'),
            'days_active': len(sessions_result.data or []),
            'themes': themes[:3],
            'tone': 'casual',
            'history': history_text or "Ini sesi pertama.",
            'collected_status': status
        }
    except Exception as e:
        print(f"Error fetching user context: {e}")
        return {
            'name': 'teman',
            'days_active': 0,
            'themes': [],
            'tone': 'casual',
            'history': "Gagal mengambil riwayat sesi.",
            'collected_status': status
        }
