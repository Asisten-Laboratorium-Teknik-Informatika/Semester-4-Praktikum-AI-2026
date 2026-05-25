import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

import matplotlib.pyplot as plt
import seaborn as sns

X_train = pd.read_csv("Data/processed/X_train.csv")

X_test = pd.read_csv("Data/processed/X_test.csv")

y_train = pd.read_csv("Data/processed/y_train.csv")

y_test = pd.read_csv("Data/processed/y_test.csv")


print("Dataset berhasil dibaca")

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train.values.ravel())

print("Training model selesai")

y_pred = model.predict(X_test)

print("Prediksi berhasil")

akurasi = accuracy_score(y_test, y_pred)

print("\n===== AKURASI MODEL =====")

print("Accuracy:", akurasi)

print("\n===== CLASSIFICATION REPORT =====")

print(classification_report(y_test, y_pred))


cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(6,5))

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues"
)

plt.title("Confusion Matrix")

plt.xlabel("Prediksi")

plt.ylabel("Actual")

plt.savefig("output/confusion_matrix.png")

plt.show()


feature_names = X_train.columns

importance = model.feature_importances_

feature_importance = pd.DataFrame({
    "Feature": feature_names,
    "Importance": importance
})

feature_importance = feature_importance.sort_values(
    by="Importance",
    ascending=False
)

print("\n===== FEATURE IMPORTANCE =====")

print(feature_importance)

plt.figure(figsize=(8,5))

sns.barplot(
    x="Importance",
    y="Feature",
    data=feature_importance
)

plt.title("Feature Importance Random Forest")

plt.savefig("output/feature_importance.png")

plt.show()

joblib.dump(
    model,
    "Data/processed/random_forest_model.pkl"
)

print("\nModel berhasil disimpan")