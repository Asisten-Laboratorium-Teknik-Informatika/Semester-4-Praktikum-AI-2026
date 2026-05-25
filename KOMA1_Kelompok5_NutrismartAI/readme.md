<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/dashboard.png" /># NutriSmart AI - Premium Health Dashboard

NutriSmart AI adalah aplikasi asisten kesehatan personal berbasis web yang mengintegrasikan kalkulasi medis standar gizi dengan algoritma kecerdasan buatan untuk menyediakan rekomendasi menu makanan yang terpersonalisasi secara instan dan aman.

## 🛠️ Arsitektur & Logika Sistem

Aplikasi ini bekerja dengan menggabungkan dua pilar utama:
1. **Pilar Medis:** Menggunakan parameter biometrik pengguna (Usia, Berat Badan, Tinggi Badan, Jenis Kelamin, dan Aktivitas) untuk menghitung nilai BMR dan TDEE berdasarkan **Persamaan Harris-Benedict**.
2. **Pilar AI (Machine Learning):** Menggunakan algoritma **K-Nearest Neighbors (KNN)** dengan konstanta $K=3$ untuk memindai basis data resep dan menarik 3 menu makanan terdekat yang nilai kalorinya paling identik dengan target kebutuhan pengguna menggunakan perhitungan *Euclidean Distance*.

## 📁 Struktur Repositori

```text
NUTRISMART_APP/
│
├── data/
│   ├── final_recipes.csv       # Basis data resep utama (hasil cleaning & filtering)
│   ├── logo.png                # Aset logo aplikasi
│   ├── makananpagi.jpg         # Aset gambar UI
│   ├── makanansiang.jpg        # Aset gambar UI
│   └── makananmalam.jpg        # Aset gambar UI
│
├── models/
│   └── knn_model.pkl           # Berkas model KNN terlatih (otak AI)
│
├── app.py                      # File utama aplikasi Streamlit (UI & Antarmuka)
├── ai_logic.py                 # Modul konfigurasi fungsi pembantu KNN
├── clean_data.py               # Skrip development untuk preprocessing data (opsional)
├── audit_data.py               # Skrip development untuk audit kualitas data (opsional)
└── README.md                   # Dokumentasi proyek
Catatan Pengembangan: File dataset mentah skala besar (RAW_recipes.csv) dan folder lingkungan virtual (venv) sengaja dieksklusi dari repositori ini untuk optimalisasi ukuran penyimpanan. Aplikasi diproduksi langsung menggunakan model terekspor .pkl dan data ringkas final_recipes.csv.

⚙️ Fitur Utama Aplikasi
Smart Input Sidebar: Panel interaktif pengisian data fisik dan preferensi pengguna.

Automated Allergen Filter: Penyaringan bahan makanan berbahaya secara dinamis menggunakan pengondisian string matching.

Dynamic Data Visuals: Visualisasi pembagian porsi makronutrisi (Karbohidrat, Protein, Lemak) secara real-time menggunakan grafik Plotly.

Personalized Recipe Cards: Kartu rekomendasi menu masakan adaptif yang dilengkapi dengan fitur penomoran otomatis panduan memasak (steps parsing) yang aman via library ast.literal_eval.

🚀 Panduan Instalasi Lokal
Ikuti langkah-langkah berikut untuk menjalankan aplikasi di lingkungan lokal Anda:

Clone atau Ekstrak Repositori
Pastikan seluruh struktur folder di atas sudah berada di dalam direktori kerja Anda.

Buat Lingkungan Virtual (Virtual Environment)
Buka terminal di direktori proyek tersebut, lalu jalankan perintah:

Bash
python -m venv venv
Aktifkan Lingkungan Virtual

Windows (PowerShell):

Bash
.\venv\Scripts\Activate.ps1
Linux / macOS:

Bash
source venv/bin/activate
Instalasi Dependensi Pustaka
Instal pustaka Python yang dibutuhkan secara manual melalui terminal:

Bash
pip install streamlit pandas scikit-learn plotly matplotlib seaborn
Jalankan Aplikasi
Eksekusi perintah Streamlit untuk meluncurkan dasbor di peramban (browser) Anda:

Bash
streamlit run app.py
👥 Anggota Kelompok 5
Tegar Madya Shafwan (241712002)

Anggota Kelompok (241712010)

Anggota Kelompok (241712012)

Reza Pahlepi (241712013)

Ruth Angel Sihombing (241712014)


---

### 💡 Keunggulan File `README.md` Ini:
- **Jelas untuk Teman Sekelompok:** Mereka langsung tahu file apa saja yang ada dan file besar apa saja yang sengaja dibuang agar tidak panik saat mengunduh berkas ZIP.
- **Petunjuk Instalasi Rapi:** Langkah-langkah pembuatan `venv` dan instalasi *library* ditulis secara urut, sehingga teman Anda yang awam koding pun bisa menjalankannya sendiri di laptop mereka tinggal mengikuti instruksi di atas.
