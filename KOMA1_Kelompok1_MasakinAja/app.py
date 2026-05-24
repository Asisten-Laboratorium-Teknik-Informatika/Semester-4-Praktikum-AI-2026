# =============================================================================
# Masakin Apa? — v3 (Top-K Detection + Expandable Recipe + Pagination)
# =============================================================================

import streamlit as st
import numpy as np
import pandas as pd
import time
from PIL import Image

st.set_page_config(
    page_title="Masakin Apa?",
    page_icon="🍳",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# CSS
# =============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:#0D0D0D; --bg-card:#161616; --bg-elevated:#1E1E1E;
    --orange:#FF6B35; --orange-dim:#FF6B3520; --orange-glow:#FF6B3540;
    --text:#F0EDE8; --text-2:#A09890; --text-muted:#605850;
    --border:#2A2A2A; --border-orange:#FF6B3560;
    --success:#4CAF7D; --warning:#FFB347;
    --r-md:16px; --r-lg:24px;
    --shadow:0 8px 32px rgba(0,0,0,0.4);
    --shadow-orange:0 8px 32px rgba(255,107,53,0.15);
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background-color:var(--bg);color:var(--text);}
.main .block-container{padding:0 1rem 4rem 1rem;max-width:780px;}
#MainMenu,footer,header{visibility:hidden;}
.stDeployButton{display:none;}

/* HERO */
/* HERO */
.hero{
    text-align:center;
    padding:3.5rem 1rem 2rem;

    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
}

.hero-badge{
    display:inline-flex;
    align-items:center;
    gap:6px;
    background:var(--orange-dim);
    border:1px solid var(--border-orange);
    color:var(--orange);
    font-size:0.72rem;
    font-weight:600;
    letter-spacing:0.12em;
    text-transform:uppercase;
    padding:5px 14px;
    border-radius:999px;
    margin-bottom:1.2rem;
}

.hero-title{
    font-family:'Playfair Display',serif;
    font-size:clamp(2.8rem,8vw,4.5rem);
    font-weight:900;
    line-height:1.05;
    color:var(--text);
    margin:0 0 0.6rem;
    letter-spacing:-0.02em;
}

.hero-title span{
    color:var(--orange);
}

.hero-subtitle{
    font-size:1.05rem;
    color:var(--text-2);
    font-weight:300;
    line-height:1.6;
    max-width:460px;
    margin:0 auto 2rem;
    text-align:center;
}

.hero-divider{
    width:48px;
    height:3px;
    background:linear-gradient(90deg,var(--orange),transparent);
    border-radius:2px;
    margin:0 auto;
}

.slabel{font-size:0.7rem;font-weight:600;letter-spacing:0.15em;text-transform:uppercase;color:var(--text-muted);margin-bottom:0.75rem;padding-left:2px;}
.or-div{display:flex;align-items:center;gap:1rem;margin:1.4rem 0;color:var(--text-muted);font-size:0.8rem;font-weight:500;letter-spacing:0.1em;text-transform:uppercase;}
.or-div::before,.or-div::after{content:'';flex:1;height:1px;background:var(--border);}

/* FILE UPLOADER */
[data-testid="stFileUploader"]{background:var(--bg-card)!important;border:2px dashed #2E2E2E!important;border-radius:var(--r-lg)!important;padding:1.5rem!important;transition:all 0.25s ease!important;}
[data-testid="stFileUploader"]:hover{border-color:var(--orange)!important;background:var(--orange-dim)!important;}
[data-testid="stFileUploader"] label{color:var(--text)!important;font-family:'DM Sans',sans-serif!important;}

/* TEXT INPUT */
[data-testid="stTextInput"] input{background:var(--bg-elevated)!important;border:1px solid var(--border)!important;border-radius:var(--r-md)!important;color:var(--text)!important;font-family:'DM Sans',sans-serif!important;font-size:0.95rem!important;padding:0.75rem 1rem!important;}
[data-testid="stTextInput"] input:focus{border-color:var(--orange)!important;box-shadow:0 0 0 3px var(--orange-dim)!important;}
[data-testid="stTextInput"] input::placeholder{color:var(--text-muted)!important;}
[data-testid="stTextInput"] label{color:var(--text-2)!important;font-size:0.85rem!important;font-weight:500!important;}

/* BUTTONS */
.stButton>button{background:var(--orange)!important;color:#0D0D0D!important;border:none!important;border-radius:var(--r-md)!important;font-family:'DM Sans',sans-serif!important;font-size:0.95rem!important;font-weight:600!important;padding:0.75rem 2rem!important;width:100%!important;transition:all 0.2s ease!important;}
.stButton>button:hover{background:#FF8355!important;box-shadow:0 6px 24px rgba(255,107,53,0.35)!important;transform:translateY(-1px)!important;}

/* IMAGE */
[data-testid="stImage"] img{border-radius:var(--r-md)!important;border:1px solid var(--border)!important;}

/* PROGRESS BAR */
[data-testid="stProgress"]>div>div{background:linear-gradient(90deg,var(--orange),#FF9F1C)!important;border-radius:999px!important;}
[data-testid="stProgress"]>div{background:var(--bg-elevated)!important;border-radius:999px!important;}

/* DETECTION CARD */
.det-card{background:var(--bg-elevated);border:1px solid var(--border);border-radius:var(--r-md);padding:1.2rem 1.4rem;margin-bottom:0.8rem;display:flex;align-items:center;justify-content:space-between;gap:1rem;}
.det-lbl{font-size:0.7rem;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;color:var(--text-muted);margin-bottom:2px;}
.det-name{font-size:1.1rem;font-weight:600;color:var(--text);}
.det-score{font-family:'Playfair Display',serif;font-size:1.6rem;font-weight:700;color:var(--orange);white-space:nowrap;}
.badge-ok{display:inline-flex;align-items:center;gap:5px;background:#4CAF7D20;color:#4CAF7D;font-size:0.72rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;padding:3px 10px;border-radius:999px;border:1px solid #4CAF7D40;margin-top:6px;}
.badge-warn{display:inline-flex;align-items:center;gap:5px;background:#FFB34720;color:var(--warning);font-size:0.72rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;padding:3px 10px;border-radius:999px;border:1px solid #FFB34740;margin-top:6px;}

/* TOP-K KANDIDAT */
.topk-wrap{margin:1rem 0;}
.topk-title{font-size:0.7rem;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;color:var(--text-muted);margin-bottom:0.75rem;}
.topk-item{background:var(--bg-elevated);border:1px solid var(--border);border-radius:var(--r-md);padding:0.9rem 1.2rem;margin-bottom:0.5rem;display:flex;align-items:center;justify-content:space-between;cursor:pointer;transition:all 0.2s;}
.topk-item:hover,.topk-item.selected{border-color:var(--orange);background:var(--orange-dim);}
.topk-name{font-size:0.95rem;font-weight:600;color:var(--text);}
.topk-conf{font-size:0.8rem;color:var(--text-2);}
.topk-bar-wrap{flex:1;margin:0 1rem;height:4px;background:var(--border);border-radius:999px;overflow:hidden;}
.topk-bar{height:100%;background:var(--orange);border-radius:999px;}

/* WARNING BOX */
.warnbox{background:#FFB34710;border:1px solid #FFB34740;border-radius:var(--r-md);padding:1rem 1.2rem;display:flex;align-items:flex-start;gap:0.75rem;margin-bottom:1.2rem;}
.warnbox-title{font-size:0.85rem;font-weight:600;color:var(--warning);margin-bottom:2px;}
.warnbox-text{font-size:0.82rem;color:var(--text-2);line-height:1.5;}

/* PROTEIN */
.protein-header{background:var(--bg-card);border:1px solid var(--border-orange);border-radius:var(--r-lg);padding:1.4rem 1.6rem;margin:1.2rem 0 0.8rem;box-shadow:var(--shadow-orange);}
.protein-title-label{font-size:0.7rem;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;color:var(--orange);margin-bottom:0.5rem;}
.protein-title{font-size:1rem;font-weight:600;color:var(--text);margin-bottom:0.3rem;}
.protein-sub{font-size:0.85rem;color:var(--text-2);}

/* RECIPE CARD */
.recipe-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--r-lg);margin-bottom:0.8rem;overflow:hidden;box-shadow:var(--shadow);transition:all 0.25s ease;}
.recipe-card:hover{border-color:var(--border-orange);box-shadow:var(--shadow-orange);}
.rc-header{padding:1.2rem 1.4rem 0.8rem;display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;}
.rc-rank{font-family:'Playfair Display',serif;font-size:2rem;font-weight:900;color:var(--orange);opacity:0.2;line-height:1;flex-shrink:0;}
.rc-title{font-family:'Playfair Display',serif;font-size:1.05rem;font-weight:700;color:var(--text);line-height:1.3;flex:1;}
.rc-tags{display:flex;gap:0.5rem;flex-wrap:wrap;margin-top:5px;}
.rc-tag{display:inline-flex;align-items:center;gap:3px;background:var(--bg-elevated);color:var(--text-2);font-size:0.72rem;font-weight:500;padding:2px 9px;border-radius:999px;border:1px solid var(--border);}

/* EXPANDER OVERRIDE */
[data-testid="stExpander"]{background:var(--bg-elevated)!important;border:1px solid var(--border)!important;border-radius:var(--r-md)!important;margin:0 1.4rem 1rem!important;}
[data-testid="stExpander"] summary{color:var(--orange)!important;font-weight:600!important;font-size:0.85rem!important;}
[data-testid="stExpander"] p,[data-testid="stExpander"] li{color:var(--text-2)!important;font-size:0.85rem!important;line-height:1.7!important;}

/* PAGINATION */
.page-info{text-align:center;font-size:0.82rem;color:var(--text-muted);margin:0.5rem 0 1rem;}

/* EMPTY */
.empty{text-align:center;padding:3rem 1rem;color:var(--text-muted);}
.empty-icon{font-size:3.5rem;margin-bottom:1rem;display:block;opacity:0.4;}
.empty-text{font-size:0.9rem;line-height:1.6;}

/* FOOTER */
.footer{text-align:center;padding:2.5rem 1rem 1rem;color:var(--text-muted);font-size:0.78rem;border-top:1px solid var(--border);margin-top:3rem;}
.footer strong{color:var(--text-2);}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# LOAD MODEL & DATA
# =============================================================================

@st.cache_resource
def load_ai_model():
    from tensorflow.keras.models import load_model
    return load_model("model/model_masakinapa_best.h5")

@st.cache_data
def load_recipes():
    return pd.read_csv("resep_clean.csv")

model    = load_ai_model()
df_resep = load_recipes()

class_names = [
    "banana","bell pepper","bitter gourd","cabbage","carrot","cauliflower",
    "chilli pepper","corn","cucumber","egg","eggplant","garlic","ginger",
    "green beans","jackfruit","jalepeno","kangkung","lemon","long beans",
    "mango","mushroom","onion","orange","paprika","peas","pineapple",
    "potato","protein","raddish","sawi","shrimp","spinach","sweetcorn",
    "sweetpotato","tauge","tempe","tofu","tomato","watermelon"
]

translate_label = {
    "banana":"pisang","bell pepper":"paprika","bitter gourd":"pare",
    "cabbage":"kubis","carrot":"wortel","cauliflower":"kembang kol",
    "chilli pepper":"cabai","corn":"jagung","cucumber":"timun",
    "egg":"telur","eggplant":"terong","garlic":"bawang putih",
    "ginger":"jahe","green beans":"buncis","jackfruit":"nangka",
    "jalepeno":"cabai hijau","kangkung":"kangkung","lemon":"lemon",
    "long beans":"kacang panjang","mango":"mangga","mushroom":"jamur",
    "onion":"bawang merah","orange":"jeruk","paprika":"paprika",
    "peas":"kacang polong","pineapple":"nanas","potato":"kentang",
    "protein":"daging","raddish":"lobak","sawi":"sawi","shrimp":"udang",
    "spinach":"bayam","sweetcorn":"jagung manis","sweetpotato":"ubi",
    "tauge":"tauge","tempe":"tempe","tofu":"tahu","tomato":"tomat",
    "watermelon":"semangka",
}

PROTEIN_OPTIONS = {
    "Ayam":("🍗","ayam"),"Daging Sapi":("🥩","daging sapi"),"Ikan":("🐟","ikan"),
}

JENIS_IKAN = [
    "lele",
    "nila",
    "tongkol",
    "patin",
    "tuna",
    "bandeng"
]

RECIPES_PER_PAGE = 5


# =============================================================================
# FUNGSI
# =============================================================================

def predict_topk(image, k=3):
    """Return top-k prediksi: [(label_en, label_id, confidence), ...]"""
    img = image.resize((224, 224))
    arr = np.array(img) / 255.0
    arr = np.expand_dims(arr, axis=0)
    preds = model.predict(arr, verbose=0)[0]
    top_idx = np.argsort(preds)[::-1][:k]
    results = []
    for idx in top_idx:
        en = class_names[idx]
        results.append((en, translate_label[en], float(preds[idx])))
    return results


def cari_resep_semua(bahan_input):
    """Kembalikan SEMUA resep yang cocok, diurutkan skor + likes."""
    hasil = []
    for _, row in df_resep.iterrows():
        bahan_resep = str(row['Ingredients']).lower()
        skor = sum(1 for b in bahan_input if b.lower() in bahan_resep)
        if skor > 0:
            hasil.append({
                "nama":   row['Title'],
                "bahan":  row['Ingredients'],
                "langkah":row['Steps'],
                "likes":  int(row.get('Loves', 0)),
                "skor":   skor,
                "url":    row.get('URL', ''),
            })
    return sorted(hasil, key=lambda x: (x['skor'], x['likes']), reverse=True)


def fmt_bahan_list(raw):
    """Format bahan jadi list bersih."""
    parts = [p.strip() for p in raw.replace('--','|').split('|') if len(p.strip()) > 2]
    return parts


def fmt_langkah_list(raw):
    """Format langkah jadi list bernomor."""
    parts = [p.strip() for p in raw.replace('--','\n').split('\n') if p.strip()]
    return parts


# =============================================================================
# SESSION STATE
# =============================================================================

defaults = {
    'step':'input',
    'topk_results':[],        # list of (en, id, conf)
    'selected_label_en':None,
    'selected_label_id':None,
    'selected_conf':0.0,
    'query':'',
    'all_recipes':[],
    'page':0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# =============================================================================
# HERO
# =============================================================================

st.markdown("""
<div class="hero">
    <div class="hero-badge">✦ Ayoo kreasikan masakanmu</div>
    <h1 class="hero-title">Masakin <span>Apa?</span></h1>
    <p class="hero-subtitle">Upload foto bahan makanan dan temukan resep masakan Indonesia terbaik dengan bantuan AI</p>
    <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# STEP 1 — INPUT
# =============================================================================

if st.session_state.step == 'input':

    st.markdown('<div class="slabel">📷 Upload Foto Bahan</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drag & drop foto bahan makanan di sini",
        type=["jpg","jpeg","png"],
    )

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, use_container_width=True)

        if st.button("🔍 Deteksi Bahan dengan AI", key="btn_detect"):
            with st.spinner("AI sedang menganalisis gambar..."):
                topk = predict_topk(image, k=3)

            st.session_state.topk_results = topk
            st.session_state.step = 'detected'
            st.rerun()

    st.markdown('<div class="or-div">atau</div>', unsafe_allow_html=True)
    st.markdown('<div class="slabel">✏️ Ketik Nama Bahan</div>', unsafe_allow_html=True)

    bahan_manual = st.text_input(
        "Nama bahan", placeholder="contoh: ayam, cabai, bawang putih",
        label_visibility="collapsed", key="input_manual",
    )
    if st.button("🍽️ Cari Resep", key="btn_manual"):
        if bahan_manual.strip():
            st.session_state.query = bahan_manual.strip()
            st.session_state.page  = 0
            st.session_state.step  = 'recipes'
            st.rerun()
        else:
            st.warning("Ketik dulu nama bahan yang ingin dicari.")


# =============================================================================
# STEP 2 — HASIL DETEKSI (TOP-3 KANDIDAT)
# =============================================================================

elif st.session_state.step == 'detected':
    topk = st.session_state.topk_results
    top1_en, top1_id, top1_conf = topk[0]
    is_ok = top1_conf >= 0.50

    st.markdown('<div class="slabel">🤖 Hasil Deteksi AI</div>', unsafe_allow_html=True)

    # Hasil utama
    badge = '<span class="badge-ok">✓ Terdeteksi</span>' if is_ok else '<span class="badge-warn">⚠ Confidence Rendah</span>'
    st.markdown(f"""
    <div class="det-card">
        <div>
            <div class="det-lbl">Prediksi Utama</div>
            <div class="det-name">{top1_id.title()}</div>
            {badge}
        </div>
        <div class="det-score">{round(top1_conf*100,1)}%</div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(top1_conf)

    if not is_ok:
        st.markdown("""
        <div class="warnbox">
            <div style="font-size:1.2rem;flex-shrink:0;margin-top:1px">⚠️</div>
            <div>
                <div class="warnbox-title">Confidence Rendah</div>
                <div class="warnbox-text">AI kurang yakin dengan hasil ini. Pilih kandidat lain di bawah, atau gunakan input manual.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── TOP-3 KANDIDAT — user bisa koreksi ──
    if len(topk) > 1:
        st.markdown("""
        <div class="topk-wrap">
            <div class="topk-title">
            🧠 AI menemukan beberapa kemungkinan bahan
            </div>
                
        </div>
                    
        """, unsafe_allow_html=True)

        st.caption("Pilih bahan yang paling mirip dengan gambar yang kamu upload.")
        
        for i, (en, label_id, conf) in enumerate(topk):
            conf_pct = round(conf * 100, 1)
            bar_w    = round(conf * 100)
            if st.button(
                f"{label_id.title()}",
                key=f"topk_{i}",
            ):
                st.session_state.selected_label_en = en
                st.session_state.selected_label_id = label_id
                st.session_state.selected_conf     = conf

                if en == "protein":
                    st.session_state.step = 'protein'
                else:
                    st.session_state.query = label_id
                    st.session_state.page  = 0
                    st.session_state.step  = 'recipes'
                st.rerun()

    # Protein flow jika top1 protein
    if top1_en == "protein" and len(topk) == 1:
        st.session_state.step = 'protein'
        st.rerun()

    # Kembali / input manual
    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Coba Lagi", key="btn_retry"):
            st.session_state.step = 'input'
            st.rerun()
    with c2:
        override = st.text_input(
            "Atau ketik manual", placeholder="nama bahan...",
            label_visibility="collapsed", key="override",
        )
        if st.button("Cari Manual →", key="btn_override"):
            if override.strip():
                st.session_state.query = override.strip()
                st.session_state.page  = 0
                st.session_state.step  = 'recipes'
                st.rerun()


# =============================================================================
# STEP 2b — PROTEIN FLOW
# =============================================================================

elif st.session_state.step == 'protein':
    st.markdown("""
    <div class="protein-header">
        <div class="protein-title-label">🥩 Protein Terdeteksi</div>
        <div class="protein-title">Pilih jenis protein kamu</div>
        <div class="protein-sub">Tentukan jenisnya agar rekomendasi lebih akurat.</div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(len(PROTEIN_OPTIONS))
    for col, (nama, (icon, query)) in zip(cols, PROTEIN_OPTIONS.items()):
        with col:
            if st.button(f"{icon} {nama}", key=f"prot_{nama}"):
                if query == "ikan":
                    st.session_state.step = 'pilih_ikan'
                else:
                    st.session_state.query = query
                    st.session_state.page  = 0
                    st.session_state.step  = 'recipes'

                st.rerun()

    if st.button("← Kembali", key="btn_back_protein"):
        st.session_state.step = 'detected'
        st.rerun()


# =============================================================================
# STEP 2c — PILIH JENIS IKAN
# =============================================================================

elif st.session_state.step == 'pilih_ikan':

    st.markdown("""
    <div class="protein-header">
        <div class="protein-title-label">🐟 Jenis Ikan</div>
        <div class="protein-title">Pilih jenis ikan kamu</div>
        <div class="protein-sub">
            Pilih jenis ikan agar rekomendasi resep lebih spesifik.
        </div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(2)

    for i, ikan in enumerate(JENIS_IKAN):

        with cols[i % 2]:

            if st.button(f"🐟 {ikan.title()}", key=f"ikan_{ikan}"):

                st.session_state.query = ikan
                st.session_state.page  = 0
                st.session_state.step  = 'recipes'

                st.rerun()

    if st.button("← Kembali", key="btn_back_ikan"):

        st.session_state.step = 'protein'
        st.rerun()


# =============================================================================
# STEP 3 — REKOMENDASI RESEP (SEMUA + PAGINATION)
# =============================================================================

elif st.session_state.step == 'recipes':
    query = st.session_state.query

    st.markdown('<div class="slabel">🍳 Rekomendasi Resep</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:0.85rem;color:#A09890;margin-bottom:1.2rem;">
        Menampilkan resep untuk bahan:
        <span style="color:#FF6B35;font-weight:600;">{query}</span>
    </div>
    """, unsafe_allow_html=True)

    # Cari resep jika belum ada atau query baru
    if not st.session_state.all_recipes:
        with st.spinner("Mencari resep terbaik..."):
            bahan_list = [b.strip() for b in query.split(',')]
            st.session_state.all_recipes = cari_resep_semua(bahan_list)

    all_r  = st.session_state.all_recipes
    total  = len(all_r)
    page   = st.session_state.page
    pages  = max(1, -(-total // RECIPES_PER_PAGE))  # ceiling division
    start  = page * RECIPES_PER_PAGE
    end    = start + RECIPES_PER_PAGE
    shown  = all_r[start:end]

    if not all_r:
        st.markdown("""
        <div class="empty">
            <span class="empty-icon">🍽️</span>
            <div class="empty-text">Belum ditemukan resep yang cocok.<br>Coba kata kunci lain.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="page-info">Menampilkan {start+1}–{min(end,total)} dari <strong>{total}</strong> resep</div>', unsafe_allow_html=True)

        for i, r in enumerate(shown, start + 1):
            bahan_list_fmt  = fmt_bahan_list(r['bahan'])
            langkah_list_fmt = fmt_langkah_list(r['langkah'])

            url_html = (
                f'<a class="rc-link" href="https://www.cookpad.com{r["url"]}" target="_blank">Buka Resep Asli ↗</a>'
                if r.get('url') and str(r.get('url')) not in ('nan','','None')
                else '<span style="color:var(--text-muted);font-size:0.82rem;">URL tidak tersedia</span>'
            )

            # Header card
            st.markdown(f"""
            <div class="recipe-card">
                <div class="rc-header">
                    <div>
                        <div class="rc-title">{r['nama']}</div>
                        <div class="rc-tags">
                            <span class="rc-tag">❤️ {r['likes']} likes</span>
                            <span class="rc-tag">🎯 {r['skor']} bahan cocok</span>
                        </div>
                    </div>
                    <div class="rc-rank">#{i}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Expander detail — native Streamlit, ringan
            with st.expander("📋 Lihat Detail Resep"):
                st.markdown("**🧂 Bahan-bahan:**")
                for b in bahan_list_fmt:
                    st.markdown(f"- {b}")

                st.markdown("---")
                st.markdown("**👨‍🍳 Langkah Memasak:**")
                for j, s in enumerate(langkah_list_fmt, 1):
                    st.markdown(f"**{j}.** {s}")

                st.markdown("---")
                st.markdown(url_html, unsafe_allow_html=True)

        # ── Pagination ──
        st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
        if pages > 1:
            pc1, pc2, pc3 = st.columns([1, 2, 1])
            with pc1:
                if page > 0:
                    if st.button("← Sebelumnya", key="btn_prev"):
                        st.session_state.page -= 1
                        st.rerun()
            with pc2:
                st.markdown(
                    f'<div style="text-align:center;font-size:0.82rem;color:var(--text-muted);padding-top:0.75rem">Halaman {page+1} / {pages}</div>',
                    unsafe_allow_html=True
                )
            with pc3:
                if page < pages - 1:
                    if st.button("Berikutnya →", key="btn_next"):
                        st.session_state.page += 1
                        st.rerun()

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
    if st.button("← Cari Resep Lain", key="btn_back"):
        st.session_state.step        = 'input'
        st.session_state.all_recipes = []
        st.session_state.query       = ''
        st.session_state.page        = 0
        st.rerun()


# =============================================================================
# FOOTER
# =============================================================================

st.markdown("""
<div class="footer">
    <strong>Masakin Apa?</strong> · Resep Indonesia
</div>
""", unsafe_allow_html=True)
