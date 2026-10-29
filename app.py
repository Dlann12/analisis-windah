import streamlit as pd_st
import streamlit as st
import pandas as pd
from pathlib import Path
from config.settings import PROCESSED_VIDEOS_PATH, PROCESSED_COMMENTS_PATH, SENTIMENT_REPORT_PATH, POPULARITY_REPORT_PATH
import json

st.set_page_config(
    page_title="Windah Basudara YouTube AI Analytics",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #94A3B8;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 1.2rem;
        text-align: center;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #38BDF8;
    }
    .kpi-label {
        font-size: 0.85rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.3rem;
    }
    .alert-box {
        background-color: #1E293B;
        border-left: 4px solid #DC2626;
        padding: 1rem 1.2rem;
        border-radius: 4px;
        margin-top: 1.5rem;
        font-size: 0.88rem;
        color: #CBD5E1;
    }
</style>
""", unsafe_allow_html=True)


def load_dataset_stats():
    if not PROCESSED_VIDEOS_PATH.exists():
        from src.preprocessing.clean_videos import clean_videos_data
        clean_videos_data()

    df_v = pd.read_csv(PROCESSED_VIDEOS_PATH)
    total_videos = len(df_v)
    total_views = int(df_v["view_count"].sum())
    avg_views = int(df_v["view_count"].mean())
    avg_er = float(df_v["engagement_rate"].mean())

    f1_sentiment = 0.0
    if SENTIMENT_REPORT_PATH.exists():
        with open(SENTIMENT_REPORT_PATH, "r", encoding="utf-8") as f:
            sent_rep = json.load(f)
            f1_sentiment = sent_rep.get("macro_f1", 0.0)

    mae_pop = 0
    if POPULARITY_REPORT_PATH.exists():
        with open(POPULARITY_REPORT_PATH, "r", encoding="utf-8") as f:
            pop_rep = json.load(f)
            mae_pop = pop_rep.get("models", {}).get("random_forest", {}).get("mae", 0)

    return total_videos, total_views, avg_views, avg_er, f1_sentiment, mae_pop


total_v, total_views, avg_views, avg_er, f1_score, rf_mae = load_dataset_stats()

# Header
st.markdown('<div class="main-title">🎮 Windah Basudara YouTube AI Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Sistem analisis performa video, sentimen penonton, dan prediksi machine learning kanal YouTube Windah Basudara.</div>', unsafe_allow_html=True)

# KPI Metrics Grid
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_v}</div>
        <div class="kpi-label">Video Terindeks</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_views / 1e6:.1f} Juta</div>
        <div class="kpi-label">Total Views Sampel</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{avg_views / 1e6:.2f}M</div>
        <div class="kpi-label">Rata-rata Views / Video</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{avg_er:.2f}%</div>
        <div class="kpi-label">Rata-rata Engagement</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Overview Section
left_col, right_col = st.columns([3, 2])

with left_col:
    st.subheader("📌 Gambaran Umum Sistem")
    st.write("""
    Aplikasi ini dirancang sesuai **Product Requirements Document (PRD) v1.0** untuk menganalisis ekosistem konten YouTube Windah Basudara:
    
    1. **Overview & Channel Metrics**: Menampilkan ringkasan channel, distribusi views, dan tren upload.
    2. **Video Performance Analytics**: Eksplorasi ranking video berdasarkan views, likes, dan engagement rate.
    3. **Comment Sentiment Analysis**: Klasifikasi sentimen komentar (Positif, Netral, Negatif) menggunakan TF-IDF dan Logistic Regression.
    4. **ML Popularity Prediction**: Memperkirakan potensi views video baru berdasarkan judul, durasi, topik, dan jam tayang menggunakan Random Forest Regressor.
    5. **Model Performance**: Transparansi metrik evaluasi model (Accuracy, Macro F1, Confusion Matrix, MAE vs Baseline).
    """)

    st.markdown("---")
    st.markdown("#### 🚀 Navigasi Menu")
    st.info("Gunakan navigasi sidebar di sebelah kiri untuk berpindah halaman atau gunakan menu di bawah:")

    nav_c1, nav_c2, nav_c3 = st.columns(3)
    with nav_c1:
        st.page_link("pages/1_Overview.py", label="1. Overview", icon="📊")
        st.page_link("pages/2_Video_Analytics.py", label="2. Video Analytics", icon="📈")
    with nav_c2:
        st.page_link("pages/3_Sentiment_Analysis.py", label="3. Sentiment Analysis", icon="💬")
        st.page_link("pages/4_ML_Prediction.py", label="4. ML Prediction", icon="🤖")
    with nav_c3:
        st.page_link("pages/5_Model_Performance.py", label="5. Model Performance", icon="🎯")

with right_col:
    st.subheader("👤 Profil Kanal")
    st.markdown("""
    - **Nama Kanal**: Windah Basudara
    - **Kreator**: Brando Franco Windah
    - **Fokus Konten**: Gaming (Horror, Simulator, Action RPG, Mobile Games), Charity Streaming, Reaction & Community Events
    - **Target Komunitas**: Penonton gaming Indonesia (Bocil Kematian)
    - **Channel ID**: `UCZrqgLMYK2iV0sV8uN1_rAw`
    """)

    st.markdown("#### ⚡ Status Model Terlatih")
    st.markdown(f"""
    - **Sentiment Classifier**: TF-IDF + Logistic Regression (Macro F1: `{f1_score * 100:.1f}%`)
    - **Popularity Regressor**: Random Forest (MAE: `{rf_mae:,.0f}` views, mengungguli Baseline)
    - **Topic Clustering**: TF-IDF + KMeans (5 Klaster Tema)
    """)

# Catatan Kepatuhan PRD & Independensi
st.markdown("""
<div class="alert-box">
    <b>Pemberitahuan Independensi:</b> Sistem ini merupakan proyek analisis data dan portofolio Machine Learning independen.
    Sistem ini bukan merupakan afiliasi, perwakilan, maupun layanan resmi dari Windah Basudara atau YouTube / Google LLC.
</div>
""", unsafe_allow_html=True)
