# =========================================================
# GENERATE SYNTHETIC BURNOUT DATASET
# =========================================================

import pandas as pd
import random


# =========================================================
# TEMPLATE DATA
# =========================================================

profesi_list = [
    "Software Developer",
    "Mahasiswa",
    "Guru",
    "Dokter Muda",
    "Desainer",
    "Marketing",
    "Akuntan",
    "Freelancer"
]

low_text = [
    "Saya masih cukup semangat bekerja.",
    "Pekerjaan masih bisa saya atur dengan baik.",
    "Saya masih punya waktu istirahat yang cukup."
]

medium_text = [
    "Belakangan saya mulai merasa lelah.",
    "Tugas semakin banyak dan cukup melelahkan.",
    "Tidur saya mulai berkurang karena pekerjaan."
]

high_text = [
    "Saya merasa sangat burnout akhir-akhir ini.",
    "Saya kelelahan setiap hari dan sulit fokus.",
    "Pekerjaan terasa sangat berat dan membuat stres."
]


# =========================================================
# GENERATE DATA
# =========================================================

data = []

for level in ["LOW", "MEDIUM", "HIGH"]:

    for profesi in profesi_list:

        for i in range(5):

            if level == "LOW":

                text = random.choice(low_text)

                workload = random.randint(2, 4)

                sleep = random.randint(7, 9)

            elif level == "MEDIUM":

                text = random.choice(medium_text)

                workload = random.randint(5, 7)

                sleep = random.randint(5, 7)

            else:

                text = random.choice(high_text)

                workload = random.randint(8, 10)

                sleep = random.randint(3, 5)

            data.append({
                "profesi": profesi,
                "burnout_level": level,
                "workload": workload,
                "sleep_hours": sleep,
                "text": text
            })


# =========================================================
# BUAT DATAFRAME
# =========================================================

df = pd.DataFrame(data)

print(df.head())

print("\nJumlah data:", len(df))


# =========================================================
# SIMPAN CSV
# =========================================================

df.to_csv(
    "Data/synthetic/synthetic_burnout.csv",
    index=False
)

print("\n✅ Synthetic dataset berhasil disimpan")