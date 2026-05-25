"""
Feature Store — Menyimpan dan mengelola fitur harian per user.

Penyimpanan: per-hari (bukan per-pesan). Jika user kirim 5 pesan hari ini,
semua data diakumulasi ke satu entry hari itu (running average).
Rolling window: 7 hari terakhir.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date
from statistics import mean
from typing import Any

import numpy as np


FeatureEntry = dict[str, float]

# {user_id: {date_str: {"values": {key: [values]}, "count": int}}}
_FEATURE_STORE: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)


def update_daily_features(user_id: str, features: FeatureEntry) -> dict[str, Any]:
    """
    Update fitur untuk user hari ini.
    Jika sudah ada entry hari ini, rata-ratakan dengan data sebelumnya.
    """
    today = date.today().isoformat()
    user_store = _FEATURE_STORE[user_id]

    if today not in user_store:
        user_store[today] = {"values": {}, "count": 0}

    entry = user_store[today]
    entry["count"] += 1

    for key, val in features.items():
        if val is None:
            continue
        try:
            fval = float(val)
        except (TypeError, ValueError):
            continue

        if key not in entry["values"]:
            entry["values"][key] = []
        entry["values"][key].append(fval)

    # Prune: simpan hanya 7 hari terakhir
    dates_sorted = sorted(user_store.keys(), reverse=True)
    for old_date in dates_sorted[7:]:
        del user_store[old_date]

    return get_7day_features(user_id)


def get_7day_features(user_id: str) -> dict[str, Any]:
    """
    Ambil ringkasan fitur 7 hari terakhir.
    Return: days, averages per fitur, dan sentiment_slope_7d.
    """
    user_store = _FEATURE_STORE.get(user_id, {})
    if not user_store:
        return {"days": 0, "averages": {}, "sentiment_slope_7d": 0.0}

    dates_sorted = sorted(user_store.keys())

    # Hitung rata-rata per hari dulu, lalu rata-rata antar hari
    daily_averages: list[dict[str, float]] = []
    all_keys: set[str] = set()

    for d in dates_sorted:
        entry = user_store[d]
        day_avg = {}
        for key, values in entry["values"].items():
            if values:
                day_avg[key] = mean(values)
                all_keys.add(key)
        daily_averages.append(day_avg)

    # Global averages (rata-rata dari rata-rata harian)
    global_averages = {}
    for key in sorted(all_keys):
        vals = [da[key] for da in daily_averages if key in da]
        if vals:
            global_averages[key] = mean(vals)

    # Sentiment slope: tren sentiment dari hari pertama ke terakhir
    sentiment_daily = []
    for da in daily_averages:
        if "sentiment_score" in da:
            sentiment_daily.append(da["sentiment_score"])

    sentiment_slope = 0.0
    if len(sentiment_daily) >= 2:
        # Linear regression slope
        x = np.arange(len(sentiment_daily))
        try:
            slope, _ = np.polyfit(x, sentiment_daily, 1)
            sentiment_slope = float(slope)
        except (np.linalg.LinAlgError, ValueError):
            sentiment_slope = sentiment_daily[-1] - sentiment_daily[0]

    return {
        "days": len(dates_sorted),
        "averages": global_averages,
        "sentiment_slope_7d": sentiment_slope,
        "daily_data": [
            {"date": d, **{k: v for k, v in daily_averages[i].items()}}
            for i, d in enumerate(dates_sorted)
        ],
    }


def get_collected_fields(user_id: str) -> dict[str, bool]:
    """
    Return field mana yang sudah dikumpulkan dari user.
    Dipakai oleh gemini.py untuk collected_status di system prompt.
    """
    user_store = _FEATURE_STORE.get(user_id, {})
    tracked_fields = [
        "sleep_hours", "sleep_quality", "workload_score",
        "mood_score", "social_score", "recovery_score",
    ]

    collected = {}
    all_keys: set[str] = set()
    for entry in user_store.values():
        all_keys.update(entry.get("values", {}).keys())

    for field in tracked_fields:
        collected[field] = field in all_keys

    return collected
