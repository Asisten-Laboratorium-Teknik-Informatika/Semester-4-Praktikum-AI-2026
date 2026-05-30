from flask import Flask, request, jsonify, render_template
import numpy as np
import cv2
import os
from tensorflow.keras.models import load_model

app = Flask(__name__)

MODEL_PATH = "model/tinthint_model.h5"
model = load_model(MODEL_PATH)

CLASS_LABELS = ["cool", "neutral", "warm"]

UNDERTONE_INFO = {
    "warm": {
        "emoji": "🌸",
        "description": "Undertone Warm — Kulit kamu punya kesan hangat keemasan atau kecokelatan.",
        "colors": ["Coral", "Peach", "Terracotta", "Olive Green", "Warm Brown"],
        "avoid": ["Cool Gray", "Icy Blue", "Pure White"],
        "makeup": "Foundation dengan undertone yellow/golden, blush warna peach atau coral.",
        "hex": ["#E8956D", "#D4845A", "#C17A4A", "#8B6914", "#6B4423"]
    },
    "cool": {
        "emoji": "❄️",
        "description": "Undertone Cool — Kulit kamu punya kesan sejuk kemerahan atau keunguan.",
        "colors": ["Rose Pink", "Lavender", "Icy Blue", "Burgundy", "Cool Gray"],
        "avoid": ["Orange", "Warm Yellow", "Camel"],
        "makeup": "Foundation dengan undertone pink/rosy, blush warna rose atau berry.",
        "hex": ["#D4A0C0", "#B07BA0", "#8B5A82", "#6B3A6B", "#4A2050"]
    },
    "neutral": {
        "emoji": "✨",
        "description": "Undertone Neutral — Kamu beruntung! Kulit kamu cocok dengan hampir semua warna.",
        "colors": ["Dusty Rose", "Sage Green", "Mauve", "Warm Taupe", "Navy"],
        "avoid": ["Sangat ekstrem warm atau cool"],
        "makeup": "Foundation dengan undertone neutral, bisa eksplor berbagai warna blush.",
        "hex": ["#C4A882", "#A89070", "#8B7355", "#6B5840", "#4A3828"]
    }
}

def preprocess_image(img_bytes):
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (224, 224))
    img = img.astype("float32") / 255.0
    img = np.expand_dims(img, axis=0)
    return img

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "Tidak ada gambar"}), 400

    file = request.files["image"]
    img_bytes = file.read()

    try:
        img = preprocess_image(img_bytes)
        preds = model.predict(img)[0]
        pred_idx = int(np.argmax(preds))
        label = CLASS_LABELS[pred_idx]
        confidence = float(np.max(preds)) * 100

        info = UNDERTONE_INFO[label]

        return jsonify({
            "undertone": label,
            "confidence": round(confidence, 2),
            "emoji": info["emoji"],
            "description": info["description"],
            "colors": info["colors"],
            "avoid": info["avoid"],
            "makeup": info["makeup"],
            "hex": info["hex"],
            "probabilities": {
                "cool": round(float(preds[0]) * 100, 2),
                "neutral": round(float(preds[1]) * 100, 2),
                "warm": round(float(preds[2]) * 100, 2),
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)