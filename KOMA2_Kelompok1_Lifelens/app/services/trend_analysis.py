import numpy as np
import pandas as pd
from typing import List, Dict

def predict_next_week_trend(daily_features: List[Dict]) -> Dict:
    """
    Prediksi kondisi minggu depan berdasarkan tren saat ini.
    Linear extrapolation sederhana — tidak butuh ML.
    """
    if len(daily_features) < 5:
        return {'prediction': 'insufficient_data', 'confidence': 'low'}
    
    df = pd.DataFrame(daily_features)
    if 'date' in df.columns:
        df = df.sort_values('date')
    
    # Hitung slope untuk metrik utama
    x = np.arange(len(df))
    
    slopes = {}
    for metric in ['mood_score', 'sleep_hours', 'workload_score', 'sentiment_score']:
        if metric in df.columns and df[metric].notna().sum() >= 3:
            values = df[metric].dropna().values
            if len(values) >= 2:
                slope, _ = np.polyfit(range(len(values)), values, 1)
                slopes[metric] = slope
    
    # Tentukan arah tren
    mood_slope = slopes.get('mood_score', 0)
    sleep_slope = slopes.get('sleep_hours', 0)
    workload_slope = slopes.get('workload_score', 0)
    
    # Prediksi sederhana
    if mood_slope < -0.3 and workload_slope > 0.2:
        trend = 'worsening'
        message = "Pola beberapa hari ini menunjukkan tren yang perlu perhatian."
    elif mood_slope > 0.2 and sleep_slope > 0:
        trend = 'improving'
        message = "Ada perbaikan yang terlihat dari pola beberapa hari ini."
    else:
        trend = 'stable'
        message = "Kondisi terlihat relatif stabil dalam beberapa hari terakhir."
    
    return {
        'trend': trend,
        'message': message,
        'slopes': slopes,
        'confidence': 'medium' if len(daily_features) >= 7 else 'low'
    }


def generate_recommendations(risk_level: str, top_factors: List[str]) -> List[Dict]:
    """
    Rekomendasi berbasis rule-based + data.
    Disesuaikan dengan faktor yang paling berkontribusi.
    """
    
    RECOMMENDATIONS = {
        'sleep': {
            'title': 'Prioritaskan Tidur',
            'tips': [
                'Coba tidur dan bangun di jam yang sama setiap hari',
                'Hindari layar (HP/laptop) 30 menit sebelum tidur',
                'Buat ritual sebelum tidur yang menenangkan'
            ]
        },
        'workload': {
            'title': 'Kelola Beban Kerja',
            'tips': [
                'Identifikasi 3 prioritas utama hari ini — fokus pada itu dulu',
                'Coba teknik Pomodoro: kerja 25 menit, istirahat 5 menit',
                'Komunikasikan kapasitasmu dengan atasan jika perlu'
            ]
        },
        'social': {
            'title': 'Jaga Koneksi Sosial',
            'tips': [
                'Hubungi satu teman atau keluarga hari ini, bahkan hanya 5 menit',
                'Pertimbangkan bergabung dengan komunitas dengan minat yang sama',
                'Bicara jujur dengan seseorang yang kamu percaya'
            ]
        },
        'recovery': {
            'title': 'Optimalkan Pemulihan',
            'tips': [
                'Jadwalkan waktu untuk aktivitas yang benar-benar kamu nikmati',
                'Coba aktivitas fisik ringan seperti jalan kaki 15–20 menit',
                'Bedakan antara "istirahat" dan "rebahan sambil scroll HP"'
            ]
        }
    }
    
    # Map faktor ke kategori rekomendasi
    # Keys harus match partial lowercase dari output explain_prediction():
    #   "Tidur hanya 4.0 jam", "Beban kerja 9/10", "Mood rendah",
    #   "Pemulihan rendah", "Sentimen percakapan negatif",
    #   "Interaksi sosial rendah", "Pola bahasa absolutist"
    FACTOR_CATEGORY_MAP = {
        'tidur': 'sleep',
        'beban kerja': 'workload',
        'workload': 'workload',
        'interaksi sosial': 'social',
        'sosial': 'social',
        'mood': 'recovery',
        'pemulihan': 'recovery',
        'recovery': 'recovery',
        'sentimen': 'sleep',        # negatif sentiment → self-care
        'absolutist': 'workload',   # distorsi → mindfulness
        'distorsi': 'workload',
    }
    
    recommendations = []
    used_categories = set()
    
    for factor in top_factors:
        for keyword, category in FACTOR_CATEGORY_MAP.items():
            if keyword.lower() in factor.lower() and category not in used_categories:
                rec = RECOMMENDATIONS[category]
                recommendations.append({
                    'category': category,
                    'title': rec['title'],
                    'tip': rec['tips'][0],  # Ambil tip pertama
                    'related_factor': factor
                })
                used_categories.add(category)
                break
    
    # Selalu tambahkan satu rekomendasi umum
    if risk_level == 'HIGH' and len(recommendations) < 3:
        recommendations.append({
            'category': 'professional',
            'title': 'Pertimbangkan Bantuan Profesional',
            'tip': 'Berbicara dengan konselor atau psikolog adalah langkah yang berani, bukan tanda kelemahan.',
            'related_factor': 'Risk level tinggi'
        })
    
    return recommendations[:3]  # Maksimal 3 rekomendasi
