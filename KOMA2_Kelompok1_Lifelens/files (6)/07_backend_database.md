# ⚙️ BACKEND & DATABASE — LifeLens
> Server yang menjalankan semua logika: terima pesan, proses, prediksi, simpan data.
> Dikerjakan oleh: Fikri

---

## 🧠 Apa itu Backend?

Backend adalah **"otak di server"** — bagian yang tidak dilihat user tapi mengerjakan semua hal penting:
- Menerima pesan dari frontend
- Memeriksa keamanan
- Memanggil Gemini API
- Menjalankan model ML
- Menyimpan data ke database
- Mengirim hasil balik ke frontend

---

## 🛠️ Tools yang Dipakai

| Tool | Untuk Apa | Kenapa Dipilih |
|---|---|---|
| **FastAPI** | Framework server Python | Async native, auto-docs, cocok untuk ML |
| **Supabase** | Database (PostgreSQL) | Gratis, ada dashboard, built-in auth |
| **Upstash Redis** | Cache sementara | Simpan sesi aktif, cepat diakses |
| **cryptography** | Enkripsi AES-256 | Amankan teks percakapan |
| **joblib** | Load/save model ML | Standar industri untuk simpan model sklearn |
| **Railway** | Deploy server | Gratis untuk mahasiswa, Docker-based |

---

## 📁 Struktur Folder Backend

```
lifelens-backend/
├── app/
│   ├── main.py              ← Titik masuk aplikasi FastAPI
│   │
│   ├── api/
│   │   ├── chat.py          ← Endpoint WebSocket chat
│   │   └── dashboard.py     ← Endpoint data dashboard
│   │
│   ├── services/
│   │   ├── safety.py        ← ⚡ KERJAKAN INI PERTAMA
│   │   ├── gemini.py        ← Koneksi ke Gemini API
│   │   ├── nlp.py           ← NLP pipeline (Michael)
│   │   ├── prediction.py    ← Jalankan model ML
│   │   ├── features.py      ← Feature engineering
│   │   └── encryption.py   ← Enkripsi data
│   │
│   └── ml_models/           ← File model yang sudah dilatih
│       ├── burnout_model.pkl
│       ├── scaler.pkl
│       └── model_card.json
│
├── .env                     ← API keys (JANGAN di-commit ke GitHub!)
├── .env.example             ← Template .env (ini yang di-commit)
├── requirements.txt
└── Dockerfile
```

---

## 🚀 Cara Kerja Server FastAPI

FastAPI adalah framework Python untuk membuat server. Cara kerjanya: kita definisikan "endpoint" (alamat URL), dan server akan menjalankan fungsi tertentu saat ada request ke alamat itu.

**Contoh konsep — bukan kode final:**
```python
# Definisikan server
app = FastAPI()

# Endpoint health check
@app.get("/health")
def cek_status():
    return {"status": "server jalan"}

# Endpoint WebSocket untuk chat
@app.websocket("/chat/{user_id}")
async def terima_pesan(websocket, user_id):
    # 1. Terima pesan dari frontend
    # 2. Cek safety
    # 3. Kirim ke Gemini
    # 4. Proses NLP + ML
    # 5. Kirim hasil balik
```

### Async (dan Kapan Perlu Dipakai)

FastAPI mendukung fungsi "async" — fungsi yang bisa "menunggu" tanpa memblokir server. Ini penting agar server bisa melayani banyak user sekaligus.

**Aturan sederhana:**
```
PAKAI async ketika:
→ Memanggil API luar (Gemini, Supabase)    ← harus nunggu
→ Operasi database                          ← harus nunggu

PAKAI def biasa ketika:
→ Menjalankan model ML (XGBoost predict)   ← langsung selesai
→ Hitung matematika                         ← langsung selesai
→ Proses teks                               ← langsung selesai
```

FastAPI secara otomatis menjalankan `def` biasa di thread pool — jadi tidak perlu khawatir.

---

## 🛡️ Safety Layer — DIKERJAKAN PERTAMA KALI

Sebelum membuat fitur lain apapun, safety layer harus sudah ada.

### Apa yang Dilakukan?
Setiap pesan yang masuk dari user **diperiksa dulu** apakah mengandung kata-kata yang mengindikasikan krisis. Jika ada → **hentikan semua proses** dan tampilkan pesan darurat + nomor hotline.

### Kenapa Harus Pertama?
Karena jika user dalam krisis dan sistem malah melanjutkan proses normal, itu sangat berbahaya. Tidak ada fitur yang lebih penting dari ini.

### Bagaimana Cara Kerjanya?
Sistem punya daftar kata/kalimat yang mengindikasikan krisis:
```
Contoh kata yang dicek:
"ingin mati", "bunuh diri", "tidak ingin ada", "menyakiti diri"

Jika ditemukan dalam pesan user:
→ Kirim pesan empati ke user
→ Tampilkan nomor hotline: Into The Light: 119 ext 8
→ STOP — jangan lanjutkan ke Gemini atau proses lain
```

### Cara Implementasi (Konsep)
Buat file `safety.py` dengan satu fungsi utama:
```python
def check_crisis(pesan_user: str):
    """
    Input: teks pesan user
    Output: None jika aman, dict berisi pesan darurat jika ada krisis
    """
    # Cek apakah ada keyword krisis
    # Jika ada → return respons darurat
    # Jika tidak → return None (lanjutkan proses normal)
```

---

## 🔐 Enkripsi Data Percakapan

### Apa yang Dilakukan?
Teks percakapan user **dienkripsi sebelum disimpan** ke database. Database hanya menyimpan "teks acak" yang tidak bisa dibaca tanpa kunci enkripsi.

### Kenapa Perlu?
Data percakapan sangat sensitif. Kalau database kena hack, hacker tidak bisa membaca isi percakapan karena terenkripsi.

### Menggunakan Apa?
Library `cryptography` Python dengan algoritma AES-256 (Fernet).

### Bagaimana Cara Kerjanya?
```
Teks asli: "capek banget, ngerasa gak ada harapan"
         ↓ enkripsi dengan kunci rahasia
Tersimpan: "gAAAAABkX9Pm2..." (teks acak tidak bisa dibaca)

Untuk baca lagi:
Teks terenkripsi + kunci yang sama → teks asli kembali
```

**Yang penting:** Kunci enkripsi disimpan sebagai environment variable di server, **TIDAK PERNAH di dalam kode**.

---

## 🗄️ Database — Supabase

### Apa yang Disimpan?

**Tabel users** — Info akun
```
Siapa user ini? Sudah beri consent? Pilihan suara apa?
```

**Tabel sessions** — Setiap sesi ngobrol
```
Kapan ngobrol? Berapa lama? Risk level hasil prediksi?
Top 3 faktor penyebab? Ringkasan singkat?
```

**Tabel daily_features** — Data harian
```
Jam tidur, skor beban kerja, mood, sentimen hari ini
→ Ini yang dipakai untuk hitung tren 7 hari
```

**Tabel conversation_texts** — Teks percakapan
```
Teks terenkripsi AES-256
HANYA ada jika user sudah beri consent (izin)
```

### Cara Pakai Supabase di Python
Supabase punya library Python yang mudah:
```python
from supabase import create_client

# Inisialisasi koneksi (sekali saja saat server start)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Contoh: simpan sesi
supabase.table("sessions").insert({
    "user_id": user_id,
    "risk_level": "MEDIUM",
    "top_factors": ["tidur kurang", "beban tinggi"]
}).execute()
```

---

## 🔑 Environment Variables (Konfigurasi Rahasia)

Server membutuhkan beberapa "kunci" untuk mengakses layanan eksternal. Ini disimpan di file `.env` — **tidak pernah di-commit ke GitHub**.

```
Yang harus ada di .env:
- SUPABASE_URL          → alamat database
- SUPABASE_SERVICE_KEY  → kunci database
- GEMINI_API_KEY        → kunci Gemini API
- ENCRYPTION_KEY        → kunci enkripsi AES-256
- REDIS_URL             → alamat cache Redis
```

Buat file `.env.example` (tanpa nilai asli) untuk dokumentasi tim.

---

## 🚀 Deploy ke Railway

Railway adalah platform yang menjalankan server Python kita di cloud.

Cara kerjanya:
```
1. Push kode ke GitHub
2. Railway connect ke repo GitHub kita
3. Railway baca Dockerfile → build server
4. Tambahkan environment variables di dashboard Railway
5. Server jalan di URL: https://lifelens-backend.railway.app
6. Setiap push ke main → Railway otomatis deploy ulang
```

---

## 📋 Aturan FastAPI yang Sering Bikin Bingung

**Kenapa pakai `await` di beberapa tempat?**
```python
# Ini tunggu dulu (karena panggil API luar)
result = await call_gemini(pesan)

# Ini langsung (tidak perlu await)
prediction = model.predict(features)
```

**Error handling — jangan biarkan server crash:**
```python
# Tambahkan global error handler di main.py
# Agar kalau ada error, server tetap jalan dan kirim pesan error yang informatif
# Bukan langsung crash dan user dapat halaman kosong
```
