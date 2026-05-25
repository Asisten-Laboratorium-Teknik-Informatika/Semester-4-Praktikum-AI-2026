import os

out_dir = "M:/Ai Tugas Akhir Project/ProjekAI/CHAT/prompts_10_akun"
os.makedirs(out_dir, exist_ok=True)

accounts = [
    {
        "id": 1,
        "fokus_profesi": "Mahasiswa, Dosen, Guru SD/SMP/SMA, Staf Akademik",
        "fokus_konteks": "Skripsi stuck, ujian, tekanan akademik, kesulitan mengajar, ekspektasi keluarga",
        "gaya_bahasa": "Formal, santai, typo, emosional",
    },
    {
        "id": 2,
        "fokus_profesi": "Software Developer, Data Analyst, Desainer Grafis, Startup Founder, IT Support",
        "fokus_konteks": "Deadline ketat (crunch time), impostor syndrome, bug code, revisi desain tiada henti",
        "gaya_bahasa": "Campur_inggris, gaul, santai, bercerita",
    },
    {
        "id": 3,
        "fokus_profesi": "Dokter muda, Perawat, Bidan, Tenaga Kesehatan, Apoteker",
        "fokus_konteks": "Overwork, jadwal shift tidak teratur, jaga malam, menghadapi pasien marah",
        "gaya_bahasa": "Formal, singkat, emosional, typo",
    },
    {
        "id": 4,
        "fokus_profesi": "Karyawan Kantoran (Finance, HRD, Marketing, Admin)",
        "fokus_konteks": "Toxic workplace, konflik dengan atasan, closing akhir bulan, masalah gaji",
        "gaya_bahasa": "Santai, campur_inggris, bercerita, formal",
    },
    {
        "id": 5,
        "fokus_profesi": "Pekerja Retail, F&B, Kasir, Ojol, Kurir, Barista",
        "fokus_konteks": "Masalah keuangan, kelelahan fisik, customer marah/toxic, target harian",
        "gaya_bahasa": "Santai, gaul, singkat, typo",
    },
    {
        "id": 6,
        "fokus_profesi": "Ibu Rumah Tangga, Caregiver, Freelancer, Pekerja Remote",
        "fokus_konteks": "Role overload, kurang istirahat, merasa tidak diapresiasi, kesepian",
        "gaya_bahasa": "Bercerita, emosional, santai, formal",
    },
    {
        "id": 7,
        "fokus_profesi": "Mahasiswa Akhir, Peneliti, Asisten Lab, Fresh Graduate",
        "fokus_konteks": "Kehilangan motivasi, quarter-life crisis, anxiety masa depan, cari kerja susah",
        "gaya_bahasa": "Campur_inggris, emosional, santai, bercerita",
    },
    {
        "id": 8,
        "fokus_profesi": "Arsitek, Kontraktor, Engineer Lapangan, Pekerja Pabrik",
        "fokus_konteks": "Lembur terus, target proyek, cuaca buruk, bahaya fisik, tekanan mandor",
        "gaya_bahasa": "Singkat, santai, gaul, typo",
    },
    {
        "id": 9,
        "fokus_profesi": "Jurnalis, Editor, Content Creator, Penulis",
        "fokus_konteks": "Writer's block, cyberbullying, tuntutan engagement/views, deadline harian",
        "gaya_bahasa": "Campur_inggris, bercerita, gaul, emosional",
    },
    {
        "id": 10,
        "fokus_profesi": "Semua profesi secara acak (Mix)",
        "fokus_konteks": "Transisi hidup: Pindah kerja, putus cinta, masalah pertemanan, masalah kesehatan fisik",
        "gaya_bahasa": "Santai, campur_inggris, emosional, typo",
    }
]

TEMPLATE = """# Prompt Dataset Chat - Akun {id} (Batch {start_batch}-{end_batch})

> **Tujuan:** Menghasilkan 100 percakapan sintetis (dibagi 10 batch) untuk **Akun {id}**.
> **PENTING UNTUK AKUN {id}:** Fokuslah HANYA pada konteks dan profesi yang ditentukan agar data tidak repetitif dengan akun lain!

---

## Instruksi Penggunaan
1. Jalankan prompt utama di bawah ini di satu tab / sesi Gemini baru.
2. Generate 10 batch secara berurutan sesuai tabel distribusi.
3. Simpan hasilnya di `Data/synthetic/batches/` dengan nama `batch_{start_batch}.json` hingga `batch_{end_batch}.json`.

---

## PROMPT UTAMA

```text
Kamu adalah generator dataset percakapan untuk proyek LifeLens, sebuah aplikasi deteksi burnout berbasis AI.

═══ TUGAS ═══
Generate percakapan unik antara USER dan RINA dalam Bahasa Indonesia untuk Batch ke-[ISI_NOMOR_BATCH]. 
Level burnout untuk batch ini: [ISI_BURNOUT_LEVEL].
Jumlah percakapan: [ISI_JUMLAH] percakapan.

═══ FOKUS KHUSUS UNTUK SESI INI (WAJIB DIIKUTI) ═══
Agar data unik dan tidak mengulang, ikuti batas berikut:
- **Profesi User (Pilih Acak dari ini saja):** {fokus_profesi}
- **Konteks Masalah (Pilih Acak dari ini saja):** {fokus_konteks}
- **Gaya Bahasa (Pilih Acak dari ini saja):** {gaya_bahasa}

═══ TENTANG RINA (PERSONA AI) ═══
- Hangat, tidak menghakimi, penasaran dengan cara yang tulus
- Bahasa mengikuti PERSIS gaya user
- Boleh pakai "hmm", "oh", "wah", "eh" untuk terasa manusiawi
- TIDAK PERNAH menyebut kata "burnout" atau "diagnosis"
- TIDAK PERNAH memberi saran panjang yang tidak diminta

═══ ATURAN MULTI-BUBBLE RINA (PENTING!) ═══
RINA merespon dengan 1 SAMPAI 3 bubble chat per giliran (pisahkan dengan |||).
Contoh 1: "Oh gitu ya? ||| Terus sekarang gimana rasanya?"
Contoh 2: "Waduh capek banget pasti ||| Kalau boleh tau, tidurnya gimana akhir-akhir ini?"

═══ PROFIL BURNOUT ═══
LOW: Tidur 6-8 jam (baik). Beban kerja 3-5/10. Mood stabil. Sosialisasi aktif. Sentimen netral-positif.
MEDIUM: Tidur 4-6 jam (buruk). Beban kerja 6-8/10. Sering lelah, tertekan, mulai menarik diri. Sentimen campuran.
HIGH: Tidur 2-4 jam. Beban kerja 8-10/10. Mood sangat negatif, apatis. Menghindari sosialisasi. Sentimen sangat negatif, banyak kata absolut.

═══ FORMAT OUTPUT ═══
Output HANYA JSON array, tanpa teks lain, tanpa markdown code block:
[
  {{
    "id": "batch[NOMOR_BATCH]_conv[NOMOR]",
    "burnout_level": "...",
    "profession": "...",
    "age": 18-45,
    "language_style": "...",
    "context": "...",
    "conversation": [
      {{"role": "rina", "text": "..."}},
      {{"role": "user", "text": "..."}}
      // Lanjutkan hingga minimal 10 - 100 pesan total
    ],
    "features": {{
      "sleep_hours": 0.0, "sleep_quality": 0, "workload_score": 0,
      "mood_score": 0, "social_score": 0, "recovery_score": 0,
      "sentiment_score": 0.0, "cognitive_distortion_score": 0.0,
      "absolutist_count": 0, "helplessness_count": 0,
      "keyword_count": 0, "dominant_domain": "...", "message_avg_length": 0
    }},
    "user_texts_combined": "..."
  }}
]

═══ ATURAN PENTING LAINNYA ═══
1. Setiap percakapan MINIMAL 10 pesan hingga MAKSIMAL 100 pesan (percakapan mendalam). RINA mulai duluan.
2. Features numerik harus konsisten dengan level burnout.
3. Percakapan harus natural. Variasikan panjang pendek bubble RINA.
```

---

## Tabel Distribusi Batch untuk Akun {id}

Jalankan perintah berikut satu per satu ke AI:

| Prompt yang diketik ke AI | Jumlah Percakapan | Level Burnout | Nama File Simpan |
| :--- | :--- | :--- | :--- |
| `Buatkan Batch {start_batch}: 10 percakapan dengan level LOW` | 10 | LOW | `batch_{start_batch}.json` |
| `Buatkan Batch {b2}: 10 percakapan dengan level LOW` | 10 | LOW | `batch_{b2}.json` |
| `Buatkan Batch {b3}: 10 percakapan dengan level LOW` | 10 | LOW | `batch_{b3}.json` |
| `Buatkan Batch {b4}: 3 percakapan LOW dan 7 percakapan MEDIUM` | 10 | 3 LOW, 7 MEDIUM | `batch_{b4}.json` |
| `Buatkan Batch {b5}: 10 percakapan dengan level MEDIUM` | 10 | MEDIUM | `batch_{b5}.json` |
| `Buatkan Batch {b6}: 10 percakapan dengan level MEDIUM` | 10 | MEDIUM | `batch_{b6}.json` |
| `Buatkan Batch {b7}: 6 percakapan MEDIUM dan 4 percakapan HIGH` | 10 | 6 MED, 4 HIGH | `batch_{b7}.json` |
| `Buatkan Batch {b8}: 10 percakapan dengan level HIGH` | 10 | HIGH | `batch_{b8}.json` |
| `Buatkan Batch {b9}: 10 percakapan dengan level HIGH` | 10 | HIGH | `batch_{b9}.json` |
| `Buatkan Batch {b10}: 10 percakapan dengan level HIGH` | 10 | HIGH | `batch_{b10}.json` |

Total dari Akun {id}: 33 LOW, 33 MEDIUM, 34 HIGH (Total: 100 percakapan).
"""

for acc in accounts:
    start_batch = (acc["id"] - 1) * 10 + 1
    end_batch = start_batch + 9
    
    b2 = start_batch + 1
    b3 = start_batch + 2
    b4 = start_batch + 3
    b5 = start_batch + 4
    b6 = start_batch + 5
    b7 = start_batch + 6
    b8 = start_batch + 7
    b9 = start_batch + 8
    b10 = start_batch + 9
    
    content = TEMPLATE.format(
        id=acc["id"],
        fokus_profesi=acc["fokus_profesi"],
        fokus_konteks=acc["fokus_konteks"],
        gaya_bahasa=acc["gaya_bahasa"],
        start_batch=start_batch,
        end_batch=end_batch,
        b2=b2, b3=b3, b4=b4, b5=b5, b6=b6, b7=b7, b8=b8, b9=b9, b10=b10
    )
    
    file_path = os.path.join(out_dir, f"prompt_akun_{acc['id']}.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Berhasil membuat 10 file markdown di {out_dir}")
