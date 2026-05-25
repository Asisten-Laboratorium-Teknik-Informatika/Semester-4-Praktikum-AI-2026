# 📦 REQUIREMENTS — LifeLens
> Semua yang perlu diinstall dan disiapkan sebelum mulai coding.
> Selesaikan dokumen ini DI HARI PERTAMA sebelum menyentuh kode apapun.

---

## 💻 Hardware Tim Kalian

```
Ryzen 7 7000 series + RTX 3050 4GB + 32GB RAM

Status: LEBIH DARI CUKUP ✅

RTX 3050 bisa dipakai untuk:
  - faster-whisper STT lokal (V2 nanti)
  - Model TTS lokal (V2 nanti)
  - Training XGBoost/LightGBM (tapi CPU sudah cukup)

Untuk MVP: hampir semua proses pakai CPU dan API online
```

---

## 🖥️ Software yang Harus Diinstall Semua Anggota

### 1. Git — Version Control
```
Download: git-scm.com
Setelah install, setup nama dan email:

  git config --global user.name "Nama Kamu"
  git config --global user.email "email@kamu.com"

Verifikasi berhasil: ketik  git --version  di terminal
```

### 2. Node.js 20+ — Untuk Frontend (Argya)
```
Download: nodejs.org → pilih versi LTS (Long Term Support)
Pastikan versi 20 ke atas.

Verifikasi: ketik  node --version  → harus muncul v20.x.x
```

### 3. Python 3.11+ — Untuk Backend & ML (Fikri, Michael, Nadya)
```
Download: python.org → pilih Python 3.11 atau 3.12

Windows: centang "Add Python to PATH" saat install!

Verifikasi: ketik  python --version  → harus muncul 3.11.x atau 3.12.x
```

### 4. VS Code — Code Editor
```
Download: code.visualstudio.com

Extensions yang harus diinstall (cari di marketplace VS Code):
- Python (by Microsoft)
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- GitLens
- Thunder Client (untuk test API)
- Prettier (auto-format kode)
```

### 5. Docker Desktop — Untuk Development Lokal
```
Download: docker.com/products/docker-desktop

Kenapa perlu: untuk jalankan semua service (backend, redis) sekaligus
dengan satu perintah.

Verifikasi: ketik  docker --version
```

---

## 🐍 Setup Python Backend

### Langkah 1 — Buat Virtual Environment
Virtual environment = "ruang terisolasi" untuk package Python.
Kenapa perlu: agar package proyek ini tidak bentrok dengan project lain.

```bash
# Buat virtual environment
python -m venv venv

# Aktifkan (WAJIB dilakukan setiap kali buka terminal baru)
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# Kalau berhasil: nama (venv) akan muncul di depan prompt terminal
```

### Langkah 2 — Install Package Python
Setelah virtual environment aktif:
```bash
pip install -r requirements.txt
```

**Package utama yang akan terinstall:**

| Package | Untuk Apa |
|---|---|
| `fastapi` | Framework server web |
| `uvicorn` | Jalankan server FastAPI |
| `supabase` | Koneksi ke database |
| `google-generativeai` | Koneksi ke Gemini API |
| `scikit-learn` | Library ML (Random Forest, scaler, dll) |
| `xgboost` | Algoritma XGBoost |
| `lightgbm` | Algoritma LightGBM |
| `shap` | Explainability model |
| `transformers` | IndoBERT dan model NLP lainnya |
| `torch` | PyTorch (dibutuhkan transformers) |
| `spacy` | NLP toolkit |
| `edge-tts` | Text-to-speech Microsoft |
| `cryptography` | Enkripsi AES-256 |
| `pandas` | Olah data tabular |
| `numpy` | Komputasi numerik |
| `matplotlib` / `seaborn` | Visualisasi data (untuk EDA) |
| `jupyter` | Notebook untuk EDA |

### Langkah 3 — Download Model AI
Setelah package terinstall, download model yang dibutuhkan:

```bash
# Download model NLP Indonesia
python -m spacy download xx_ent_wiki_sm

# Download IndoBERT (otomatis saat pertama kali dipakai)
python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('indobenchmark/indobert-base-p1')"
# Ini akan download ~500MB, tunggu sampai selesai
```

---

## ⚛️ Setup Frontend (Argya)

### Langkah 1 — Buat Project React
```bash
# Buat project baru
npm create vite@latest lifelens-frontend -- --template react
cd lifelens-frontend

# Install dependencies dasar
npm install
```

### Langkah 2 — Install Semua Package
```bash
npm install framer-motion gsap zustand axios swr recharts \
            lucide-react howler @supabase/supabase-js \
            react-router-dom clsx

npm install -D tailwindcss postcss autoprefixer

npx tailwindcss init -p
```

**Package utama yang terinstall:**

| Package | Untuk Apa |
|---|---|
| `framer-motion` | Animasi UI (chat bubble, transisi halaman) |
| `gsap` | Animasi karakter 2D SVG |
| `zustand` | State management (simpan data global) |
| `recharts` | Grafik tren mood |
| `@supabase/supabase-js` | Login dan akses database |
| `react-router-dom` | Navigasi antar halaman |
| `lucide-react` | Icon (send, mic, settings, dll) |

### Langkah 3 — Verifikasi
```bash
npm run dev
# Buka browser ke http://localhost:5173
# Harus muncul halaman default Vite + React
```

---

## 🔑 Akun yang Harus Dibuat (Semua GRATIS)

### 1. GitHub
```
URL: github.com

Yang harus dilakukan:
- Semua anggota punya akun
- Buat 2 repository: lifelens-frontend dan lifelens-backend
- Invite semua anggota sebagai collaborator
- Setup .gitignore (penting: jangan commit file .env!)
```

### 2. Supabase (Database)
```
URL: supabase.com
Plan: Free (500MB, lebih dari cukup)

Yang didapat:
- Database PostgreSQL
- Login sistem (Google, email, anonymous)
- Dashboard untuk lihat dan edit data secara visual

Setup steps:
1. Daftar → buat project baru
2. Catat: Project URL dan anon key
3. Di Authentication → Providers → aktifkan Google
4. Jalankan SQL untuk buat tabel (lihat 02_system_architecture.md)
```

### 3. Google AI Studio (Gemini API)
```
URL: aistudio.google.com
Plan: Free — Gemini 2.0 Flash: 15 request/menit, 1 juta token/hari

Setup:
1. Login dengan Google account
2. Klik "Create API Key"
3. Salin API key-nya
4. SIMPAN DI FILE .env, JANGAN di kode langsung!
```

### 4. Vercel (Deploy Frontend)
```
URL: vercel.com
Plan: Free selamanya untuk project personal

Setup:
1. Daftar dengan GitHub account
2. Import repository lifelens-frontend
3. Vercel otomatis detect React + Vite
4. Tambahkan environment variables
5. Deploy! URL tersedia dalam < 1 menit
```

### 5. Railway (Deploy Backend)
```
URL: railway.app
Plan: Free ($5 credit/bulan)

Setup:
1. Daftar dengan GitHub account
2. New Project → Deploy from GitHub repo
3. Pilih lifelens-backend
4. Tambahkan environment variables di Settings
5. Railway baca Dockerfile dan deploy otomatis
```

### 6. Upstash (Redis Cache)
```
URL: upstash.com
Plan: Free (10.000 request/hari)

Setup:
1. Daftar
2. Create Database → pilih region Singapore
3. Catat: REDIS_URL
```

### 7. Kaggle (Download Dataset)
```
URL: kaggle.com
Gratis.

Setup:
1. Daftar
2. Pergi ke Settings → API → "Create New API Token"
3. Download file kaggle.json
4. Taruh di folder: C:\Users\NamaKamu\.kaggle\ (Windows)
   atau: ~/.kaggle/ (Mac/Linux)
5. Coba download: kaggle datasets download blurredmachine/are-your-employees-burning-out
```

---

## 🔒 File .env — Konfigurasi Rahasia

Buat file `.env` di root folder backend. **JANGAN commit ke GitHub.**

```
# .env — isi dengan nilai asli

SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJxxx...
GEMINI_API_KEY=AIzaSyxxx...
ENCRYPTION_KEY=xxxxx...
REDIS_URL=rediss://xxx@xxx.upstash.io:6379
ALLOWED_ORIGINS=http://localhost:5173
```

**Cara generate ENCRYPTION_KEY:**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Salin output → taruh di .env sebagai ENCRYPTION_KEY
```

Buat juga file `.env.example` (commit ini ke GitHub):
```
# .env.example — template tanpa nilai asli

SUPABASE_URL=
SUPABASE_SERVICE_KEY=
GEMINI_API_KEY=
ENCRYPTION_KEY=
REDIS_URL=
ALLOWED_ORIGINS=
```

---

## ✅ Checklist Setup Per Anggota

```
SEMUA ANGGOTA:
□ Git terinstall dan terkonfigurasi
□ Punya akun GitHub dan sudah di-invite ke repo tim
□ Punya akun Supabase (tim share 1 project)
□ Punya Gemini API key sendiri
□ Punya akun Vercel dan Railway
□ Bisa clone repo tim

NADYA (tambahan):
□ Python + venv bisa aktif
□ pip install berhasil (coba import pandas)
□ Kaggle API key setup, bisa download dataset
□ Jupyter Notebook bisa jalan

ARGYA (tambahan):
□ Node.js 20+ terinstall
□ npm run dev jalan di localhost:5173

FIKRI (tambahan):
□ uvicorn jalan di localhost:8000
□ Supabase connection berhasil (test query sederhana)
□ safety.py sudah dibuat dan ditest

MICHAEL (tambahan):
□ IndoBERT berhasil didownload
□ Test: analisis sentimen 1 kalimat berhasil
□ spaCy model terinstall
□ Figma atau Inkscape terinstall
```

---

## 🔧 Error yang Sering Terjadi dan Solusinya

```
ERROR: "module not found" di Python
→ Pastikan virtual environment aktif: (venv) harus muncul di terminal
→ Coba: pip install [nama_module]

ERROR: "torch not found" saat import transformers
→ Install PyTorch dulu: pip install torch
→ Kalau pakai GPU: pip install torch --index-url https://download.pytorch.org/whl/cu121

ERROR: CORS error di browser
→ Backend belum include URL frontend di ALLOWED_ORIGINS
→ Tambahkan http://localhost:5173 di .env

ERROR: Supabase connection refused
→ Cek SUPABASE_URL dan SUPABASE_SERVICE_KEY di .env
→ Pastikan python-dotenv sudah load .env

ERROR: Gemini quota exceeded (429)
→ Free tier: 15 request/menit
→ Tambahkan jeda antara request saat testing

ERROR: .env tidak terbaca
→ Pastikan file .env ada di root folder backend
→ Pastikan ada kode: from dotenv import load_dotenv; load_dotenv()
```
