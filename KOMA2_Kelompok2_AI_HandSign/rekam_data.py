import cv2
import mediapipe as mp
import numpy as np
import os
import time

kata_isyarat = "Semua"  
jumlah_video = 30       
jumlah_frame = 30       

lokasi_folder = os.path.join("Data_Isyarat", kata_isyarat)
if not os.path.exists(lokasi_folder):
    os.makedirs(lokasi_folder)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

def ekstrak_koordinat(results):
    titik_tangan = np.zeros(126) 
    if results.multi_hand_landmarks:
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            if i < 2: 
                titik = np.array([[res.x, res.y, res.z] for res in hand_landmarks.landmark]).flatten()
                titik_tangan[i*63 : (i+1)*63] = titik
    return titik_tangan

cap = cv2.VideoCapture(0)

print(f"Mulai program perekaman untuk kata: {kata_isyarat}")

while True:
    ret, frame = cap.read()
    if not ret: continue

    frame = cv2.flip(frame, 1)
    cv2.putText(frame, f"Siap merekam: {kata_isyarat} (Total {jumlah_video} Video)", (15, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, "Tekan 'S' lalu posisikan tangan!", (15, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.imshow('Kamera Perekam', frame)

    key = cv2.waitKey(10) & 0xFF
    if key == ord('s'):
        for i in range(3, 0, -1):
            waktu_awal = time.time()
            while time.time() - waktu_awal < 1.0:
                ret, frame_mundur = cap.read()
                if ret:
                    frame_mundur = cv2.flip(frame_mundur, 1)
                    cv2.putText(frame_mundur, f"Mulai dalam {i}...", (150, 250), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 165, 255), 4)
                    cv2.imshow('Kamera Perekam', frame_mundur)
                    cv2.waitKey(10)
        break

for video in range(jumlah_video):
    data_gerakan = [] 
    
    for frame_num in range(jumlah_frame):
        ret, frame = cap.read()
        if not ret: continue

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.putText(frame, f"Merekam: {kata_isyarat} | Video: {video+1}/{jumlah_video} | Frame: {frame_num+1}/30", (15, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.imshow('Kamera Perekam', frame)

        koordinat = ekstrak_koordinat(results)
        data_gerakan.append(koordinat)

        cv2.waitKey(10)

    lokasi_file = os.path.join(lokasi_folder, f"{video}.npy")
    np.save(lokasi_file, data_gerakan)
    print(f"Video ke-{video+1} berhasil disimpan!")

cap.release()
cv2.destroyAllWindows()
print(f"Selesai! Seluruh data {kata_isyarat} telah terekam secara berurutan.")