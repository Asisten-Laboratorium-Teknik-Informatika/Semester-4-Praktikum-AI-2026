import pandas as pd
from sklearn.neighbors import NearestNeighbors
import warnings

# Mengabaikan peringatan kecil dari library
warnings.filterwarnings("ignore")

# 1. FUNGSI PENGHITUNG KEBUTUHAN ENERGI (TDEE)
def hitung_tdee(berat, tinggi, umur, gender, aktivitas):
    """
    Menghitung Total Daily Energy Expenditure (TDEE) menggunakan rumus Harris-Benedict.
    Aktivitas multiplier: 1.2 (Sangat jarang), 1.375 (Jarang), 1.55 (Sedang), 1.725 (Sering).
    """
    if gender.lower() == 'pria':
        bmr = 88.362 + (13.397 * berat) + (4.799 * tinggi) - (5.677 * umur)
    else:
        bmr = 447.593 + (9.247 * berat) + (3.098 * tinggi) - (4.330 * umur)
    
    tdee = bmr * aktivitas
    return tdee

# 2. FUNGSI FILTER ALERGI
def filter_alergi(df, list_alergi):
    """
    Membuang baris data yang mengandung kata-kata alergi pada kolom ingredients.
    """
    if not list_alergi:
        return df # Jika tidak ada alergi, kembalikan semua data
    
    df_aman = df.copy()
    for alergi in list_alergi:
        # Hapus resep yang ingredients-nya mengandung kata alergi (case-insensitive)
        df_aman = df_aman[~df_aman['ingredients'].str.contains(alergi, case=False, na=False)]
    
    return df_aman

# 3. FUNGSI REKOMENDASI MACHINE LEARNING (KNN)
def rekomendasi_menu(df, target_kalori, n_rekomendasi=3):
    """
    Mencari n menu yang nilai kalorinya paling mendekati target_kalori menggunakan KNN.
    """
    # Siapkan model KNN (mencari tetangga terdekat)
    knn = NearestNeighbors(n_neighbors=n_rekomendasi, algorithm='auto')
    
    # Ambil kolom kalori saja sebagai fitur pembelajaran
    X = df[['calories']].values
    knn.fit(X)
    
    # Prediksi/Cari menu dengan kalori paling mendekati target
    distances, indices = knn.kneighbors([[target_kalori]])
    
    # Ambil hasil resep berdasarkan index yang ditemukan
    hasil_rekomendasi = df.iloc[indices[0]]
    return hasil_rekomendasi


# === BLOK TESTING (Hanya jalan jika file ini dieksekusi langsung) ===
if __name__ == "__main__":
    print("⏳ Memuat data bersih (cleaned_recipes.csv)...")
    df_bersih = pd.read_csv('data/cleaned_recipes.csv')
    
    # Simulasi Input User (Misal: Pria, 70kg, 170cm, 20 tahun, jarang olahraga)
    tdee = hitung_tdee(berat=70, tinggi=170, umur=20, gender='pria', aktivitas=1.2)
    kalori_per_makan = tdee / 3 # Kita bagi 3 (Pagi, Siang, Malam)
    
    print("\n" + "="*40)
    print(f"🎯 Target Kalori Harian: {tdee:.0f} kkal")
    print(f"🍽️ Target Kalori per Waktu Makan: {kalori_per_makan:.0f} kkal")
    print("="*40)
    
    # Simulasi Alergi (User alergi 'peanut' / kacang)
    print("\n🛡️ Menyaring menu yang mengandung 'peanut'...")
    df_aman = filter_alergi(df_bersih, ['peanut'])
    print(f"Sisa menu yang aman: {len(df_aman)} dari {len(df_bersih)} resep.")
    
    # Mencari Rekomendasi Menggunakan AI
    print("\n🤖 AI sedang mencari rekomendasi menu terbaik...")
    rekomendasi = rekomendasi_menu(df_aman, target_kalori=kalori_per_makan, n_rekomendasi=3)
    
    print("\n✅ HASIL REKOMENDASI:")
    print(rekomendasi[['name', 'calories']])