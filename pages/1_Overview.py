import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config.settings import PROCESSED_VIDEOS_PATH
from src.preprocessing.clean_videos import clean_videos_data

st.set_page_config(page_title="Overview - Windah Basudara AI Analytics", page_icon="📊", layout="wide")

st.title("📊 Halaman 1: YouTube Channel Overview")
st.markdown("Statistik makro performa video kanal YouTube Windah Basudara berdasarkan data yang terindeks.")


@st.cache_data
def get_clean_videos():
    if not PROCESSED_VIDEOS_PATH.exists():
        clean_videos_data()
    df = pd.read_csv(PROCESSED_VIDEOS_PATH)
    if "published_at" in df.columns:
        df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")
    return df


df = get_clean_videos()

if df.empty:
    st.warning("Data video belum tersedia. Silakan jalankan pengambilan data terlebih dahulu.")
    st.stop()

# 1. Ringkasan Metrik
col1, col2, col3, col4 = st.columns(4)
total_vids = len(df)
total_views = int(df["view_count"].sum())
avg_views = int(df["view_count"].mean())
avg_er = float(df["engagement_rate"].mean())

col1.metric("Total Video Terindeks", f"{total_vids:,}")
col2.metric("Total Views Terakumulasi", f"{total_views / 1e6:.2f} Juta")
col3.metric("Rata-rata Views / Video", f"{avg_views / 1e6:.2f} Juta")
col4.metric("Rata-rata Engagement Rate", f"{avg_er:.2f}%")

st.markdown("---")

# 2. Grafik Distribusi Views & Upload Timeline
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Distribusi Jumlah Views Video")
    fig_dist = px.histogram(
        df,
        x="view_count",
        nbins=25,
        title="Sebaran Views Video (Skala Jutaan)",
        labels={"view_count": "Jumlah Views", "count": "Frekuensi Video"},
        color_discrete_sequence=["#38BDF8"]
    )
    fig_dist.update_layout(
        template="plotly_dark",
        plot_bgcolor="#0F172A",
        paper_bgcolor="#1E293B",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_dist, use_container_width=True)

with chart_col2:
    st.subheader("Tren Publikasi Video per Tahun")
    df["year_str"] = df["published_at"].dt.year.astype(str)
    yearly_counts = df.groupby("year_str")["video_id"].count().reset_index()
    yearly_counts.columns = ["Tahun", "Jumlah Video"]

    fig_year = px.bar(
        yearly_counts,
        x="Tahun",
        y="Jumlah Video",
        text="Jumlah Video",
        title="Jumlah Video Berdasarkan Tahun Publikasi",
        color_discrete_sequence=["#DC2626"]
    )
    fig_year.update_traces(textposition="outside")
    fig_year.update_layout(
        template="plotly_dark",
        plot_bgcolor="#0F172A",
        paper_bgcolor="#1E293B",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_year, use_container_width=True)

st.markdown("---")

# 3. Top Performing Videos
st.subheader("🏆 Top 10 Video Paling Populer (Views Tertinggi)")
top_10 = df.sort_values(by="view_count", ascending=False).head(10).copy()

display_cols = ["title", "view_count", "like_count", "comment_count", "engagement_rate", "topic_label", "published_at"]
rename_map = {
    "title": "Judul Video",
    "view_count": "Views",
    "like_count": "Likes",
    "comment_count": "Komentar",
    "engagement_rate": "ER (%)",
    "topic_label": "Kategori Tema",
    "published_at": "Tanggal Rilis"
}

top_10_display = top_10[display_cols].rename(columns=rename_map)
top_10_display["Views"] = top_10_display["Views"].apply(lambda x: f"{x:,.0f}")
top_10_display["Likes"] = top_10_display["Likes"].apply(lambda x: f"{x:,.0f}")
top_10_display["Komentar"] = top_10_display["Komentar"].apply(lambda x: f"{x:,.0f}")
top_10_display["ER (%)"] = top_10_display["ER (%)"].apply(lambda x: f"{x:.2f}%")
top_10_display["Tanggal Rilis"] = pd.to_datetime(top_10_display["Tanggal Rilis"]).dt.strftime("%d %b %Y")

st.dataframe(top_10_display, use_container_width=True, hide_index=True)
