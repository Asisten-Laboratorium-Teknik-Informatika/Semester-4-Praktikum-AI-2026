# 📋 PROJECT OVERVIEW — LifeLens
**Baca ini PERTAMA sebelum dokumen lain apapun.**

---

## 🧠 Apa yang Kita Bangun?

**LifeLens** adalah website yang membantu mendeteksi risiko burnout melalui percakapan — bukan form panjang. User ngobrol santai dengan karakter AI bernama **RINA**, dan sistem di balik layar menganalisis pola percakapan itu untuk memprediksi kondisi mental mereka.

Hasil akhirnya: user mendapatkan insight seperti *"minggu ini kamu berisiko MEDIUM, karena tidur kurang dan beban kerja tinggi."*

---

## 👥 Tim & Tanggung Jawab

| Nama | NIM | Fokus Utama |
|---|---|---|
| **Nadya** | 241712040 | Data — EDA, bersihkan dataset, siapkan untuk model |
| **Argya** | 241712028 | Tampilan — buat website-nya, animasi, deploy |
| **Fikri** | 241712027 | Otak — server backend, model ML, safety system |
| **Michael** | 241712042 | Bahasa — NLP, persona RINA, desain karakter 2D |

> **Karakter 2D RINA** dikerjakan bersama **Fikri + Michael**.

---

## ⚠️ Syarat Akademis — Wajib Dipenuhi

Proyek **harus** mencakup 4 tahap. Ini yang dinilai dosen:

```
Tahap 1 → EDA           → Analisis & pahami data burnout       [Nadya]
Tahap 2 → Preprocessing → Bersihkan & siapkan data             [Nadya]
Tahap 3 → Modeling      → Buat & latih model prediksi          [Fikri]
Tahap 4 → Implementasi  → Masukkan ke website yang bisa jalan  [Semua]
```

### Boleh Pakai Gemini API? Apa Batasannya?

**Boleh** — tapi hanya untuk bagian percakapan (RINA ngobrol dengan user). Model yang memprediksi burnout **harus buatan tim sendiri**.

Analoginya sederhana:
```
Dokter pakai stetoskop buatan pabrik lain → untuk kumpulkan data
Tapi diagnosisnya dari si dokter sendiri  → itu yang dinilai

Dalam proyek ini:
  Gemini API  = stetoskop  → kumpulkan info dari obrolan user
  Model Tim   = dokternya  → putuskan: LOW / MEDIUM / HIGH
```

---

## 🗺️ Alur Sistem — Versi Sederhana

Ini gambaran besar apa yang terjadi saat user pakai LifeLens:

```
1. User buka website & ngobrol dengan RINA
        ↓
2. Gemini API proses percakapan → ekstrak data
   contoh: "tidur 5 jam, deadline banyak, mood jelek"
        ↓
3. Pipeline tim (NLP + ML) analisis data itu
        ↓
4. Hasil: MEDIUM RISK
   Penjelasan: "Tidur kurang + beban kerja tinggi"
        ↓
5. User lihat insight & rekomendasi di dashboard
```

---

## 🔬 Apa yang Diukur?

Sistem mengukur **3 dimensi burnout** dari standar psikologi internasional (MBI):

| Dimensi | Artinya | Sinyal yang Dicari |
|---|---|---|
| **Exhaustion** | Kehabisan energi | "Capek banget, tidur 4 jam" |
| **Cynicism** | Mulai tidak peduli | "Kerjaan ini percuma aja" |
| **Reduced Efficacy** | Merasa tidak berguna | "Mau usaha pun sama aja" |

> Burnout tidak muncul tiba-tiba — berkembang selama **berminggu-minggu**. Makanya sistem tracking selama **7–14 hari**, bukan sekali.

---

## ✅ Semua Keputusan Teknis (JANGAN Diubah Tanpa Diskusi Tim)

| Komponen | Pilihan | Alasan Singkat |
|---|---|---|
| Tampilan website | React + Vite | Ekosistem animasi terlengkap |
| Animasi UI (tombol, bubble chat) | Framer Motion | Mudah di React, hasil mulus |
| Animasi karakter 2D | GSAP | Terbaik untuk gerakkan file SVG |
| AI percakapan | Gemini 2.0 Flash (API gratis) | Support bahasa Indonesia sangat bagus |
| Model prediksi | XGBoost + LightGBM + Random Forest | Latih semua, pilih yang terbaik |
| Penjelasan hasil model | SHAP | Bisa tunjukkan "kenapa HIGH" ke user |
| Database | Supabase (PostgreSQL cloud) | Gratis, ada dashboard visual |
| Server | FastAPI (Python) | Ringan, cocok untuk ML |
| Suara RINA (default) | edge-tts | Gratis, support bahasa Indonesia |
| Login user | Google + Email + Anonymous | Semua via Supabase, mudah |
| Deploy website | Vercel (frontend) | Gratis, auto dari GitHub |
| Deploy server | Railway (backend) | Gratis untuk skala mahasiswa |

---

## 🚨 4 Prinsip yang Tidak Boleh Dilanggar

**1. Safety dulu, fitur belakangan**
Sebelum apapun dibangun, sistem harus bisa deteksi jika user dalam kondisi darurat. Ini tugas Fikri di hari pertama.

**2. Ini bukan diagnosis medis**
Selalu ada tulisan jelas bahwa ini screening tool, bukan pengganti psikolog.

**3. Data user dienkripsi**
Teks percakapan tidak boleh tersimpan sebagai teks biasa. Harus dienkripsi.

**4. Akurasi lebih penting dari tampilan keren**
Model yang akurat dengan UI sederhana lebih baik dari UI cantik tapi prediksinya tidak valid.

---

## 📖 Cara Membaca Semua Dokumen

Baca sesuai peranmu:

```
SEMUA ANGGOTA — mulai dari sini dulu:
  ✅ requirements.md     → install semua yang dibutuhkan
  ✅ planning.md         → lihat jadwal & target

NADYA  → 08_dataset.md + 03_ai_ml_pipeline.md + nadya.md
ARGYA  → style.md + 06_frontend_ui.md + argya.md
FIKRI  → 07_backend_database.md + 03_ai_ml_pipeline.md + fikri.md
MICHAEL → 04_conversation_persona.md + assets.md + michael.md
```
