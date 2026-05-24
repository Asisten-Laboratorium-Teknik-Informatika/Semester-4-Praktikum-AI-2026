import streamlit as st
import pickle
import nltk
import re
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

st.set_page_config(page_title="SpamScan", page_icon="🔍", layout="wide")

model = pickle.load(open("spam_model.pkl", "rb"))
tfidf = pickle.load(open("tfidf_vectorizer.pkl", "rb"))

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    tokens = [w for w in tokens if w not in stop_words]
    return " ".join(tokens)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&family=Inter:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #18181b 0%, #27200f 50%, #1a1500 100%) !important;
    color: #f0e9d6;
}

#MainMenu, footer, header { visibility: hidden; }

.main > div:first-child { padding-top: 0 !important; }
.main .block-container {
    padding-top: 0 !important;
    padding-left: 40px !important;
    padding-right: 40px !important;
    padding-bottom: 40px !important;
    max-width: 100% !important;
}

/* ---- NAVBAR ---- */
.navbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 26px 0 22px 0;
    border-bottom: 1px solid rgba(240,233,214,0.12);
    margin-bottom: 50px;
}
.brand {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 22px; font-weight: 800; color: #f0e9d6;
}
.brand-accent { color: #f59e0b; }
.live-pill {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(240,233,214,0.08);
    border: 1px solid rgba(240,233,214,0.15);
    color: #c9b97a;
    font-family: 'Inter', sans-serif;
    font-size: 10px; font-weight: 500;
    letter-spacing: 2px; text-transform: uppercase;
    padding: 7px 16px; border-radius: 100px;
}
.live-dot {
    width: 6px; height: 6px; background: #22c55e;
    border-radius: 50%; animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.2} }

/* ---- LEFT PANEL ---- */
.eyebrow {
    font-family: 'Inter', sans-serif;
    font-size: 10px; font-weight: 500;
    letter-spacing: 3px; text-transform: uppercase;
    color: #6b5f3e; margin-bottom: 20px;
}
.hero-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 48px; font-weight: 800;
    line-height: 1.05; letter-spacing: -1.5px;
    color: #f0e9d6; margin-bottom: 18px;
}
.hero-title .amber { color: #f59e0b; }
.hero-desc {
    font-family: 'Inter', sans-serif;
    font-size: 14.5px; font-weight: 400;
    color: #a89060; line-height: 1.75; margin-bottom: 32px;
}

/* ---- MINI LABEL ---- */
.mini-label {
    font-family: 'Inter', sans-serif;
    font-size: 10px; font-weight: 600;
    letter-spacing: 2px; text-transform: uppercase;
    color: #6b5f3e; margin-bottom: 12px;
}

/* ---- STAT CARDS ---- */
.stat-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 10px; margin-bottom: 30px;
}
.s-card {
    background: rgba(240,233,214,0.05);
    border: 1px solid rgba(240,233,214,0.12);
    border-radius: 14px; padding: 16px 18px;
}
.s-num {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 24px; font-weight: 800;
    color: #f59e0b; line-height: 1;
}
.s-lbl {
    font-family: 'Inter', sans-serif;
    font-size: 11px; font-weight: 400;
    color: #6b5f3e; margin-top: 5px;
}

/* ---- STEPS ---- */
.step-row { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 12px; }
.step-num {
    width: 22px; height: 22px;
    background: rgba(245,158,11,0.15);
    border: 1px solid rgba(245,158,11,0.4);
    color: #f59e0b;
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 11px; font-weight: 800;
    flex-shrink: 0; margin-top: 1px;
}
.step-text {
    font-family: 'Inter', sans-serif;
    font-size: 13.5px; font-weight: 400;
    color: #a89060; line-height: 1.6;
}

/* ---- RIGHT PANEL ---- */
.section-label {
    font-family: 'Inter', sans-serif;
    font-size: 10px; font-weight: 600;
    letter-spacing: 2px; text-transform: uppercase;
    color: #6b5f3e; margin-bottom: 10px;
}

/* streamlit columns */
[data-testid="column"] { padding: 0 12px !important; }
[data-testid="column"]:first-child { padding-left: 0 !important; }
[data-testid="column"]:last-child  { padding-right: 0 !important; }

/* ---- TEXTAREA ---- */
textarea {
    background: rgba(240,233,214,0.05) !important;
    color: #f0e9d6 !important;
    border: 1px solid rgba(240,233,214,0.15) !important;
    border-radius: 14px !important;
    padding: 16px 18px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important; font-weight: 400 !important;
    line-height: 1.7 !important;
    box-shadow: none !important;
    resize: none !important;
    transition: border-color .2s, background .2s !important;
}
textarea:focus {
    outline: none !important;
    border-color: rgba(245,158,11,0.5) !important;
    background: rgba(240,233,214,0.07) !important;
    box-shadow: 0 0 0 3px rgba(245,158,11,0.1) !important;
}
textarea::placeholder { color: #4a3f28 !important; font-style: italic !important; }

/* ---- BUTTON ---- */
div[data-testid="stButton"] > button {
    width: 100% !important;
    background: #1a1a1a !important;
    color: #f0e9d6 !important;
    border: 2px solid #1a1a1a !important;
    border-radius: 12px !important;
    padding: 14px 0 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important; font-weight: 700 !important;
    letter-spacing: 1.5px !important; text-transform: uppercase !important;
    box-shadow: 4px 4px 0 #f59e0b !important;
    transition: all .15s !important; margin-top: 12px !important;
}
div[data-testid="stButton"] > button:hover {
    background: #f59e0b !important;
    border-color: #f59e0b !important;
    color: #18181b !important;
    box-shadow: 4px 4px 0 #1a1a1a !important;
    transform: translate(-1px, -1px) !important;
}
div[data-testid="stButton"] > button:active {
    transform: translate(2px, 2px) !important;
    box-shadow: 2px 2px 0 #f59e0b !important;
}

/* ---- RESULT CARDS ---- */
.res-spam {
    margin-top: 18px;
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.35);
    border-radius: 16px; padding: 20px 22px;
    display: flex; gap: 14px; align-items: flex-start;
}
.res-safe {
    margin-top: 18px;
    background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.3);
    border-radius: 16px; padding: 20px 22px;
    display: flex; gap: 14px; align-items: flex-start;
}
.res-icon { font-size: 28px; line-height: 1; flex-shrink: 0; }
.res-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 17px; font-weight: 700; margin-bottom: 5px;
}
.res-spam .res-title { color: #f87171; }
.res-safe .res-title  { color: #4ade80; }
.res-body {
    font-family: 'Inter', sans-serif;
    font-size: 13.5px; font-weight: 400; line-height: 1.6;
}
.res-spam .res-body { color: #fca5a5; }
.res-safe .res-body  { color: #86efac; }

/* hide textarea label */
div[data-testid="stTextArea"] label { display: none !important; }

/* warning */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: 1px solid rgba(245,158,11,0.4) !important;
    background: rgba(245,158,11,0.08) !important;
    color: #fcd34d !important;
    font-family: 'Inter', sans-serif !important;
}

/* ---- FOOTER ---- */
.app-footer {
    display: flex; justify-content: space-between; align-items: center;
    margin-top: 52px; padding-top: 18px;
    border-top: 1px solid rgba(240,233,214,0.1);
}
.footer-brand {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 13px; font-weight: 800; color: #f0e9d6;
}
.footer-copy {
    font-family: 'Inter', sans-serif;
    font-size: 12px; font-weight: 400; color: #4a3f28;
}
</style>
""", unsafe_allow_html=True)

# ── NAVBAR ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
  <div class="brand">Spam<span class="brand-accent">Scan</span></div>
  <div class="live-pill"><span class="live-dot"></span>Model Aktif · Naive Bayes</div>
</div>
""", unsafe_allow_html=True)

# ── TWO COLUMNS ──────────────────────────────────────────────────────────
left, right = st.columns([4, 5], gap="large")

with left:
    st.markdown("""
    <div class="eyebrow">Machine Learning · NLP</div>
    <div class="hero-title">Deteksi<br>Pesan<br><span class="amber">Spam.</span></div>
    <p class="hero-desc">
      Tempelkan pesan mencurigakan dan biarkan model menganalisisnya.
      Didukung Naive Bayes dengan akurasi tinggi.
    </p>

    <div class="mini-label">Statistik Model</div>
    <div class="stat-grid">
      <div class="s-card"><div class="s-num">96%</div><div class="s-lbl">Akurasi Model</div></div>
      <div class="s-card"><div class="s-num">NB</div><div class="s-lbl">Naive Bayes</div></div>
      <div class="s-card"><div class="s-num">6.3K</div><div class="s-lbl">Data Training</div></div>
      <div class="s-card"><div class="s-num">TF‑IDF</div><div class="s-lbl">Feature Extraction</div></div>
    </div>

    <div class="mini-label">Cara Penggunaan</div>
    <div class="step-row"><div class="step-num">1</div><div class="step-text">Salin pesan dari WhatsApp, SMS, atau email yang mencurigakan.</div></div>
    <div class="step-row"><div class="step-num">2</div><div class="step-text">Tempel teks ke kolom input di sebelah kanan.</div></div>
    <div class="step-row"><div class="step-num">3</div><div class="step-text">Klik tombol Analisis dan baca hasilnya.</div></div>
    """, unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-label">Teks Pesan</div>', unsafe_allow_html=True)

    message = st.text_area(
        label="pesan",
        height=230,
        placeholder='Tempel atau ketik pesan di sini…\nContoh: "Selamat! Anda memenangkan hadiah Rp 10 juta. Klik tautan untuk klaim."'
    )

    detect = st.button("→ Analisis Pesan Sekarang")

    if detect:
        if message.strip() == "":
            st.warning("⚠️  Pesan tidak boleh kosong.")
        else:
            pred = model.predict(tfidf.transform([preprocess_text(message)]))[0]
            if pred == "spam":
                st.markdown("""
                <div class="res-spam">
                  <div class="res-icon">🚨</div>
                  <div>
                    <div class="res-title">Pesan Terdeteksi Spam</div>
                    <div class="res-body">Pesan ini memiliki pola spam. Hindari mengklik tautan atau memberikan data pribadi.</div>
                  </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="res-safe">
                  <div class="res-icon">✅</div>
                  <div>
                    <div class="res-title">Pesan Aman · Non-Spam</div>
                    <div class="res-body">Tidak ditemukan indikasi spam. Pesan ini tampak seperti komunikasi normal dan sah.</div>
                  </div>
                </div>""", unsafe_allow_html=True)

# ── FOOTER ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-footer">
  <div class="footer-brand">SpamScan</div>
  <div class="footer-copy">© 2026 · Untuk keperluan edukasi</div>
</div>
""", unsafe_allow_html=True)