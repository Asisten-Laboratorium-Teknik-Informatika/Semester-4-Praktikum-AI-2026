# Cara Menjalankan LifeLens

Dokumen ini berlaku untuk lokasi lama:

```text
M:\Ai Tugas Akhir Project\ProjekAI
```

dan lokasi paket baru:

```text
M:\KOMA2_Kelompok1_Lifelens
```

## 1. Persiapan Backend

Masuk ke folder proyek:

```powershell
cd "M:\KOMA2_Kelompok1_Lifelens"
```

Atau untuk lokasi lama:

```powershell
cd "M:\Ai Tugas Akhir Project\ProjekAI"
```

Buat/aktifkan virtual environment jika belum ada:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Pastikan file `.env` ada. Minimal:

```env
GEMINI_API_KEY=isi_api_key_gemini
```

## 2. Persiapan Frontend

```powershell
cd frontend
npm install
```

## 3. Menjalankan Aplikasi

Terminal 1, backend:

```powershell
cd "M:\KOMA2_Kelompok1_Lifelens"
.\start_backend.ps1
```

Terminal 2, frontend:

```powershell
cd "M:\KOMA2_Kelompok1_Lifelens"
.\start_frontend.ps1
```

Buka:

```text
http://127.0.0.1:5173
```

## 4. Mode Suara

Default backend menjalankan chat tanpa warm-up TTS supaya RINA cepat bisa membalas chat.

Jika ingin preload model voice clone saat backend start:

```powershell
.\start_backend.ps1 -WarmupTts
```

Log TTS ada di:

```text
logs\tts.log
```

Pipeline suara saat ini:

```text
edge-tts source audio -> ChatterboxVC voice conversion -> audio clone WAV
```

Referensi voice:

```text
Indonesia: 6096144127445966044.oga
Jepang:    Hu Tao-Voice-Overs-Japanese - Genshin Impact Wiki.ogg
```

Di lokasi lama file referensi boleh berada di parent folder proyek:

```text
M:\Ai Tugas Akhir Project\
```

Di paket baru file referensi sudah ikut disalin ke root proyek:

```text
M:\KOMA2_Kelompok1_Lifelens\
```

WAV hasil konversi referensi ikut tersimpan di:

```text
ml_models\voice_ref\
```

## 5. Validasi Cepat

Backend:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/health -UseBasicParsing
```

Frontend build:

```powershell
cd frontend
npm run build
```

TTS strict clone:

```powershell
$body = @{
  text = "Hai, aku Rina."
  emotion = "neutral"
  voice_lang = "id"
  require_clone = $true
  client_trace_id = "manual-check"
} | ConvertTo-Json

Invoke-WebRequest `
  -Uri http://127.0.0.1:8000/api/voice/tts `
  -Method Post `
  -Body $body `
  -ContentType "application/json" `
  -OutFile manual-check.wav
```
