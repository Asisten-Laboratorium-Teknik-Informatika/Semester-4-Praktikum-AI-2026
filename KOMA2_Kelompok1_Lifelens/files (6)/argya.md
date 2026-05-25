# 🎨 TUGAS ARGYA — Frontend, UI/UX & Deployment
> Argya Ariella | 241712028
> Panduan lengkap tugasmu dari awal hingga selesai.

---

## 🎯 Peranmu dalam Tim

Argya adalah **wajah proyek ini** — semua yang user lihat dan rasakan adalah hasil kerjamu. Sekuat apapun model ML Fikri dan NLP Michael, kalau UI-nya buruk, user tidak akan mau pakai.

```
Yang kamu hasilkan untuk tim:
├── Website React yang bisa dibuka di browser
├── Chat interface dengan animasi yang mulus
├── Layout yang enak dipakai di laptop maupun HP
├── Onboarding (pilih login + pilih suara)
├── Dashboard (risk card + grafik tren)
└── Deploy ke Vercel (bisa diakses publik)
```

---

## 📦 Deliverables (Yang Harus Diserahkan)

| # | Output | Kapan |
|---|---|---|
| 1 | Project React + Vite bisa jalan | Sprint 0 |
| 2 | Layout skeleton (sidebar + chat) | Sprint 0 |
| 3 | Chat interface teks berjalan | Sprint 1 |
| 4 | Auth modal (Google/email/anonymous) | Sprint 1 |
| 5 | Responsive desktop + mobile | Sprint 1 |
| 6 | Framer Motion di semua komponen | Sprint 2 |
| 7 | Risk card + grafik tren | Sprint 2 |
| 8 | Karakter RINA terintegrasi | Sprint 3 |
| 9 | Voice input button | Sprint 3 |
| 10 | Deploy ke Vercel (URL public) | Sprint 4 |

---

## 🚀 TUGAS 1 — Setup Project React

### Apa yang Dilakukan
Membuat project React baru dari nol dengan semua tools yang dibutuhkan.

### Langkah-langkah
```bash
# 1. Buat project
npm create vite@latest lifelens-frontend -- --template react
cd lifelens-frontend

# 2. Install semua package (satu perintah)
npm install framer-motion gsap zustand axios swr recharts \
            lucide-react howler @supabase/supabase-js \
            react-router-dom clsx

npm install -D tailwindcss postcss autoprefixer

# 3. Setup Tailwind CSS
npx tailwindcss init -p

# 4. Test
npm run dev
# Buka localhost:5173 → harus muncul halaman default
```

### Setup Tailwind CSS
Buka `tailwind.config.js`, tambahkan warna custom dari `style.md`:
```javascript
// tailwind.config.js
module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        primary: '#7C6FCD',
        'primary-soft': '#EEE9FF',
        // tambahkan warna lain dari style.md
      },
      fontFamily: {
        display: ['Plus Jakarta Sans', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      }
    }
  }
}
```

---

## 💬 TUGAS 2 — Chat Interface

### Apa yang Dibuat
Halaman utama percakapan — tempat user ngobrol dengan RINA.

### Komponen yang Harus Dibuat

#### ChatBubble.jsx — Gelembung Chat
**Apa:** Kotak teks yang muncul saat RINA atau user kirim pesan.
**Menggunakan:** Framer Motion untuk animasi muncul.

Dua variasi:
- Bubble RINA (kiri): putih, sudut kiri bawah kotak (tidak melengkung)
- Bubble user (kanan): warna primary/lavender, sudut kanan bawah kotak

Animasi yang diinginkan: bubble "muncul dari bawah" dengan efek spring (tidak kaku, terasa hidup).

**Contoh konsep animasi (ilustrasi):**
```jsx
// Ide animasinya: mulai dari bawah + tidak terlihat → naik ke posisi normal + terlihat
// Gunakan Framer Motion dengan type: 'spring' untuk efek yang natural
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ type: 'spring', stiffness: 300 }}
>
  {/* isi bubble */}
</motion.div>
```

---

#### TypingIndicator.jsx — Animasi "Sedang Mengetik"
**Apa:** Tiga titik yang beranimasi bergantian saat RINA memproses respons.
**Menggunakan:** Framer Motion dengan stagger (titik 1 → 2 → 3 dengan jeda kecil).
**Kenapa perlu:** User tahu sistem masih berjalan, bukan hang.

---

#### InputBar.jsx — Area Input
**Apa:** Bar di bawah layar dengan tombol mikrofon, input teks, dan tombol kirim.
**Yang harus diperhatikan:**
- Tombol kirim disabled kalau teks masih kosong
- Tombol mikrofon tersembunyi kalau browser tidak support Web Speech API
- Input harus punya placeholder yang ramah: "Cerita dong..."
- Tekan Enter = kirim (kecuali Shift+Enter = baris baru)

---

#### ChatArea.jsx — Container Chat
**Apa:** Wadah yang menampung semua bubble chat, dengan auto-scroll ke bawah saat ada pesan baru.
**Kenapa perlu auto-scroll:** Tanpa ini, user harus scroll manual setiap RINA balas.

---

### WebSocket — Koneksi Real-time ke Backend

**Apa itu WebSocket?**
Berbeda dari HTTP biasa (request → response → tutup), WebSocket membuat **koneksi yang terus terbuka**. Ini diperlukan agar respons RINA bisa dikirim kapanpun tanpa user harus refresh.

**Cara kerja sederhana:**
```
Frontend buka koneksi ke backend
  ↓
User kirim pesan → dikirim lewat WebSocket
  ↓
Backend proses → kirim balik lewat WebSocket yang sama
  ↓
Frontend terima → tampilkan bubble baru
```

Implementasikan ini di `hooks/useChat.js` — hook yang mengelola semua logic WebSocket.

---

## 🔐 TUGAS 3 — Auth Modal (Login)

### Apa yang Dibuat
Modal (popup) yang muncul saat user pertama kali buka website.

### 3 Pilihan Login
Semua menggunakan Supabase JS yang sudah diinstall:

**Google OAuth:**
```
User klik "Lanjut dengan Google" → browser buka popup Google login
→ User pilih akun → redirect balik ke website → sudah login
Ini semua ditangani Supabase, tidak perlu kode kompleks
```

**Email + Password:**
```
User isi email dan password → Supabase handle verifikasi
Perlu: form email, form password, tombol daftar, tombol masuk
```

**Lanjut Tanpa Akun:**
```
User klik "Lanjut tanpa akun" → buat ID anonymous di localStorage
Tampilkan peringatan: "Data tidak tersimpan kalau browser ditutup"
```

---

## 📊 TUGAS 4 — Dashboard Components

### RiskCard.jsx — Kartu Kondisi
**Apa yang ditampilkan:**
```
- Badge level: LOW / MEDIUM / HIGH (warna berbeda)
- Top 3 faktor penyebab (dari SHAP, dikirim backend)
- Mini grafik tren 7 hari
- Disclaimer kecil: "ini estimasi, bukan diagnosis"
```

**Animasi:** Badge beranimasi kecil (pulse) untuk menarik perhatian tapi tidak mengganggu.

### MoodTrendChart.jsx — Grafik Tren
**Apa:** Grafik garis yang menunjukkan perubahan mood/sentimen selama 7 hari.
**Menggunakan:** Library Recharts (sudah diinstall).

---

## 🎭 TUGAS 5 — Integrasi Karakter RINA

### Apa yang Dilakukan
Memasang file SVG karakter RINA (yang dibuat Michael) ke dalam halaman dan menghubungkannya dengan state aplikasi.

### Cara Kerjanya
```
State backend kirim emotion: "empathy"
         ↓
useCharacter hook mendeteksi perubahan
         ↓
CharacterController (GSAP) menyembunyikan ekspresi lama
         ↓
CharacterController menampilkan ekspresi "empathy"
         ↓
Transisi smooth selama 0.3 detik
```

### Koordinasi dengan Fikri dan Michael
- Michael membuat file SVG dengan ID yang benar (`#rina-eyes`, `#expression-idle`, dll)
- Fikri membuat `CharacterController.js` dengan logika GSAP
- Argya **memasang** komponen itu ke dalam layout React

---

## 📱 TUGAS 6 — Responsif Mobile

### Aturan Adaptasi

**Layout berubah:**
```
Desktop: sidebar kiri (35%) + chat area kanan (65%)
Mobile:  semua vertikal, karakter di atas, chat di tengah, input di bawah
```

**Animasi berubah:**
```
Desktop: animasi penuh (spring, idle karakter, background bergerak)
Mobile:  animasi minimal (simple fade, karakter statis)
Cara: cek lebar layar, kalau < 768px → pakai animasi lite
```

**Input berubah:**
```
Desktop: input dengan Enter untuk kirim
Mobile:  input dengan tombol kirim (keyboard virtual tidak punya Enter yang sama)
```

---

## 🚀 TUGAS 7 — Deploy ke Vercel

### Langkah-langkah
```
1. Pastikan npm run build berjalan tanpa error
   (ini buat file produksi di folder dist/)

2. Push kode ke GitHub

3. Buka vercel.com → New Project
   → Import dari GitHub → pilih lifelens-frontend

4. Build settings (biasanya auto-detect):
   - Framework: Vite
   - Build command: npm run build
   - Output directory: dist

5. Tambahkan Environment Variables di Vercel:
   - VITE_SUPABASE_URL
   - VITE_SUPABASE_ANON_KEY
   - VITE_API_URL (URL backend Railway)
   - VITE_WS_URL (WebSocket URL backend)

6. Deploy!
   URL tersedia dalam < 2 menit
   Contoh: https://lifelens.vercel.app
```

### Auto-Deploy
Setiap kali push ke branch `main` di GitHub → Vercel otomatis deploy ulang. Jadi kalau ada update → tinggal push, URL publik langsung update.

---

## ✅ Checklist Tugasmu

```
SPRINT 0:
□ npm run dev berjalan di localhost:5173
□ Tailwind CSS terkonfigurasi dengan warna dari style.md
□ Folder structure sesuai 06_frontend_ui.md
□ Layout skeleton (sidebar + chat) tampil

SPRINT 1:
□ ChatBubble.jsx selesai (RINA + user variant)
□ TypingIndicator animasi berjalan
□ InputBar.jsx dengan keyboard shortcut (Enter = kirim)
□ WebSocket terhubung ke backend Fikri
□ AuthModal.jsx selesai (Google + email + anonymous)
□ Test di mobile view (Chrome DevTools)

SPRINT 2:
□ Framer Motion spring animation di chat bubbles
□ RiskCard.jsx dengan badge berwarna
□ MoodTrendChart.jsx dengan Recharts
□ Onboarding voice selection dengan preview audio

SPRINT 3:
□ Karakter RINA SVG tampil di sidebar
□ Ekspresi berubah berdasarkan emotion dari backend
□ Animasi lite mode aktif di mobile
□ Semua error states ada (koneksi putus, loading, dll)

SPRINT 4:
□ Deploy ke Vercel — URL bisa dibuka siapapun
□ Test di device HP fisik
□ Screenshot untuk presentasi
□ Lighthouse score > 75
```
