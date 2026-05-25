import pandas as pd
import ast

# 1. Load data lengkap
df = pd.read_csv('data/RAW_recipes.csv')

# 2. Parsing Kolom Nutrition
# Kolom nutrition adalah string list, kita ubah jadi list beneran lalu jadi kolom
def parse_nutrition(x):
    # Mengubah string "[51.5, 0.0, ...]" jadi list [51.5, 0.0, ...]
    return pd.Series(ast.literal_eval(x))

print("Sedang memproses kolom nutrition...")
nutrition_df = df['nutrition'].apply(parse_nutrition)
nutrition_df.columns = ['calories', 'total_fat', 'sugar', 'sodium', 'protein', 'saturated_fat', 'carbohydrates']

# Gabungkan kolom baru ke dataframe utama
df = pd.concat([df, nutrition_df], axis=1)

# 3. Bersihkan kolom ingredients agar lebih rapi
df['ingredients'] = df['ingredients'].apply(lambda x: ', '.join(ast.literal_eval(x)))

# 4. Simpan ke file baru (agar aplikasi nanti cepat)
df.to_csv('data/cleaned_recipes.csv', index=False)
print("✅ Selesai! Data bersih telah disimpan di data/cleaned_recipes.csv")