"""
Merge semua batch percakapan sintetis menjadi satu file JSON.
Jalankan: python scripts/merge_synthetic_batches.py
"""

import json
from pathlib import Path


DATA_DIR = Path("Data/synthetic/batches")
OUTPUT = Path("Data/synthetic/synthetic_conversations_1000.json")


def main() -> None:
    all_conversations: list[dict] = []

    batch_files = sorted(DATA_DIR.glob("batch_*.json"))
    if not batch_files:
        print(f"Tidak ada file batch ditemukan di {DATA_DIR}")
        print("Pastikan file bernama batch_01.json, batch_02.json, dst.")
        return

    for batch_file in batch_files:
        with open(batch_file, "r", encoding="utf-8") as f:
            batch = json.loads(f.read())
            if isinstance(batch, list):
                all_conversations.extend(batch)
            else:
                all_conversations.append(batch)
        print(f"Loaded {batch_file.name}: {len(batch) if isinstance(batch, list) else 1} conversations")

    # Deduplicate by id
    seen_ids: set[str] = set()
    unique: list[dict] = []
    for conv in all_conversations:
        cid = conv.get("id", "")
        if cid not in seen_ids:
            seen_ids.add(cid)
            unique.append(conv)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

    # Stats
    levels: dict[str, int] = {}
    for conv in unique:
        lvl = conv.get("burnout_level", "UNKNOWN")
        levels[lvl] = levels.get(lvl, 0) + 1

    print(f"\nTotal conversations: {len(unique)}")
    print(f"Distribution: {levels}")
    print(f"Saved to: {OUTPUT}")


if __name__ == "__main__":
    main()
