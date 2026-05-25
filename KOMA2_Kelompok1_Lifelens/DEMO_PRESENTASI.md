# Demo Presentasi LifeLens

## Status Demo

- Chat AI RINA tetap aktif.
- TTS chat dimatikan sementara supaya demo tidak macet menunggu generate suara.
- Preview suara di settings tetap bisa diputar dari file audio statis yang sudah dibuat.
- Karakter RINA tetap berubah ekspresi dan menampilkan dialog ala visual novel.
- Tombol speaker dan preview suara dibuat nonaktif untuk mode demo.

## Cara Menjalankan

```powershell
cd "M:\KOMA2_Kelompok1_Lifelens"
.\start_backend.ps1
```

Buka terminal kedua:

```powershell
cd "M:\KOMA2_Kelompok1_Lifelens"
.\start_frontend.ps1
```

Buka:

```text
http://127.0.0.1:5173
```

## Flow Demo 3 Menit

1. Onboarding
   - Masukkan nama user.
   - Tunjukkan RINA menyapa user.

2. Chat Curhat
   - Kirim contoh:

```text
rina, aku capek banget akhir-akhir ini
```

   - Tunjukkan RINA membalas dengan gaya natural dan bubble dialog.

3. Ekspresi Karakter
   - Tunjukkan karakter RINA berubah ke ekspresi seperti listening, thinking, concerned, atau talking.
   - Tunjukkan dialog besar di area karakter seperti adegan otome/visual novel.

4. Dashboard
   - Klik tombol dashboard.
   - Tunjukkan ringkasan risiko, faktor, dan rekomendasi.

5. Penutup
   - Jelaskan bahwa TTS clone sudah disiapkan, tetapi autoplay chat dimatikan untuk demo agar presentasi stabil.
   - Preview suara tetap bisa diputar dari audio statis.

## Outline PPT

1. Judul
   - LifeLens: AI Companion untuk Deteksi Risiko Burnout

2. Latar Belakang
   - Banyak orang sulit menyadari stres dan burnout sejak awal.
   - Chatbot biasa terasa kaku, sehingga user kurang nyaman bercerita.

3. Solusi
   - LifeLens menghadirkan RINA sebagai teman bicara virtual.
   - RINA membaca sinyal emosi dari chat dan memberi respons natural.

4. Fitur Utama
   - Chat AI dengan gaya bahasa santai.
   - Safety check untuk kondisi krisis.
   - Ekstraksi fitur psikologis dari percakapan.
   - Prediksi risiko burnout.
   - Dashboard rekomendasi.
   - Visual novel style character dialog.

5. Arsitektur
   - Frontend: React + Vite.
   - Backend: FastAPI.
   - AI chat: Gemini dengan fallback lokal.
   - NLP dan feature tracking.
   - ML prediction untuk burnout risk.
   - TTS clone disiapkan, dimatikan saat demo.

6. Alur Sistem
   - User mengirim pesan.
   - Backend melakukan safety check.
   - RINA menghasilkan respons.
   - NLP mengekstrak fitur.
   - Model memprediksi risiko.
   - Frontend menampilkan bubble chat, ekspresi, dan rekomendasi.

7. Demo
   - Tampilkan onboarding.
   - Kirim pesan curhat.
   - Tampilkan respons RINA.
   - Tampilkan dashboard.

8. Kesimpulan
   - LifeLens membantu user bercerita dengan pengalaman yang lebih personal.
   - Sistem menggabungkan AI chat, NLP, prediksi risiko, dan visual character.
