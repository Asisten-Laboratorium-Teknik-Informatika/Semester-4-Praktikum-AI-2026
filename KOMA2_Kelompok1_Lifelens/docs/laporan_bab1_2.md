# LAPORAN TUGAS AKHIR — LifeLens
## AI-based Lifestyle Pattern Analysis and Burnout Risk Prediction

**Tim Pengembang:**
- Nadya Putri Anggina (241712040)
- Argya Ariella (241712028)
- Muhammad Fikri Ramadhan (241712027)
- Michael Deryl Aaron Matthew (241712042)

**Program Studi:** D3 Teknik Informatika  
**Universitas:** Universitas Sumatera Utara  
**Kelas:** KOM A2

---

# BAB 1: PENDAHULUAN

## 1.1 Latar Belakang

Burnout merupakan sindrom yang diakibatkan oleh stres kerja kronis yang tidak berhasil dikelola dengan baik (WHO, 2019). Menurut International Classification of Diseases 11th Revision (ICD-11), burnout ditandai oleh tiga dimensi utama: kelelahan emosional (*emotional exhaustion*), depersonalisasi (*cynicism*), dan berkurangnya pencapaian personal (*reduced personal accomplishment*).

Fenomena burnout semakin meningkat secara global, terutama setelah pandemi COVID-19 yang mengubah pola kerja dan gaya hidup secara drastis. Survei Gallup (2023) menunjukkan bahwa 76% pekerja mengalami burnout setidaknya kadang-kadang, sementara 28% melaporkan burnout "sangat sering" atau "selalu." Di Indonesia, data Kementerian Kesehatan menunjukkan peningkatan signifikan dalam gangguan kesehatan mental terkait pekerjaan, termasuk burnout.

Deteksi dini burnout menjadi krusial karena burnout yang tidak ditangani dapat berujung pada depresi klinis, gangguan kecemasan, masalah kardiovaskular, dan dalam kasus ekstrem, bunuh diri. Namun, akses ke profesional kesehatan mental di Indonesia masih sangat terbatas, dengan rasio psikolog terhadap populasi yang jauh di bawah standar WHO.

Kemajuan dalam bidang kecerdasan buatan (AI), khususnya *Natural Language Processing* (NLP) dan *Machine Learning* (ML), membuka peluang untuk mengembangkan sistem screening burnout yang dapat diakses secara luas. Dengan menganalisis pola percakapan dan gaya hidup pengguna, AI dapat mengidentifikasi tanda-tanda awal burnout sebelum kondisi memburuk.

LifeLens hadir sebagai solusi berupa aplikasi web yang menggunakan chatbot AI bernama RINA (*Responsive Intelligent Nurturing Assistant*) untuk melakukan screening burnout secara non-invasif melalui percakapan natural dalam Bahasa Indonesia. RINA dirancang bukan sebagai pengganti profesional kesehatan mental, melainkan sebagai alat deteksi dini yang mendorong pengguna untuk mendapatkan bantuan yang tepat.

## 1.2 Rumusan Masalah

1. Bagaimana merancang dan mengimplementasikan sistem AI yang dapat menganalisis pola gaya hidup melalui percakapan natural untuk mendeteksi risiko burnout?
2. Bagaimana membangun pipeline NLP yang efektif untuk mengekstraksi fitur bermakna dari teks percakapan Bahasa Indonesia?
3. Bagaimana membangun model Machine Learning yang akurat untuk mengklasifikasikan tingkat risiko burnout (LOW, MEDIUM, HIGH)?
4. Bagaimana merancang persona AI (RINA) yang empatik dan mampu membangun kepercayaan pengguna tanpa terasa seperti chatbot generik?

## 1.3 Tujuan

### Tujuan Umum
Mengembangkan aplikasi web berbasis AI yang mampu mendeteksi risiko burnout secara dini melalui analisis pola percakapan dan gaya hidup pengguna.

### Tujuan Khusus
1. Membangun pipeline NLP menggunakan IndoBERT untuk analisis sentimen teks Bahasa Indonesia.
2. Melatih dan mengevaluasi model Machine Learning (Random Forest, XGBoost, LightGBM) untuk klasifikasi tingkat burnout.
3. Mengintegrasikan Gemini AI sebagai mesin percakapan dengan persona RINA yang hangat dan empatik.
4. Mengimplementasikan sistem keamanan termasuk deteksi kondisi krisis dan enkripsi data pengguna.
5. Membangun antarmuka web yang responsif dan mudah digunakan.

## 1.4 Batasan Sistem

1. **Bukan Alat Diagnosis:** LifeLens adalah screening tool, bukan pengganti diagnosis klinis oleh profesional kesehatan mental.
2. **Bahasa:** Sistem dioptimalkan untuk percakapan Bahasa Indonesia.
3. **Dataset:** Model dilatih menggunakan dataset Employee Burnout Analysis dari Kaggle (berbahasa Inggris) yang dilengkapi dengan dataset sintetis berbahasa Indonesia.
4. **Konektivitas:** Sistem membutuhkan koneksi internet untuk Gemini API dan IndoBERT inference.
5. **Validasi:** Model belum divalidasi secara klinis dengan populasi Indonesia yang lebih luas.

## 1.5 Manfaat

1. **Bagi Pengguna:** Menyediakan sarana deteksi dini burnout yang mudah diakses, gratis, dan tanpa stigma.
2. **Bagi Institusi:** Memberikan insight mengenai kesejahteraan mental karyawan/mahasiswa.
3. **Bagi Akademik:** Berkontribusi pada penelitian NLP dan ML untuk kesehatan mental dalam konteks bahasa Indonesia.
4. **Bagi Masyarakat:** Meningkatkan kesadaran akan pentingnya kesehatan mental dan deteksi dini burnout.

---

# BAB 2: TINJAUAN PUSTAKA

## 2.1 Burnout

### 2.1.1 Definisi Burnout
Burnout pertama kali didefinisikan oleh Herbert Freudenberger (1974) sebagai keadaan kelelahan yang diakibatkan oleh tuntutan berlebihan terhadap energi, kekuatan, atau sumber daya seseorang. Christina Maslach kemudian mengembangkan konsep ini dan mendefinisikan burnout sebagai sindrom psikologis yang melibatkan tiga dimensi:

1. **Kelelahan Emosional (*Emotional Exhaustion*):** Perasaan kehabisan sumber daya emosional dan fisik.
2. **Depersonalisasi (*Cynicism*):** Sikap negatif, sinis, atau terpisah terhadap pekerjaan dan orang di sekitar.
3. **Berkurangnya Pencapaian Personal (*Reduced Personal Accomplishment*):** Evaluasi negatif terhadap diri sendiri dan merasa tidak produktif.

### 2.1.2 Maslach Burnout Inventory (MBI)
MBI adalah instrumen pengukuran burnout yang paling banyak digunakan dalam penelitian (Maslach & Jackson, 1981). MBI terdiri dari 22 item yang mengukur tiga dimensi burnout. Skor yang lebih tinggi pada dimensi kelelahan emosional dan depersonalisasi, serta skor yang lebih rendah pada pencapaian personal, mengindikasikan burnout yang lebih berat.

### 2.1.3 Faktor Risiko Burnout
Berdasarkan meta-analisis dari berbagai penelitian, faktor risiko burnout meliputi:
- **Faktor Pekerjaan:** Beban kerja berlebihan, kurang otonomi, kurang dukungan sosial, ketidakjelasan peran.
- **Faktor Individual:** Perfeksionisme, kesulitan mengelola emosi, rendahnya *self-efficacy*.
- **Faktor Gaya Hidup:** Kurang tidur, kurang olahraga, isolasi sosial, kurangnya waktu pemulihan.

## 2.2 Machine Learning untuk Prediksi Kesehatan Mental

### 2.2.1 Supervised Learning Classification
Klasifikasi *supervised learning* merupakan pendekatan ML yang paling umum digunakan untuk prediksi risiko kesehatan mental. Dalam konteks burnout, model menerima fitur-fitur (jam tidur, beban kerja, skor sentimen, dll.) dan memprediksi label kelas (LOW, MEDIUM, HIGH).

### 2.2.2 Algoritma yang Digunakan

**Random Forest** (Breiman, 2001): Ensemble method yang menggunakan banyak decision tree dan menggabungkan prediksi melalui voting. Kelebihan: robust terhadap overfitting, mampu menangani fitur yang banyak.

**XGBoost** (Chen & Guestrin, 2016): Gradient boosting framework yang mengoptimalkan loss function menggunakan gradient descent. Kelebihan: performa tinggi, regularisasi bawaan, mampu menangani missing values.

**LightGBM** (Ke et al., 2017): Gradient boosting framework dari Microsoft dengan teknik leaf-wise tree growth. Kelebihan: lebih cepat dari XGBoost untuk dataset besar, efisien memori, akurasi kompetitif.

### 2.2.3 SHAP Explainability
SHAP (*SHapley Additive exPlanations*) (Lundberg & Lee, 2017) adalah metode untuk menjelaskan prediksi ML berdasarkan teori permainan Shapley. SHAP mengukur kontribusi setiap fitur terhadap prediksi model, memungkinkan transparansi dan *explainability* yang penting dalam konteks kesehatan mental.

### 2.2.4 Evaluasi Model
Metrik evaluasi yang relevan untuk prediksi burnout:
- **AUC-ROC:** Mengukur kemampuan model membedakan antar kelas secara keseluruhan.
- **Recall (Sensitivity):** Sangat penting untuk kelas HIGH — lebih baik salah prediksi HIGH daripada melewatkan kasus serius.
- **F1-Score:** Harmonic mean dari precision dan recall, cocok untuk dataset imbalanced.
- **Confusion Matrix:** Visualisasi kesalahan klasifikasi antar kelas.

## 2.3 Natural Language Processing untuk Analisis Sentimen

### 2.3.1 IndoBERT
IndoBERT (Wilie et al., 2020) adalah model bahasa pre-trained berbasis BERT yang dilatih pada korpus teks Bahasa Indonesia. IndoBERT mampu melakukan berbagai tugas NLP termasuk analisis sentimen, named entity recognition, dan text classification.

Dalam proyek ini, digunakan model `mdhugol/indonesia-bert-sentiment-classification` yang merupakan fine-tuned IndoBERT untuk klasifikasi sentimen tiga kelas (positif, netral, negatif).

### 2.3.2 Keyword Extraction dan Domain Analysis
Selain sentimen, analisis teks percakapan juga meliputi:
- **Domain Keyword Detection:** Mendeteksi kata kunci yang berkaitan dengan dimensi burnout (work stress, exhaustion, sleep problems, social withdrawal, motivation loss).
- **Absolutist Language Detection:** Mendeteksi pola bahasa absolutist ("selalu", "tidak pernah", "semua orang") yang merupakan indikator distorsi kognitif.
- **Helplessness Phrase Detection:** Mendeteksi frasa ketidakberdayaan ("percuma", "tidak bisa", "untuk apa") yang berkorelasi dengan tingkat burnout yang lebih tinggi.

### 2.3.3 Conversational AI — Gemini
Google Gemini (2024) adalah model bahasa multimodal generasi terbaru dari Google DeepMind. Dalam proyek ini, Gemini 2.5 Flash digunakan sebagai mesin percakapan untuk RINA, dengan system prompt yang mengatur persona, gaya bahasa, dan tugas tersembunyi (data extraction via JSON).

## 2.4 Keamanan dan Etika

### 2.4.1 Safety Protocol
Sistem deteksi krisis menggunakan keyword matching untuk mengidentifikasi pesan yang mengindikasikan pikiran bunuh diri atau self-harm. Ketika terdeteksi, sistem langsung memberikan informasi hotline darurat (119 ext 8 — Into The Light Indonesia) dan menghentikan proses analisis normal.

### 2.4.2 Enkripsi Data
Data percakapan pengguna dienkripsi menggunakan Fernet symmetric encryption dari library `cryptography`. Ini memastikan bahwa data sensitif tidak pernah disimpan dalam bentuk plain text.

### 2.4.3 Disclaimer
Sistem secara konsisten menampilkan disclaimer bahwa LifeLens adalah screening tool, bukan pengganti diagnosis klinis oleh profesional kesehatan mental.

---

*Laporan ini akan dilanjutkan dengan BAB 3 (Metodologi), BAB 4 (Desain Sistem), BAB 5 (Implementasi), BAB 6 (Evaluasi & Pengujian), dan BAB 7 (Kesimpulan & Saran).*
