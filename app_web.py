import cv2
import numpy as np
import mediapipe as mp
import threading
from io import BytesIO
from tensorflow.keras.models import load_model
from flask import Flask, render_template, Response
from gtts import gTTS
import pygame


app = Flask(__name__)

model = load_model('model_isyarat(bisa).h5')
kata_kunci = ['Tugas', 'Kamu', 'Gimana', 'Halo', 'Semua', 'Aku', 'Selesai', 'Cinta', 'Aku sayang kamu', 'Mantap'] 

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

pygame.mixer.init()

def ucapkan_suara_google(teks):
    try:
        tts = gTTS(text=teks, lang='id')
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        pygame.mixer.music.load(fp)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print("Gagal memutar suara.")

def ekstrak_koordinat(results):
    titik_tangan = np.zeros(126) 
    if results.multi_hand_landmarks:
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            if i < 2:
                titik = np.array([[res.x, res.y, res.z] for res in hand_landmarks.landmark]).flatten()
                titik_tangan[i*63 : (i+1)*63] = titik
    return titik_tangan

def generate_frames():
    cap = cv2.VideoCapture(0)
    sequence = [] 
    teks_tampil = "Menunggu Gerakan..."
    kalimat = [] 
    
    kata_sebelumnya = ""
    hitung_konsisten = 0

    while True:
        success, frame = cap.read()
        if not success:
            break
        
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            koordinat = ekstrak_koordinat(results)
            sequence.append(koordinat)
            sequence = sequence[-30:]

            if len(sequence) == 30:
                input_data = np.expand_dims(sequence, axis=0)
                prediksi = model.predict(input_data, verbose=0)[0]
                
                indeks_tertinggi = np.argmax(prediksi)
                if prediksi[indeks_tertinggi] > 0.6:
                    teks_sementara = kata_kunci[indeks_tertinggi]
                    
                    if teks_sementara == kata_sebelumnya:
                        hitung_konsisten += 1
                    else:
                        hitung_konsisten = 0
                        kata_sebelumnya = teks_sementara

                    if hitung_konsisten == 15:
                        teks_tampil = teks_sementara
                        if len(kalimat) == 0 or teks_tampil != kalimat[-1]:
                            kalimat.append(teks_tampil)
                            threading.Thread(target=ucapkan_suara_google, args=(teks_tampil,)).start()
                            if len(kalimat) > 5:
                                kalimat = kalimat[-5:]
                else:
                    hitung_konsisten = 0
                    kata_sebelumnya = ""
        else:
            teks_tampil = "Menunggu Gerakan..."
            sequence = []
            hitung_konsisten = 0
            kata_sebelumnya = ""

        cv2.rectangle(frame, (0,0), (640, 50), (0, 0, 0), -1)
        cv2.putText(frame, teks_tampil, (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.rectangle(frame, (0, 430), (640, 480), (255, 255, 255), -1)
        kalimat_teks = " ".join(kalimat)
        cv2.putText(frame, kalimat_teks, (15, 465), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("\n" + "="*50)
    print("SERVER WEB AKTIF!")
    print("Buka browser dan ketik: http://127.0.0.1:5000")
    print("Tekan CTRL+C di terminal ini untuk mematikan server.")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=False)