from flask import Flask, request, jsonify, render_template
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import re
import string
import numpy as np

app = Flask(__name__)

print("Memuat model AI, harap tunggu...")
model = tf.keras.models.load_model('best_model.h5')
with open('tokenizer_bilstm.pkl', 'rb') as f:
    tokenizer = pickle.load(f)

max_length = 300

def advanced_text_cleaner(text):
    text = str(text).lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'^.*?\(reuters\)\s*-\s*', '', text)
    text = re.sub(r'^.*?reuters\s*-\s*', '', text)
    text = re.sub(f"[{re.escape(string.punctuation)}]", ' ', text)
    text = re.sub(r'\w*\d\w*', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        if not data or 'text' not in data:
            return jsonify({'error': 'Data tidak valid. Field "text" diperlukan.'}), 400

        teks_berita = data['text']

        if not teks_berita or not teks_berita.strip():
            return jsonify({'error': 'Teks berita tidak boleh kosong.'}), 400

        if len(teks_berita.strip()) < 20:
            return jsonify({'error': 'Teks berita terlalu pendek. Minimal 20 karakter.'}), 400

        teks_bersih = advanced_text_cleaner(teks_berita)

        if not teks_bersih.strip():
            return jsonify({'error': 'Teks tidak dapat diproses setelah pembersihan.'}), 400

        sekuens = tokenizer.texts_to_sequences([teks_bersih])
        pad_sekuens = pad_sequences(sekuens, maxlen=max_length, padding='post', truncating='post')

        probabilitas = float(model.predict(pad_sekuens, verbose=0)[0][0])

        if probabilitas > 0.5:
            status = "HOAX"
            keyakinan = round(probabilitas * 100, 2)
        else:
            status = "FAKTA"
            keyakinan = round((1 - probabilitas) * 100, 2)

        word_count = len(teks_berita.split())

        return jsonify({
            'status': status,
            'confidence': keyakinan,
            'probability': round(probabilitas * 100, 2),
            'word_count': word_count
        })

    except KeyError:
        return jsonify({'error': 'Format request tidak valid.'}), 400
    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan server: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint tidak ditemukan.'}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'error': 'Method tidak diizinkan.'}), 405

if __name__ == '__main__':
    app.run(debug=True, port=5000)
