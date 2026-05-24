# TruthLens — AI Fake News Detector

## Setup
1. Copy `best_model.h5` dan `tokenizer_bilstm.pkl` dari project lama ke folder ini.
2. Install dependencies: `pip install flask tensorflow numpy`
3. Jalankan: `python app.py`
4. Buka browser: `http://localhost:5000`

## Perubahan
- **app.py**: Ditambahkan validasi input, error handling lengkap, HTTP status codes yang benar, dan response data tambahan (word_count).
- **templates/index.html**: UI/UX didesain ulang sepenuhnya — dark theme premium, animasi halus, confidence bar, sample teks, dan pesan error yang informatif.
