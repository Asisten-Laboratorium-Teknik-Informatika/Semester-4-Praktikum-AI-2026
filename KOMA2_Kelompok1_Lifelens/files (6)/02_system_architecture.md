# 🏗️ SYSTEM ARCHITECTURE — LifeLens
> Dokumen ini menjelaskan bagaimana semua bagian sistem terhubung.
> Baca sebelum mulai coding apapun.

---

## 🧠 Gambaran Besar

Sistem LifeLens terdiri dari **3 bagian utama** yang harus dibuat:

```
┌─────────────────────────────────────────────────────┐
│  FRONTEND (Argya)                                   │
│  → Yang user lihat: website, chat, karakter, grafik │
├─────────────────────────────────────────────────────┤
│  BACKEND (Fikri)                                    │
│  → Otak di server: terima pesan, proses, prediksi   │
├─────────────────────────────────────────────────────┤
│  DATABASE (Supabase)                                │
│  → Penyimpanan: data user, riwayat, hasil prediksi  │
└─────────────────────────────────────────────────────┘
```

Ketiganya saling bicara. Frontend mengirim pesan user ke backend. Backend memproses dan menyimpan ke database. Hasilnya dikirim balik ke frontend untuk ditampilkan ke user.

---

## 🔄 Perjalanan Satu Pesan User (Step by Step)

Ini yang terjadi saat user kirim satu pesan ke RINA:

### Step 1 — User Kirim Pesan
User mengetik "capek banget, deadline numpuk" lalu tekan kirim.
Frontend mengirim teks itu ke backend melalui **WebSocket** (koneksi real-time).

### Step 2 — Safety Check (PERTAMA KALI, SEBELUM APAPUN)
Backend langsung cek: apakah pesan mengandung kata-kata krisis?
```
Contoh keyword yang dicek:
"ingin mati", "bunuh diri", "tidak ingin ada"

Jika ditemukan → kirim pesan darurat + nomor hotline ke user
Jika tidak → lanjut ke step berikutnya
```
> **Kenapa ini harus pertama?** Karena keselamatan user lebih penting dari fitur apapun.

### Step 3 — Kirim ke Gemini API
Backend mengirim pesan user ke Gemini dengan **instruksi khusus** (system prompt):
- "Kamu adalah RINA, teman yang hangat..."
- "Balas dengan natural, jangan robotik..."
- "Ekstrak data: jam tidur, beban kerja, mood..."

Gemini membalas dua hal:
1. Teks respons RINA yang natural (langsung dikirim ke user)
2. Data terstruktur tersembunyi: `{ sleep: 5, workload: 8, mood: 3 }`

### Step 4 — NLP Pipeline (Michael)
Backend memproses teks percakapan user dengan NLP:
- Analisis sentimen: apakah pesannya positif/negatif?
- Cari kata kunci: "capek", "deadline", "tidak bisa"
- Hitung pola bahasa negatif

### Step 5 — Feature Engineering (Nadya's pipeline)
Gabungkan semua data menjadi satu daftar angka:
```
[ tidur:5, beban:8, mood:3, sentimen:-0.6, trend:-0.3, ... ]
```
Ini yang akan dimasukkan ke model ML.

### Step 6 — Prediksi (Fikri's model)
Model ML buatan tim menganalisis daftar angka itu:
```
Input:  [ tidur:5, beban:8, mood:3, ... ]
Output: MEDIUM RISK, confidence: 73%
        Faktor utama: "Tidur kurang + Beban kerja tinggi"
```

### Step 7 — Kirim Hasil ke Frontend
Backend mengirim:
- Teks balasan RINA (untuk chat bubble)
- Risk level terbaru (untuk risk card di dashboard)
- Top 3 faktor penyebab (dari SHAP)

### Step 8 — Tampilkan & Suarakan
Frontend:
- Tampilkan chat bubble RINA dengan animasi
- Update risk card
- Generate suara via TTS → sinkron dengan mulut karakter 2D

---

## 🏛️ 6 Layer Backend

Backend punya 6 lapisan yang dilewati setiap pesan, berurutan:

| Layer | Nama | Dikerjakan oleh | Fungsi |
|---|---|---|---|
| 1 | **Safety Gate** | Fikri | Cek krisis — tidak bisa dilewati |
| 2 | **Conversation Engine** | Michael | Kirim ke Gemini, dapat respons |
| 3 | **NLP Pipeline** | Michael | Analisis teks, ekstrak fitur bahasa |
| 4 | **Feature Store** | Nadya | Gabungkan fitur, hitung tren 7 hari |
| 5 | **Prediction Engine** | Fikri | Model ML beri prediksi + SHAP |
| 6 | **Output Composer** | Fikri | Format hasil untuk dikirim ke frontend |

---

## 🗄️ Apa yang Disimpan di Database?

Database Supabase menyimpan 4 jenis data:

**Tabel `users`** — Data akun user
```
Menyimpan: nama, pengaturan suara, apakah sudah beri consent
```

**Tabel `sessions`** — Setiap sesi ngobrol
```
Menyimpan: tanggal, durasi, risk level hasil prediksi,
           top 3 faktor, ringkasan 1-2 kalimat
```

**Tabel `daily_features`** — Data harian (untuk tren 7 hari)
```
Menyimpan: jam tidur, skor beban kerja, mood, sentimen
           Ini yang dipakai untuk hitung tren
```

**Tabel `conversation_texts`** — Teks percakapan
```
Menyimpan: teks percakapan yang SUDAH DIENKRIPSI AES-256
           HANYA disimpan jika user sudah beri izin (consent)
```

---

## 🚀 Deployment — Di Mana Semua Dijalankan?

```
USER (browser)
     ↓ buka website
VERCEL → melayani website React (frontend)
     ↓ kirim/terima data
RAILWAY → menjalankan server FastAPI (backend + ML model)
     ↓ simpan/baca data
SUPABASE → database PostgreSQL
     ↓ cache sesi
UPSTASH → Redis (penyimpanan sementara untuk sesi aktif)
```

**Kenapa dipisah frontend dan backend?**
Karena Vercel sangat bagus untuk website React (cepat, CDN global), tapi tidak bisa menjalankan proses Python yang lama seperti ML model. Railway bisa.

---

## ⚡ Berapa Lama Prosesnya?

| Bagian | Estimasi Waktu |
|---|---|
| Gemini API balas | 0.5–2 detik |
| NLP analisis teks | 0.1–0.3 detik |
| ML prediksi | <0.1 detik |
| TTS generate suara | 0.3–1 detik |
| **Total** | **~2–4 detik** |

Agar tidak terasa lambat: respons Gemini langsung di-**streaming** (user mulai baca sambil server masih proses).
