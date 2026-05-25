# 📊 DATASET — LifeLens
> Data apa yang dibutuhkan, dari mana mendapatkannya, dan bagaimana menggunakannya.
> Dikerjakan oleh: Nadya (download + EDA + preprocessing)

---

## 🧠 Kenapa Kita Perlu Dataset?

Model ML tidak bisa "berpikir sendiri". Kita harus **mengajarinya** dengan contoh-contoh nyata: "ini data orang yang burnout, ini yang tidak". Makin banyak dan berkualitas contohnya, makin pintar modelnya.

Tantangan terbesar: **dataset burnout berbahasa Indonesia hampir tidak ada**. Jadi kita pakai strategi kombinasi.

---

## 🗂️ Strategi Dataset — 4 Sumber

```
Sumber 1: Dataset Kaggle (utama, sudah ada labelnya)
Sumber 2: Dataset NLP Indonesia (untuk analisis teks)
Sumber 3: Dataset Buatan Sendiri (via Gemini, konteks Indonesia)
Sumber 4: Profil MBI (untuk labeling yang valid secara psikologis)
```

---

## 📦 DATASET 1 — Employee Burnout (Kaggle)
**Prioritas: WAJIB | Dikerjakan pertama**

### Apa ini?
Dataset survei 22.750 karyawan dengan data beban kerja, kelelahan mental, dan tingkat burnout.

### Dari mana?
```
URL: kaggle.com/datasets/blurredmachine/are-your-employees-burning-out
Nama file: employee_burnout_analysis.csv
```

### Cara Download
1. Daftar akun Kaggle (gratis)
2. Buka Settings → API → Create Token → download `kaggle.json`
3. Taruh file `kaggle.json` di folder `~/.kaggle/`
4. Jalankan di terminal:
```bash
kaggle datasets download blurredmachine/are-your-employees-burning-out
```

### Isi Datanya
```
Kolom yang tersedia:
- Employee ID       → ID karyawan (tidak berguna, dihapus)
- Gender            → Laki-laki/Perempuan
- Company Type      → Service/Product
- WFH Setup         → Kerja dari rumah atau tidak
- Designation       → Jabatan (0-5, makin tinggi makin senior)
- Resource Alloc    → Jam kerja yang dialokasikan (1-10)
- Mental Fatigue    → Tingkat kelelahan mental (0-10)
- Burn Rate         → ← INI TARGET/LABEL kita (0-1, makin tinggi makin burnout)
```

### Cara Menggunakannya
Kolom `Burn Rate` adalah angka 0-1. Ubah jadi label kategori:
```
0.00 - 0.33  →  LOW burnout
0.34 - 0.66  →  MEDIUM burnout
0.67 - 1.00  →  HIGH burnout
```

---

## 📦 DATASET 2 — IndoNLU (NLP Bahasa Indonesia)
**Prioritas: WAJIB untuk Michael (NLP Pipeline)**

### Apa ini?
Kumpulan dataset NLP Bahasa Indonesia, termasuk dataset sentimen dan emosi.

### Dari mana?
```
GitHub: github.com/IndoNLP/indonlu
Bisa download via library Python 'datasets'
```

### Cara Download
```python
# Install library dulu
pip install datasets

# Download subset sentimen
from datasets import load_dataset
dataset = load_dataset("indonlp/indonlu", "smsa")
```

### Untuk Apa?
- Melatih model sentimen Bahasa Indonesia
- Validasi bahwa NLP pipeline kita akurat untuk teks Indonesia

---

## 📦 DATASET 3 — Synthetic (Buatan Sendiri)
**Prioritas: PENTING | Dikerjakan setelah dataset Kaggle selesai**

### Kenapa Perlu Buat Sendiri?
Dataset Kaggle berbahasa Inggris dan konteks barat. Kita perlu contoh percakapan burnout dalam **Bahasa Indonesia dengan konteks lokal** (jam lembur di Indonesia, kultur kerja Indonesia, dll).

### Cara Membuatnya
Gunakan Gemini API untuk generate percakapan sintesis:

**Idenya:** Minta Gemini generate 150+ percakapan antara RINA dan user dengan berbagai profil burnout (LOW/MEDIUM/HIGH) dan berbagai profesi.

**Contoh instruksi ke Gemini (bukan kode final):**
```
"Buat percakapan 6-8 pesan antara RINA dan seorang software developer
 yang mengalami MEDIUM burnout. Kondisinya: tidur 5-6 jam, deadline banyak,
 mulai menarik diri dari sosial. Bahasa: Indonesia casual.
 Output: JSON dengan conversation[] dan features{}"
```

### Target Dataset Synthetic
```
3 level × 10 profesi × 5 variasi = 150 percakapan

Profesi yang dicakup:
- Software developer, desainer, guru, mahasiswa,
  marketing, akuntan, freelancer, customer service, dll
```

### Format Output JSON
Setiap percakapan disimpan sebagai:
```json
{
  "burnout_level": "MEDIUM",
  "profession": "software developer",
  "conversation": [
    {"role": "rina", "text": "Hai! Hari ini gimana?"},
    {"role": "user", "text": "Lumayan, agak capek..."}
  ],
  "features": {
    "sleep_hours": 5.5,
    "workload_score": 7,
    "mood_score": 4
  }
}
```

---

## 📦 DATASET 4 — MBI-Based Profiles (Standar Psikologi)
**Prioritas: PENTING untuk validitas ilmiah**

### Apa ini?
MBI (Maslach Burnout Inventory) adalah instrumen psikologi standar untuk mengukur burnout. Kita pakai skoring MBI sebagai **cara labeling yang valid secara ilmiah**.

### Tiga Dimensi MBI

```
Exhaustion    → Kelelahan emosional (skala 0-6, HIGH jika ≥ 3.2)
Cynicism      → Sikap dingin terhadap kerja (skala 0-6, HIGH jika ≥ 2.1)
Efficacy      → Rasa kompeten (skala 0-6, LOW jika ≤ 3.0)
```

### Cara Labeling dengan MBI
```
HIGH burnout = Exhaustion tinggi + Cynicism tinggi + Efficacy rendah
MEDIUM       = Salah satu atau dua dimensi bermasalah
LOW          = Semua dalam range normal
```

Ini yang membuat sistem kita bisa dipertanggungjawabkan secara ilmiah — kita menggunakan standar yang sudah tervalidasi.

---

## 🔄 Cara Menggabungkan Semua Dataset

Setelah semua dataset ada, gabungkan:

```
Dataset Kaggle:
  → Fitur numerik kuat (workload, fatigue, designation)
  → Label dari burn_rate
  → Kelemahan: tidak ada fitur NLP, konteks barat

Dataset Synthetic:
  → Fitur NLP kuat (sentimen, kata kunci, pola bahasa)
  → Label dari profil yang di-generate
  → Kelemahan: data buatan, validitas eksternal lebih rendah

Gabungan keduanya → model yang lebih kuat dari masing-masing
```

Saat menggabungkan, perhatikan:
- Kolom harus sama namanya
- Nilai kosong tetap harus dihandle
- Catat sumber data di kolom `source` ('kaggle' atau 'synthetic')

---

## ⚠️ Keterbatasan Dataset — Wajib Ditulis di Laporan

Ini bukan kelemahan — ini menunjukkan kejujuran dan kedewasaan akademis:

```
1. Dataset primer berbahasa Inggris, konteks barat
   → Norma jam kerja di Indonesia berbeda
   → Kita atasi dengan: synthetic data Indonesia

2. Dataset burnout Indonesia hampir tidak ada
   → Synthetic data membantu tapi validitas terbatas
   → Dokumentasikan ini di laporan

3. Data imbalanced (HIGH burnout hanya ~10-15%)
   → Kita atasi dengan SMOTE + class weight

4. Dataset Kaggle dominan sektor tech
   → Kita atasi dengan synthetic data berbagai profesi
```

> **Tip laporan:** Menulis keterbatasan dengan jujur dan menyebutkan mitigasinya justru menunjukkan bahwa tim memahami data dan metodologinya. Ini nilai plus, bukan nilai minus.
