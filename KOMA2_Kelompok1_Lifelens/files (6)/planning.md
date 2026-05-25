# 🗓️ PLANNING & ROADMAP — LifeLens
> Jadwal kerja tim, target per sprint, dan definisi "selesai".

---

## 🎯 5 Prinsip Pengembangan

Sebelum mulai, semua anggota tim harus sepakat pada prinsip ini:

```
1. SAFETY DULU, BARU FITUR
   → Fikri harus selesaikan safety layer sebelum fitur apapun
   
2. MODEL DULU, BARU UI CANTIK
   → Pipeline ML harus valid sebelum fokus ke animasi
   
3. JALAN DULU, BARU SEMPURNA
   → MVP yang jalan > fitur lengkap yang belum selesai
   
4. DOKUMENTASI SEPANJANG JALAN
   → Tulis keputusan penting saat diambil, jangan nunggu akhir
   
5. TEST DI HP SEJAK AWAL
   → Jangan baru test mobile di minggu terakhir
```

---

## 📅 Sprint Plan (8 Minggu)

### 🔴 SPRINT 0 — Setup (Minggu 1)
**Target: Semua tools terinstall, akun terdaftar, repo siap**

Semua anggota:
```
□ Install Git, Node.js 20+, Python 3.11+, VS Code
□ Buat akun GitHub, Supabase, Vercel, Railway, Kaggle
□ Dapatkan Gemini API key (Google AI Studio — gratis)
□ Clone repo tim
□ Bisa run "hello world" masing-masing bagian
```

Nadya:
```
□ Download dataset Kaggle (burnout + mental health)
□ Setup Jupyter Notebook
□ Coba buka dataset, lihat isinya
```

Argya:
```
□ Init project React + Vite
□ Setup Tailwind CSS
□ Buat halaman kosong yang bisa dibuka di browser
```

Fikri:
```
□ Init project FastAPI
□ Server bisa jalan di localhost:8000
□ Koneksi ke Supabase berhasil
□ SELESAIKAN safety.py (ini PRIORITAS #1)
```

Michael:
```
□ Download model IndoBERT dari HuggingFace
□ Test: analisis sentimen 1 kalimat berhasil
□ Setup spaCy
□ Mulai sketsa desain karakter RINA (kasar pun tidak apa-apa)
```

---

### 🟡 SPRINT 1 — Core Pipeline (Minggu 2–3)
**Target: Pipeline utama bisa jalan, meski sederhana**

Nadya:
```
□ EDA lengkap (6 analisis di 03_ai_ml_pipeline.md)
□ Preprocessing pipeline selesai
□ Dataset bersih dan siap untuk training
□ Mulai generate synthetic dataset via Gemini API
```

Argya:
```
□ Chat interface bisa kirim dan terima pesan (teks)
□ WebSocket terhubung ke backend Fikri
□ Onboarding: pilihan login (Google/email/anonymous)
□ Layout dasar desktop + mobile
```

Fikri:
```
□ Latih 3 model (Random Forest, XGBoost, LightGBM)
□ Evaluasi dan pilih model terbaik
□ Model tersimpan sebagai .pkl
□ Endpoint prediksi bisa dipanggil
□ Rule-based scoring sebagai fallback MVP
```

Michael:
```
□ NLP pipeline selesai (sentimen + keyword extraction)
□ System prompt RINA di Gemini selesai dan ditest
□ JSON extraction dari respons Gemini berjalan
□ SVG karakter RINA base + minimal 4 ekspresi
```

---

### 🟢 SPRINT 2 — Integrasi (Minggu 4–5)
**Target: Semua komponen terhubung, flow utama berjalan end-to-end**

Semua anggota bekerja bersama:
```
□ User chat → Gemini → JSON → NLP → ML → output → tampil di frontend
□ Dashboard: risk card + top factors tampil
□ Test flow utama dari ujung ke ujung
□ Fix semua yang masih error
```

Argya:
```
□ Karakter RINA SVG tampil di sidebar
□ Risk card component selesai
□ Settings halaman (pilih bahasa suara)
```

Fikri:
```
□ Feature store: update data per sesi
□ Hitung tren 7 hari (rolling average + slope)
□ SHAP explanation terhubung ke output
```

Michael:
```
□ Adaptive language matching (RINA ikut gaya user)
□ Animasi GSAP karakter: talking + listening state
□ Koordinasi SVG IDs dengan Fikri
```

Nadya:
```
□ Fitur longitudinal selesai (sentiment_slope_7d dll)
□ Retrain model dengan dataset final (Kaggle + synthetic)
□ Dokumentasi EDA notebook rapi
```

---

### 🔵 SPRINT 3 — Polish & Voice (Minggu 6–7)
**Target: Experience yang terasa profesional**

Argya:
```
□ Framer Motion animasi di semua komponen UI
□ Mobile responsiveness sempurna
□ Adaptive animation (desktop full, mobile lite)
□ Error states dan loading states yang proper
□ Onboarding voice selection dengan preview
```

Fikri + Michael (karakter & suara):
```
□ Voice: TTS edge-tts terintegrasi
□ Lip sync karakter dengan audio
□ Semua 7 ekspresi karakter GSAP selesai
□ Multilingual voice router (ID/JP/EN/KR)
```

Nadya:
```
□ Bias audit model
□ Finalize model card
□ EDA notebook siap dipresentasikan
```

---

### 🏁 SPRINT 4 — Deploy & Presentasi (Minggu 8)
**Target: Website bisa diakses publik, laporan siap**

```
□ Deploy frontend ke Vercel
□ Deploy backend ke Railway
□ Test semua fitur di URL production
□ User testing dengan minimal 5 orang di luar tim
□ Fix bug dari feedback
□ Laporan akhir selesai
□ Slide presentasi selesai
□ Demo rehearsal
```

---

## 🏆 Definition of Done

### MVP (Minimum — harus ada saat demo):
```
✅ User bisa chat dengan RINA
✅ RINA merespons dengan karakter yang tepat
✅ Risk score ditampilkan (rule-based sudah cukup untuk MVP)
✅ Safety protocol berjalan (test dengan kata kunci krisis)
✅ Website bisa dibuka di HP
✅ Disclaimer selalu tampil
✅ Tidak ada data plain text di database
```

### Profesional (target sebenarnya):
```
✅ Semua MVP done
✅ Model ML proper dengan AUC > 0.75
✅ SHAP explanation ditampilkan ke user
✅ Karakter 2D minimal 4 ekspresi + animasi
✅ Voice input/output berjalan
✅ Dashboard tren 7 hari
✅ Deploy di Vercel + Railway
✅ EDA notebook rapi + bisa dipresentasikan
✅ Model card terdokumentasi
```

---

## 🤝 Aturan Kerja Tim

### Git & GitHub
```
Cara buat branch baru untuk setiap fitur:
  git checkout -b feature/nama-fitur

Cara commit yang deskriptif:
  feat: tambah chat bubble animation   ← fitur baru
  fix: perbaiki websocket disconnect   ← perbaikan bug
  docs: update README                  ← dokumentasi

Pull Request: minimal 1 anggota tim lain review sebelum merge ke main
```

### Naming Convention
```
Python files:   snake_case → feature_extraction.py
React files:    PascalCase → ChatBubble.jsx
CSS classes:    kebab-case → chat-bubble
```

### Daily Check-in (10 menit/hari)
```
Setiap hari kerja, masing-masing jawab:
1. Kemarin saya mengerjakan: ...
2. Hari ini saya akan: ...
3. Butuh bantuan dengan: ...
```

### Kalau Stuck
```
1. Baca dokumentasi resmi dulu (FastAPI docs, React docs, dll)
2. Coba 30 menit sendiri
3. Tanya ke anggota tim yang relevan
4. Kalau masih stuck → minta bantuan dosen/asisten
```
