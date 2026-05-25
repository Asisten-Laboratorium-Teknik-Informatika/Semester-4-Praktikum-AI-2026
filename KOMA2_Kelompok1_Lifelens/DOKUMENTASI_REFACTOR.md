# Dokumentasi Refactor

## Tujuan

Paket baru `KOMA2_Kelompok1_Lifelens` dibuat sebagai folder proyek bersih untuk presentasi/pengumpulan. Folder ini tidak membawa dependency berat yang bisa digenerate ulang.

## Struktur Penting

```text
app\                  Backend FastAPI
frontend\             Frontend React + Vite
ml_models\voice_ref\  WAV referensi voice clone yang sudah diprepare
docs\                 Dokumen laporan/proyek
files (6)\            Materi pendukung yang ikut disalin
CARA_MENJALANKAN.md   Panduan run lokasi lama dan baru
start_backend.ps1     Script start backend
start_frontend.ps1    Script start frontend
```

## Yang Tidak Disalin ke Paket Baru

```text
node_modules\
venv\
.venv\
frontend\dist\
.cache\
logs\
__pycache__\
.pytest_cache\
testing\
Data\
Output\
Notebooks\
CHAT\
```

## Catatan Chat

Backend chat utama ada di:

```text
app\api\chat.py
app\services\gemini.py
```

Jika `GEMINI_API_KEY` belum diisi atau Gemini gagal karena network/proxy/API key, backend tetap mengembalikan balasan fallback RINA yang natural agar chat tidak macet.

## Catatan Voice

Endpoint TTS:

```text
POST /api/voice/tts
```

Field penting:

```json
{
  "text": "Hai, aku Rina.",
  "emotion": "neutral",
  "voice_lang": "id",
  "require_clone": true,
  "client_trace_id": "manual-test"
}
```

Jika `require_clone=true`, backend tidak boleh mengirim edge-tts polos saat voice conversion gagal. Ini sengaja supaya suara yang terdengar benar-benar clone, bukan fallback yang menyamar.

Referensi clone dicek dari root proyek dulu, lalu parent folder proyek lama:

```text
6096144127445966044.oga
Hu Tao-Voice-Overs-Japanese - Genshin Impact Wiki.ogg
```

Header debug:

```text
X-TTS-Trace-Id
X-TTS-Elapsed-Ms
X-TTS-Engine
X-TTS-Clone
X-TTS-Cache
X-TTS-Source-Voice
```
