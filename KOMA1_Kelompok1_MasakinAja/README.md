# 🍳 Masakin Apa? — AI Food Ingredient Detection & Recipe Recommendation

## Deskripsi Aplikasi
“Masakin Apa?” merupakan aplikasi berbasis Artificial Intelligence yang dapat membantu pengguna menemukan rekomendasi resep masakan Indonesia berdasarkan bahan makanan yang dimiliki.
Pengguna dapat mengunggah gambar bahan makanan, kemudian sistem akan mendeteksi bahan menggunakan model Deep Learning berbasis MobileNetV2 dan menampilkan rekomendasi resep secara otomatis.
Aplikasi ini dibangun menggunakan Python, Streamlit, TensorFlow/Keras, serta recommendation system berbasis dataset resep Indonesia.

---

# ✨ Fitur Utama

- Upload gambar bahan makanan
- Deteksi bahan makanan menggunakan AI
- Top-k prediction (beberapa kemungkinan hasil deteksi)
- Confidence score hasil prediksi
- Input manual bahan makanan
- Rekomendasi resep otomatis
- Tampilan resep modern berbentuk card
- Pagination resep
- Flow khusus protein (ayam, daging, ikan)
- Pilihan jenis ikan untuk rekomendasi lebih spesifik
- Dark mode modern UI

---

# 🧠 Teknologi yang Digunakan

## Backend & AI
- Python
- TensorFlow
- Keras
- MobileNetV2
- NumPy
- Pandas
- PIL (Python Imaging Library)

## Frontend
- Streamlit
- Custom CSS

## Development Tools
- Visual Studio Code (VS Code)
- Google Colab
- Google Drive

## Dataset
- Kaggle Food Ingredient Dataset
- Indonesian Food Recipe Dataset

---

# 📂 Struktur Folder

```bash
MasakinApa/
│
├── app.py
├── requirements.txt
├── resep_clean.csv
├── label_bahan.json
│
├── model/
│   └── model_masakinapa_best.h5
│
├── dataset_gambar/
│   ├── train/
│   ├── validation/
│   └── test/
│
└── assets/
```

## ⚙️ Persyaratan Sistem

Sebelum menjalankan aplikasi, pastikan sudah menginstal:
1. Python 3.10 atau lebih baru
2. pip
3. Virtual environment (opsional)

## 📦 Instalasi Dependensi

Buka terminal atau Command Prompt di dalam folder project, lalu jalankan:
```bash
pip install -r requirements.txt
```

Jika belum memiliki file requirements.txt, gunakan:
```bash
pip install streamlit tensorflow pandas numpy pillow scikit-learn
```

## ▶️ Cara Menjalankan Aplikasi

Masuk ke folder project:
```bash
cd MasakinApa
```
Lalu jalankan Streamlit:
```bash
streamlit run app.py
```

Tunggu beberapa saat hingga browser terbuka otomatis.
Jika tidak terbuka otomatis, akses:
```bash
```bash
pip install -r requirements.txt
```

## 📸 Cara Menggunakan Aplikasi
1. Upload gambar bahan makanan
2. AI akan mendeteksi bahan makanan
3. Pilih hasil deteksi yang paling sesuai
4. Jika terdeteksi protein, pilih jenis protein
5. Jika memilih ikan, pilih jenis ikan
6. Sistem akan menampilkan rekomendasi resep secara otomatis

🧠 Model AI

Model AI menggunakan:
1. MobileNetV2 (Transfer Learning)
2. Input size 224x224
3. Fine-tuning pada layer akhir
4. Augmentasi gambar untuk meningkatkan generalisasi model

## ❤️ Terima Kasih 
Terima kasih telah menggunakan aplikasi “Masakin Apa?” 🍳
