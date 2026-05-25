import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE

df = pd.read_csv("Data/Employee Burnout Dataset/train.csv")

print("\n===== Missing Value Sebelum =====")
print(df.isnull().sum())

df = df.dropna(subset=["Burn Rate"])


kolom_numerik = df.select_dtypes(include=np.number).columns

for kolom in kolom_numerik:

    df[kolom] = df[kolom].fillna(df[kolom].median())

kolom_kategorikal = df.select_dtypes(include="object").columns

for kolom in kolom_kategorikal:

    df[kolom] = df[kolom].fillna(df[kolom].mode()[0])


print("\n===== Missing Value Sesudah =====")
print(df.isnull().sum())


df["Gender"] = df["Gender"].map({
    "Male": 0,
    "Female": 1
})

df["Company Type"] = df["Company Type"].map({
    "Service": 0,
    "Product": 1
})

df["WFH Setup Available"] = df["WFH Setup Available"].map({
    "No": 0,
    "Yes": 1
})


df = df.drop(columns=["Employee ID", "Date of Joining"])


def burnout_label(nilai):

    if nilai <= 0.33:
        return 0

    elif nilai <= 0.66:
        return 1

    else:
        return 2


df["Burnout Label"] = df["Burn Rate"].apply(burnout_label)

X = df.drop(columns=["Burn Rate", "Burnout Label"])

y = df["Burnout Label"]


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTrain test split berhasil")


scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)

X_test = scaler.transform(X_test)

print("Scaling berhasil")


smote = SMOTE(random_state=42)

X_train, y_train = smote.fit_resample(
    X_train,
    y_train
)

print("SMOTE berhasil")



print("\n===== DATA AKHIR =====")

print("X_train:", X_train.shape)

print("X_test :", X_test.shape)

print("y_train:", y_train.shape)

print("y_test :", y_test.shape)



pd.DataFrame(X_train).to_csv(
    "Data/processed/X_train.csv",
    index=False
)

pd.DataFrame(X_test).to_csv(
    "Data/processed/X_test.csv",
    index=False
)

pd.DataFrame(y_train).to_csv(
    "Data/processed/y_train.csv",
    index=False
)

pd.DataFrame(y_test).to_csv(
    "Data/processed/y_test.csv",
    index=False
)

print("\nDataset preprocessing berhasil disimpan")