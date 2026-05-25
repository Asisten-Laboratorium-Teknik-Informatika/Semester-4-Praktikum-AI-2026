from flask import Flask, render_template, request, jsonify, session
import numpy as np
from PIL import Image
import io
import base64
import os
import json
import cv2

app = Flask(__name__)
app.secret_key = 'facemood-secret-key-2024'

# Load model
import tensorflow as tf
model = tf.keras.models.load_model('facemood_raf_model.h5')

# Face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# Class labels
CLASS_LABELS = ['Surprise', 'Fear', 'Disgust', 'Happy', 'Sad', 'Angry', 'Neutral']

# Mood colors
MOOD_COLORS = {
    'Surprise': {'primary': '#FF1493', 'light': '#FF69B4', 'dark': '#C0006E', 'text': '#ffffff'},
    'Fear':     {'primary': '#7B2FBE', 'light': '#A855F7', 'dark': '#4A0E8F', 'text': '#ffffff'},
    'Disgust':  {'primary': '#16A34A', 'light': '#4ADE80', 'dark': '#0A5C2A', 'text': '#ffffff'},
    'Happy':    {'primary': '#EAB308', 'light': '#FDE047', 'dark': '#A16207', 'text': '#1a1a1a'},
    'Sad':      {'primary': '#2563EB', 'light': '#60A5FA', 'dark': '#1E3A8A', 'text': '#ffffff'},
    'Angry':    {'primary': '#DC2626', 'light': '#F87171', 'dark': '#991B1B', 'text': '#ffffff'},
    'Neutral':  {'primary': '#e5e5e5', 'light': '#f5f5f5', 'dark': '#a3a3a3', 'text': '#1a1a1a'},
}

# Mood emoji
MOOD_EMOJI = {
    'Surprise': '😲',
    'Fear': '😨',
    'Disgust': '🤢',
    'Happy': '😊',
    'Sad': '😢',
    'Angry': '😠',
    'Neutral': '😐',
}

# Mood recommendations
MOOD_RECOMMENDATIONS = {
    'Surprise': [
        'Catat momen ini dalam jurnal dan refleksikan apa yang membuatmu terkejut.',
        'Bagikan pengalaman mengejutkan ini dengan orang terdekatmu.',
        'Gunakan rasa penasaran ini untuk mengeksplorasi hal baru yang belum pernah kamu coba.',
        'Ambil napas dalam dan nikmati kejutan yang datang sebagai bagian dari perjalanan hidupmu.',
    ],
    'Fear': [
        'Coba teknik pernapasan dalam: tarik napas 4 detik, tahan 4 detik, hembuskan 4 detik.',
        'Tuliskan apa yang kamu takutkan dan langkah kecil yang bisa kamu lakukan untuk menghadapinya.',
        'Hubungi seseorang yang kamu percaya dan ceritakan perasaanmu.',
        'Dengarkan musik yang menenangkan dan berikan dirimu waktu untuk beristirahat.',
    ],
    'Disgust': [
        'Jauhkan dirimu sejenak dari situasi yang membuatmu tidak nyaman.',
        'Lakukan aktivitas yang kamu sukai untuk mengalihkan pikiran.',
        'Coba berjalan-jalan sebentar untuk menyegarkan pikiran.',
        'Tulis perasaanmu di jurnal untuk membantu memproses emosi yang kamu rasakan.',
    ],
    'Happy': [
        'Bagikan kebahagiaanmu dengan orang-orang di sekitarmu!',
        'Manfaatkan energi positif ini untuk menyelesaikan tugas atau proyek yang tertunda.',
        'Abadikan momen bahagia ini dengan foto atau tulisan di jurnal.',
        'Lakukan kebaikan kecil untuk orang lain dan sebarkan kebahagiaanmu.',
    ],
    'Sad': [
        'Izinkan dirimu untuk merasakan kesedihan ini, tidak apa-apa untuk merasa sedih.',
        'Tonton film atau dengarkan lagu favoritmu untuk menghibur diri.',
        'Hubungi teman atau anggota keluarga yang kamu percaya untuk berbicara.',
        'Coba berjalan-jalan di luar ruangan dan hirup udara segar untuk menenangkan pikiran.',
    ],
    'Angry': [
        'Tarik napas dalam-dalam dan hitung sampai sepuluh sebelum bereaksi.',
        'Lakukan olahraga ringan seperti jalan cepat atau peregangan untuk melepaskan energi.',
        'Tulis perasaanmu di kertas sebagai cara untuk melepaskan emosi yang terpendam.',
        'Dengarkan musik favorit dan berikan dirimu waktu untuk tenang sebelum menghadapi situasi.',
    ],
    'Neutral': [
        'Gunakan momen tenang ini untuk merencanakan tujuan dan aktivitasmu ke depan.',
        'Coba aktivitas baru yang menarik perhatianmu untuk menambah semangat hari ini.',
        'Luangkan waktu untuk membaca buku atau menonton konten yang menginspirasi.',
        'Lakukan meditasi singkat untuk memperkuat ketenangan yang sedang kamu rasakan.',
    ],
}

def preprocess_image(image_bytes):
    # Convert bytes ke numpy array (OpenCV)
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # Deteksi wajah
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=3, minSize=(20, 20)
    )

    if len(faces) == 0:
        # Tidak ada wajah terdeteksi, pakai seluruh foto
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        face = cv2.resize(img_rgb, (100, 100))
    else:
        # Ambil wajah terbesar
        faces = sorted(faces, key=lambda x: x[2]*x[3], reverse=True)
        x, y, w, h = faces[0]
        # Tambah margin sedikit
        margin = int(0.1 * w)
        x = max(0, x - margin)
        y = max(0, y - margin)
        w = min(img_cv.shape[1] - x, w + 2*margin)
        h = min(img_cv.shape[0] - y, h + 2*margin)
        face = img_cv[y:y+h, x:x+w]
        face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        face = cv2.resize(face, (100, 100))

    face = face / 255.0
    face = face.reshape(1, 100, 100, 3)
    return face

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    image_bytes = file.read()

    # Preprocess dengan face detection + predict
    img_array = preprocess_image(image_bytes)
    predictions = model.predict(img_array)

    predicted_idx = np.argmax(predictions[0])
    predicted_mood = CLASS_LABELS[predicted_idx]
    confidence = float(predictions[0][predicted_idx]) * 100

    # Encode image to base64 for display
    img_b64 = base64.b64encode(image_bytes).decode('utf-8')

    return jsonify({
        'mood': predicted_mood,
        'confidence': round(confidence, 1),
        'emoji': MOOD_EMOJI[predicted_mood],
        'colors': MOOD_COLORS[predicted_mood],
        'recommendations': MOOD_RECOMMENDATIONS[predicted_mood],
        'image': f'data:{file.content_type};base64,{img_b64}',
    })

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    mood = data.get('mood')
    user_input = data.get('user_input', '')

    if not mood or mood not in CLASS_LABELS:
        return jsonify({'error': 'Invalid mood'}), 400

    positive_messages = {
        'Surprise': 'Kejutan bisa menjadi awal dari sesuatu yang luar biasa! Tetap terbuka terhadap hal-hal baru yang datang dalam hidupmu.',
        'Fear': 'Rasa takut adalah tanda bahwa kamu peduli. Ingat, keberanian bukan berarti tidak takut, tetapi tetap melangkah meski rasa takut itu ada.',
        'Disgust': 'Perasaan tidak nyaman ini menunjukkan bahwa kamu memiliki nilai dan batasan yang jelas. Itu adalah hal yang baik.',
        'Happy': 'Kebahagiaan yang kamu rasakan saat ini adalah nyata dan berharga. Terus jaga energi positif ini!',
        'Sad': 'Setiap kesedihan pasti akan berlalu. Kamu lebih kuat dari yang kamu kira, dan hari yang lebih baik pasti akan datang.',
        'Angry': 'Kemarahanmu menunjukkan bahwa kamu peduli. Salurkan energi ini ke arah yang positif dan konstruktif.',
        'Neutral': 'Ketenangan adalah kekuatan. Gunakan momen ini untuk refleksi dan persiapan diri menuju hal-hal yang lebih baik.',
    }

    return jsonify({
        'positive_message': positive_messages.get(mood, ''),
        'recommendations': MOOD_RECOMMENDATIONS.get(mood, []),
    })

if __name__ == '__main__':
    app.run(debug=True)