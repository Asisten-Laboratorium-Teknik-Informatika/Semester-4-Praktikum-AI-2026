from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import json, datetime
import os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = joblib.load(os.path.join(BASE_DIR, 'model_deteksi_diabetes.pkl'))
scaler = joblib.load(os.path.join(BASE_DIR, 'scaler.pkl'))

def generate_saran(data, prediksi, label):
    """
    Hasilkan saran kesehatan berdasarkan nilai input dan hasil prediksi.
    Semua logika berbasis ambang batas medis standar — tidak butuh model tambahan.
    Sekarang juga menerima data gaya hidup (aktivitas, diet, alkohol, stres, tidur)
    untuk menghasilkan rekomendasi yang lebih cerdas dan kontekstual.
    """
    saran = []
 
    age     = float(data['age'])
    bmi     = float(data['bmi'])
    hba1c   = float(data['HbA1c_level'])
    glucose = float(data['blood_glucose_level'])
    htn     = int(data['hypertension'])
    hd      = int(data['heart_disease'])
    smoking = data['smoking_history']

    # Data gaya hidup dari langkah 7, 8, 9
    activity = data.get('activity', 'SEDANG')
    diet     = data.get('diet', '')
    alcohol  = data.get('alcohol', 'never')
    stress   = data.get('stress', '')
    sleep    = data.get('sleep', 'normal')

    # Konversi tipe data untuk perbandingan yang aman
    try:
        diet_val   = int(diet) if diet != '' else None
    except (ValueError, TypeError):
        diet_val = None
    try:
        stress_val = int(stress) if stress != '' else None
    except (ValueError, TypeError):
        stress_val = None

    # ─── ANALISIS BIOMARKER UTAMA ───

    if glucose >= 200:
        saran.append({
            "ikon":  "🔴",
            "judul": "Gula Darah Sangat Tinggi",
            "teks":  f"Kadar gula darah {glucose} mg/dL sangat melebihi batas normal (<140 mg/dL). "
                     "Segera konsultasikan ke dokter untuk pemeriksaan lebih lanjut."
        })
    elif glucose >= 140:
        saran.append({
            "ikon":  "🟠",
            "judul": "Gula Darah Tinggi",
            "teks":  f"Kadar gula darah {glucose} mg/dL di atas normal. "
                     "Kurangi konsumsi makanan tinggi gula dan karbohidrat sederhana."
        })
    else:
        saran.append({
            "ikon":  "🟢",
            "judul": "Gula Darah Normal",
            "teks":  f"Kadar gula darah {glucose} mg/dL masih dalam batas normal. Pertahankan pola makan sehat."
        })
 
    if hba1c >= 6.5:
        saran.append({
            "ikon":  "🔴",
            "judul": "HbA1c Masuk Kategori Diabetes",
            "teks":  f"HbA1c {hba1c}% ≥ 6.5% merupakan ambang diagnosis diabetes. "
                     "Diperlukan pemantauan rutin dan konsultasi dokter segera."
        })
    elif hba1c >= 5.7:
        saran.append({
            "ikon":  "🟠",
            "judul": "HbA1c Masuk Kategori Prediabetes",
            "teks":  f"HbA1c {hba1c}% berada di zona prediabetes (5.7–6.4%). "
                     "Terapkan pola makan rendah gula dan olahraga rutin minimal 30 menit/hari."
        })
    else:
        saran.append({
            "ikon":  "🟢",
            "judul": "HbA1c Normal",
            "teks":  f"HbA1c {hba1c}% masih dalam batas normal (<5.7%). Pertahankan gaya hidup sehat."
        })
 
    if bmi >= 30:
        saran.append({
            "ikon":  "🟠",
            "judul": "BMI Kategori Obesitas",
            "teks":  f"BMI {bmi:.1f} kg/m² masuk kategori obesitas (≥30). "
                     "Obesitas meningkatkan risiko diabetes secara signifikan. "
                     "Targetkan penurunan berat badan 5–10% melalui diet dan olahraga."
        })
    elif bmi >= 25:
        saran.append({
            "ikon":  "🟡",
            "judul": "BMI Kategori Overweight",
            "teks":  f"BMI {bmi:.1f} kg/m² masuk kategori overweight (25–29.9). "
                     "Jaga pola makan dan tingkatkan aktivitas fisik."
        })
    elif bmi < 18.5:
        saran.append({
            "ikon":  "🟡",
            "judul": "BMI Terlalu Rendah",
            "teks":  f"BMI {bmi:.1f} kg/m² di bawah normal (<18.5). "
                     "Pastikan asupan nutrisi mencukupi dan konsultasikan ke ahli gizi."
        })
    else:
        saran.append({
            "ikon":  "🟢",
            "judul": "BMI Normal",
            "teks":  f"BMI {bmi:.1f} kg/m² dalam rentang ideal (18.5–24.9). Pertahankan berat badan."
        })
 
    if age >= 45:
        saran.append({
            "ikon":  "🟡",
            "judul": "Faktor Risiko Usia",
            "teks":  f"Usia {int(age)} tahun termasuk kelompok rentan diabetes. "
                     "Disarankan melakukan skrining gula darah minimal 1x per tahun."
        })
 
    if htn == 1:
        saran.append({
            "ikon":  "🟠",
            "judul": "Hipertensi Terdeteksi",
            "teks":  "Hipertensi dan diabetes sering muncul bersamaan dan saling memperburuk. "
                     "Pantau tekanan darah secara rutin dan patuhi anjuran dokter."
        })
 
    if hd == 1:
        saran.append({
            "ikon":  "🔴",
            "judul": "Riwayat Penyakit Jantung",
            "teks":  "Penyakit jantung meningkatkan risiko komplikasi diabetes. "
                     "Pengelolaan gula darah yang ketat sangat penting. "
                     "Konsultasikan jadwal pemeriksaan rutin ke dokter spesialis."
        })
 
    if smoking == 'current':
        saran.append({
            "ikon":  "🟠",
            "judul": "Perokok Aktif",
            "teks":  "Merokok memperburuk resistensi insulin dan meningkatkan risiko komplikasi diabetes. "
                     "Program berhenti merokok sangat dianjurkan."
        })
    elif smoking == 'former':
        saran.append({
            "ikon":  "🟡",
            "judul": "Mantan Perokok",
            "teks":  "Risiko akibat merokok masih bisa bertahan beberapa tahun. "
                     "Pertahankan keputusan berhenti merokok dan pantau kondisi kesehatan secara rutin."
        })

    # ─── ANALISIS GAYA HIDUP (Langkah 7, 8, 9) ───

    # Aktivitas Fisik (Langkah 7)
    if activity == 'RENDAH':
        if bmi >= 25:
            saran.append({
                "ikon":  "🏃",
                "judul": "Aktivitas Rendah + Berat Badan Berlebih",
                "teks":  "Kombinasi kurang gerak dan BMI berlebih meningkatkan risiko diabetes secara signifikan. "
                         "Mulailah dengan jalan kaki 15 menit sehari, lalu tingkatkan bertahap "
                         "ke 150 menit olahraga aerobik per minggu (jalan cepat, bersepeda, atau berenang)."
            })
        else:
            saran.append({
                "ikon":  "🚶",
                "judul": "Tingkatkan Aktivitas Fisik",
                "teks":  "Anda melaporkan aktivitas fisik yang rendah. Aktivitas fisik teratur membantu "
                         "sel tubuh menggunakan insulin lebih efektif. Targetkan minimal 30 menit "
                         "aktivitas sedang setiap hari."
            })
    elif activity == 'AKTIF':
        saran.append({
            "ikon":  "💪",
            "judul": "Gaya Hidup Aktif — Pertahankan!",
            "teks":  "Aktivitas fisik rutin Anda sangat membantu menjaga sensitivitas insulin "
                     "dan metabolisme glukosa. Terus pertahankan rutinitas olahraga Anda."
        })

    # Pola Makan (Langkah 8 — diet)
    if diet_val == 0:
        if glucose >= 140 or hba1c >= 5.7:
            saran.append({
                "ikon":  "🥗",
                "judul": "Pola Makan Buruk + Gula Darah Tinggi",
                "teks":  "Anda tidak rutin mengonsumsi sayur dan buah, sementara indikator gula darah Anda "
                         "menunjukkan angka di atas normal. Perbanyak konsumsi serat dari sayuran hijau, "
                         "buah-buahan rendah glikemik (apel, pir, beri), dan biji-bijian utuh. "
                         "Kurangi nasi putih, roti putih, dan makanan olahan."
            })
        else:
            saran.append({
                "ikon":  "🥦",
                "judul": "Perbaiki Pola Makan",
                "teks":  "Kurangnya asupan sayur dan buah dapat meningkatkan risiko diabetes jangka panjang. "
                         "Usahakan mengonsumsi minimal 5 porsi sayur dan buah setiap hari "
                         "untuk menjaga kadar gula darah tetap stabil."
            })

    # Alkohol (Langkah 8 — alcohol)
    if alcohol == 'often':
        saran.append({
            "ikon":  "🍷",
            "judul": "Konsumsi Alkohol Berlebih",
            "teks":  "Konsumsi alkohol yang sering (>1x per minggu) dapat mengganggu regulasi gula darah, "
                     "meningkatkan trigliserida, dan memperburuk fungsi hati. "
                     "Batasi konsumsi alkohol atau hentikan sama sekali untuk perlindungan metabolik optimal."
        })
    elif alcohol == 'rare':
        saran.append({
            "ikon":  "🟡",
            "judul": "Konsumsi Alkohol Sesekali",
            "teks":  "Konsumsi alkohol sesekali masih tergolong aman, namun tetap perlu dibatasi. "
                     "Hindari minum alkohol saat perut kosong karena bisa menyebabkan hipoglikemia."
        })

    # Stres & Tidur (Langkah 9) — LOGIKA MEDIS KONTEKSTUAL
    is_stressed = stress_val == 1
    is_sleep_short = sleep == 'short'
    is_sleep_long = sleep == 'long'

    # Kombinasi kritis: Stres + Kurang Tidur + Risiko Tinggi/Sangat Tinggi
    if is_stressed and is_sleep_short and label in ('Risiko Menengah', 'Risiko Tinggi', 'Risiko Sangat Tinggi (Kritis)'):
        saran.append({
            "ikon":  "🧠",
            "judul": "Stres Kronis + Kurang Tidur — Risiko Tinggi",
            "teks":  "Kombinasi stres kronis dan kurang tidur (<6 jam) sangat berbahaya bagi metabolisme Anda. "
                     "Stres memicu pelepasan hormon kortisol berlebih yang menyebabkan lonjakan gula darah "
                     "dan resistensi insulin. Kurang tidur memperburuk efek ini. "
                     "Rekomendasi: (1) Terapkan teknik relaksasi sebelum tidur (meditasi, napas dalam), "
                     "(2) Hindari kafein setelah jam 2 siang, "
                     "(3) Targetkan tidur 7-8 jam per malam, "
                     "(4) Konsultasikan ke dokter jika stres berlangsung lebih dari 2 minggu."
        })
    else:
        # Stres saja
        if is_stressed:
            saran.append({
                "ikon":  "😰",
                "judul": "Manajemen Stres Diperlukan",
                "teks":  "Stres kronis meningkatkan kadar kortisol yang berdampak langsung pada resistensi insulin "
                         "dan lonjakan gula darah. Cobalah teknik relaksasi seperti meditasi mindfulness, "
                         "yoga, atau pernapasan dalam secara rutin. "
                         "Jika perlu, pertimbangkan konseling profesional."
            })

        if is_sleep_short:
            if label in ('Risiko Tinggi', 'Risiko Sangat Tinggi (Kritis)'):
                saran.append({
                    "ikon":  "😴",
                    "judul": "Durasi Tidur Kurang + Risiko Tinggi",
                    "teks":  "Tidur kurang dari 6 jam secara konsisten terbukti menurunkan sensitivitas insulin "
                             "hingga 25%. Pada kondisi berisiko tinggi, ini sangat kritis. "
                             "Prioritaskan jadwal tidur yang konsisten dan usahakan tidur 7-8 jam per malam."
                })
            else:
                saran.append({
                    "ikon":  "🌙",
                    "judul": "Perbaiki Kualitas Tidur",
                    "teks":  "Tidur kurang dari 6 jam per malam dapat mengganggu metabolisme glukosa "
                             "dan meningkatkan nafsu makan akan makanan tinggi kalori. "
                             "Usahakan tidur 7-8 jam dan ciptakan rutinitas tidur yang teratur."
                })

        # Tidur berlebih
        if is_sleep_long:
            saran.append({
                "ikon":  "🛌",
                "judul": "Durasi Tidur Berlebih",
                "teks":  "Tidur lebih dari 8 jam secara rutin juga dikaitkan dengan peningkatan risiko "
                         "diabetes tipe 2 dan sindrom metabolik. Usahakan durasi tidur optimal 7-8 jam "
                         "dan jaga jadwal bangun yang konsisten."
            })

    # ─── RINGKASAN AKHIR ───
 
    if prediksi == 1:
        saran.append({
            "ikon":  "📋",
            "judul": "Langkah Selanjutnya",
            "teks":  "Berdasarkan kombinasi faktor risiko di atas, disarankan segera berkonsultasi "
                     "dengan dokter untuk pemeriksaan HbA1c dan gula darah puasa secara klinis. "
                     "Hasil ini bersifat prediktif dan bukan diagnosis medis resmi."
        })
    else:
        saran.append({
            "ikon":  "✅",
            "judul": "Tetap Jaga Kesehatan",
            "teks":  "Risiko saat ini tergolong rendah. Pertahankan gaya hidup aktif, "
                     "pola makan seimbang, dan lakukan pemeriksaan rutin setidaknya 1x per tahun."
        })
 
    return saran

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/edukasi')
def edukasi():
    return render_template('edukasi.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json

    GENDER_MAP  = {'Female': 0, 'Male': 1}
    SMOKING_MAP = {'never': 0, 'No Info': 1, 'not current': 2, 'ever': 3, 'former': 4, 'current': 5}
    gender  = GENDER_MAP.get(data['gender'], 0)
    smoking = SMOKING_MAP.get(data['smoking_history'], 1)

    fitur_raw = np.array([[
        gender,
        float(data['age']),
        int(data['hypertension']),
        int(data['heart_disease']),
        smoking,
        float(data['bmi']),
        float(data['HbA1c_level']),
        float(data['blood_glucose_level'])
    ]])

    fitur_scaled = fitur_raw.copy()
    fitur_scaled[:, [1, 5, 6, 7]] = scaler.transform(fitur_raw[:, [1, 5, 6, 7]])
    proba = model.predict_proba(fitur_scaled)[0]
    confidence = proba[1] * 100
    
    if confidence <= 20.0:
        label = "Risiko Sangat Rendah"
        prediksi = 0
    elif confidence <= 40.0:
        label = "Risiko Rendah"
        prediksi = 0
    elif confidence <= 60.0:
        label = "Risiko Menengah"
        prediksi = 1
    elif confidence <= 80.0:
        label = "Risiko Tinggi"
        prediksi = 1
    else:
        label = "Risiko Sangat Tinggi (Kritis)"
        prediksi = 1

    # Menyimpan riwayat prediksi ke file JSON
    record = {
        'waktu'     : datetime.datetime.now().strftime('%d/%m/%Y %H:%M'),
        'hasil'     : label,
        'confidence': f"{confidence:.1f}%",
        'input'     : data
    }
    with open(os.path.join(BASE_DIR, 'riwayat.json'), 'a') as f:
        f.write(json.dumps(record) + '\n')
    fitur_names  = ['Gender','Usia','Hipertensi','P. Jantung',
                 'Merokok','BMI','HbA1c','Gula Darah']
    importances  = model.feature_importances_.tolist()
    
    saran_kesehatan = generate_saran(data, prediksi, label)

    return jsonify({
        'label'     : label,
        'confidence': f"{confidence:.1f}%",
        'risiko'    : int(prediksi),
        'importances' : dict(zip(fitur_names, importances)),
        'saran'     : saran_kesehatan
    })

if __name__ == '__main__':
    app.run(debug=True)