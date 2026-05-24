# 🤟 AI Hand-Sign Translator

![Python](https://img.shields.io/badge/Python-3.11-3776ab?style=flat-square&logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15.0-FF6F00?style=flat-square&logo=tensorflow&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web_Framework-000000?style=flat-square&logo=flask&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Computer_Vision-00C853?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

> Sistem kecerdasan buatan berbasis *Computer Vision* yang mendeteksi dan menerjemahkan gerakan tangan secara *real-time* menjadi teks dan suara Bahasa Indonesia — langsung dari browser, tanpa instalasi tambahan.

Dikembangkan sebagai Projek Akhir Praktikum Artificial Intelligence, Program Studi D-3 Teknik Informatika, Universitas Sumatera Utara.

---

## ✨ Fitur Utama

| Fitur | Deskripsi |
|---|---|
| 🎯 **Real-Time Tracking** | Melacak 126 titik koordinat (*landmark*) dari kedua tangan secara presisi menggunakan **Google MediaPipe** |
| 🧠 **Time-Series Detection** | Arsitektur **LSTM** memahami urutan gerak 30 frame (~1 detik), bukan sekadar gambar statis |
| 🗂️ **10 Kosakata Dinamis** | Mengenali: *Halo, Kamu, Gimana, Semua, Aku, Tugas, Selesai, Cinta, Aku sayang kamu, Mantap* |
| 🛡️ **Debounce Algorithm** | Algoritma penahan jeda memastikan akurasi transisi antar kata dan mencegah deteksi ganda |
| 🔊 **Voice Output** | *Text-to-Speech* via **gTTS** yang menyuarakan kalimat dalam aksen Bahasa Indonesia natural |
| 🌐 **Web-Based Interface** | Di-*deploy* sebagai aplikasi web lokal menggunakan **Flask** — cukup buka browser |

---

## 🛠️ Arsitektur & Teknologi

Sistem dibangun dari hulu ke hilir melalui empat tahap pipeline:

```
Kamera (OpenCV)
      │
      ▼
MediaPipe Hands ──► Ekstrak 126 koordinat (21 landmark × 3 sumbu × 2 tangan)
      │
      ▼
Sliding Window ──► Kumpulkan 30 frame terakhir → tensor (30 × 126)
      │
      ▼
Model LSTM ──► LSTM(64) → LSTM(128) → LSTM(64) → Dense(64) → Dense(32) → Softmax(10)
      │
      ▼
Debounce ──► Keyakinan > 60% & konsisten ≥ 15 frame
      │
      ▼
Output: Teks di layar + Suara (gTTS + PyGame, thread terpisah)
```

### Stack Teknologi

| Tahap | Teknologi |
|---|---|
| Akuisisi Data | `OpenCV` + `MediaPipe` |
| Preprocessing | `NumPy` + `Scikit-Learn` |
| Pelatihan Model | `TensorFlow` / `Keras` |
| Deployment | `Flask` + `gTTS` + `PyGame` |

---

## ⚙️ Instalasi & Menjalankan

### Prasyarat
- Python **3.11**
- Kamera (webcam internal atau eksternal)
- Koneksi internet (untuk fitur gTTS)

## 🎮 Cara Penggunaan

1. Jalankan server (`python app_web.py`) dan buka browser ke `http://127.0.0.1:5000`
2. Izinkan akses kamera saat diminta browser
3. Posisikan tangan di depan kamera dalam area yang terlihat jelas
4. Peragakan salah satu dari 10 gestur isyarat yang didukung
5. **Tahan gestur ± 1 detik** hingga sistem mengenali dan menampilkan teks
6. Suara akan keluar otomatis — kalimat terakumulasi di bagian bawah layar

> **Tips:** Pastikan pencahayaan cukup dan latar belakang tidak terlalu kompleks untuk hasil deteksi terbaik.

---

## 🗃️ Dataset & Pelatihan Ulang

Untuk merekam kata isyarat baru:
```bash
# Edit variabel kata_isyarat di rekam_data.py, lalu jalankan:
python rekam_data.py
```

Untuk melatih ulang model setelah menambah data:
```bash
python latih_ai.py
```

Model terbaik akan otomatis tersimpan sebagai `model_isyarat.h5` via `ModelCheckpoint`.

---

## 👥 Tim Pengembang

**Praktikum AI — Kelompok A2**  
Program Studi D-3 Teknik Informatika, Universitas Sumatera Utara

| Nama | NIM | Peran |
|---|---|---|
| Adeptri Sagala | 241712024 | Model (Training & Evaluasi) |
| Kabul Manik | 241712023 | App / Deployment |
| Peter Rangga Situmorang | 241712039 | Data (EDA & Preprocessing) |

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE).
