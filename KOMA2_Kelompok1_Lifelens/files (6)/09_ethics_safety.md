# ⚠️ ETHICS & SAFETY — LifeLens
> Protokol keamanan, etika, dan perlindungan pengguna.
> Bagian ini NON-NEGOTIABLE. Tidak ada fitur yang lebih penting.

---

## 🧠 Kenapa Ini Penting Banget?

LifeLens berinteraksi dengan orang yang mungkin sedang dalam kondisi **rentan secara emosional**. Kalau sistemnya tidak aman secara etis, kita bisa secara tidak sengaja **membahayakan** user yang justru butuh bantuan.

Ini bukan formalitas — ini tanggung jawab nyata.

---

## 🛡️ Framework SAFE

Empat prinsip yang mengatur semua keputusan etis dalam proyek ini:

| Huruf | Prinsip | Artinya dalam Praktik |
|---|---|---|
| **S** | Screening, bukan diagnosis | Kita deteksi risiko, BUKAN mendiagnosis penyakit |
| **A** | Always refer when needed | Kalau kondisi berat → selalu arahkan ke profesional |
| **F** | Framing yang tidak menstigmatisasi | Kata-kata kita tidak boleh membuat user merasa dihakimi |
| **E** | Emergency protocol | Kalau ada krisis → STOP semua, tampilkan bantuan |

---

## 🚨 Emergency Protocol

### Apa ini?
Sistem yang mendeteksi jika user mengirim pesan yang mengindikasikan kondisi darurat (pikiran menyakiti diri, dll).

### Kapan Aktif?
Segera saat backend menerima pesan — ini Layer 1, **sebelum Gemini API, sebelum NLP, sebelum apapun**.

### Apa yang Terjadi?
```
User kirim: "sudah tidak mau ada lagi"
         ↓
Safety check mendeteksi keyword krisis
         ↓
STOP semua proses
         ↓
Kirim ke user:
"Aku dengar kamu. Ini terdengar sangat berat.
 Kamu tidak harus menanggung ini sendirian.
 📞 Into The Light Indonesia: 119 ext 8"
         ↓
Percakapan dilanjutkan dengan sangat hati-hati
(bukan kembali ke topik biasa)
```

### Kapan Sistem Wajib Rujuk ke Profesional?
```
1. Keyword krisis terdeteksi
2. Risk score HIGH selama 5+ hari berturut-turut
3. User sendiri meminta bicara dengan manusia nyata
```

---

## 🔒 Consent — Izin dari User

### Apa itu Consent?
Sebelum menyimpan teks percakapan, kita **harus minta izin** dari user secara eksplisit dan jelas.

### Cara Memintanya (via RINA, bukan form kaku)
```
RINA: "Eh, sebelum kita mulai — boleh aku nanya satu hal?"

RINA: "Percakapan kita bisa aku simpan untuk membantu aku
       jadi lebih baik ke depannya. Tapi ini pilihan kamu."

RINA: "Kalau boleh, percakapannya akan dienkripsi dan aman.
       Kalau tidak mau, oke banget — kita tetap ngobrol,
       cuma statistiknya yang aku simpan."

[Tombol: "Boleh 💙" | "Tidak dulu"]
```

### Apa Bedanya Kalau User Bilang Boleh vs Tidak?

| Data | Tanpa Izin | Dengan Izin |
|---|---|---|
| Fitur numerik (tidur, skor kerja, dll) | ✅ Disimpan | ✅ Disimpan |
| Risk level per sesi | ✅ Disimpan | ✅ Disimpan |
| Ringkasan singkat | ✅ Disimpan | ✅ Disimpan |
| Teks percakapan lengkap | ❌ Tidak | ✅ Tersimpan (dienkripsi) |

### User Bisa Cabut Izin Kapanpun
Di halaman Settings, ada tombol "Hapus semua data saya". Kalau diklik → semua data percakapan dihapus dari database.

---

## 📢 Disclaimer — Wajib Selalu Ditampilkan

### Di Onboarding (halaman sambutan pertama kali)
```
LifeLens adalah alat bantu refleksi diri,
BUKAN pengganti konsultasi dengan psikolog
atau tenaga kesehatan profesional.

Butuh bantuan profesional? Hubungi:
- Konselor kampus/psikolog
- Puskesmas terdekat
- Hotline Into The Light: 119 ext 8
```

### Di Setiap Output Risk Score
```
⚠️ Ini estimasi berdasarkan pola percakapan,
bukan diagnosis medis.
```

---

## 🗣️ Cara Framing Output yang Aman

Ini beda yang kecil tapi sangat penting:

```
❌ JANGAN PERNAH:
"Kamu mengalami burnout tingkat tinggi."
"Kamu terdiagnosis burnout berat."
"Kondisi kamu berbahaya."

✅ HARUS SELALU:
"Ada beberapa tanda yang mungkin perlu diperhatikan."
"Minggu ini terasa lebih berat dari biasanya."
"Pola yang muncul menunjukkan kamu perlu lebih banyak istirahat."
```

Perbedaannya: yang pertama adalah vonis. Yang kedua adalah informasi yang bisa ditindaklanjuti tanpa membuat user panik atau merasa "dilabeli".

---

## 🔐 Keamanan Data

### Enkripsi
```
Teks percakapan yang disimpan → dienkripsi AES-256
Kunci enkripsi → hanya ada di server, TIDAK di database
Artinya: bahkan kalau database bocor → teks tidak bisa dibaca
```

### Yang TIDAK PERNAH Disimpan
```
✗ Kata sandi user
✗ Nomor HP
✗ Lokasi
✗ Teks percakapan tanpa enkripsi
```

### HTTPS Wajib
Semua komunikasi antara frontend dan backend harus melalui HTTPS (terenkripsi). Vercel dan Railway sudah handle ini otomatis.

---

## 📝 Yang Harus Ditulis di Laporan

Bagian etika di laporan akhir harus mencakup:

**1. Keterbatasan Sistem**
"Sistem ini adalah screening tool. Tidak tervalidasi secara klinis. Tidak bisa menggantikan diagnosis profesional."

**2. Bias Dataset**
"Dataset primer berbahasa Inggris dan konteks barat. Kami mengatasi ini dengan..."

**3. Keputusan Privacy**
"Kami tidak menyimpan teks percakapan tanpa consent karena data mental health sangat sensitif."

**4. Privacy by Design**
"Kami menerapkan enkripsi AES-256 dan prinsip minimal data collection."

> Menulis ini secara jujur justru **menaikkan nilai laporan** karena menunjukkan tim berpikir tentang dampak teknologi yang dibangun.
