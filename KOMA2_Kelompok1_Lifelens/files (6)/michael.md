# 🧠 TUGAS MICHAEL — NLP, Persona RINA, Karakter & Dokumentasi
> Michael Deryl Aaron Matthew | 241712042
> Panduan lengkap tugasmu dari awal hingga selesai.

---

## 🎯 Peranmu dalam Tim

Michael membuat RINA "hidup" — baik secara bahasa maupun visual. Kamu menentukan bagaimana RINA berbicara, bagaimana sistem memahami emosi dari teks, dan bagaimana RINA terlihat.

```
Yang kamu hasilkan untuk tim:
├── NLP pipeline: analisis sentimen, ekstrak kata kunci
├── Gemini API integration: percakapan natural RINA
├── System prompt RINA yang menghasilkan percakapan berkualitas
├── JSON extraction dari percakapan
├── Adaptive language matching
├── (bersama Fikri) Desain dan animasi karakter 2D RINA
└── Laporan akhir dan dokumentasi teknis
```

---

## 📦 Deliverables (Yang Harus Diserahkan)

| # | Output | Kapan |
|---|---|---|
| 1 | IndoBERT test inference berhasil | Sprint 0 |
| 2 | `nlp.py` — sentiment + keyword extraction | Sprint 1 |
| 3 | `gemini.py` — integrasi + system prompt RINA | Sprint 1 |
| 4 | JSON extraction berjalan | Sprint 1 |
| 5 | Adaptive language matching | Sprint 2 |
| 6 | Trend analysis + rekomendasi | Sprint 2 |
| 7 | (dengan Fikri) SVG RINA base + 7 ekspresi | Sprint 2-3 |
| 8 | Laporan akhir lengkap | Sprint 4 |
| 9 | README.md komprehensif | Sprint 4 |

---

## 🔬 TUGAS 1 — Setup dan Test IndoBERT

### Apa yang Dilakukan
Download model IndoBERT dan verifikasi bisa dipakai untuk analisis sentimen Bahasa Indonesia.

### Menggunakan Apa
Library `transformers` dari HuggingFace. IndoBERT adalah model BERT yang sudah dilatih khusus untuk Bahasa Indonesia.

### Langkah-langkah

**Download model:**
```python
# Jalankan ini sekali untuk download dan cache model (~500MB)
from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("indobenchmark/indobert-base-p1")
model = AutoModel.from_pretrained("indobenchmark/indobert-base-p1")
print("IndoBERT berhasil didownload!")
```

**Test sentimen sederhana:**
```python
# Gunakan model sentiment yang sudah fine-tuned untuk Indonesia
from transformers import pipeline

sentiment = pipeline(
    "sentiment-analysis",
    model="mdhugol/indonesia-bert-sentiment-classifier"
)

# Test beberapa kalimat
hasil = sentiment("capek banget, deadline numpuk")
print(hasil)
# Output: [{'label': 'negative', 'score': 0.95}]
```

**Verifikasi berhasil:** Model mengenali kalimat negatif sebagai negatif dan positif sebagai positif dalam Bahasa Indonesia.

---

## 🔍 TUGAS 2 — NLP Pipeline

### Apa yang Dibuat
File `app/services/nlp.py` — kumpulan fungsi untuk menganalisis teks percakapan.

### Yang Harus Diimplementasikan

#### Fungsi 1: Analisis Sentimen

**Apa:** Mengukur apakah pesan user bersifat positif, negatif, atau netral.
**Output:** Angka dari -1 (sangat negatif) sampai +1 (sangat positif).
**Menggunakan:** IndoBERT yang sudah di-load.

Kenapa angka, bukan hanya "positif/negatif"?
Karena kita butuh melacak *perubahan* dari waktu ke waktu — naik atau turun?

---

#### Fungsi 2: Keyword Extraction

**Apa:** Temukan kata-kata kunci yang berkaitan dengan dimensi burnout.

**Cara kerja:** Punya kamus kata-kata per kategori:
```
Kategori 'stress_kerja': deadline, lembur, target, kpi, atasan, klien, ...
Kategori 'kelelahan': capek, lelah, exhausted, drain, loyo, habis, ...
Kategori 'masalah_tidur': insomnia, begadang, kurang tidur, susah tidur, ...
Kategori 'isolasi_sosial': sendirian, males keluar, menghindar, menyendiri, ...
```

Cek apakah ada kata dari setiap kategori di teks user.

**Menggunakan:** spaCy untuk tokenisasi + kamus kata domain burnout yang kamu buat sendiri.

---

#### Fungsi 3: Deteksi Pola Bahasa Kognitif

**Apa:** Cari kata-kata yang mengindikasikan cara pikir yang negatif.

**Absolutist language** — kata-kata yang berlebihan dan mutlak:
```
"selalu", "tidak pernah", "semua orang", "tidak ada yang"
```
Kenapa penting: orang yang burnout sering berpikir dengan pola absolut.

**Helplessness language** — frasa yang menunjukkan ketidakberdayaan:
```
"percuma", "mau apa lagi", "tidak bisa", "tidak ada gunanya"
```
Kenapa penting: perasaan tidak berdaya adalah tanda burnout yang kuat.

---

#### Fungsi Utama: extract_nlp_features(teks)

Satu fungsi yang memanggil semua fungsi di atas dan mengembalikan satu dict:
```python
def extract_nlp_features(teks: str) -> dict:
    """
    Input:  teks pesan user
    Output: dict berisi semua fitur NLP
    
    Contoh output:
    {
      'sentiment_score': -0.6,
      'domain_keywords': {'stress_kerja': ['deadline', 'atasan']},
      'absolutist_count': 2,
      'helplessness_count': 1,
      'message_length': 15
    }
    """
```

---

## 🤖 TUGAS 3 — Gemini API Integration

### Apa yang Dibuat
File `app/services/gemini.py` — koneksi ke Gemini API dengan persona RINA.

### Dua Bagian Penting

#### Bagian 1: System Prompt RINA

System prompt adalah "instruksi kepribadian" untuk Gemini — dikirim setiap kali ada percakapan.

**Yang harus ada dalam system prompt:**

1. **Identitas RINA** — siapa dia, apa yang tidak boleh dia katakan
2. **Aturan berbicara** — maks 1 pertanyaan, kalimat pendek, ikut gaya user
3. **Tugas tersembunyi** — data apa yang harus dikumpulkan secara natural
4. **Format output tersembunyi** — JSON di akhir respons (tidak terlihat user)
5. **Konteks user** — nama, hari ke-berapa, riwayat topik sebelumnya

**Lihat `04_conversation_persona.md` untuk contoh skrip percakapan yang diinginkan.**

---

#### Bagian 2: Kirim Pesan dan Parse Respons

Fungsi utama `get_rina_response(user_id, pesan)`:

1. Ambil konteks user dari database (riwayat topik, nama, dll)
2. Format system prompt dengan konteks itu
3. Kirim ke Gemini API
4. Terima respons yang berisi:
   - Teks percakapan RINA (yang user lihat)
   - JSON tersembunyi di akhir (data yang diekstrak)
5. Pisahkan keduanya:
   - Teks bersih → kirim ke frontend
   - JSON → parse dan kirim ke pipeline fitur

**Contoh konsep parsing:**
```python
import re

respons_penuh = """
Wah, itu berat banget ya... Deadlinenya sendiri atau ada tekanan lain?
[DATA:{"sleep_hours":5,"workload":8,"mood":4}]
"""

# Pisahkan teks dari JSON
json_pattern = r'\[DATA:(.*?)\]'
json_match = re.search(json_pattern, respons_penuh)

teks_bersih = re.sub(json_pattern, '', respons_penuh).strip()
data = json.loads(json_match.group(1)) if json_match else {}
```

---

## 🔤 TUGAS 4 — Adaptive Language Matching

### Apa yang Dibuat
Fungsi yang mendeteksi gaya bahasa user lalu menyesuaikan instruksi untuk RINA.

### Yang Dideteksi
```
Formalitas: pakai "saya/anda" (formal) vs "gw/lo" (santai)
English mix: berapa % kata berbahasa Inggris
Panjang pesan: pendek (< 10 kata) vs panjang (> 50 kata)
Emoji: ada atau tidak
```

### Cara Kerjanya
Hasil deteksi dimasukkan ke system prompt sebagai instruksi tambahan:
```
"Gaya user: santai, campur Inggris, pesan pendek.
 → Balas dengan gaya santai, boleh campur Inggris, jangan panjang."
```

---

## 📈 TUGAS 5 — Trend Analysis & Rekomendasi

### Trend Analysis

**Apa:** Prediksi arah kondisi user berdasarkan data 7 hari terakhir.

**Cara sederhana:** Lihat apakah sentimen dan fitur lain naik atau turun.
```
Sentimen hari 1: -0.2
Sentimen hari 7: -0.8
→ Tren: memburuk → prediksi minggu depan: kemungkinan memburuk lebih lanjut
```

### Sistem Rekomendasi

**Apa:** Berdasarkan faktor penyebab utama (dari SHAP), berikan saran praktis.

**Cara:** Punya "bank rekomendasi" per kategori masalah:
```
Masalah tidur → saran soal rutinitas tidur
Masalah beban kerja → saran manajemen prioritas
Masalah sosial → saran menjaga koneksi
Masalah pemulihan → saran aktivitas yang memulihkan
```

Pilih rekomendasi yang relevan berdasarkan top 3 faktor dari SHAP.

---

## 🎨 TUGAS 6 — Karakter RINA (bersama Fikri)

### Pembagian Kerja

**Michael mengerjakan:**
- Sketsa konsep karakter (gambar di kertas atau Figma)
- Digitize ke format SVG (Inkscape atau Figma)
- Membuat 7 layer ekspresi
- Memastikan semua ID SVG sesuai konvensi (lihat `assets.md`)

**Fikri mengerjakan:**
- GSAP CharacterController.js
- Logika state machine
- Lip sync controller

### Prioritas Ekspresi (buat urutan ini)
```
Prioritas 1 (harus ada untuk MVP):
  □ idle
  □ listening
  □ talking
  □ empathy

Prioritas 2 (untuk V1):
  □ happy
  □ thinking
  □ surprised
```

### Proses Membuat SVG

Langkah yang disarankan:
1. Cari referensi visual (lihat `assets.md` untuk keyword)
2. Sketch kasar di kertas — tentukan proporsi wajah, gaya rambut, pakaian
3. Digitize di Figma (gratis, berbasis web, tidak perlu install)
4. Export sebagai SVG
5. Buka SVG di VS Code — pastikan ID elemen sesuai konvensi
6. Test di browser — cek apakah semua terlihat benar
7. Kirim ke Fikri untuk diintegrasikan ke GSAP

**Pastikan konsultasi dengan Fikri** sebelum finalize ID karena GSAP akan menggunakan ID itu.

---

## 📝 TUGAS 7 — Laporan Akhir & Dokumentasi

### Struktur Laporan

```
BAB 1: Pendahuluan
  - Latar belakang (burnout, urgensi deteksi dini)
  - Rumusan masalah
  - Tujuan proyek

BAB 2: Tinjauan Pustaka
  - Burnout: definisi, MBI, 3 dimensi
  - NLP untuk analisis teks
  - ML untuk prediksi kesehatan mental

BAB 3: Metodologi
  - Dataset (tulis dari Nadya)
  - EDA dan preprocessing (dari Nadya)
  - Arsitektur sistem
  - NLP pipeline

BAB 4: Modeling
  - 3 algoritma yang dievaluasi (dari Fikri)
  - Hasil evaluasi dan model terpilih
  - SHAP explainability

BAB 5: Implementasi
  - Stack teknologi
  - Arsitektur deployment
  - Fitur aplikasi

BAB 6: Evaluasi
  - Hasil model (dari Fikri + Nadya)
  - User testing
  - Keterbatasan sistem

BAB 7: Kesimpulan & Saran

Lampiran:
  - Link GitHub
  - Model card
  - Contoh EDA notebook
```

### README.md untuk GitHub

README yang baik berisi:
```
- Nama proyek + tagline satu kalimat
- Screenshot atau GIF demo
- Link demo live (URL Vercel)
- Cara setup di lokal (langkah per langkah)
- Tech stack
- Daftar anggota tim + peran
- Disclaimer etis
```

---

## ✅ Checklist Tugasmu

```
SPRINT 0:
□ IndoBERT berhasil didownload
□ Test sentiment 1 kalimat berhasil
□ spaCy model terinstall
□ Sketsa RINA (kasar) sudah ada

SPRINT 1:
□ nlp.py: sentiment, keyword, cognitive pattern selesai
□ gemini.py: system prompt RINA selesai
□ JSON extraction dari respons Gemini berjalan
□ Test percakapan RINA terasa natural

SPRINT 2:
□ Adaptive language matching berjalan
□ Trend analysis module selesai
□ Recommendation system selesai
□ SVG RINA base selesai (4 ekspresi prioritas)
□ Semua SVG ID sesuai konvensi — konfirmasi dengan Fikri

SPRINT 3:
□ Semua 7 ekspresi SVG selesai
□ Koordinasi lip sync dengan Fikri

SPRINT 4:
□ Laporan akhir (koordinasi semua anggota)
□ README.md lengkap
□ Model card final
□ Slide presentasi teknis
```
