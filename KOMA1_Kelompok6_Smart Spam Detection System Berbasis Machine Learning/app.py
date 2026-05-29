import streamlit as st
import pickle
import nltk
import re
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# CONFIG
st.set_page_config(
    page_title="Spam Detector",
    page_icon="📩",
    layout="wide"
)

# LOAD MODEL
model = pickle.load(open("spam_model.pkl", "rb"))
tfidf = pickle.load(open("tfidf_vectorizer.pkl", "rb"))

# DOWNLOAD NLTK DATA
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
stop_words = set(stopwords.words('english'))

# PREPROCESSING FUNCTION
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    tokens = [w for w in tokens if w not in stop_words]
    return " ".join(tokens)

# STYLING
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&family=Inter:wght@400;500&display=swap');

* { box-sizing: border-box; }

html, body, .stApp {
    font-family: 'Inter', sans-serif;
    background: #d4ff52 !important;  # ← BAGIAN INI (warna background)
    background-attachment: fixed;
    color: #1a1a1a;
}

#MainMenu, footer, header { visibility: hidden; }

.main > div:first-child { padding-top: 0 !important; }

.main .block-container {
    padding-top: 2rem !important;
    padding-left: 40px !important;
    padding-right: 40px !important;
    padding-bottom: 40px !important;
    max-width: 100% !important;
}

/* NAVBAR */
.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 0 24px 0;
    border-bottom: 1px solid rgba(0, 0, 0, 0.08);
    margin-bottom: 40px;
}

.brand {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 22px;
    font-weight: 800;
    color: #1a1a1a;
}

.brand-accent { color: #2563eb; }

.live-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(0, 0, 0, 0.06);
    border: 1px solid rgba(0, 0, 0, 0.12);
    color: #4b5563;
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 7px 14px;
    border-radius: 100px;
}

.live-dot {
    width: 6px;
    height: 6px;
    background: #10b981;
    border-radius: 50%;
    animation: blink 2s infinite;
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* EYEBROW TEXT */
.eyebrow {
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #666666;
    margin-bottom: 16px;
}

/* HERO SECTION */
.hero-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 48px;
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: -1.5px;
    color: #1a1a1a;
    margin-bottom: 18px;
}

.hero-title .amber { color: #2563eb; }

.hero-desc {
    font-family: 'Inter', sans-serif;
    font-size: 14.5px;
    font-weight: 400;
    color: #555555;
    line-height: 1.75;
    margin-bottom: 32px;
}

/* MINI LABEL */
.mini-label {
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #666666;
    margin-bottom: 16px;
    margin-top: 24px;
}

/* STAT GRID */
.stat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 32px;
}

.stat-card {
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 14px;
    padding: 18px 16px;
}

.stat-num {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 24px;
    font-weight: 800;
    color: #2563eb;
    line-height: 1;
}

.stat-lbl {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    font-weight: 400;
    color: #666666;
    margin-top: 6px;
}

/* STEPS */
.step-row {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 14px;
}

.step-num {
    width: 24px;
    height: 24px;
    background: rgba(37, 99, 235, 0.15);
    border: 1.5px solid rgba(37, 99, 235, 0.4);
    color: #2563eb;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 11px;
    font-weight: 800;
    flex-shrink: 0;
    margin-top: 2px;
}

.step-text {
    font-family: 'Inter', sans-serif;
    font-size: 13.5px;
    font-weight: 400;
    color: #555555;
    line-height: 1.6;
    padding-top: 2px;
}

/* SECTION LABEL */
.section-label {
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #666666;
    margin-bottom: 12px;
}

/* COLUMN PADDING */
[data-testid="column"] { padding: 0 12px !important; }
[data-testid="column"]:first-child { padding-left: 0 !important; }
[data-testid="column"]:last-child { padding-right: 0 !important; }

/* TEXTAREA */
textarea {
    background: rgba(255, 255, 255, 0.8) !important;
    color: #1a1a1a !important;
    border: 1px solid rgba(0, 0, 0, 0.12) !important;
    border-radius: 14px !important;
    padding: 16px 18px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    font-weight: 400 !important;
    line-height: 1.7 !important;
    box-shadow: none !important;
    resize: none !important;
    transition: all 0.2s !important;
}

textarea:focus {
    outline: none !important;
    border-color: rgba(37, 99, 235, 0.5) !important;
    background: rgba(255, 255, 255, 0.95) !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
}

textarea::placeholder {
    color: #999999 !important;
    font-style: italic !important;
}

/* BUTTON */
div[data-testid="stButton"] > button {
    width: 100% !important;
    background: #1a1a1a !important;
    color: #d4ff52 !important;
    border: 2px solid #1a1a1a !important;
    border-radius: 12px !important;
    padding: 14px 0 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    box-shadow: 4px 4px 0 #2563eb !important;
    transition: all 0.15s !important;
    margin-top: 12px !important;
}

div[data-testid="stButton"] > button:hover {
    background: #2563eb !important;
    border-color: #2563eb !important;
    color: #ffffff !important;
    box-shadow: 4px 4px 0 #1a1a1a !important;
    transform: translate(-1px, -1px) !important;
}

div[data-testid="stButton"] > button:active {
    transform: translate(2px, 2px) !important;
    box-shadow: 2px 2px 0 #2563eb !important;
}

/* RESULT CARDS */
.res-spam {
    margin-top: 18px;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.35);
    border-radius: 16px;
    padding: 20px 22px;
    display: flex;
    gap: 14px;
    align-items: flex-start;
}

.res-safe {
    margin-top: 18px;
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.35);
    border-radius: 16px;
    padding: 20px 22px;
    display: flex;
    gap: 14px;
    align-items: flex-start;
}

.res-icon { font-size: 28px; line-height: 1; flex-shrink: 0; }

.res-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 5px;
}

.res-spam .res-title { color: #b91c1c; }
.res-safe .res-title { color: #15803d; }

.res-body {
    font-family: 'Inter', sans-serif;
    font-size: 13.5px;
    font-weight: 400;
    line-height: 1.6;
}

.res-spam .res-body { color: #7f1d1d; }
.res-safe .res-body { color: #166534; }

/* HIDE TEXTAREA LABEL */
div[data-testid="stTextArea"] label { display: none !important; }

/* WARNING */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: 1px solid rgba(37, 99, 235, 0.4) !important;
    background: rgba(37, 99, 235, 0.08) !important;
    color: #1e40af !important;
    font-family: 'Inter', sans-serif !important;
}

/* FOOTER */
.app-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 50px;
    padding-top: 20px;
    border-top: 1px solid rgba(0, 0, 0, 0.08);
}

.footer-brand {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 13px;
    font-weight: 800;
    color: #1a1a1a;
}

.footer-copy {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 400;
    color: #666666;
}
</style>
""", unsafe_allow_html=True)

# NAVBAR
st.markdown("""
<div class="navbar">
  <div class="brand">Spam<span class="brand-accent">Scan</span></div>
  <div class="live-pill"><span class="live-dot"></span>Model Aktif · Naive Bayes</div>
</div>
""", unsafe_allow_html=True)

# MAIN CONTENT - TWO COLUMNS
left, right = st.columns([4, 5], gap="large")

# LEFT COLUMN - INFO
with left:
    st.markdown("""
    <div class="eyebrow">Machine Learning · NLP</div>
    <div class="hero-title">Deteksi<br>Pesan<br><span class="amber">Spam.</span></div>
    <p class="hero-desc">
      Tempelkan pesan mencurigakan dan biarkan model menganalisisnya.
      Didukung Naive Bayes dengan akurasi tinggi.
    </p>
    """, unsafe_allow_html=True)

    # STATISTICS
    st.markdown('<div class="mini-label">Statistik Model</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-num">96%</div>
            <div class="stat-lbl">Akurasi Model</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="stat-card">
            <div class="stat-num">6.3K</div>
            <div class="stat-lbl">Data Training</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-num">NB</div>
            <div class="stat-lbl">Naive Bayes</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="stat-card">
            <div class="stat-num">TF‑IDF</div>
            <div class="stat-lbl">Feature Extraction</div>
        </div>
        """, unsafe_allow_html=True)

    # USAGE STEPS
    st.markdown('<div class="mini-label">Cara Penggunaan</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="step-row">
        <div class="step-num">1</div>
        <div class="step-text">Salin pesan dari WhatsApp, SMS, atau email yang mencurigakan.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="step-row">
        <div class="step-num">2</div>
        <div class="step-text">Tempel teks ke kolom input di sebelah kanan.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="step-row">
        <div class="step-num">3</div>
        <div class="step-text">Klik tombol Analisis dan baca hasilnya.</div>
    </div>
    """, unsafe_allow_html=True)

# RIGHT COLUMN - INPUT
with right:
    st.markdown('<div class="section-label">Teks Pesan</div>', unsafe_allow_html=True)

    message = st.text_area(
        label="pesan",
        height=230,
        placeholder='Tempel atau ketik pesan di sini…\nContoh: "Selamat! Anda memenangkan hadiah Rp 10 juta. Klik tautan untuk klaim."'
    )

    detect = st.button("→ Analisis Pesan Sekarang")

    # RESULT SECTION
    if detect:
        if message.strip() == "":
            st.warning("⚠️ Pesan tidak boleh kosong.")
        else:
            try:
                pred = model.predict(tfidf.transform([preprocess_text(message)]))[0]
                
                if pred == "spam":
                    st.markdown("""
                    <div class="res-spam">
                      <div class="res-icon">🚨</div>
                      <div>
                        <div class="res-title">Pesan Terdeteksi Spam</div>
                        <div class="res-body">Pesan ini memiliki pola spam. Hindari mengklik tautan atau memberikan data pribadi.</div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="res-safe">
                      <div class="res-icon">✅</div>
                      <div>
                        <div class="res-title">Pesan Aman · Non-Spam</div>
                        <div class="res-body">Tidak ditemukan indikasi spam. Pesan ini tampak seperti komunikasi normal dan sah.</div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# FOOTER
st.markdown("""
<div class="app-footer">
  <div class="footer-brand">SpamScan</div>
  <div class="footer-copy">© 2026 · Untuk keperluan edukasi</div>
</div>
""", unsafe_allow_html=True)