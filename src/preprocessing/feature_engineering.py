import pandas as pd
from typing import Optional
from config.settings import PROCESSED_VIDEOS_PATH


def extract_video_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menghasilkan fitur tambahan dari metadata video untuk model ML & Analytics:
    - title_length
    - title_word_count
    - publish_hour
    - publish_day (nama hari)
    - publish_day_idx (0-6)
    - publish_year
    - is_weekend (0 atau 1)
    - caps_word_ratio
    - has_exclamation
    """
    df = df.copy()

    # Pastikan published_at berbentuk datetime
    if not pd.api.types.is_datetime64_any_dtype(df["published_at"]):
        df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce", utc=True)

    # 1. Fitur dari judul
    df["title_length"] = df["title"].astype(str).str.len()
    df["title_word_count"] = df["title"].astype(str).apply(lambda x: len(x.split()))

    # Rasio kata kapital (gaya khas judul video gaming: "TAMAT", "NGAKAK", "GILA")
    def get_caps_ratio(title: str) -> float:
        words = title.split()
        if not words:
            return 0.0
        caps = [w for w in words if w.isupper() and len(w) > 1]
        return round(len(caps) / len(words), 3)

    df["caps_word_ratio"] = df["title"].astype(str).apply(get_caps_ratio)
    df["has_exclamation"] = df["title"].astype(str).apply(lambda x: 1 if "!" in x else 0)

    # 2. Fitur temporal dari tanggal publikasi
    df["publish_hour"] = df["published_at"].dt.hour
    df["publish_day_idx"] = df["published_at"].dt.day_of_week
    df["publish_year"] = df["published_at"].dt.year

    day_names_id = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    df["publish_day"] = df["publish_day_idx"].apply(lambda idx: day_names_id[idx] if 0 <= idx <= 6 else "Lainnya")
    df["is_weekend"] = df["publish_day_idx"].apply(lambda idx: 1 if idx in [5, 6] else 0)

    # Pastikan video_age_days tersedia
    if "video_age_days" not in df.columns:
        now_utc = pd.Timestamp.now(tz="UTC")
        df["video_age_days"] = ((now_utc - df["published_at"]).dt.total_seconds() / 86400.0).round(1)

    return df


def prepare_processed_videos() -> pd.DataFrame:
    """Membaca data bersih dan melakukan feature engineering lengkap."""
    if not PROCESSED_VIDEOS_PATH.exists():
        from src.preprocessing.clean_videos import clean_videos_data
        clean_videos_data()

    df = pd.read_csv(PROCESSED_VIDEOS_PATH)
    df_feat = extract_video_features(df)
    df_feat.to_csv(PROCESSED_VIDEOS_PATH, index=False)
    print(f"[feature_engineering] Fitur baru berhasil ditambahkan pada {len(df_feat)} video.")
    return df_feat


if __name__ == "__main__":
    df = prepare_processed_videos()
    print("Contoh kolom:", df[["title", "title_length", "publish_hour", "publish_day", "caps_word_ratio"]].head())
