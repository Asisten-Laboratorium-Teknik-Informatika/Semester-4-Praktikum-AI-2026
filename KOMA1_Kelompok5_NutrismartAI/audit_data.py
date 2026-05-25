import pandas as pd

# 1. Memuat Dataset
print("Memuat dataset, mohon tunggu sebentar...\n")
try:
    # Kita ambil 1000 baris pertama dulu agar sangat cepat
    df = pd.read_csv('data/RAW_recipes.csv', nrows=1000)
    print("✅ Berhasil memuat 1000 sampel data!\n")
except FileNotFoundError:
    print("❌ Error: File RAW_recipes.csv tidak ditemukan di folder data/")
    exit()

# 2. Cek Informasi Dasar (Tipe data kolom)
print("--- 📊 Informasi Dataset ---")
print(df.info())

# 3. Cek Data Kosong (Missing Values)
print("\n--- ⚠️ Cek Data Kosong (NaN) ---")
print(df.isnull().sum())

# 4. Intip Data (Fokus ke kolom penting kita)
print("\n--- 🔍 Intip Sampel Data (5 Baris Pertama) ---")
print(df[['name', 'nutrition', 'ingredients']].head())

print("\nAudit selesai! Silakan copy hasilnya.")