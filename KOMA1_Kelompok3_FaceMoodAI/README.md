<div align="center">

# 🎭 FaceMood AI
### Know Your Mood, Embrace Yourself

**Sistem deteksi emosi wajah berbasis kecerdasan buatan yang memberikan rekomendasi aktivitas personal.**

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-3.1.2-lightgrey?style=flat-square)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.21.0-orange?style=flat-square)
![Akurasi](https://img.shields.io/badge/Akurasi%20Model-81%25-green?style=flat-square)

</div>

---

## Tentang Proyek

FaceMood AI adalah sistem yang mampu mendeteksi emosi seseorang melalui citra wajah, kemudian memberikan rekomendasi aktivitas yang sesuai dengan kondisi emosional tersebut. Pengguna cukup mengunggah foto wajah atau menggunakan kamera secara langsung, dan sistem akan menganalisis ekspresi wajah secara otomatis menggunakan model Convolutional Neural Network (CNN) yang telah dilatih dengan dataset RAF-DB.

---

## ✨ Fitur Utama

- **Deteksi 7 Emosi** — Happy, Sad, Angry, Surprise, Fear, Disgust, Neutral
- **Dua Metode Input** — Upload foto dari perangkat atau gunakan kamera secara langsung
- **Tingkat Keyakinan** — Menampilkan persentase keyakinan dari hasil prediksi
- **Rekomendasi Aktivitas** — Saran aktivitas yang disesuaikan dengan kondisi emosional pengguna
- **Tema Dinamis** — Warna halaman berubah otomatis mengikuti emosi yang terdeteksi

---

## 🛠️ Teknologi yang Digunakan

| Komponen | Teknologi |
|----------|-----------|
| Model AI | TensorFlow, Keras, CNN |
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| Dataset | RAF-DB (Real-world Affective Faces Database) |
| Pendukung | OpenCV, NumPy, Pillow, scikit-learn |

---

## 📊 Hasil Model

| Kelas | F1-Score |
|-------|----------|
| Happy | 0.92 |
| Surprise | 0.82 |
| Sad | 0.77 |
| Neutral | 0.76 |
| Angry | 0.75 |
| Fear | 0.59 |
| Disgust | 0.41 |
| **Rata-rata (Akurasi)** | **81%** |

> Model tidak mengalami overfitting — nilai akurasi validasi secara konsisten lebih tinggi dibandingkan akurasi data latih sepanjang proses pelatihan.

---

## 📁 Struktur Proyek

```
KOMA1_Kelompok3_FaceMoodAI/
│
├── static/                      # File CSS dan JavaScript
├── templates/                   # File HTML halaman web
├── model/
│   └── facemood_raf_model.h5    # Model CNN yang telah dilatih
├── app.py                       # File utama Flask
├── requirements.txt             # Daftar dependensi
└── README.md
```

---

## 🚀 Cara Menjalankan Proyek

### 1. Clone repositori ini

```bash
git clone https://github.com/Asisten-Laboratorium-Teknik-Informatika/Semester-4-Praktikum-AI-2026.git
cd Semester-4-Praktikum-AI-2026/KOMA1_Kelompok3_FaceMoodAI
```

### 2. Install dependensi

Pastikan Python sudah terinstall di perangkatmu, lalu jalankan:

```bash
pip install -r requirements.txt
```

> Proses instalasi mungkin membutuhkan beberapa menit karena ukuran library seperti TensorFlow cukup besar.

### 3. Jalankan aplikasi

```bash
python app.py
```

### 4. Buka di browser

```
http://localhost:5000
```

Aplikasi siap digunakan. ✓

---

## 🔄 Alur Penggunaan

```
Buka aplikasi
     ↓
Pilih metode input → Upload foto  ──┐
                  → Gunakan kamera ─┤
                                    ↓
                             Klik "Analisis"
                                    ↓
                          Emosi terdeteksi
                                    ↓
                        Isi kolom cerita (opsional)
                                    ↓
                       Rekomendasi aktivitas muncul
```

---

## 👥 Tim Pengembang

Proyek ini dikembangkan oleh Kelompok 3 dalam mata kuliah Praktikum Kecerdasan Buatan 2026.

| Nama | NIM |
|------|-----|
| Aditya Fahreza | 241712013 |
| Ivana Kristina Siagian | 241712021 |
| Jelita Crisna Zalukhu | 241712022 |

*Kelompok 3 · Praktikum Kecerdasan Buatan · 2026*
