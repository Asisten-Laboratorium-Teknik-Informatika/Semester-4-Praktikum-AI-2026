# 🔬 AI & ML PIPELINE — LifeLens
> EDA → Preprocessing → Modeling → Evaluasi
> Dokumen ini untuk Nadya (EDA & data) dan Fikri (modeling).

---

## 🧠 Kenapa Kita Perlu Pipeline Ini?

Kita perlu mengajarkan komputer untuk mengenali pola burnout.
Caranya: kasih komputer banyak contoh data orang yang burnout dan yang tidak → komputer belajar polanya → bisa prediksi orang baru.

Pipeline ini adalah **proses belajarnya**, dari data mentah sampai model yang siap pakai.

```
Data Mentah → Pahami → Bersihkan → Latih Model → Evaluasi → Deploy
   (EDA)    (EDA)    (Preprocessing)  (Modeling)  (Evaluasi) (Fikri)
```

---

## 📊 FASE 1 — EDA (Exploratory Data Analysis)
**Dikerjakan oleh: Nadya**

### Apa itu EDA?
EDA adalah proses **mengenal dataset sebelum memprosesnya**. Seperti membaca buku baru — kamu baca daftar isi dulu sebelum baca isinya.

Tujuannya: pahami data kita, temukan masalah, putuskan cara handle-nya.

### Analisis 1: Distribusi Label

**Apa yang dilakukan:** Lihat berapa banyak data LOW, MEDIUM, HIGH burnout.

**Kenapa perlu:** Kalau datanya 90% LOW dan 10% HIGH, model akan "malas" belajar mengenali HIGH. Ini masalah yang harus diatasi.

**Menggunakan:** `pandas` untuk hitung, `matplotlib/seaborn` untuk visualisasi.

**Contoh sederhana:**
```python
import pandas as pd
import seaborn as sns

df = pd.read_csv('burnout_data.csv')

# Lihat distribusi label
print(df['burnout_label'].value_counts())
# Output contoh:
# LOW      14000  (62%)
# MEDIUM    6000  (26%)
# HIGH      2750  (12%)  ← ini yang perlu perhatian khusus

# Visualisasi
df['burnout_label'].value_counts().plot(kind='bar')
```

**Hasil:** Tahu apakah data kita seimbang atau tidak → menentukan strategi selanjutnya.

---

### Analisis 2: Missing Values (Data yang Kosong)

**Apa yang dilakukan:** Temukan kolom-kolom yang datanya tidak lengkap.

**Kenapa perlu:** Model ML tidak bisa proses data yang kosong — harus ada strategi untuk handle ini.

**Contoh sederhana:**
```python
# Hitung persentase data kosong per kolom
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(1)
print(missing_pct[missing_pct > 0])

# Contoh output:
# Mental Fatigue Score    8.3%  ← perlu diisi (imputasi)
# Burn Rate               1.5%  ← baris ini dihapus (target variable)
```

**Keputusan yang harus dibuat:**
- Kolom target (burn_rate) kosong → hapus baris itu
- Kolom fitur kosong → isi dengan nilai median

---

### Analisis 3: Korelasi Antar Fitur

**Apa yang dilakukan:** Lihat apakah ada hubungan antara fitur-fitur yang kita punya.

**Kenapa perlu:** Kalau `mental_fatigue` sangat berkorelasi dengan burnout, itu fitur paling penting. Kalau dua fitur sangat mirip satu sama lain, kita bisa buang salah satunya.

**Contoh sederhana:**
```python
# Heatmap korelasi
corr = df[['resource_allocation', 'mental_fatigue', 'burn_rate']].corr()
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm')

# Fokus pada: korelasi dengan burn_rate
# Kolom dengan korelasi tinggi = fitur penting untuk model
```

---

### Analisis 4: Outlier (Data Ekstrem)

**Apa yang dilakukan:** Temukan nilai-nilai yang sangat tidak normal.

**Kenapa perlu:** Outlier bisa merusak model — tapi di kasus burnout, outlier justru bisa = kasus burnout ekstrem yang penting!

**Aturan penting:**
```
❌ JANGAN auto-hapus outlier tanpa diperiksa manual
✅ Periksa dulu: apakah outlier ini data error atau kasus burnout berat?
   Jika kasus burnout berat → PERTAHANKAN, ini justru penting untuk model
```

---

## 🔧 FASE 2 — PREPROCESSING
**Dikerjakan oleh: Nadya**

### Apa itu Preprocessing?
Preprocessing adalah **membersihkan dan memformat data** agar bisa dimasukkan ke model ML. Model ML hanya bisa membaca angka — semua harus diubah jadi angka dulu.

### Langkah 1: Handle Missing Values

**Strategi:**
```
Kolom target (burn_rate) kosong → hapus baris ini sepenuhnya
Kolom fitur kosong → isi dengan nilai median kolom itu
   Kenapa median? Karena median tidak terpengaruh outlier
```

**Contoh cara kerjanya:**
```python
# Isi nilai kosong dengan median
from sklearn.impute import SimpleImputer

imputer = SimpleImputer(strategy='median')
df_filled = imputer.fit_transform(df[numerical_columns])
# Sekarang tidak ada lagi nilai kosong
```

---

### Langkah 2: Encode Kategorikal

**Apa yang dilakukan:** Ubah teks jadi angka.

**Kenapa:** Model ML tidak mengerti kata "Male"/"Female" atau "Yes"/"No". Harus diubah jadi 0 dan 1.

**Contoh:**
```python
# Sebelum: Gender = "Male" / "Female"
# Sesudah: Gender = 0 / 1

mapping = {'Male': 0, 'Female': 1, 'Yes': 1, 'No': 0}
df['Gender'] = df['Gender'].map(mapping)
```

---

### Langkah 3: Scaling (Normalisasi)

**Apa yang dilakukan:** Seragamkan skala semua angka.

**Kenapa:** Kalau `sleep_hours` nilainya 1–10 tapi `workload_score` nilainya 1–100, model akan lebih "memperhatikan" workload padahal belum tentu lebih penting.

**Aturan penting:**
```
StandardScaler di-FIT hanya pada data training
Lalu di-TRANSFORM pada data training DAN testing
JANGAN fit pada data testing! Ini akan "bocorkan" informasi
```

---

### Langkah 4: Handle Imbalanced Data (SMOTE)

**Apa yang dilakukan:** Tambah data buatan untuk kelas yang kurang (HIGH burnout).

**Kenapa:** Kalau data HIGH burnout cuma 10%, model tidak akan belajar mengenalinya dengan baik.

**Menggunakan:** library `imbalanced-learn` dengan teknik SMOTE.

**Aturan penting:**
```
SMOTE hanya dilakukan pada data TRAINING
JANGAN lakukan SMOTE pada data testing!
Kenapa? Karena kita ingin test pada data nyata, bukan data buatan
```

---

### Langkah 5: Train/Test Split

**Apa yang dilakukan:** Bagi data jadi dua — untuk belajar (train) dan untuk ujian (test).

**Kenapa:** Kita tidak bisa ujian model dengan soal yang sama persis dengan yang dipelajari — hasilnya tidak akan jujur.

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,      # 20% untuk test
    random_state=42,    # agar hasilnya bisa diulang
    stratify=y          # PENTING: jaga proporsi LOW/MEDIUM/HIGH
)
```

---

## 🤖 FASE 3 — MODELING
**Dikerjakan oleh: Fikri**

### Apa yang Dibuat?
Tiga model ML dilatih, dievaluasi, dan **dipilih satu yang terbaik** untuk di-deploy.

### Tiga Model yang Dilatih

**Random Forest** — "komite ahli"
Bayangkan 200 orang ahli berbeda masing-masing memberi pendapat, lalu diambil suara terbanyak.
- Kelebihan: stabil, tidak mudah overfit
- Cocok untuk: data kecil (<1000 baris)

**XGBoost** — "belajar dari kesalahan"
Setiap model baru belajar dari kesalahan model sebelumnya, semakin lama semakin pintar.
- Kelebihan: sangat akurat untuk data tabular
- Cocok untuk: dataset ukuran sedang-besar

**LightGBM** — "versi cepat XGBoost"
Cara kerja mirip XGBoost tapi jauh lebih cepat.
- Kelebihan: paling cepat dilatih, hemat memori
- Cocok untuk: dataset besar atau resource terbatas

### Cara Evaluasi Model

**Jangan pakai Accuracy saja!** Karena data imbalanced, accuracy bisa 90% padahal model tidak pernah benar mendeteksi HIGH burnout.

Metrik yang wajib dilihat:
```
AUC-ROC     → seberapa baik model membedakan LOW/MEDIUM/HIGH
              Nilai 1.0 = sempurna, 0.5 = sama dengan tebak-tebakan
              Target kita: > 0.75

Recall@HIGH → dari semua kasus HIGH burnout yang ada,
              berapa persen berhasil dideteksi?
              Ini PALING PENTING — lebih baik false alarm
              daripada miss kasus burnout berat

Confusion Matrix → tabel yang tunjukkan
              berapa yang benar terdeteksi per kategori
```

### SHAP — Menjelaskan Hasil Model

**Apa itu SHAP?** SHAP adalah library yang bisa menjelaskan **kenapa** model memutuskan sesuatu.

**Kenapa perlu?** Karena user harus tahu kenapa mereka dapat label HIGH, bukan cuma angkanya. "Kamu HIGH RISK karena: tidur kurang + beban kerja tinggi + sentimen memburuk."

**Contoh output SHAP:**
```
Prediksi: HIGH RISK
Faktor yang berkontribusi:
  1. Sentimen memburuk 7 hari terakhir  (+0.35)
  2. Tidur hanya 5 jam                  (+0.28)
  3. Beban kerja 8/10                   (+0.21)
```

---

## 📊 FASE 4 — EVALUASI & PILIH MODEL TERBAIK

Setelah ketiga model dilatih, bandingkan hasilnya:

```
Model           | AUC-ROC | Recall@HIGH | Waktu Training
----------------|---------|-------------|---------------
Random Forest   | 0.812   | 0.74        | 45 detik
XGBoost         | 0.847   | 0.81        | 30 detik
LightGBM        | 0.851   | 0.83        | 8 detik

→ Pilih LightGBM (atau XGBoost jika selisih kecil)
```

Model yang menang disimpan sebagai file `.pkl` dan dipakai di server.

---

## 💾 Menyimpan Model

Setelah model dipilih, simpan ke file:
```
ml_models/
├── burnout_model.pkl     → model ML yang dipilih
├── scaler.pkl            → StandardScaler (untuk transform data baru)
├── shap_explainer.pkl    → untuk hitung SHAP values
└── model_card.json       → dokumentasi: algoritma, performa, keterbatasan
```

Model card (`model_card.json`) wajib ada untuk laporan — berisi nama algoritma, tanggal training, performa, dan keterbatasan sistem.

---

## ⚠️ Hal yang Sering Salah (dan Cara Hindarinya)

| Kesalahan Umum | Kenapa Salah | Cara Benar |
|---|---|---|
| Fit scaler pada test data | "Bocorkan" info test ke model | Fit hanya pada train data |
| Hapus outlier langsung | Bisa hapus kasus burnout penting | Periksa manual dulu |
| Pakai accuracy untuk imbalanced data | Menyesatkan | Pakai AUC-ROC + Recall |
| SMOTE pada test data | Test jadi tidak representatif | SMOTE hanya pada train |
| Tidak pakai stratify di split | Proporsi kelas bisa berubah | Selalu gunakan stratify=y |
