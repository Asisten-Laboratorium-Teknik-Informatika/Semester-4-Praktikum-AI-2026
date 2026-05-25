import pandas as pd
import numpy as np

df = pd.read_csv("Data/Employee Burnout Dataset/train.csv")

print("Dataset berhasil dibaca")

df = df.dropna(subset=["Burn Rate"])

kolom_numerik = df.select_dtypes(include=np.number).columns

for kolom in kolom_numerik:

    df[kolom] = df[kolom].fillna(df[kolom].median())

df["sleep_workload_ratio"] = (
    10 - df["Mental Fatigue Score"]
) / (
    df["Resource Allocation"] + 1
)

print("\nFeature sleep_workload_ratio berhasil dibuat")

df["recovery_deficit"] = (
    df["Mental Fatigue Score"]
    - (10 - df["Resource Allocation"])
)

print("Feature recovery_deficit berhasil dibuat")

df["fatigue_per_workload"] = (
    df["Mental Fatigue Score"]
    / (df["Resource Allocation"] + 1)
)

print("Feature fatigue_per_workload berhasil dibuat")

print("\n===== FEATURE BARU =====")

print(df[
    [
        "Mental Fatigue Score",
        "Resource Allocation",
        "sleep_workload_ratio",
        "recovery_deficit",
        "fatigue_per_workload"
    ]
].head())

fitur_baru = [
    "sleep_workload_ratio",
    "recovery_deficit",
    "fatigue_per_workload",
    "Burn Rate"
]

print("\n===== KORELASI FEATURE BARU =====")

print(df[fitur_baru].corr())

df.to_csv(
    "Data/processed/feature_engineered.csv",
    index=False
)

print("\nDataset feature engineering berhasil disimpan")