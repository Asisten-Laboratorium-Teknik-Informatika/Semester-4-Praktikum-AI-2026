import numpy as np
import os
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

kata_kunci = np.array(['Tugas', 'Kamu', 'Gimana', 'Halo', 'Semua', 'Aku', 'Selesai', 'Cinta', 'Aku sayang kamu', 'Mantap']) 

jumlah_video = 30
jumlah_frame = 30

label_map = {label:num for num, label in enumerate(kata_kunci)}

semua_data = []
semua_label = []

print("Sedang membaca data gerakan dari folder...")
for kata in kata_kunci:
    for video in range(jumlah_video):
        lokasi_file = os.path.join("Data_Isyarat", kata, f"{video}.npy")

        res = np.load(lokasi_file)
        semua_data.append(res)
        semua_label.append(label_map[kata])

X = np.array(semua_data)
y = to_categorical(semua_label).astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)

print("Membangun jaringan saraf AI...")
model = Sequential()


model.add(LSTM(64, return_sequences=True, activation='relu', input_shape=(30, 126)))
model.add(Dropout(0.2))


model.add(LSTM(128, return_sequences=True, activation='relu'))
model.add(Dropout(0.2))

model.add(LSTM(64, return_sequences=False, activation='relu'))
model.add(Dropout(0.2))


model.add(Dense(64, activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(kata_kunci.shape[0], activation='softmax'))

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])

print("Mulai proses belajar! Silakan tunggu...")

early_stopping = EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True)

checkpoint = ModelCheckpoint('model_isyarat.h5', monitor='val_categorical_accuracy', save_best_only=True, mode='max')

history = model.fit(
    X_train, y_train, 
    validation_data=(X_test, y_test), 
    epochs=200, 
    callbacks=[early_stopping, checkpoint]
)


print("\nEvaluasi model pada data test:")
res = model.evaluate(X_test, y_test)
print(f"Akurasi Test: {res[1]*100:.2f}%")
print("\nLuar Biasa! Otak AI berhasil dilatih dan disimpan sebagai 'model_isyara'")