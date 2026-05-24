# KOMA1 Kelompok 4 - Deteksi Review Pada Platform E-Commerce

Aplikasi ini merupakan sistem deteksi ulasan/review (asli atau palsu) pada platform e-commerce menggunakan Machine Learning dan Tesseract OCR (Optical Character Recognition). Aplikasi ini memiliki arsitektur client-server sederhana: backend menggunakan Python Flask dan frontend menggunakan HTML/CSS/JS.

## Persyaratan Sistem

Sebelum menjalankan aplikasi, pastikan Anda telah menginstal:

1. **Python** (versi 3.7 atau lebih baru)
2. **Tesseract OCR**:
   - Unduh installer Tesseract OCR untuk Windows dari [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
   - Saat instalasi, pastikan Tesseract diinstal di path bawaan aplikasi ini: `C:\Program Files\Tesseract-OCR\tesseract.exe`
   - Jika Anda menginstalnya di lokasi yang berbeda, Anda perlu mengubah variabel konfigurasi di baris 37 pada file `app.py`:
     ```python
     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
     ```

## Cara Instalasi Dependensi

Buka terminal/Command Prompt di dalam folder proyek ini (`KOMA1_Kelompok4_DeteksiReviewPadaPlatformE-Commerce`), lalu instal library Python yang dibutuhkan dengan menjalankan perintah berikut:

```bash
pip install flask joblib pytesseract Pillow scikit-learn
```

> **Catatan**: Jika Anda mendapati error terkait model `scikit-learn` saat menjalankan aplikasi, pastikan versi `scikit-learn` sesuai dengan versi saat model (`model_deteksi.pkl` dan `vectorizer.pkl`) dilatih.

## Cara Menjalankan Aplikasi

Aplikasi ini terdiri dari dua bagian yang berjalan bersamaan: Backend (API Flask) dan Frontend (Antarmuka Web).

### Langkah 1: Menjalankan Backend (Server API)

1. Buka terminal atau Command Prompt.
2. Arahkan ke direktori proyek ini.
3. Jalankan file `app.py` menggunakan Python:
   ```bash
   python app.py
   ```
4. Biarkan terminal tetap terbuka. Server API akan berjalan pada `http://127.0.0.1:5000`.

### Langkah 2: Menjalankan Frontend (Antarmuka Web)

Frontend dari aplikasi ini menggunakan file HTML statis sederhana, sehingga ga perlu server web khusus. Bisa menjalankannya dengan salah satu cara berikut:

- **1. Cara Termudah**: Cukup klik ganda (double-click) pada file `index.html` di dalam folder ini untuk membukanya langsung di browser (seperti Chrome, Edge, atau Firefox).
- **2. Menggunakan Live Server (VS Code)**: Jika Anda menggunakan Visual Studio Code, Anda bisa menginstal ekstensi "Live Server", lalu klik kanan pada file `index.html` dan pilih **"Open with Live Server"**.

Setelah halaman terbuka, aplikasi siap digunakan. Anda dapat memasukkan ulasan secara manual melalui teks, atau mengunggah gambar berisi ulasan. 

**Terimakasih Sudah Membaca Panduan**
