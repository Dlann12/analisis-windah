import pytest
import pandas as pd
from config.settings import PROCESSED_VIDEOS_PATH, PROCESSED_COMMENTS_PATH


def test_processed_videos_integrity():
    assert PROCESSED_VIDEOS_PATH.exists(), "File videos_clean.csv harus ada."
    df = pd.read_csv(PROCESSED_VIDEOS_PATH)
    assert len(df) >= 100, f"Harus ada minimal 100 video (terdapat {len(df)})."
    required_cols = [
        "video_id", "title", "published_at", "duration_seconds",
        "view_count", "like_count", "comment_count", "engagement_rate",
        "topic_label"
    ]
    for col in required_cols:
        assert col in df.columns, f"Kolom {col} wajib ada pada dataset video."
    assert df["video_id"].duplicated().sum() == 0, "video_id tidak boleh ada duplikat."


def test_processed_comments_integrity():
    assert PROCESSED_COMMENTS_PATH.exists(), "File comments_clean.csv harus ada."
    df = pd.read_csv(PROCESSED_COMMENTS_PATH)
    assert len(df) >= 300, f"Harus ada minimal 300 komentar (terdapat {len(df)})."
    required_cols = ["comment_id", "clean_text", "sentiment_label"]
    for col in required_cols:
        assert col in df.columns, f"Kolom {col} wajib ada pada dataset komentar."
