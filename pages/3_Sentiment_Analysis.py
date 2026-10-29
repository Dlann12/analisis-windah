import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config.settings import PROCESSED_COMMENTS_PATH, PROCESSED_VIDEOS_PATH
from src.preprocessing.clean_comments import clean_comments_data
from src.prediction.predict_sentiment import predict_comment_sentiment

st.set_page_config(page_title="Sentiment Analysis - Windah Basudara AI Analytics", page_icon="💬", layout="wide")

st.title("💬 Halaman 3: Comment Sentiment Analysis")
st.markdown("Analisis sentimen komentar penonton kanal Windah Basudara menggunakan model NLP TF-IDF dan Logistic Regression.")


@st.cache_data
def get_comments_and_videos():
    if not PROCESSED_COMMENTS_PATH.exists():
        clean_comments_data()
    df_c = pd.read_csv(PROCESSED_COMMENTS_PATH)
    df_v = pd.read_csv(PROCESSED_VIDEOS_PATH) if PROCESSED_VIDEOS_PATH.exists() else pd.DataFrame()
    return df_c, df_v


df_comments, df_videos = get_comments_and_videos()

if df_comments.empty:
    st.warning("Data komentar belum tersedia.")
    st.stop()

# 1. Pilihan Sumber Komentar
st.subheader("🎯 Pilih Lingkup Analisis Komentar")
scope_option = st.radio(
    "Lingkup Data:",
    ["Seluruh Dataset Komentar Terkumpul", "Filter Berdasarkan Video Tertentu"],
    horizontal=True
)

active_comments = df_comments.copy()

if scope_option == "Filter Berdasarkan Video Tertentu" and not df_videos.empty:
    video_map = dict(zip(df_videos["title"], df_videos["video_id"]))
    selected_video_title = st.selectbox("Pilih Video:", list(video_map.keys()))
    selected_vid = video_map[selected_video_title]
    active_comments = df_comments[df_comments["video_id"] == selected_vid]
    if active_comments.empty:
        st.info("Komentar untuk video ini belum terkumpul secara spesifik. Menampilkan sampel acak dari dataset.")
        active_comments = df_comments.sample(min(30, len(df_comments)), random_state=42)

# Hitung Distribusi Sentimen
total_analyzed = len(active_comments)
sentiment_counts = active_comments["sentiment_label"].value_counts()
pos_count = sentiment_counts.get("Positif", 0)
neu_count = sentiment_counts.get("Netral", 0)
neg_count = sentiment_counts.get("Negatif", 0)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Komentar Dianalisis", f"{total_analyzed:,}")
col2.metric("Sentimen Positif", f"{pos_count} ({pos_count / total_analyzed * 100:.1f}%)" if total_analyzed else "0")
col3.metric("Sentimen Netral", f"{neu_count} ({neu_count / total_analyzed * 100:.1f}%)" if total_analyzed else "0")
col4.metric("Sentimen Negatif", f"{neg_count} ({neg_count / total_analyzed * 100:.1f}%)" if total_analyzed else "0")

st.markdown("---")

# 2. Visualisasi Distribusi Sentimen
chart_c1, chart_c2 = st.columns(2)

with chart_c1:
    st.subheader("Proporsi Sentimen Komentar")
    fig_pie = px.pie(
        values=[pos_count, neu_count, neg_count],
        names=["Positif", "Netral", "Negatif"],
        color=["Positif", "Netral", "Negatif"],
        color_discrete_map={"Positif": "#10B981", "Netral": "#F59E0B", "Negatif": "#EF4444"},
        hole=0.4,
        title="Distribusi Rasio Sentimen"
    )
    fig_pie.update_layout(
        template="plotly_dark",
        plot_bgcolor="#0F172A",
        paper_bgcolor="#1E293B"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with chart_c2:
    st.subheader("Jumlah Komentar per Kategori")
    df_counts = pd.DataFrame({
        "Sentimen": ["Positif", "Netral", "Negatif"],
        "Jumlah": [pos_count, neu_count, neg_count]
    })
    fig_bar = px.bar(
        df_counts,
        x="Sentimen",
        y="Jumlah",
        color="Sentimen",
        color_discrete_map={"Positif": "#10B981", "Netral": "#F59E0B", "Negatif": "#EF4444"},
        text="Jumlah",
        title="Frekuensi Komentar per Kategori"
    )
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(
        template="plotly_dark",
        plot_bgcolor="#0F172A",
        paper_bgcolor="#1E293B"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# 3. Uji Sentimen Langsung (Interactive Live Tester)
st.subheader("🧪 Uji Coba Model Sentimen Secara Langsung")
st.markdown("Masukkan kalimat komentar baru untuk diuji oleh model Machine Learning yang telah dilatih.")

test_col1, test_col2 = st.columns([2, 1])

with test_col1:
    sample_input = st.text_area(
        "Ketik teks komentar:",
        value="Bang Windah lucu banget pas dikejar hantu wkwk, bikin mood naik!",
        height=100
    )
    btn_predict = st.button("Analisis Sentimen Komentar", type="primary")

with test_col2:
    if btn_predict and sample_input.strip():
        pred_res = predict_comment_sentiment(sample_input)
        label = pred_res["label"]
        conf = pred_res["confidence"] * 100
        probs = pred_res["probabilities"]

        color_map = {"Positif": "#10B981", "Netral": "#F59E0B", "Negatif": "#EF4444"}
        st.markdown(f"""
        <div style="background-color: #1E293B; border: 1px solid {color_map.get(label, '#FFF')}; border-radius: 8px; padding: 1rem; text-align: center;">
            <div style="font-size: 0.9rem; color: #94A3B8;">Hasil Prediksi Model</div>
            <div style="font-size: 1.8rem; font-weight: bold; color: {color_map.get(label, '#FFF')}; margin: 0.3rem 0;">{label}</div>
            <div style="font-size: 0.95rem; color: #CBD5E1;">Tingkat Keyakinan (Confidence): <b>{conf:.1f}%</b></div>
        </div>
        """, unsafe_allow_html=True)

        st.caption("Rincian Distribusi Probabilitas:")
        for cls, p in probs.items():
            st.progress(float(p), text=f"{cls}: {p*100:.1f}%")

st.markdown("---")

# 4. Tabel Daftar Komentar Berdasarkan Filter
st.subheader("📋 Sampel Komentar Terindeks")
f_sent = st.selectbox("Filter Sentimen Tabel:", ["Semua", "Positif", "Netral", "Negatif"])

display_table = active_comments.copy()
if f_sent != "Semua":
    display_table = display_table[display_table["sentiment_label"] == f_sent]

st.dataframe(
    display_table[["comment_text", "sentiment_label", "like_count", "published_at"]].rename(columns={
        "comment_text": "Isi Komentar",
        "sentiment_label": "Prediksi Sentimen",
        "like_count": "Likes",
        "published_at": "Waktu"
    }),
    use_container_width=True,
    hide_index=True
)
