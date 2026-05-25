# RINA Visual Character - Image Generation Prompts

Dokumen ini berisi prompt (instruksi) yang bisa disalin-tempel ke AI Image Generator (seperti Midjourney, DALL-E 3, Leonardo AI, atau Bing Image Creator) untuk menghasilkan gambar referensi karakter RINA. Hasil dari gambar ini nantinya bisa di-*trace* menjadi SVG.

## 🎨 1. Prompt Karakter Dasar (Base Character)

Gunakan prompt ini untuk menghasilkan bentuk dasar RINA. **(Jika punya gambar referensi, upload gambar tersebut terlebih dahulu sebelum mengirim prompt ini)**:

> **Prompt (English):**
> "High-quality 2D Anime VTuber style character design of a friendly 22-year-old Indonesian woman named Rina. She has a warm, approachable, and genuine smile with large, expressive anime eyes. She is wearing stylish smart-casual clothing (a neat modern cardigan over a t-shirt). Natural black or dark brown hair with anime-style highlights, natural Indonesian skin tone. Cel-shaded anime coloring, clean lineart, pure white background. Front-facing character sheet style suitable for Live2D or VTuber rigging. Look like a caring peer or friend. CRITICAL: Avoid generic AI gloss, avoid over-rendered 3D shading, avoid overly plastic skin. Keep it strictly authentic 2D studio anime cel-shaded style."

## 🎭 2. Prompt untuk 7 Ekspresi Wajah

Setelah mendapatkan *base character* yang cocok, gunakan *seed* yang sama atau referensi gambar tersebut untuk menghasilkan variasi ekspresi. 

Jika menggunakan Midjourney, gunakan parameter `--cref` (Character Reference).

### 🟢 Ekspresi 1: IDLE (Menunggu)
> "Character sheet variation: The same Indonesian female character in a relaxed 'idle' state. Normal open eyes, subtle resting smile, head slightly tilted, relaxed posture. Flat vector art style, white background."

### 🟢 Ekspresi 2: LISTENING (Mendengarkan)
> "Character sheet variation: The same Indonesian female character actively listening. Eyes slightly wider and focused, mouth closed with a very thin smile, leaning forward slightly to show interest. Flat vector art style, white background."

### 🟢 Ekspresi 3: TALKING (Berbicara)
> "Character sheet variation: The same Indonesian female character mid-conversation. Expressive open eyes, mouth open in a natural speaking shape. Hand gestures indicating she is explaining something gently. Flat vector art style, white background."

### 🟢 Ekspresi 4: HAPPY / ENCOURAGING (Senang/Menyemangati)
> "Character sheet variation: The same Indonesian female character looking very happy and encouraging. Eyes slightly narrowed into crescent moon shapes (genuine smile), wide happy smile, energetic posture. Flat vector art style, white background."

### 🔴 Ekspresi 5: EMPATHY / CONCERNED (Empati)
> "Character sheet variation: The same Indonesian female character showing deep empathy and concern. Eyebrows slightly drawn together in the middle (worried), outer corners of eyes slightly down, soft mellow sympathetic smile, leaning forward in a comforting way. Flat vector art style, white background."

### 🔵 Ekspresi 6: THINKING (Memproses)
> "Character sheet variation: The same Indonesian female character deep in thought. Looking slightly up and to the side, one eyebrow slightly raised, hand touching chin, mouth slightly skewed in a 'hmm' expression. Flat vector art style, white background."

### 🔵 Ekspresi 7: SURPRISED / IMPRESSED (Terkejut)
> "Character sheet variation: The same Indonesian female character looking pleasantly surprised or impressed. Eyes widened, eyebrows raised, mouth slightly open in an 'oh' shape. Flat vector art style, white background."

---

## 🛠️ Tips Penggunaan (Untuk Michael)
1. **Pilih 1 Gaya yang Konsisten:** Pastikan gambar tidak terlalu 3D atau bergradasi rumit. Semakin flat gambarnya (*solid colors*), semakin mudah di-convert ke SVG (via Inkscape *Trace Bitmap*).
2. **Hapus Background:** Pastikan background benar-benar putih bersih agar mudah dihapus.
3. **Proporsi Wajah:** Usahakan proporsi wajah untuk setiap ekspresi tetap sama ukurannya agar Fikri mudah melakukan animasi transisi (GSAP `opacity` swap) antar *layer* SVG tanpa terlihat *jumping*.
