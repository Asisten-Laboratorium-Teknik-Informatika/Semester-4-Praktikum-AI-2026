# 🤖 TUGAS FIKRI — Backend, Model ML & Karakter 2D
> Muhammad Fikri Ramadhan | 241712027
> Panduan lengkap tugasmu dari awal hingga selesai.

---

## 🎯 Peranmu dalam Tim

Fikri adalah **otak dan tulang punggung teknis** proyek ini. Server yang melayani semua request, model yang memprediksi burnout, dan safety system yang melindungi user — semuanya tanggung jawabmu.

```
Yang kamu hasilkan untuk tim:
├── Server FastAPI yang berjalan dan melayani semua request
├── Safety layer (HARUS selesai hari pertama)
├── 3 model ML terlatih + evaluasi + model terpilih
├── SHAP explainability (jelaskan prediksi ke user)
├── Pipeline prediksi real-time
├── Deploy ke Railway
└── (bersama Michael) GSAP animation controller karakter RINA
```

---

## 📦 Deliverables (Yang Harus Diserahkan)

| # | Output | Kapan |
|---|---|---|
| 1 | `safety.py` berjalan dan ditest | Sprint 0 — **HARI PERTAMA** |
| 2 | Server FastAPI jalan di localhost:8000 | Sprint 0 |
| 3 | Koneksi Supabase berhasil | Sprint 0 |
| 4 | Rule-based scoring (fallback MVP) | Sprint 1 |
| 5 | 3 model terlatih + evaluasi lengkap | Sprint 1 |
| 6 | Model terpilih + SHAP tersimpan | Sprint 1 |
| 7 | Endpoint prediksi berjalan | Sprint 2 |
| 8 | Feature store 7-hari berjalan | Sprint 2 |
| 9 | (dengan Michael) GSAP CharacterController | Sprint 2-3 |
| 10 | Deploy ke Railway | Sprint 4 |

---

## 🛡️ TUGAS 1 — Safety Layer (KERJAKAN INI PERTAMA KALI)

### Apa yang Dibuat
File `app/services/safety.py` — fungsi yang **memeriksa setiap pesan user** sebelum diproses apapun.

### Kenapa Harus Pertama?
Karena kalau user sedang dalam krisis dan sistem melanjutkan proses normal, itu berbahaya. Safety tidak bisa menunggu fitur lain selesai.

### Yang Harus Dilakukan

Buat daftar kata/frasa yang mengindikasikan krisis (cukup 15-20 frasa yang paling umum), lalu buat fungsi yang:
1. Menerima teks pesan user
2. Mengecek apakah ada kata/frasa krisis di dalamnya
3. Kalau ada → kembalikan pesan darurat + nomor hotline
4. Kalau tidak ada → kembalikan None (aman, lanjutkan)

**Contoh konsep (bukan kode final):**
```python
# Daftar kata yang harus dicek (kembangkan sendiri)
KATA_KRISIS = ['ingin mati', 'bunuh diri', 'tidak ingin ada', ...]

def check_crisis(pesan: str):
    pesan_lower = pesan.lower()
    
    for kata in KATA_KRISIS:
        if kata in pesan_lower:
            return {
                'response': 'Aku dengar kamu...[pesan empati]',
                'hotline': 'Into The Light: 119 ext 8',
                'stop': True  # jangan lanjutkan ke proses lain
            }
    
    return None  # aman, lanjutkan
```

### Cara Test Safety Layer
Buat file test kecil untuk memastikan fungsinya benar:
```python
# Test manual — jalankan ini untuk verifikasi
hasil = check_crisis("ingin mati rasanya")
assert hasil is not None, "GAGAL: krisis tidak terdeteksi!"

hasil = check_crisis("hari ini capek banget")
assert hasil is None, "GAGAL: kalimat normal dianggap krisis!"

print("Safety layer berfungsi dengan benar ✓")
```

---

## ⚙️ TUGAS 2 — Setup Server FastAPI

### Apa yang Dibuat
File `app/main.py` — titik masuk aplikasi server.

### Yang Harus Ada di main.py

**FastAPI app:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LifeLens API")

# CORS: izinkan frontend akses backend
# (tanpa ini, browser akan block semua request)
app.add_middleware(CORSMiddleware, ...)
```

**Error handler global:**
Kalau ada error di mana saja, server tidak boleh crash. Tambahkan handler yang:
- Print error lengkap ke terminal (untuk debugging)
- Kirim pesan error yang informatif ke frontend (bukan halaman kosong)

**Health check endpoint:**
```
GET /health
→ Return: {"status": "ok"}
→ Berguna untuk cek apakah server jalan
```

### Cara Jalankan Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# --reload: otomatis restart kalau kode berubah (untuk development)

# Buka browser: http://localhost:8000/docs
# Akan muncul Swagger UI — dokumentasi API otomatis dari FastAPI!
```

---

## 📊 TUGAS 3 — Rule-Based Scoring (Fallback MVP)

### Apa yang Dibuat
Fungsi di `app/services/prediction.py` yang menghitung risk level berdasarkan aturan sederhana — **tanpa ML model**.

### Kenapa Perlu
Saat Sprint 1, model ML belum tentu sudah siap. Rule-based scoring memungkinkan frontend Argya sudah bisa menampilkan hasil sementara model masih dikembangkan.

### Logika Sederhananya
Sistem memberi "skor" berdasarkan tiap fitur, lalu tentukan level:

```
Tidur < 5 jam      → +3 poin (sangat kurang)
Tidur 5-6 jam      → +2 poin (kurang)
Beban kerja ≥ 9    → +3 poin
Beban kerja ≥ 7    → +2 poin
Sentimen memburuk  → +2-3 poin (berdasarkan tingkat penurunan)
Recovery buruk     → +2 poin
Sosial menarik diri → +1 poin

Total 0-3  → LOW
Total 4-7  → MEDIUM
Total 8+   → HIGH
```

**Contoh konsep:**
```python
def rule_based_predict(features: dict) -> dict:
    skor = 0
    alasan = []
    
    if features.get('sleep_hours', 7) < 5:
        skor += 3
        alasan.append("Tidur sangat kurang")
    # ... cek fitur lainnya ...
    
    if skor >= 8: level = "HIGH"
    elif skor >= 4: level = "MEDIUM"
    else: level = "LOW"
    
    return {"risk_level": level, "factors": alasan[:3]}
```

---

## 🤖 TUGAS 4 — Training 3 Model ML

### Apa yang Dilakukan
Buat script `scripts/train_model.py` yang:
1. Load dataset dari Nadya
2. Latih 3 algoritma berbeda
3. Evaluasi dan bandingkan
4. Simpan pemenang + alat lainnya ke file

### Tiga Algoritma yang Dilatih

**Random Forest** — pakai `RandomForestClassifier` dari scikit-learn
- Setting: `n_estimators=200`, `class_weight='balanced'`
- Kenapa balanced: data burnout imbalanced, ini handle otomatis

**XGBoost** — pakai `XGBClassifier` dari library xgboost
- Setting standar dulu, tuning nanti kalau perlu

**LightGBM** — pakai `LGBMClassifier` dari library lightgbm
- Setting: `verbose=-1` (matikan output yang terlalu banyak)

### Cara Evaluasi

Untuk setiap model, hitung:
```
AUC-ROC   → angka 0-1, makin tinggi makin baik (target > 0.75)
Recall@HIGH → berapa persen kasus HIGH burnout berhasil dideteksi
F1-score  → keseimbangan precision dan recall
Confusion Matrix → visualisasi kesalahan prediksi per kategori
```

**Jangan hanya lihat accuracy!** Karena data imbalanced, accuracy 90% bisa berarti model tidak pernah mendeteksi HIGH burnout sama sekali.

### Pilih Pemenang
Model dengan AUC-ROC tertinggi di cross-validation (bukan hanya test set) yang dipilih.

### Yang Harus Disimpan
```
ml_models/
├── burnout_model.pkl     ← model terpilih
├── scaler.pkl            ← StandardScaler yang sudah di-fit
├── shap_explainer.pkl    ← untuk hitung SHAP
└── model_card.json       ← dokumentasi model (untuk laporan)
```

---

## 🔮 TUGAS 5 — SHAP Explainability

### Apa itu SHAP?
Library Python yang menjelaskan kenapa model membuat prediksi tertentu.

### Untuk Apa?
Bukan hanya untuk user — SHAP juga penting untuk laporan. Bisa menunjukkan fitur mana yang paling berpengaruh pada prediksi model.

### Yang Harus Dibuat
Fungsi yang menerima satu set fitur user dan mengembalikan 3 faktor teratas:

```python
def explain_prediction(features: dict) -> list:
    """
    Input:  dict fitur user
    Output: list 3 faktor dengan penjelasan bahasa manusia
    
    Contoh output:
    [
      "Sentimen memburuk 7 hari terakhir",
      "Tidur hanya 5 jam",
      "Beban kerja 8/10"
    ]
    """
```

Translate nama fitur teknis ke bahasa manusia:
```
'sleep_hours'         → "Durasi tidur"
'workload_score'      → "Beban kerja"
'sentiment_slope_7d'  → "Tren suasana hati 7 hari"
```

---

## 🔐 TUGAS 6 — Enkripsi Data

### Apa yang Dibuat
File `app/services/encryption.py` dengan dua fungsi:
- `encrypt_text(teks)` → ubah teks jadi teks terenkripsi
- `decrypt_text(teks_terenkripsi)` → balikkan ke teks asli

### Menggunakan Apa
Library `cryptography` dengan algoritma Fernet (AES-256).

### Yang Penting Dipahami
```
Kunci enkripsi DISIMPAN sebagai environment variable di .env
JANGAN hardcode kunci di dalam kode!
Kenapa: kalau kode di-commit ke GitHub, kunci terlihat semua orang
```

### Cara Generate Kunci
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy outputnya → taruh di .env sebagai ENCRYPTION_KEY
```

---

## 🎭 TUGAS 7 — GSAP CharacterController (bersama Michael)

### Pembagian Kerja
- **Michael** membuat file SVG karakter dengan ID yang benar
- **Fikri** membuat `CharacterController.js` dengan logika GSAP

### Yang Harus Dibuat

File `src/components/character/CharacterController.js`:
- Fungsi `init()` — mulai animasi idle (napas, kedip)
- Fungsi `setState(state)` — ganti ekspresi berdasarkan state
- Fungsi `setMouthOpen(amount)` — untuk lip sync (0.0-1.0)

**Konsep setState (ilustrasi):**
```javascript
function setState(newState) {
  // Sembunyikan ekspresi sekarang
  gsap.to(`#expression-${currentState}`, { opacity: 0 })
  
  // Tampilkan ekspresi baru
  gsap.to(`#expression-${newState}`, { opacity: 1 })
  
  currentState = newState
}
```

---

## 🚀 TUGAS 8 — Deploy ke Railway

### Langkah-langkah
```
1. Buat file Dockerfile di root backend
   (Railway perlu ini untuk tahu cara build server)

2. Push kode ke GitHub

3. Buka railway.app → New Project
   → Deploy from GitHub repo → pilih lifelens-backend

4. Tambahkan Environment Variables di Railway dashboard:
   SUPABASE_URL, SUPABASE_SERVICE_KEY, GEMINI_API_KEY,
   ENCRYPTION_KEY, REDIS_URL, ALLOWED_ORIGINS

5. Railway otomatis build dan deploy

6. Dapat URL: https://lifelens-backend.railway.app
   Kasih URL ini ke Argya untuk dimasukkan ke VITE_API_URL
```

---

## ✅ Checklist Tugasmu

```
SPRINT 0:
☑ safety.py selesai dan DITEST
☑ Server FastAPI jalan di localhost:8000
☑ Koneksi Supabase berhasil
□ Tabel database dibuat (SQL dari 02_system_architecture.md)

SPRINT 1:
☑ Rule-based scoring berjalan
□ Chat WebSocket endpoint dasar berjalan
☑ 3 model dilatih dengan evaluasi lengkap
☑ Model terpilih + scaler + SHAP tersimpan
☑ Model card.json terdokumentasi

SPRINT 2:
□ Endpoint prediksi terhubung ke WebSocket
☑ Feature store update per sesi
☑ 7-day trend calculation berjalan
□ Koordinasi dengan Michael untuk SVG IDs
☑ CharacterController.js dasar berjalan

SPRINT 3:
□ Semua 7 state karakter GSAP selesai
☑ Lip sync controller berjalan
☑ Enkripsi data berjalan

SPRINT 4:
□ Deploy ke Railway — URL bisa diakses
□ Semua environment variables terkonfigurasi
☑ Health check endpoint berjalan
□ Koordinasi dengan Argya: beri URL backend
```
