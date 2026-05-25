"""
Konversi dataset percakapan sintetis JSON ke CSV untuk training model.
Jalankan: python scripts/synthetic_to_csv.py
"""

import json
from pathlib import Path

import pandas as pd


INPUT = Path("Data/synthetic/synthetic_conversations_1000.json")
OUTPUT = Path("Data/synthetic/synthetic_features.csv")


def main() -> None:
    if not INPUT.exists():
        print(f"File {INPUT} tidak ditemukan.")
        print("Jalankan merge_synthetic_batches.py terlebih dahulu.")
        return

    with open(INPUT, "r", encoding="utf-8") as f:
        conversations = json.load(f)

    rows: list[dict] = []
    for conv in conversations:
        features = conv.get("features", {})
        row = {
            "id": conv.get("id"),
            "burnout_level": conv.get("burnout_level"),
            "profession": conv.get("profession"),
            "age": conv.get("age"),
            "language_style": conv.get("language_style"),
            "context": conv.get("context"),
            "user_texts": conv.get("user_texts_combined", ""),
            **features,
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    # Encode burnout_level ke numerik
    label_map = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    df["burnout_label"] = df["burnout_level"].map(label_map)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False, encoding="utf-8")

    print(f"Saved {len(df)} rows to {OUTPUT}")
    print(f"\nDistribution:")
    print(df["burnout_level"].value_counts())
    print(f"\nFeature columns: {list(df.columns)}")


if __name__ == "__main__":
    main()
