# 🎨 ASSETS — LifeLens
> Semua aset visual yang dibutuhkan: karakter, suara, logo, ilustrasi.
> Karakter RINA dikerjakan bersama oleh Michael (desain) dan Fikri (animasi GSAP).

---

## 👤 Karakter RINA — Konsep Visual

### RINA Bukan Apa?
```
❌ Anime yang terlalu "moe" atau hypersexualized
❌ Robot atau AI yang terlihat futuristik dan dingin
❌ Karakter terlalu muda (tampak seperti anak-anak)
❌ Psikolog dengan jas putih formal
```

### RINA Adalah:
```
✅ Teman sebaya yang hangat (tampak usia 20-25 tahun)
✅ Ekspresi wajah yang genuine dan empatik
✅ Gaya berpakaian casual-smart (bukan formal, bukan asal-asalan)
✅ Warna kulit dan rambut natural untuk Indonesia
✅ Visual yang membuat user merasa nyaman untuk bercerita
```

### Referensi untuk Inspirasi
Cari di Pinterest atau ArtStation dengan keyword:
```
- "2D visual novel character female friend"
- "anime casual character warm friendly"
- "simple SVG animated character"
```

Referensi aplikasi:
```
- Replika app (gaya casual, bukan dokter)
- Duolingo characters (friendly, approachable)
- Visual novel game Persona (ekspresi yang kaya)
```

---

## 🎭 7 Ekspresi RINA yang Harus Dibuat

Setiap ekspresi adalah **layer SVG terpisah** yang bisa ditampilkan/disembunyikan via GSAP.

### Ekspresi 1: IDLE (Menunggu)
```
Kapan: saat sistem menunggu user mengetik
Mata: terbuka normal, berkedip otomatis setiap beberapa detik
Mulut: senyum tipis dan rileks
Postur: tegak, sedikit condong ke depan
Animasi desktop: napas pelan (body naik-turun 4px), kepala sedikit goyang
```

### Ekspresi 2: LISTENING (Mendengarkan)
```
Kapan: saat user sedang mengetik
Mata: sedikit lebih terbuka, fokus ke depan
Mulut: tertutup, senyum sangat tipis
Postur: condong lebih ke depan dari idle
Animasi: kepala sedikit miring ke kanan (inquisitive)
```

### Ekspresi 3: TALKING (Berbicara)
```
Kapan: saat TTS audio sedang diputar
Mata: terbuka ekspresif
Mulut: BERGERAK mengikuti amplitude audio (lip sync)
Animasi: mulut buka-tutup sesuai volume suara
```

### Ekspresi 4: HAPPY / ENCOURAGING
```
Kapan: user kabar baik, RINA beri semangat, user capai milestone
Mata: sedikit menyipit (genuine smile), seperti "mata bulan sabit"
Mulut: senyum lebar
Postur: lebih tegak dan energik
Animasi: bounce kecil sekali saat pertama muncul
```

### Ekspresi 5: EMPATHY / CONCERNED
```
Kapan: user cerita hal berat, risk level naik
Mata: sudut luar sedikit turun (sad-sympathetic)
Alis: tengah sedikit turun (worried)
Mulut: sudut sedikit turun, "mellow smile"
Postur: condong ke depan, "hadir sepenuhnya"
Animasi: gerakan sangat pelan dan lembut
```

### Ekspresi 6: THINKING (Memproses)
```
Kapan: saat loading, saat Gemini masih proses
Mata: melihat sedikit ke atas atau samping
Alis: salah satu naik (quizzical)
Mulut: sedikit miring, ekspresi "hmm"
Postur: tangan ke dagu atau pipi
Animasi: kepala tilt saat masuk ekspresi ini
```

### Ekspresi 7: SURPRISED / IMPRESSED
```
Kapan: user share sesuatu mengejutkan, milestone pertama kali
Mata: sedikit lebih besar
Alis: naik
Mulut: sedikit terbuka, ekspresi "oh"
Animasi: micro-bounce kecil saat pertama muncul
```

---

## 🗂️ Struktur File SVG

File SVG karakter disimpan di:
```
public/assets/rina/
├── rina-base.svg          ← Body + rambut + pakaian (tidak berubah)
├── expressions/
│   ├── expr-idle.svg
│   ├── expr-listening.svg
│   ├── expr-talking.svg   ← Base untuk lip sync
│   ├── expr-happy.svg
│   ├── expr-empathy.svg
│   ├── expr-thinking.svg
│   └── expr-surprised.svg
└── mouth-shapes/          ← Opsional: untuk lip sync lebih detail
    ├── mouth-closed.svg
    ├── mouth-open-small.svg
    └── mouth-open-wide.svg
```

### Spesifikasi Teknis SVG

```
Ukuran canvas: 400 × 600 pixel (portrait)
Format: SVG inline (embedded langsung di React component)

Penamaan ID — WAJIB konsisten (dipakai GSAP):
#rina-body      → seluruh badan
#rina-head      → kepala
#rina-eyes      → kedua mata (untuk blinking)
#rina-mouth     → mulut (untuk lip sync)
#rina-eyebrows  → alis
#rina-chest     → area dada (untuk animasi napas)

#expression-idle       → layer ekspresi idle
#expression-listening  → layer ekspresi listening
#expression-talking    → layer ekspresi talking
#expression-happy      → layer ekspresi happy
#expression-empathy    → layer ekspresi empathy
#expression-thinking   → layer ekspresi thinking
#expression-surprised  → layer ekspresi surprised
```

---

## 🖊️ Cara Membuat SVG (2 Opsi)

### Opsi A — Gambar Manual (Direkomendasikan)
```
1. Sketsa di kertas → tentukan proporsi dan gaya
2. Foto sketsa
3. Buka di Figma (gratis, berbasis web)
4. Trace manual → export sebagai SVG
5. Buka SVG di text editor → pastikan ID sudah sesuai konvensi
6. Test di browser
```

### Opsi B — AI Image Gen → Trace ke SVG
```
1. Generate referensi di Leonardo AI atau Bing Image Creator (gratis)
   Prompt contoh: "simple 2D female character, casual clothes,
   friendly, warm smile, flat design, no background, Indonesia"
2. Download hasil
3. Buka di Inkscape (software gratis)
4. Gunakan fitur "Trace Bitmap" untuk auto-trace
5. Manual cleanup path yang masih berantakan
6. Export sebagai SVG plain
7. Buka di text editor → tambahkan ID yang benar
```

**Tips penting untuk kedua opsi:**
```
- Desain sesederhana mungkin (lebih sedikit path = lebih cepat animasi)
- Gunakan warna solid, hindari gradien kompleks
- Test animasi di browser SEBELUM finalize desain
- Kalau ada yang aneh saat dianimasikan → mungkin masalah ID atau struktur
```

---

## 🔊 Audio Assets

### Sound Effects UI (Efek Suara Kecil)
File-file audio kecil untuk feedback interaksi:

```
public/assets/sounds/
├── message-send.mp3     ← Saat user kirim pesan (klik lembut)
├── message-receive.mp3  ← Saat RINA balas (chime pelan)
├── risk-update.mp3      ← Saat risk score berubah (notifikasi halus)
└── session-start.mp3    ← Saat sesi dimulai (welcome tone hangat)

Spesifikasi:
- Format: MP3
- Durasi: < 1 detik
- Volume: lembut, tidak mengejutkan
- Karakter: hangat dan organik (bukan beep elektronik)

Sumber gratis:
- freesound.org
- mixkit.co
- zapsplat.com
```

### Rekaman Suara untuk KokoroClone (Opsional V2)
Jika tim ingin membuat suara RINA yang unik menggunakan KokoroClone:
```
Yang direkam: salah satu anggota tim yang suaranya cocok untuk RINA
Durasi: 5-10 menit percakapan beragam
Format: WAV, 22050Hz, mono
Lingkungan: ruangan sunyi, tidak ada gema
Alat: headset decent sudah cukup
```

---

## 🖼️ Aset Visual Lainnya

### Logo LifeLens
```
Harus ada:
- logo.svg         → logo lengkap (untuk header)
- logo-icon.svg    → icon saja (untuk favicon dan app icon)

Konsep:
- Gabungan bentuk "lensa" dengan elemen organik/natural
- Warna utama: lavender (#7C6FCD)
- Font: Plus Jakarta Sans
- Harus terbaca jelas dalam ukuran kecil (mobile)
```

### Ilustrasi Onboarding
```
3 ilustrasi sederhana untuk halaman sambutan:
- Ilustrasi 1: "Kenalan dengan RINA"
- Ilustrasi 2: "Bagaimana cara kerjanya"
- Ilustrasi 3: "Privasi dan keamananmu"

Style: flat illustration, warna hangat
Bisa dibuat di Figma atau Canva (gratis)
```

---

## ✅ Prioritas Pembuatan Aset

```
HARUS ADA untuk MVP:
□ Karakter RINA SVG — minimal 4 ekspresi (idle, listening, talking, empathy)
□ Logo SVG
□ Favicon

PENTING untuk V1:
□ Semua 7 ekspresi RINA
□ Sound effects (minimal send + receive)
□ Ilustrasi onboarding

NICE TO HAVE untuk V2:
□ Rekaman KokoroClone untuk suara RINA
□ Mouth shapes untuk lip sync detail
□ Animasi idle karakter yang halus
```
