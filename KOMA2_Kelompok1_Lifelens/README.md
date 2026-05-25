# LifeLens

> AI-based Lifestyle Pattern Analysis and Burnout Risk Prediction

LifeLens adalah aplikasi web berbasis AI yang mendeteksi risiko burnout melalui percakapan natural dengan RINA, teman bicara AI yang hangat dan empatik. Sistem menggunakan kombinasi NLP (IndoBERT), Machine Learning (LightGBM), dan Gemini AI untuk menganalisis pola gaya hidup dan memberikan screening risiko burnout.

---

## Tim Pengembang

| Nama | NIM | Peran |
|------|-----|-------|
| Nadya Putri Anggina | 241712040 | Data EDA & Preprocessing |
| Argya Ariella | 241712028 | Frontend & Deployment |
| Muhammad Fikri Ramadhan | 241712027 | ML Modeling & Backend |
| Michael Deryl Aaron Matthew | 241712042 | NLP, Persona & Dokumentasi |

**Program Studi:** D3 Teknik Informatika, Universitas Sumatera Utara  
**Kelas:** KOM A2

---

## Fitur Utama

- **Chat dengan RINA** — Percakapan natural dalam Bahasa Indonesia
- **Deteksi Risiko Burnout** — Scoring otomatis (LOW / MEDIUM / HIGH)
- **Analisis NLP** — Sentimen, kata kunci burnout, distorsi kognitif
- **Safety Protocol** — Deteksi krisis dan referral hotline darurat (119 ext 8)
- **Dashboard Insight** — Faktor risiko utama dan rekomendasi personal
- **Voice Input** — Input suara via Web Speech API
- **Dark Mode** — Tema gelap untuk kenyamanan

---

## Tech Stack

| Layer | Teknologi |
|-------|-----------|
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) |
| **Backend** | FastAPI (Python 3.11), Flask (demo server) |
| **AI/ML** | LightGBM, XGBoost, Random Forest, SHAP |
| **NLP** | IndoBERT (Sentiment), Keyword Extraction, Cognitive Pattern Detection |
| **Conversation** | Google Gemini 2.5 Flash |
| **Database** | Supabase (PostgreSQL) |
| **Security** | Fernet Encryption, API Key Rotation |

---

## Arsitektur Sistem

```
User Input (teks/suara)
    |
    v
[Safety Check] ──> Krisis? ──> Emergency Response + Hotline
    |
    v (aman)
[Gemini RINA] ──> Respons natural + JSON data extraction
    |
    v
[NLP Pipeline] ──> IndoBERT sentiment + keyword + cognitive patterns
    |
    v
[Feature Store] ──> Update fitur harian (7-day rolling)
    |
    v
[ML Prediction] ──> LightGBM burnout classification (LOW/MEDIUM/HIGH)
    |
    v
[Dashboard] ──> Risk level + Top factors + Recommendations
```

---

## Setup Lokal

### 1. Clone Repository

```bash
git clone <repo-url>
cd ProjekAI
```

### 2. Setup Python Environment

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

### 3. Konfigurasi Environment Variables

Buat file `.env` di root (contoh di `.env.example`):

```
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_key
ENCRYPTION_KEY=your_fernet_key
```

### 4. Training Model (jika belum ada file .pkl)

```bash
python scripts/train_model.py
```

Output: `ml_models/burnout_model.pkl`, `scaler.pkl`, `shap_explainer.pkl`

### 5. Jalankan Web Demo

```bash
set PYTHONPATH=.
python web_demo/run_server.py
```

Buka: `http://localhost:5000`

### 6. Jalankan FastAPI Server (opsional)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: `http://localhost:8000/docs`

---

## Struktur Proyek

```
ProjekAI/
├── app/                          # Backend FastAPI
│   ├── api/                      # API endpoints
│   │   ├── chat.py               # Chat HTTP + WebSocket
│   │   └── dashboard.py          # Dashboard API
│   ├── services/                 # Business logic
│   │   ├── gemini.py             # RINA conversation engine
│   │   ├── nlp.py                # NLP pipeline (IndoBERT, keywords)
│   │   ├── prediction.py         # ML + rule-based prediction
│   │   ├── safety.py             # Crisis detection
│   │   ├── trend_analysis.py     # Trend prediction + recommendations
│   │   ├── features.py           # Feature store (7-day rolling)
│   │   ├── encryption.py         # Fernet encryption
│   │   ├── feedback.py           # User feedback
│   │   └── supabase_client.py    # Database client
│   └── main.py                   # FastAPI app entry point
├── web_demo/                     # Flask demo server
│   ├── static/
│   │   ├── css/style.css         # Design system
│   │   ├── js/app.js             # Frontend logic
│   │   └── index.html            # Main UI
│   └── run_server.py             # Flask server
├── scripts/                      # Utility scripts
│   ├── train_model.py            # ML training pipeline
│   ├── merge_synthetic_batches.py
│   ├── synthetic_to_csv.py
│   └── schema.sql                # Database schema
├── Data/                         # Datasets
│   ├── Employee Burnout Dataset/
│   ├── processed/                # Train/test splits
│   └── synthetic/                # Synthetic conversations
├── ml_models/                    # Trained model artifacts
│   ├── burnout_model.pkl
│   ├── scaler.pkl
│   ├── shap_explainer.pkl
│   └── model_card.json
├── Notebooks/
│   └── eda_burnout.ipynb         # EDA notebook
├── tests/                        # Unit tests
├── promptchat.md                 # Prompt untuk generate training data
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/health` | Health check |
| POST | `/api/chat` | Chat dengan RINA |
| WS | `/api/chat/ws/{user_id}` | WebSocket real-time chat |
| GET | `/api/dashboard/{user_id}` | Dashboard data |
| POST | `/safety/check` | Safety check manual |
| POST | `/predict` | Prediksi burnout manual |

---

## Model ML

- **Algoritma Terpilih:** LightGBM
- **CV AUC-ROC:** 0.954 (weighted, one-vs-rest)
- **Recall HIGH:** 0.701
- **Label:** LOW (0), MEDIUM (1), HIGH (2)
- **Explainability:** SHAP TreeExplainer

Lihat `ml_models/model_card.json` untuk detail lengkap.

---

## Catatan Etis

> **LifeLens adalah screening tool, BUKAN pengganti diagnosis medis.**

- Sistem ini tidak dimaksudkan sebagai alat diagnosis klinis
- Jika dalam kondisi darurat, hubungi **119 ext 8** (Into The Light Indonesia)
- Data pengguna dienkripsi menggunakan Fernet dan tidak dibagikan ke pihak ketiga
- Model memiliki keterbatasan pada dataset berbahasa Inggris dan perlu validasi lebih lanjut

---

## Lisensi

Proyek ini dibuat untuk keperluan akademis — Tugas Akhir D3 Teknik Informatika USU.
