# 🎨 FRONTEND & UI — LifeLens
> Panduan membangun tampilan website dari nol.
> Dikerjakan oleh: Argya (dengan karakter dari Fikri + Michael)

---

## 🧠 Apa yang Dibuat di Frontend?

Frontend adalah **semua yang user lihat dan sentuh** — website-nya sendiri. Bukan server, bukan database, tapi layar yang tampil di browser.

Yang harus dibuat Argya:
```
✅ Halaman chat (percakapan dengan RINA)
✅ Karakter 2D RINA di sidebar (animasi)
✅ Dashboard (risk card, grafik tren 7 hari)
✅ Onboarding (login + pilih suara)
✅ Settings (ganti suara, dll)
✅ Responsif — enak dipakai di HP dan laptop
```

---

## 🛠️ Tools yang Dipakai

| Tool | Untuk Apa | Kenapa Dipilih |
|---|---|---|
| **React + Vite** | Framework utama | Ekosistem terlengkap, dokumentasi terbanyak |
| **Tailwind CSS** | Styling (warna, ukuran, layout) | Cepat, tidak perlu tulis CSS dari nol |
| **Framer Motion** | Animasi komponen UI | Spring physics bawaan, mudah untuk React |
| **GSAP** | Animasi karakter 2D | Paling presisi untuk animasi SVG |
| **Zustand** | State management | Lebih simpel dari Redux |
| **Recharts** | Grafik tren mood | Library chart paling mudah untuk React |
| **Supabase JS** | Login & database | Satu library untuk semua auth |

---

## 📱 Layout Website

### Desktop (layar laptop)
```
┌────────────────────────────────────────────────────┐
│  Logo LifeLens                    [⚙] [👤 Profile] │
├──────────────────┬─────────────────────────────────┤
│                  │                                 │
│   SIDEBAR 35%    │         CHAT AREA 65%           │
│                  │                                 │
│  ┌────────────┐  │   [bubble RINA]                 │
│  │ RINA 2D   │  │         [bubble user]            │
│  │ Animasi   │  │   [bubble RINA]                  │
│  └────────────┘  │                                 │
│                  │   ──────────────────────────    │
│  ┌────────────┐  │   [🎤] [ketik pesan...] [→]     │
│  │ Risk Card  │  │                                 │
│  │ ● MEDIUM   │  │                                 │
│  └────────────┘  │                                 │
│                  │                                 │
│  ┌────────────┐  │                                 │
│  │ Grafik     │  │                                 │
│  │ 7 hari     │  │                                 │
│  └────────────┘  │                                 │
└──────────────────┴─────────────────────────────────┘
```

### Mobile (HP)
```
┌────────────────────┐
│ [≡] LifeLens  [⚙] │  ← Header tetap di atas
├────────────────────┤
│  [RINA - kecil]   │  ← Karakter lebih kecil
├────────────────────┤
│  [bubble RINA]    │
│     [bubble user] │  ← Area chat (bisa scroll)
│  [bubble RINA]    │
├────────────────────┤
│ [🎤] [_______] [→]│  ← Input selalu di bawah
└────────────────────┘
```

**Aturan responsif:** Di mobile, animasi berat (partikel, idle karakter) DIMATIKAN agar tidak lag.

---

## 🧩 Komponen Utama yang Harus Dibuat

Setiap bagian UI adalah sebuah "komponen" — file `.jsx` tersendiri.

### 1. ChatBubble — Gelembung Chat

**Apa:** Kotak teks yang muncul saat RINA atau user kirim pesan.
**Menggunakan:** Framer Motion untuk animasi muncul.
**Bagaimana:** Bubble muncul dari bawah dengan efek "spring" (seperti gelembung sabun yang naik).

Konsep animasinya:
```
Bubble baru dibuat → mulai dari posisi Y+20, opacity 0
                  → bergerak ke Y=0, opacity 1
                  → dengan "spring physics" (terasa hidup, tidak kaku)
```

Dua variasi bubble:
- **Bubble RINA** (kiri): warna putih, sudut kiri bawah kotak
- **Bubble User** (kanan): warna lavender/ungu, sudut kanan bawah kotak

---

### 2. TypingIndicator — "RINA sedang mengetik..."

**Apa:** Tiga titik yang beranimasi (... bergerak bergantian) saat RINA sedang proses respons.
**Menggunakan:** Framer Motion dengan animasi stagger (titik kedua muncul setelah pertama, dst).
**Kenapa perlu:** User harus tahu sistem masih berjalan, bukan hang.

---

### 3. RinaCharacter — Karakter 2D

**Apa:** File SVG karakter RINA yang bisa berubah ekspresi dan bergerak.
**Menggunakan:** GSAP untuk mengontrol animasi.
**Bagaimana:** SVG punya banyak "layer" — satu untuk setiap ekspresi. GSAP menyembunyikan layer yang tidak aktif dan menampilkan yang aktif.

State karakter yang harus direspons:
```
IDLE      → Menunggu user (bernapas pelan, kedip otomatis)
LISTENING → User sedang mengetik (condong sedikit ke depan)
TALKING   → RINA sedang bicara (mulut bergerak - lip sync)
HAPPY     → Respons positif (senyum lebar, bounce kecil)
EMPATHY   → User cerita hal berat (ekspresi khawatir, lembut)
THINKING  → Sedang loading (lihat ke samping, tangan ke dagu)
SURPRISED → Respons mengejutkan (mata sedikit membesar)
```

---

### 4. RiskCard — Kartu Risiko

**Apa:** Kartu di sidebar yang tampilkan level risiko: LOW, MEDIUM, atau HIGH.
**Menggunakan:** Framer Motion untuk animasi ketika risk level berubah.
**Konten kartu:**
```
┌────────────────────┐
│ Kondisi Minggu Ini │
│ ● MEDIUM           │  ← badge berwarna sesuai level
│                    │
│ Faktor Utama:      │
│ • Tidur kurang     │
│ • Beban kerja ↑    │
│ • Sentimen ↓       │
│                    │
│ [grafik 7 hari]    │
│                    │
│ ⚠️ Ini estimasi,   │
│ bukan diagnosis    │
└────────────────────┘
```

---

### 5. InputBar — Area Input Pesan

**Apa:** Bar di bawah layar berisi tombol mikrofon + text input + tombol kirim.
**Menggunakan:** React state untuk kelola teks, Web Speech API untuk suara.
**Penting:** Tombol kirim harus disabled kalau text kosong.

---

### 6. AuthModal — Popup Login

**Apa:** Modal yang muncul saat user pertama kali buka website.
**Pilihan:** Login Google, email/password, atau lanjut tanpa akun.
**Menggunakan:** Supabase JS (semua auth sudah built-in).

---

## 📁 Struktur Folder

Ini struktur folder yang harus dibuat dari awal:

```
src/
├── components/
│   ├── chat/
│   │   ├── ChatArea.jsx       ← Container semua chat
│   │   ├── ChatBubble.jsx     ← Satu gelembung chat
│   │   ├── TypingIndicator.jsx ← "..." animasi
│   │   └── InputBar.jsx       ← Input + tombol kirim
│   ├── character/
│   │   ├── RinaCharacter.jsx  ← Tampilkan SVG karakter
│   │   └── CharacterController.js ← Logika GSAP
│   ├── dashboard/
│   │   ├── RiskCard.jsx       ← Kartu risiko
│   │   └── MoodTrendChart.jsx ← Grafik 7 hari
│   └── auth/
│       └── AuthModal.jsx      ← Popup login
│
├── hooks/
│   ├── useChat.js             ← Logic WebSocket
│   └── useVoice.js            ← Logic STT/TTS
│
├── store/
│   └── chatStore.js           ← State global (Zustand)
│
├── pages/
│   ├── Chat.jsx               ← Halaman utama
│   └── Settings.jsx           ← Halaman pengaturan
│
└── styles/
    └── globals.css            ← CSS variables (warna, font)
```

---

## ✨ Animasi — Desktop vs Mobile

| Animasi | Desktop | Mobile |
|---|---|---|
| Karakter idle (napas, kedip) | ✅ Aktif | ❌ Mati (hemat baterai) |
| Background partikel | ✅ Aktif | ❌ Mati |
| Chat bubble spring | ✅ Spring physics | ✅ Simple fade |
| Page transition | ✅ Slide + fade | ✅ Simple fade |
| Risk card update | ✅ Animasi | ✅ Animasi |

Cara deteksi mobile:
```javascript
// Cek apakah layar kecil (mobile) atau user minta animasi minimal
const isMobile = window.matchMedia('(max-width: 768px)').matches;
const prefersLess = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// Kalau salah satu true → pakai animasi ringan
const useLiteMode = isMobile || prefersLess;
```

---

## 🔗 Cara Frontend Bicara dengan Backend

Frontend dan backend berkomunikasi dua cara:

**WebSocket** — untuk chat (real-time)
```
Kenapa WebSocket, bukan HTTP biasa?
Karena chat harus real-time — user tidak mau nunggu polling.
WebSocket = koneksi yang terus terbuka, pesan bisa dikirim kapanpun.

Alurnya:
Frontend buka koneksi → kirim pesan → backend balas (streaming)
                      → terima balasan → tampilkan ke user
```

**REST API (HTTP)** — untuk data statis
```
Untuk mengambil: riwayat sesi, risk score sebelumnya, profil user
Ini tidak perlu real-time, cukup request-response biasa.
```

---

## 🚀 Deploy ke Vercel

Setelah semua jalan di lokal:
1. Push kode ke GitHub
2. Connect repository ke Vercel
3. Vercel otomatis detect React + Vite
4. Tambahkan environment variables di Vercel dashboard
5. Setiap push ke main → Vercel otomatis deploy ulang
