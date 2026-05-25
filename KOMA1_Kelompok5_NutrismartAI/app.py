import streamlit as st
import pandas as pd
import pickle
import plotly.graph_objects as go
import numpy as np
import os
import base64
import ast

def get_img_as_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as img_file:
            return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"
    else:
        # Fallback placeholder jika gambar lokal belum dibuat
        return "https://via.placeholder.com/500?text=Gambar+Tidak+Ada"

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="NutriSmart AI | Premium Dashboard",
    page_icon="data/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. INJEKSI CSS PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Font global */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* KUSTOM KARTU (Card UI) */
    .kpi-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        border: 1px solid #f1f5f9;
    }
    
    .mini-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
        border: 1px solid #f1f5f9;
    }

    /* Resep Card Styling */
    .recipe-card {
        background: #ffffff;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 10px;
        border: 1px solid #f1f5f9;
    }
    .recipe-img {
        width: 100%;
        height: 180px;
        object-fit: cover;
    }
    .recipe-content {
        padding: 20px;
    }
    .recipe-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #000000;
        margin-bottom: 5px;
    }
    .flex-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
    }
    .cal-text {
        font-size: 1.5rem;
        font-weight: 800;
        color: #000000;
    }
    .match-badge {
        background-color: #dcfce7;
        color: #000000;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .macro-text {
        font-size: 0.8rem;
        color: #000000;
        font-weight: 500;
        margin-top: 5px;
        margin-bottom: 10px;
    }
    
    /* Menyembunyikan padding default Streamlit pada kolom */
    div[data-testid="column"] {
        padding: 0 0.5rem;
    }

    /* Ubah background menu expander (Prep Time & Details) menjadi putih */
    [data-testid="stExpanderDetails"] {
        background-color: #ffffff !important;
        border-radius: 0 0 8px 8px;
    }
    details {
        background-color: #ffffff;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. FUNGSI LOGIKA SISTEM ---
@st.cache_data
def load_data():
    return pd.read_csv('data/final_recipes.csv')

@st.cache_resource
def load_model():
    with open('models/knn_model.pkl', 'rb') as file:
        return pickle.load(file)

try:
    df = load_data()
    knn_model = load_model()
except FileNotFoundError:
    st.error("Error: Pastikan file data dan model tersedia.")
    st.stop()

def hitung_tdee(berat, tinggi, umur, gender, aktivitas):
    if gender == 'Pria':
        bmr = 88.362 + (13.397 * berat) + (4.799 * tinggi) - (5.677 * umur)
    else:
        bmr = 447.593 + (9.247 * berat) + (3.098 * tinggi) - (4.330 * umur)
    return bmr * aktivitas

def hitung_bmi(berat, tinggi_cm):
    tinggi_m = tinggi_cm / 100
    return berat / (tinggi_m ** 2)

def hitung_skor_kecocokan(kalori_target, kalori_menu):
    selisih = abs(kalori_target - kalori_menu)
    skor = 100 - ((selisih / kalori_target) * 100)
    return max(0.0, min(100.0, skor))


# --- 4. SIDEBAR (PANEL KONTROL KIRI) ---
st.sidebar.image("data/logo.png", use_container_width=True)

st.sidebar.markdown("""
<div style="background-color: #f8fafc; padding: 12px; border-radius: 8px; border-left: 5px solid #3b82f6; margin-bottom: 15px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
    <p style="margin:0; font-weight: 600; color: #000000; font-size: 15px;">Data Personal & Metabolisme</p>
</div>
""", unsafe_allow_html=True)
col_umur, col_gender = st.sidebar.columns(2)
with col_umur:
    umur = st.number_input("Umur", min_value=10, max_value=100, value=35)
with col_gender:
    gender = st.radio("Gender", ["Pria", "Wanita"])

col_berat, col_tinggi = st.sidebar.columns(2)
with col_berat:
    berat = st.number_input("Berat (kg)", min_value=30.0, max_value=150.0, value=60.0, step=0.5)
with col_tinggi:
    tinggi = st.number_input("Tinggi (cm)", min_value=100.0, max_value=220.0, value=170.0, step=0.5)

aktivitas_dict = {
    "Sangat Jarang": 1.2, "Jarang": 1.375, "Sedang": 1.55, "Sering": 1.725
}
aktivitas_label = st.sidebar.selectbox("Tingkat Aktivitas", list(aktivitas_dict.keys()))
aktivitas_val = aktivitas_dict[aktivitas_label]

st.sidebar.divider()

# FITUR 1: TARGET TUBUH
st.sidebar.markdown("""
<div style="background-color: #f8fafc; padding: 12px; border-radius: 8px; border-left: 5px solid #10b981; margin-bottom: 15px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
    <p style="margin:0; font-weight: 600; color: #000000; font-size: 15px;">Target & Preferensi</p>
</div>
""", unsafe_allow_html=True)
target_tubuh = st.sidebar.selectbox("Target Berat Badan", [
    "Turunkan Berat Badan (Defisit)",
    "Pertahankan Berat (Normal)",
    "Naikkan Massa Otot (Surplus)"
])

# FITUR 3 (Bagian 1): INPUT VARIASI MENU
variasi_menu = st.sidebar.number_input("Alternatif Rekomendasi Menu", min_value=1, max_value=3, value=1, help="Ganti angka untuk mencari menu alternatif lain jika Anda kurang cocok dengan hasil pertama.")

alergi_input = st.sidebar.multiselect("Filter Alergi", ["peanut", "milk", "egg", "seafood", "beef"])

st.sidebar.divider()
tombol_analisis = st.sidebar.button("Analisis Kebutuhan Energi", use_container_width=True, type="primary")


# --- 5. TATA LETAK UTAMA (KANAN) ---
st.markdown("<h2 style='font-weight: 800; color: #000000; margin-bottom: 20px;'>Dashboard Kesehatan Pribadi Anda</h2>", unsafe_allow_html=True)

# Kalkulasi TDEE Dasar (selalu hitung, tapi gunakan 0 jika belum diklik)
tdee_dasar = hitung_tdee(berat, tinggi, umur, gender, aktivitas_val)

# LOGIKA FITUR 1: Penyesuaian Kalori berdasarkan Target
if "Turunkan" in target_tubuh:
    kalori_modifikasi = -500
    estimasi_berat_per_hari = -0.065
elif "Naikkan" in target_tubuh:
    kalori_modifikasi = 300
    estimasi_berat_per_hari = 0.039
else:
    kalori_modifikasi = 0
    estimasi_berat_per_hari = 0

tdee_final = tdee_dasar + kalori_modifikasi if tombol_analisis else 0
target_sekali_makan = (tdee_final / 3) if tombol_analisis else 0
bmi = hitung_bmi(berat, tinggi) if tombol_analisis else 0

st.markdown("<h4 style='font-weight: 600; color: #000000; margin-top: 10px;'>Profil Metabolik & Target Kalori</h4>", unsafe_allow_html=True)

# BARIS 1: 3 Kolom untuk Profil Metabolik
col1, col2, col3 = st.columns([1.2, 0.8, 1])

# 5A. Grafik TDEE (Gauge Chart)
with col1:
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = int(tdee_final),
        title = {'text': "Target Kalori Harian<br><span style='font-size:0.8em;color:black;font-weight:600'>Sesuai Goal Tubuh Anda</span>"},
        gauge = {
            'axis': {'range': [None, 4000], 'visible': False},
            'bar': {'color': "#0f766e"},
            'bgcolor': "#e2e8f0",
            'shape': "angular"
        }
    ))
    fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=10), paper_bgcolor="white", font=dict(color="#000000"))
    
    st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

# 5B. Kotak Angka BMI dan Target Porsi
with col2:
    st.markdown(f"""
        <div class='mini-card'>
            <span style='color: #000000; font-size: 0.9rem; font-weight: 600;'>BMI Anda</span><br>
            <span style='color: #000000; font-size: 1.8rem; font-weight: 800;'>{bmi:.1f}</span>
        </div>
        <div class='mini-card'>
            <span style='color: #000000; font-size: 0.9rem; font-weight: 600;'>Target Porsi Sekali Makan</span><br>
            <span style='color: #000000; font-size: 1.8rem; font-weight: 800;'>{target_sekali_makan:.0f} kkal</span>
        </div>
    """, unsafe_allow_html=True)

# 5C. Grafik Macro Split
with col3:
    labels = ['Protein', 'Karbohidrat', 'Lemak']
    values = [30, 50, 20]
    colors = ['#0f766e', '#14b8a6', '#99f6e4']
    
    fig_donut = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, marker=dict(colors=colors), textfont=dict(color="#000000"))])
    fig_donut.update_layout(
        title_text="Macro Split Target",
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="white",
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=0.9, font=dict(color="#000000")),
        font=dict(color="#000000")
    )
    
    st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

# --- 6. BAGIAN REKOMENDASI MENU ---
st.markdown("<h4 style='font-weight: 600; color: #000000; margin-top: 30px; margin-bottom: 10px;'>Rekomendasi Menu Hari Ini</h4>", unsafe_allow_html=True)

if tombol_analisis:
    df_aman = df.copy()
    if alergi_input:
        for bahan in alergi_input:
            df_aman = df_aman[~df_aman['ingredients'].str.contains(bahan, case=False, na=False)]

    # Memastikan data cukup untuk variasi sampai tingkat 3 (butuh min 9 data)
    if len(df_aman) >= 9:
        from sklearn.neighbors import NearestNeighbors
        # Menarik 10 tetangga terdekat sekaligus agar bisa divariasikan
        knn_instan = NearestNeighbors(n_neighbors=10, algorithm='auto')
        knn_instan.fit(df_aman[['calories']].values)
        jarak, indeks = knn_instan.kneighbors([[target_sekali_makan]])
        
        col_pagi, col_siang, col_malam = st.columns(3)
        waktu = ["Menu Pagi (Sarapan)", "Menu Siang", "Menu Malam"]
        
        gambar_makanan = [
            get_img_as_base64("data/makananpagi.jpg"),
            get_img_as_base64("data/makanansiang.jpg"),
            get_img_as_base64("data/makananmalam.jpg")
        ]

        kolom_wadah = [col_pagi, col_siang, col_malam]

        # FITUR 3 (Bagian 2): Pergeseran Indeks Array KNN berdasarkan variasi
        offset_variasi = (variasi_menu - 1) * 3

        for i in range(3):
            with kolom_wadah[i]:
                # Mengambil index yang sudah digeser oleh slider variasi
                index_aktual = offset_variasi + i
                baris_data = df_aman.iloc[indeks[0][index_aktual]]
                
                kalori_menu = baris_data['calories']
                nama_masakan = str(baris_data['name']).title()
                
                if len(nama_masakan) > 22:
                    nama_masakan = nama_masakan[:22] + "..."
                    
                skor = hitung_skor_kecocokan(target_sekali_makan, kalori_menu)
                
                st.markdown(f"<div style='font-weight:600; color:#000000; margin-bottom: 8px;'>{waktu[i]}</div>", unsafe_allow_html=True)
                
                # Mendapatkan data macro dengan nilai default 0 jika tidak ada di dataset
                protein = baris_data.get('protein', '-')
                karbo = baris_data.get('carbohydrates', '-')
                
                # HTML Kustom + FITUR 2 (Rincian Makro di bawah judul)
                st.markdown(f"""
                    <div class='recipe-card'>
                        <img src='{gambar_makanan[i]}' class='recipe-img'>
                        <div class='recipe-content'>
                            <div class='recipe-title'>{nama_masakan}</div>
                            <div class='macro-text'>Protein: {protein}g &bull; Karbo: {karbo}g</div>
                            <div class='flex-row'>
                                <div class='cal-text'>{kalori_menu:.0f} kkal</div>
                                <div class='match-badge'>{skor:.1f}% Match</div>
                            </div>
                            <div style='background:#14b8a6; height:6px; border-radius:10px; width:{skor}%; margin-top:10px;'></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                with st.expander("🕒 Prep Time & Details"):
                    st.write(f"**Prep Time:** {baris_data['minutes']} Menit")
                    st.write("**Ingredients:**", str(baris_data['ingredients']).capitalize())
                    steps_raw = baris_data.get('steps', '[]')
                    steps_list = []

                    if isinstance(steps_raw, list):
                        steps_list = steps_raw
                    elif isinstance(steps_raw, str) and steps_raw.strip():
                        try:
                            parsed_steps = ast.literal_eval(steps_raw)
                            if isinstance(parsed_steps, list):
                                steps_list = parsed_steps
                        except (ValueError, SyntaxError):
                            steps_list = []

                    if steps_list:
                        langkah_rapi = "\n".join(
                            f"{idx}. {str(step).strip().capitalize()}"
                            for idx, step in enumerate(steps_list, start=1)
                            if str(step).strip()
                        )
                        if langkah_rapi:
                            st.write("**Cooking Steps:**")
                            st.write(langkah_rapi)
    else:
        st.error("Data terlalu sedikit. Kurangi filter alergi Anda.")
else:
    # Tampilkan placeholder saat belum diklik
    col_pagi, col_siang, col_malam = st.columns(3)
    waktu = ["Menu Pagi (Sarapan)", "Menu Siang", "Menu Malam"]
    gambar_makanan = [
        get_img_as_base64("data/makananpagi.jpg"),
        get_img_as_base64("data/makanansiang.jpg"),
        get_img_as_base64("data/makananmalam.jpg")
    ]
    
    kolom_wadah = [col_pagi, col_siang, col_malam]
    
    for i in range(3):
        with kolom_wadah[i]:
            st.markdown(f"<div style='font-weight:600; color:#000000; margin-bottom: 8px;'>{waktu[i]}</div>", unsafe_allow_html=True)
            st.markdown(f"""
                <div class='recipe-card'>
                    <img src='{gambar_makanan[i]}' class='recipe-img'>
                    <div class='recipe-content'>
                        <div class='recipe-title'>Menu Kosong</div>
                        <div class='macro-text'>Protein: - &bull; Karbo: -</div>
                        <div class='flex-row'>
                            <div class='cal-text'>0 kkal</div>
                            <div class='match-badge'>0.0% Match</div>
                        </div>
                        <div style='background:#14b8a6; height:6px; border-radius:10px; width:0%; margin-top:10px;'></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- 5.5 LOGIKA FITUR 4: GRAFIK PROYEKSI BERAT BADAN ---
st.markdown("<h4 style='font-weight: 600; color: #000000; margin-top: 30px; margin-bottom: 10px;'>Proyeksi Berat Badan 30 Hari Ke Depan</h4>", unsafe_allow_html=True)
st.markdown("<div class='kpi-card' style='padding: 10px 20px;'>", unsafe_allow_html=True)

hari = list(range(1, 32))
proyeksi_berat = [berat + (d * estimasi_berat_per_hari) for d in hari] if tombol_analisis else [berat for d in hari]

fig_line = go.Figure()
fig_line.add_trace(go.Scatter(x=hari, y=proyeksi_berat, mode='lines', line=dict(color='#14b8a6', width=4), name='Berat (kg)'))
fig_line.update_layout(
    height=250, 
    margin=dict(l=20, r=20, t=20, b=20), 
    paper_bgcolor="white", 
    plot_bgcolor="white",
    font=dict(color="#000000"),
    xaxis=dict(showgrid=True, gridcolor='#f1f5f9', title=dict(text="Hari", font=dict(color="#000000")), tickfont=dict(color="#000000")),
    yaxis=dict(showgrid=True, gridcolor='#f1f5f9', title=dict(text="Berat Badan (kg)", font=dict(color="#000000")), tickfont=dict(color="#000000"))
)
st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})
st.markdown("</div>", unsafe_allow_html=True)