# Prompt Asset Ekspresi + Pose RINA

Gunakan prompt ini untuk membuat 10 aset PNG RINA yang konsisten dengan state di aplikasi.

## Base Prompt

Pakai base prompt ini di semua gambar:

```text
anime visual novel girl character named RINA, 22 years old, warm caring expression, same face, same hairstyle, same outfit, same character design, clean full body character sprite, front facing, polished otome game style, soft studio lighting, transparent background or plain white background, high detail, consistent proportions
```

Tambahkan pose/ekspresi dari daftar di bawah sesuai nomor file.

## Negative Prompt

```text
different outfit, different hairstyle, different face, extra fingers, missing fingers, distorted hands, bad anatomy, cropped body, duplicate character, low quality, blurry, text, watermark, logo, harsh shadow, messy background
```

## Daftar Asset

Simpan hasil akhir ke:

```text
frontend/public/assets/rina/
```

Nama file harus sama seperti mapping aplikasi.

### 1. Idle

File:

```text
1.png
```

Prompt tambahan:

```text
neutral face, gentle closed mouth smile, relaxed posture, arms resting naturally, sitting or standing straight, looking at viewer, calm idle pose
```

### 2. Happy

File:

```text
2.png
```

Prompt tambahan:

```text
happy face, big warm smile, bright eyes, cheerful expression, slight head tilt, one hand waving gently or touching chest, lively welcoming posture
```

### 3. Empathy

File:

```text
3.png
```

Prompt tambahan:

```text
empathetic expression, soft sad smile, caring eyes, gentle gaze, leaning forward slightly, both hands clasped near chest, comforting posture
```

### 4. Thinking

File:

```text
4.png
```

Prompt tambahan:

```text
thinking face, eyes looking slightly up and to the side, finger on chin, slightly parted lips, thoughtful posture, subtle serious expression
```

### 5. Surprised

File:

```text
5.png
```

Prompt tambahan:

```text
surprised expression, widened eyes, slightly open mouth, shoulders pulled back a little, hands raised slightly, concerned but cute reaction
```

### 6. Talking

File:

```text
6.png
```

Prompt tambahan:

```text
talking expression, open mouth, gentle smile, looking at viewer, one hand making a natural conversational gesture, active friendly posture
```

### 7. Listening

File:

```text
7.png
```

Prompt tambahan:

```text
listening intently, gentle closed mouth smile, focused attentive eyes, leaning forward slightly, hands on lap or one hand near cheek, patient attentive posture
```

### 8. Concerned

File:

```text
8.png
```

Prompt tambahan:

```text
deeply concerned expression, worried eyes, slightly furrowed brows, leaning forward, hands clasped tightly or reaching out slightly, soft comforting posture
```

### 9. Encouraging

File:

```text
9.png
```

Prompt tambahan:

```text
encouraging smile, confident soft look, determined but gentle expression, leaning forward, one hand in a small cheering fist gesture, energetic supportive posture
```

### 10. Neutral

File:

```text
10.png
```

Prompt tambahan:

```text
calm expression, professional but friendly, gentle closed mouth smile, straight posture, hands neatly on lap, relaxed formal posture
```

## Mapping di Aplikasi

```text
idle        -> 1.png
happy       -> 2.png
empathy     -> 3.png
thinking    -> 4.png
surprised   -> 5.png
talking     -> 6.png
listening   -> 7.png
concerned   -> 8.png
encouraging -> 9.png
neutral     -> 10.png
```

## Catatan

Untuk hasil terbaik, generate dari satu referensi RINA yang sama memakai image-to-image. Jangan generate tiap pose dari nol, karena wajah dan outfit akan gampang berubah.
