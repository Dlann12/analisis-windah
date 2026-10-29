import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from config.settings import RAW_VIDEOS_PATH, PROCESSED_VIDEOS_PATH, SAMPLE_VIDEOS_PATH


def clean_videos_data(input_path: Path = RAW_VIDEOS_PATH, output_path: Path = PROCESSED_VIDEOS_PATH) -> pd.DataFrame:
    """
    Membersihkan dataset metadata video:
    - Menghapus duplikasi video_id
    - Mengonversi format tanggal publikasi
    - Menghitung umur video dalam hari
    - Menghitung metrik Engagement Rate
    - Menangani missing values
    """
    if not input_path.exists():
        if SAMPLE_VIDEOS_PATH.exists():
            input_path = SAMPLE_VIDEOS_PATH
        else:
            raise FileNotFoundError(f"File raw video tidak ditemukan di {input_path}")

    df = pd.read_csv(input_path)

    # 1. Hapus duplikasi berdasarkan video_id
    df = df.drop_duplicates(subset=["video_id"]).copy()

    # 2. Konversi tanggal publikasi ke datetime UTC
    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce", utc=True)
    df = df.dropna(subset=["published_at"]).copy()

    # 3. Pastikan tipe data numerik valid
    numeric_cols = ["duration_seconds", "view_count", "like_count", "comment_count", "category_id"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # 4. Hitung umur video (dalam hari)
    now_utc = datetime.now(timezone.utc)
    df["video_age_days"] = (now_utc - df["published_at"]).dt.total_seconds() / 86400.0
    df["video_age_days"] = df["video_age_days"].apply(lambda x: max(1, round(x, 1)))

    # 5. Hitung Engagement Rate (%) = (Likes + Comments) / Views * 100
    # Berdasarkan PRD 4.2
    df["engagement_rate"] = df.apply(
        lambda row: round(((row["like_count"] + row["comment_count"]) / row["view_count"]) * 100.0, 3)
        if row["view_count"] > 0 else 0.0,
        axis=1
    )

    # 6. Bersihkan kolom teks
    df["title"] = df["title"].fillna("").astype(str).str.strip()
    df["description"] = df["description"].fillna("").astype(str).str.strip()

    # Simpan hasil
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[clean_videos] Berhasil membersihkan {len(df)} video ke {output_path}")

    return df


if __name__ == "__main__":
    df_clean = clean_videos_data()
    print("Contoh kolom:", df_clean.columns.tolist())
