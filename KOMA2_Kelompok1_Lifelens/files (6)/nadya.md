# 📊 TUGAS NADYA — Data EDA & Preprocessing
> Nadya Putri Anggina | 241712040
> Panduan lengkap tugasmu dari awal hingga selesai.

---

## 🎯 Peranmu dalam Tim

Nadya adalah **fondasi ilmiah proyek ini**. Tanpa EDA dan preprocessing yang bagus, model ML Fikri tidak bisa dipercaya — garbage in, garbage out.

```
Yang kamu hasilkan untuk tim:
├── Pemahaman mendalam tentang data burnout
├── Dataset yang bersih dan siap dilatih
├── Pipeline preprocessing yang bisa dipakai ulang
├── Synthetic dataset berbahasa Indonesia
├── Dokumentasi EDA yang rapi (untuk laporan)
└── Analisis fitur untuk membantu Fikri memilih model
```

---

## 📦 Deliverables (Yang Harus Diserahkan)

| # | Output | Format | Kapan |
|---|---|---|---|
| 1 | Notebook EDA lengkap | `eda_burnout.ipynb` | Akhir Sprint 1 |
| 2 | Script preprocessing | `preprocessing.py` | Akhir Sprint 1 |
| 3 | Dataset final (train/test) | `.csv` | Akhir Sprint 1 |
| 4 | Script generate synthetic data | `generate_synthetic.py` | Akhir Sprint 2 |
| 5 | Pipeline fitur longitudinal | `feature_engineering.py` | Akhir Sprint 2 |
| 6 | Visualisasi untuk presentasi | gambar `.png` di `outputs/` | Sprint 4 |

---

## 🗂️ TUGAS 1 — Download Dataset

### Apa yang Dilakukan
Download dataset dari Kaggle yang akan jadi bahan training model.

### Langkah-langkah
1. Setup Kaggle API (lihat `requirements.md` bagian Kaggle)
2. Buka terminal, aktifkan virtual environment
3. Jalankan perintah download
4. Cek file berhasil didownload

**Dataset yang didownload:**
```bash
# Dataset utama burnout
kaggle datasets download blurredmachine/are-your-employees-burning-out

# Dataset mental health pendukung
kaggle datasets download osmi/mental-health-in-tech-survey

# Ekstrak file
# (unzip di folder data/)
```

5. Buat struktur folder:
```
data/
├── raw/          ← taruh file CSV asli di sini (jangan ubah)
├── processed/    ← dataset yang sudah dibersihkan
└── synthetic/    ← dataset buatan sendiri nanti
```

---

## 📊 TUGAS 2 — EDA (Exploratory Data Analysis)

### Apa yang Dilakukan
Memahami dataset secara mendalam sebelum memprosesnya. Seperti membaca peta sebelum mulai perjalanan.

### Buat File: `eda_burnout.ipynb`
Notebook Jupyter dengan beberapa section. Setiap section harus punya:
- **Kode** untuk analisis
- **Visualisasi** yang informatif
- **Markdown** yang menjelaskan temuan dalam bahasa Indonesia

---

### Section 1: Eksplorasi Awal

**Apa:** Lihat isi dataset secara umum — berapa baris, kolom apa saja, tipe datanya.

**Menggunakan:** `pandas`

**Contoh potongan kode (ini ilustrasi, kembangkan sendiri):**
```python
import pandas as pd

df = pd.read_csv('data/raw/employee_burnout_analysis.csv')

print("Jumlah baris dan kolom:", df.shape)
print("\nNama kolom:", df.columns.tolist())
print("\nTipe data:\n", df.dtypes)
print("\n5 baris pertama:\n", df.head())
```

**Yang dicatat di Markdown:** Jumlah data, nama kolom, apa artinya masing-masing kolom.

---

### Section 2: Distribusi Label Burnout

**Apa:** Ubah kolom `Burn Rate` (angka 0-1) menjadi label LOW/MEDIUM/HIGH, lalu lihat distribusinya.

**Kenapa penting:** Kalau datanya 80% LOW dan hanya 5% HIGH, kita punya masalah imbalanced data yang harus diatasi. Ini menentukan banyak keputusan selanjutnya.

**Contoh potongan kode:**
```python
import matplotlib.pyplot as plt

# Ubah angka jadi label
def buat_label(nilai):
    if nilai <= 0.33: return 'LOW'
    elif nilai <= 0.66: return 'MEDIUM'
    else: return 'HIGH'

df['burnout_label'] = df['Burn Rate'].apply(buat_label)

# Visualisasi
df['burnout_label'].value_counts().plot(kind='bar', color=['green','orange','red'])
plt.title('Distribusi Label Burnout')
plt.savefig('outputs/distribusi_label.png')
```

**Yang dicatat di Markdown:** Persentase masing-masing label, dan keputusan: "karena data imbalanced, kita akan pakai SMOTE saat preprocessing."

---

### Section 3: Missing Values

**Apa:** Cari kolom-kolom yang datanya kosong (null/NaN).

**Kenapa penting:** Model ML tidak bisa proses data kosong — harus ada keputusan: hapus atau isi?

**Contoh potongan kode:**
```python
# Lihat berapa persen data yang kosong per kolom
missing_pct = (df.isnull().sum() / len(df) * 100).round(1)
print(missing_pct[missing_pct > 0])
```

**Yang dicatat di Markdown:** Kolom mana yang kosong, berapa persennya, dan **keputusan**: hapus baris atau isi dengan median/mode?

---

### Section 4: Distribusi Fitur Numerik

**Apa:** Lihat sebaran nilai setiap kolom numerik dengan histogram.

**Kenapa penting:** Fitur yang sangat "miring" (skewed) mungkin perlu transformasi. Fitur yang tidak bervariasi mungkin tidak berguna.

**Contoh potongan kode:**
```python
import seaborn as sns

fitur_numerik = ['Resource Allocation', 'Mental Fatigue Score', 'Burn Rate']
df[fitur_numerik].hist(bins=20, figsize=(12, 4))
plt.savefig('outputs/distribusi_fitur.png')
```

---

### Section 5: Korelasi (Hubungan Antar Fitur)

**Apa:** Lihat seberapa kuat hubungan antara satu fitur dengan fitur lain, terutama dengan Burn Rate.

**Kenapa penting:** Fitur yang sangat berkorelasi dengan Burn Rate = fitur penting untuk model. Fitur yang saling berkorelasi satu sama lain = mungkin bisa dipilih salah satu saja.

**Contoh potongan kode:**
```python
sns.heatmap(df[fitur_numerik].corr(), annot=True, fmt='.2f', cmap='coolwarm')
plt.title('Korelasi Antar Fitur')
plt.savefig('outputs/korelasi.png')
```

---

### Section 6: Outlier

**Apa:** Cari nilai yang sangat jauh dari rata-rata.

**Kenapa penting:** Outlier bisa merusak model, TAPI di kasus burnout, outlier bisa = kasus burnout paling parah yang justru harus dideteksi.

**Yang dicatat di Markdown:** Berapa outlier ditemukan, dan keputusan: **jangan auto-hapus**. Periksa dulu apakah itu error data atau kasus ekstrem yang valid.

---

### Section 7: Bias Audit

**Apa:** Cek apakah ada perbedaan pola burnout berdasarkan gender, jenis perusahaan, atau jabatan.

**Kenapa penting:** Kalau model lebih akurat untuk satu kelompok tertentu, itu masalah etis. Harus didokumentasikan di laporan.

---

## 🔧 TUGAS 3 — Preprocessing Pipeline

### Apa yang Dibuat
File Python `preprocessing.py` berisi kelas/fungsi yang bisa dipanggil Fikri untuk menyiapkan data sebelum training.

### Yang Harus Diimplementasikan

**Handle Missing Values:**
```
Strategi:
- Baris dengan Burn Rate kosong → HAPUS (ini target variable)
- Kolom fitur kosong → ISI dengan nilai median
  Kenapa median? Tidak dipengaruhi outlier
```

**Encode Kategorikal:**
```
Ubah teks jadi angka:
- Gender: Male→0, Female→1
- Company Type: Service→0, Product→1
- WFH Setup: No→0, Yes→1
```

**Scaling (Normalisasi):**
```
Pakai StandardScaler dari scikit-learn
PENTING: fit() hanya pada data training!
         transform() pada training DAN testing
```

**Train/Test Split:**
```
Proporsi: 80% training, 20% testing
Parameter stratify=y: WAJIB, agar proporsi LOW/MEDIUM/HIGH
                      sama di kedua bagian
```

**Handle Imbalanced (SMOTE):**
```
Pakai SMOTE dari imbalanced-learn
PENTING: SMOTE hanya pada data training!
         JANGAN pada data testing!
```

### Cara Pakainya (untuk Fikri)
```python
# Fikri tinggal import dan pakai
from preprocessing import BurnoutPreprocessor

prep = BurnoutPreprocessor()
X_train, X_test, y_train, y_test = prep.fit_transform(df)

# Simpan preprocessor untuk dipakai saat prediksi real-time
prep.save('ml_models/preprocessor.pkl')
```

---

## 🤖 TUGAS 4 — Synthetic Dataset

### Apa yang Dibuat
Script `generate_synthetic.py` yang menggunakan Gemini API untuk generate percakapan burnout dalam Bahasa Indonesia.

### Kenapa Perlu
Dataset Kaggle berbahasa Inggris dan konteks barat. Kita butuh contoh percakapan dalam Bahasa Indonesia dengan konteks lokal.

### Cara Kerjanya
Kamu mengirim prompt ke Gemini yang berisi:
- Profil user (profesi, level burnout, kondisi tidur, dll)
- Instruksi format output (JSON)
- Aturan: percakapan harus natural, bahasa Indonesia

Gemini menghasilkan satu percakapan lengkap beserta data fiturnya dalam format JSON.

### Target
```
3 level × 10 profesi × 5 variasi = 150 percakapan

Level: LOW, MEDIUM, HIGH
Profesi: software developer, mahasiswa, guru, dokter muda,
         desainer, marketing, akuntan, freelancer, dll
```

---

## 🔄 TUGAS 5 — Feature Engineering Longitudinal

### Apa yang Dibuat
Fungsi di `feature_engineering.py` untuk menghitung fitur berbasis tren dari data 7 hari.

### Fitur Kritis yang Harus Dihitung

**sentiment_slope_7d** — Ini yang paling prediktif
```
Apa: Apakah sentimen user membaik atau memburuk dalam 7 hari?
Cara hitung: ambil sentimen score 7 hari → hitung kemiringan garis trend
Nilai negatif = sentimen memburuk (tanda burnout berkembang)
```

**sleep_workload_ratio** — Rasio tidur vs beban kerja
```
Apa: Apakah tidur sebanding dengan beban kerja?
Cara hitung: jam_tidur / (beban_kerja + 1)
Nilai kecil = tidur tidak cukup untuk beban yang ada
```

**recovery_deficit** — Defisit pemulihan
```
Apa: Apakah waktu luang cukup memulihkan?
Cara hitung: beban_kerja - (kepuasan_recovery * 2)
Nilai besar = butuh lebih banyak pemulihan
```

---

## ✅ Checklist Tugasmu

```
SPRINT 0:
□ Dataset Kaggle berhasil didownload
□ Bisa buka file CSV di Python
□ Folder data/ sudah terbuat

SPRINT 1:
□ EDA notebook selesai (7 section)
□ Semua visualisasi tersimpan di outputs/
□ Setiap section ada penjelasan Markdown
□ Preprocessing pipeline selesai dan ditest

SPRINT 2:
□ Generate 150 synthetic conversations
□ Feature engineering pipeline selesai
□ Dataset final (gabungan Kaggle + synthetic) siap

SPRINT 3:
□ Bias audit selesai
□ Re-train jika ada dataset baru

SPRINT 4:
□ Notebook rapi untuk presentasi
□ Export visualisasi untuk slide
□ Bantu Michael/Fikri jika butuh analisis tambahan
```
