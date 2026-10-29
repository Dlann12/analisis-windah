import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config.settings import PROCESSED_VIDEOS_PATH
from src.preprocessing.clean_videos import clean_videos_data

st.set_page_config(page_title="Video Analytics - Windah Basudara AI Analytics", page_icon="📈", layout="wide")

st.title("📈 Halaman 2: Video Performance Analytics")
st.markdown("Eksplorasi mendalam performa per video, ranking interaksi, dan perbandingan antarvideo.")


@st.cache_data
def get_processed_data():
    if not PROCESSED_VIDEOS_PATH.exists():
        clean_videos_data()
    df = pd.read_csv(PROCESSED_VIDEOS_PATH)
    if "published_at" in df.columns:
        df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")
        df["year"] = df["published_at"].dt.year
    return df


df = get_processed_data()

if df.empty:
    st.warning("Data video belum tersedia.")
    st.stop()

# 1. Filter Interaktif
st.subheader("🔍 Filter & Pencarian Video")
f_col1, f_col2, f_col3 = st.columns([2, 1, 1])

with f_col1:
    search_query = st.text_input("Cari judul video:", placeholder="Contoh: Resident Evil, Simulator, GTA, Charity...")

with f_col2:
    years_available = sorted([int(y) for y in df["year"].dropna().unique()])
    selected_years = st.multiselect("Pilih Tahun:", years_available, default=years_available)

with f_col3:
    topics_available = sorted(df["topic_label"].dropna().unique().tolist())
    selected_topics = st.multiselect("Pilih Tema:", topics_available, default=topics_available)

# Terapkan Filter
filtered_df = df.copy()

if search_query.strip():
    filtered_df = filtered_df[filtered_df["title"].str.contains(search_query.strip(), case=False, na=False)]

if selected_years:
    filtered_df = filtered_df[filtered_df["year"].isin(selected_years)]

if selected_topics:
    filtered_df = filtered_df[filtered_df["topic_label"].isin(selected_topics)]

st.caption(f"Menampilkan **{len(filtered_df)}** dari total {len(df)} video yang cocok dengan kriteria.")

st.markdown("---")

# 2. Ranking Tabulasi
tab1, tab2, tab3 = st.tabs(["🔥 Ranking Views", "❤️ Ranking Likes", "⚡ Ranking Engagement Rate"])

with tab1:
    st.markdown("#### Video dengan Jumlah Views Tertinggi")
    top_views = filtered_df.sort_values(by="view_count", ascending=False).head(10)
    fig_views = px.bar(
        top_views,
        x="view_count",
        y="title",
        orientation="h",
        color="topic_label",
        labels={"view_count": "Total Views", "title": "Judul Video", "topic_label": "Kategori"},
        title="Top 10 Video Berdasarkan Views"
    )
    fig_views.update_layout(
        template="plotly_dark",
        plot_bgcolor="#0F172A",
        paper_bgcolor="#1E293B",
        yaxis=dict(autorange="reversed")
    )
    st.plotly_chart(fig_views, use_container_width=True)

with tab2:
    st.markdown("#### Video dengan Jumlah Likes Tertinggi")
    top_likes = filtered_df.sort_values(by="like_count", ascending=False).head(10)
    fig_likes = px.bar(
        top_likes,
        x="like_count",
        y="title",
        orientation="h",
        color="topic_label",
        labels={"like_count": "Total Likes", "title": "Judul Video", "topic_label": "Kategori"},
        title="Top 10 Video Berdasarkan Likes"
    )
    fig_likes.update_layout(
        template="plotly_dark",
        plot_bgcolor="#0F172A",
        paper_bgcolor="#1E293B",
        yaxis=dict(autorange="reversed")
    )
    st.plotly_chart(fig_likes, use_container_width=True)

with tab3:
    st.markdown("#### Video dengan Rasio Engagement Rate Tertinggi")
    st.info("Engagement Rate (ER) = (Likes + Comments) / Views * 100%")
    top_er = filtered_df.sort_values(by="engagement_rate", ascending=False).head(10)
    fig_er = px.bar(
        top_er,
        x="engagement_rate",
        y="title",
        orientation="h",
        color="topic_label",
        labels={"engagement_rate": "Engagement Rate (%)", "title": "Judul Video", "topic_label": "Kategori"},
        title="Top 10 Video Berdasarkan Engagement Rate (%)"
    )
    fig_er.update_layout(
        template="plotly_dark",
        plot_bgcolor="#0F172A",
        paper_bgcolor="#1E293B",
        yaxis=dict(autorange="reversed")
    )
    st.plotly_chart(fig_er, use_container_width=True)

st.markdown("---")

# 3. Fitur Komparasi Antarvideo (PRD 4.2)
st.subheader("⚖️ Perbandingan Antarvideo Langsung")
st.markdown("Pilih 2 atau 3 video untuk membandingkan metrik views, likes, durasi, dan engagement rate secara berdampingan.")

video_options = df["title"].tolist()
selected_compare = st.multiselect(
    "Pilih video untuk dibandingkan (Maksimal 3):",
    options=video_options,
    default=video_options[:2] if len(video_options) >= 2 else video_options
)

if len(selected_compare) > 3:
    st.warning("Silakan pilih maksimal 3 video untuk perbandingan optimal.")
    selected_compare = selected_compare[:3]

if selected_compare:
    comp_df = df[df["title"].isin(selected_compare)].copy()
    
    comp_cols = st.columns(len(comp_df))
    for idx, (_, row) in enumerate(comp_df.iterrows()):
        with comp_cols[idx]:
            st.markdown(f"**{row['title']}**")
            st.markdown(f"- 🏷️ **Tema**: {row['topic_label']}")
            st.markdown(f"- 👁️ **Views**: {row['view_count']:,}")
            st.markdown(f"- 👍 **Likes**: {row['like_count']:,}")
            st.markdown(f"- 💬 **Komentar**: {row['comment_count']:,}")
            st.markdown(f"- ⚡ **Engagement**: {row['engagement_rate']:.2f}%")
            st.markdown(f"- ⏱️ **Durasi**: {row['duration_seconds'] // 60} menit")
            st.markdown(f"- 📅 **Rilis**: {pd.to_datetime(row['published_at']).strftime('%d %b %Y')}")

    # Visual Bar Chart Perbandingan
    fig_compare = go.Figure()
    for _, row in comp_df.iterrows():
        short_title = row["title"][:25] + "..." if len(row["title"]) > 25 else row["title"]
        fig_compare.add_trace(go.Bar(
            name=short_title,
            x=["Views (Juta)", "Likes (Puluh Ribu)", "Komentar (Ribu)", "Durasi (Menit)"],
            y=[
                round(row["view_count"] / 1e6, 2),
                round(row["like_count"] / 1e4, 2),
                round(row["comment_count"] / 1e3, 2),
                round(row["duration_seconds"] / 60, 1)
            ]
        ))
    fig_compare.update_layout(
        title="Perbandingan Normalisasi Metrik Video Terpilih",
        barmode="group",
        template="plotly_dark",
        plot_bgcolor="#0F172A",
        paper_bgcolor="#1E293B"
    )
    st.plotly_chart(fig_compare, use_container_width=True)
