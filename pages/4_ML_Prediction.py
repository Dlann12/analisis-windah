import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config.settings import PROCESSED_VIDEOS_PATH
from src.prediction.predict_popularity import predict_video_popularity

st.set_page_config(page_title="ML Prediction - Windah Basudara AI Analytics", page_icon="🤖", layout="wide")

st.title("🤖 Halaman 4: Video Popularity Prediction")
st.markdown("Fitur Machine Learning utama untuk memperkirakan potensi jumlah views video baru berbasis metadata dan riwayat kanal.")


@st.cache_data
def get_channel_avg_views():
    if PROCESSED_VIDEOS_PATH.exists():
        df = pd.read_csv(PROCESSED_VIDEOS_PATH)
        return int(df["view_count"].mean())
    return 4200000


channel_avg_views = get_channel_avg_views()

# 1. Form Input Metadata Video
st.subheader("📝 Input Rencana Video Baru")

with st.form("prediction_form"):
    title_input = st.text_input(
        "Judul Rencana Video:",
        value="RESIDENT EVIL REQUIEM - KITA LAXAN MONSTER NGERI SAMPAI TAMAT!",
        help="Gunakan kata kunci menarik dan penegasan seperti gaya khas Windah Basudara."
    )

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        topic_options = [
            "Horror Games",
            "Simulator & Casual Games",
            "Adventure & Story Games",
            "Mobile & Multiplayer Games",
            "Special, Charity & Reaction"
        ]
        topic_input = st.selectbox("Kategori / Tema Konten:", topic_options, index=0)
        duration_minutes = st.slider("Estimasi Durasi Video (Menit):", min_value=10, max_value=360, value=90, step=5)

    with col_f2:
        days_map = {
            "Senin": 0,
            "Selasa": 1,
            "Rabu": 2,
            "Kamis": 3,
            "Jumat": 4,
            "Sabtu": 5,
            "Minggu": 6
        }
        day_name = st.selectbox("Rencana Hari Upload:", list(days_map.keys()), index=4) # Default Jumat
        upload_hour = st.slider("Rencana Jam Upload (WIB):", min_value=0, max_value=23, value=14, step=1)

    age_horizon_days = st.select_slider(
        "Horizon Waktu Snapshot Views:",
        options=[7, 14, 30, 90, 180, 365],
        value=30,
        help="Estimasi views setelah video tayang selama N hari di kanal."
    )

    submit_btn = st.form_submit_button("🚀 Prediksi Potensi Views", type="primary")

# 2. Hasil Prediksi
if submit_btn:
    duration_seconds = duration_minutes * 60
    day_idx = days_map[day_name]

    res = predict_video_popularity(
        title=title_input,
        duration_seconds=duration_seconds,
        publish_hour=upload_hour,
        publish_day_idx=day_idx,
        topic_label=topic_input,
        video_age_days=float(age_horizon_days)
    )

    pred_views = res["predicted_views"]
    lower_bound = res["lower_bound_views"]
    upper_bound = res["upper_bound_views"]
    tier = res["performance_tier"]
    tier_desc = res["tier_description"]
    tips = res["actionable_tips"]

    st.markdown("---")
    st.subheader("🎯 Hasil Estimasi Model Machine Learning")

    r_col1, r_col2, r_col3 = st.columns([1, 1, 1])

    with r_col1:
        st.metric(
            label="Prediksi Jumlah Views",
            value=f"{pred_views:,.0f}",
            delta=f"{pred_views - channel_avg_views:,.0f} vs Rata-rata Kanal"
        )
    with r_col2:
        st.metric(
            label="Rentang Estimasi (Interval 15%)",
            value=f"{lower_bound:,.0f} - {upper_bound:,.0f}"
        )
    with r_col3:
        st.metric(
            label="Kategori Potensi Performa",
            value=tier
        )

    st.caption(f"Keterangan kategori: {tier_desc}")

    # Grafik Gauge Visualisasi Perbandingan
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pred_views,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Estimasi Views ({age_horizon_days} Hari Tayang)", 'font': {'size': 20}},
        delta={'reference': channel_avg_views, 'increasing': {'color': "#10B981"}, 'decreasing': {'color': "#EF4444"}},
        gauge={
            'axis': {'range': [None, max(10000000, pred_views * 1.3)], 'tickformat': ',.0f'},
            'bar': {'color': "#38BDF8"},
            'steps': [
                {'range': [0, 3200000], 'color': "#334155"},
                {'range': [3200000, 5500000], 'color': "#1E293B"},
                {'range': [5500000, 12000000], 'color': "#0F172A"}
            ],
            'threshold': {
                'line': {'color': "#DC2626", 'width': 4},
                'thickness': 0.75,
                'value': channel_avg_views
            }
        }
    ))
    fig_gauge.update_layout(
        template="plotly_dark",
        plot_bgcolor="#0F172A",
        paper_bgcolor="#1E293B",
        height=350,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Rekomendasi Berbasis Data
    st.markdown("#### 💡 Catatan & Rekomendasi Taktis")
    for tip in tips:
        st.info(f"• {tip}")

    # Informasi Model dan Batasan Interpretasi (PRD 4.4 & 4.6)
    with st.expander("ℹ️ Transparansi Model & Batasan Interpretasi"):
        st.markdown(f"""
        - **Algoritma**: `{res['model_used']}`
        - **Fitur Terhitung**:
          - Panjang Judul: `{res['features_computed']['title_length']}` karakter ({res['features_computed']['title_word_count']} kata)
          - Rasio Kata Kapital: `{res['features_computed']['caps_word_ratio'] * 100:.1f}%`
          - Tanda Seru (!): `{'Ada' if res['features_computed']['has_exclamation'] else 'Tidak ada'}`
          - Hari Libur / Weekend: `{'Ya' if res['features_computed']['is_weekend'] else 'Tidak'}`
        - **Batasan Metodologi**: Prediksi ini adalah perkiraan empiris berbasis korelasi data historis kanal. Prediksi ini bukan jaminan pasti karena faktor algoritma rekomendasi YouTube, tren eksternal, dan retensi penonton secara realtime tetap berpengaruh signifikan.
        """)
