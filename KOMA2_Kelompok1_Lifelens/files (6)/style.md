# 🎨 STYLE GUIDE — LifeLens
> Sistem desain website: warna, font, jarak, animasi.
> Argya mengimplementasikan ini. Semua anggota harus paham konsepnya.

---

## 🌈 Filosofi Desain: "Warm Intelligence"

LifeLens bukan aplikasi medis yang steril. LifeLens harus terasa seperti **ruang yang hangat dan aman untuk bercerita**.

```
BUKAN seperti ini:          TAPI seperti ini:
❌ Klinik rumah sakit       ✅ Kafe dengan lampu hangat
❌ Dashboard analytics      ✅ Jurnal personal yang indah
❌ Chatbot perusahaan       ✅ Teman yang mendengarkan
❌ Formulir pemerintah      ✅ Percakapan yang mengalir
```

---

## 🎨 Warna

Semua warna didefinisikan sebagai "CSS variables" — variabel yang bisa dipakai di seluruh project. Keuntungannya: kalau mau ganti warna, cukup ubah di satu tempat.

### Palet Warna Utama

**Primary — Lavender Hangat**
```
#7C6FCD — warna utama (tombol, link, aksen)
#EEE9FF — versi terang (background card)
#F5F2FF — sangat terang (background halaman)
```
Kenapa lavender? Warna ini diasosiasikan dengan ketenangan, bukan dingin seperti biru korporat.

**Accent — Amber Hangat**
```
#F5A623 — warna aksen (badge, highlight)
#FFF4E0 — versi terang
```

**Neutral — Warm Gray (bukan abu-abu dingin)**
```
#FAFAF8 — background utama (off-white hangat)
#FFFFFF — cards, modal
#2D2D2D — teks utama
#6B6B6B — teks sekunder
```

**Risk Level Colors**
```
LOW    → #52C97A  (hijau tenang) + #EDFFF4 (background)
MEDIUM → #F5A623  (amber)        + #FFF4E0 (background)
HIGH   → #E8635A  (merah hangat, BUKAN merah alarm) + #FFF0EF
```
Kenapa bukan merah cerah untuk HIGH? Karena kita tidak ingin user panik — kita ingin mereka mengambil tindakan dengan tenang.

### Cara Pakai di CSS
```css
/* Definisikan di globals.css */
:root {
  --color-primary: #7C6FCD;
  --color-bg: #FAFAF8;
  --color-risk-high: #E8635A;
  /* dll */
}

/* Pakai di komponen */
.tombol-utama {
  background: var(--color-primary);
}
```

---

## ✍️ Tipografi (Font)

Dua font yang dipakai — keduanya gratis dari Google Fonts:

**Plus Jakarta Sans** — untuk judul dan heading
```
Kenapa: font modern, tegas tapi tetap ramah
Pakai untuk: nama section, kartu, tombol besar
```

**Inter** — untuk teks isi dan chat
```
Kenapa: sangat mudah dibaca, netral
Pakai untuk: chat bubble, paragraf, caption
```

**Cara import (di index.html atau CSS):**
```html
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
```

**Ukuran font yang dipakai:**
```
12px → caption kecil, timestamp
14px → teks sekunder, label
16px → teks utama, chat bubble
18px → subheading kecil
24px → heading section
30px → heading besar
```

---

## 📐 Sistem Jarak (Spacing)

Gunakan kelipatan 4px untuk semua jarak. Ini membuat layout terlihat rapi dan konsisten.

```
4px   → jarak sangat kecil (antara icon dan teks)
8px   → jarak kecil (padding tombol kecil)
12px  → jarak sedang-kecil
16px  → jarak standard (padding card)
24px  → jarak sedang
32px  → jarak besar
48px  → jarak antar section
```

Tailwind CSS sudah punya sistem ini: `p-4` = 16px, `p-6` = 24px, dst.

---

## 🔲 Border Radius (Sudut Melengkung)

LifeLens menggunakan sudut melengkung — **tidak ada kotak tajam**.

```
8px  → input field kecil
16px → cards, tombol
24px → modal, panel besar
32px → chat bubble
9999px → lingkaran penuh (tombol voice, avatar)
```

Kenapa tidak kotak? Sudut tajam terasa "kaku" dan "formal". Sudut melengkung terasa lebih ramah dan personal.

---

## ✨ Panduan Animasi

### Framer Motion — untuk komponen UI

Animasi yang "terasa hidup" menggunakan **spring physics** (bukan durasi tetap):

```javascript
// Contoh: chat bubble muncul
// Mulai: tidak terlihat, sedikit di bawah, sedikit kecil
// Akhir: terlihat, posisi normal, ukuran normal
// Dengan: efek "spring" yang terasa natural

{
  initial: { opacity: 0, y: 20, scale: 0.95 },
  animate: { opacity: 1, y: 0, scale: 1 },
  transition: { type: 'spring', stiffness: 300, damping: 20 }
}
```

Animasi yang tersedia di Framer Motion dan kapan dipakai:
```
Spring animation → chat bubble muncul
Fade + slide     → page transition antar halaman
Scale            → modal muncul/tutup
Stagger          → list item muncul bergiliran
Layout           → card berubah ukuran saat konten update
```

### GSAP — untuk karakter 2D

GSAP (GreenSock Animation Platform) dipakai untuk animasi SVG karakter RINA karena lebih presisi.

```javascript
// Contoh: animasi napas (body naik turun pelan)
gsap.to('#rina-body', {
  y: -4,           // naik 4px
  duration: 2.5,   // selama 2.5 detik
  ease: 'sine.inOut', // kurva yang mulus
  repeat: -1,      // ulangi selamanya
  yoyo: true       // balik lagi ke posisi awal
});
```

### Desktop vs Mobile

```
DESKTOP                      MOBILE
✅ Idle animation karakter    ❌ Matikan (hemat baterai)
✅ Background bergerak        ❌ Static background
✅ Spring animation bubble    ✅ Simple fade (lebih ringan)
✅ Hover effects              ❌ Tidak ada (layar sentuh)
✅ Partikel                   ❌ Matikan
```

Cara deteksi di JavaScript:
```javascript
const isMobile = window.matchMedia('(max-width: 768px)').matches;
// Jika isMobile = true → pakai animasi lite
```

---

## 🌊 Background

**Desktop:** Gradient yang bergerak sangat pelan (hampir tidak terasa bergerak).
```
Warna: lavender sangat terang → off-white → amber sangat terang
Pergerakan: sangat lambat, 15 detik per siklus
```

**Mobile:** Background statis — tidak bergerak. Menghemat baterai dan CPU.

---

## 🌙 Dark Mode (Opsional)

Kalau waktu memungkinkan, tambahkan dark mode. Warna berubah otomatis mengikuti pengaturan sistem user:
```
Background: hitam kebiruan (#1A1A2E)
Surface: sedikit lebih terang (#232340)
Teks: putih kebiruan (#E8E8F0)
Primary: lavender tetap, tapi versi lebih gelap
```

> Prioritas: selesaikan fitur utama dulu, dark mode bisa ditambah di V2.
