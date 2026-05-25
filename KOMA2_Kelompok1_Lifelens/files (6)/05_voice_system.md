# 🎙️ VOICE SYSTEM — LifeLens
> Sistem suara lengkap: user bisa bicara ke RINA, RINA bisa balas dengan suara.
> Plus fitur unik: pilih bahasa suara RINA (Indonesia/Jepang/Inggris/Korea).
> Dikerjakan oleh: Fikri + Michael

---

## 🗺️ Gambaran Besar Sistem Suara

Ada dua arah suara dalam sistem ini:

```
USER BICARA → [STT] → Teks → Diproses → Balasan RINA
                                              ↓
                                          [TTS] → Suara → Speaker User
                                                     ↓
                                           Trigger lip sync karakter 2D
```

**STT** = Speech to Text (suara user jadi teks)
**TTS** = Text to Speech (teks balasan RINA jadi suara)

---

## 🗣️ BAGIAN 1 — STT (User Bicara ke RINA)

### Apa yang Dibuat?
Tombol mikrofon di chat. Kalau user pencet dan bicara, suaranya langsung jadi teks di input box.

### Menggunakan Apa?
**Web Speech API** — ini sudah ada di dalam browser, tidak perlu install apapun.

### Kenapa Web Speech API (bukan yang lain)?
- **Gratis** dan tidak butuh server
- **Langsung jalan** di browser tanpa setup
- **Cukup akurat** untuk bahasa Indonesia di Chrome
- **Hemat resource** — prosesnya di browser user, bukan di server kita

### Bagaimana Cara Kerjanya?
Saat user pencet tombol mikrofon:
1. Browser minta izin akses mikrofon
2. Browser dengarkan suara user
3. Hasilnya langsung muncul sebagai teks di input
4. User bisa edit sebelum kirim, atau langsung kirim

**Contoh cara pakainya (ilustrasi — jangan copy paste langsung):**
```javascript
// Buat objek pengenal suara
const recognition = new webkitSpeechRecognition();
recognition.lang = 'id-ID';  // atur ke bahasa Indonesia

// Ketika ada hasil
recognition.onresult = (event) => {
  const teks = event.results[0][0].transcript;
  // Masukkan teks ini ke input box
  setInputText(teks);
};

// Mulai dengarkan
recognition.start();
```

### Keterbatasan yang Harus Dihandle
- Chrome: bagus ✅
- Firefox: terbatas ⚠️
- Safari mobile: perlu HTTPS ⚠️

**Solusi wajib:** Jika Web Speech API tidak tersedia di browser user → tampilkan input teks biasa sebagai fallback. User tetap bisa pakai aplikasi, hanya tanpa fitur suara.

### Upgrade di V2 (opsional)
Kalau akurasi terasa kurang: gunakan **faster-whisper** yang jalan di server (RTX 3050 kita cukup). Tapi ini bisa nanti setelah MVP berjalan.

---

## 🔊 BAGIAN 2 — TTS (RINA Bicara ke User)

### Apa yang Dibuat?
Setiap respons RINA dibacakan dengan suara, bukan hanya teks. Suaranya bisa dipilih user di awal.

### Pilihan Suara

| Bahasa | Tool | Kualitas | Kenapa Dipilih |
|---|---|---|---|
| 🇮🇩 Indonesia | Model tim sendiri | Dikembangkan sendiri | Ini yang jadi milik tim |
| 🇯🇵 Japanese | Kokoro TTS | ⭐⭐⭐⭐⭐ | Support native, sangat natural |
| 🇺🇸 English | Kokoro TTS | ⭐⭐⭐⭐⭐ | Support native, terbaik |
| 🇰🇷 Korean | edge-tts | ⭐⭐⭐⭐ | Neural, gratis, online |

### Bagaimana Cara Kerjanya?

**Untuk suara Indonesia (default):**
```
Teks respons RINA → Model TTS tim → File audio → Diputar ke user
```

**Untuk suara asing (JP/EN/KR):**
```
Teks respons (Indonesia) → Terjemahkan dulu ke JP/EN/KR → TTS → Audio → User
Catatan: TEXT BUBBLE TETAP BAHASA INDONESIA
         Hanya SUARA yang dalam bahasa asing
```

### Kenapa Teks Tetap Indonesia Tapi Suara Bisa Asing?

Ini fitur unik yang sengaja dirancang:
- User mengerti konten percakapan (teks Indonesia)
- Tapi suara RINA terdengar dalam bahasa yang user suka (seperti menonton anime dengan subtitle)
- Memberikan "karakter" yang kuat pada RINA

### Emosi pada Suara

Suara RINA tidak datar. Menyesuaikan tone berdasarkan konten:

```
Konten empati → bicara lebih pelan, nada lebih rendah
Konten semangat → bicara lebih cepat, nada lebih tinggi
Konten serius → sangat pelan, sangat lembut
```

Ini dikendalikan lewat **SSML** (bahasa markup untuk TTS), contoh konsepnya:
```
Teks: "Wah, itu berat banget ya..."
Instruksi: [pelan] + [nada rendah] + [volume lembut]
→ Terdengar empatik, bukan robotik
```

### Terjemahan untuk Suara Asing

**Menggunakan:** Argos Translate — library Python yang bisa terjemahkan offline.

**Kenapa offline?** Karena terjemahan ini hanya untuk TTS, bukan untuk disimpan. Kalau pakai API online seperti Google Translate, ada biaya dan ketergantungan internet. Argos Translate: download sekali, jalan selamanya tanpa internet.

**Yang penting dipahami:** Terjemahan ini **hanya masuk ke TTS, langsung dibuang setelah jadi audio**. Tidak disimpan ke database, tidak mempengaruhi analisis apapun.

---

## 🎭 BAGIAN 3 — Lip Sync (Sinkronisasi Mulut Karakter)

### Apa yang Dibuat?
Saat RINA berbicara (audio diputar), mulut karakter 2D bergerak mengikuti suara.

### Bagaimana Cara Kerjanya?
Sistem menganalisis **volume audio** setiap saat dan menggerakkan mulut karakter sesuai volume itu.

```
Volume tinggi → mulut terbuka lebar
Volume rendah → mulut hampir tertutup
Tidak ada suara → mulut tertutup
```

Secara teknis: Web Audio API mengukur amplitudo audio setiap frame, hasilnya dikasih ke GSAP untuk gerakkan mulut SVG karakter.

**Contoh konsepnya (ilustrasi):**
```javascript
// Setiap frame audio diputar, ukur volumenya
const checkVolume = () => {
  const volume = getAudioAmplitude();  // 0.0 sampai 1.0
  character.setMouthOpen(volume);      // gerakkan mulut
  
  if (audioIsPlaying) requestAnimationFrame(checkVolume);
};
```

---

## 🎛️ UI Pemilihan Suara

Saat onboarding (pertama kali buka), user memilih suara RINA:

```
┌─────────────────────────────────────┐
│  Suara RINA yang mana yang          │
│  paling kamu suka?                  │
│                                     │
│  ○ [▶ Dengar] 🇮🇩 Indonesia        │
│  ○ [▶ Dengar] 🇯🇵 Japanese         │
│  ○ [▶ Dengar] 🇺🇸 English          │
│  ○ [▶ Dengar] 🇰🇷 Korean           │
│                                     │
│  💬 Teks chat tetap Bahasa Indonesia│
│  [Mulai →]                          │
└─────────────────────────────────────┘
```

- Tombol **[▶ Dengar]**: user bisa dengar sample dulu sebelum pilih
- Pilihan bisa diubah kapanpun di Settings

---

## ⚠️ Hal Penting yang Harus Diingat

```
1. Safety layer TIDAK TERPENGARUH pilihan suara
   → Deteksi krisis selalu pakai teks Indonesia, apapun pilihan voice user

2. Teks bubble SELALU Indonesia
   → Hanya suara yang berubah, bukan isi percakapan

3. Selalu ada tombol MATIKAN SUARA
   → User punya kontrol penuh, jangan paksa mereka dengarkan

4. Fallback ke teks jika browser tidak support
   → Jangan biarkan user stuck hanya karena browser tidak support STT
```
