import pytest
import pandas as pd
from src.preprocessing.clean_comments import clean_text_id
from src.data_collection.fetch_videos import parse_duration_to_seconds
from src.preprocessing.feature_engineering import extract_video_features


def test_parse_duration_to_seconds():
    assert parse_duration_to_seconds("PT1H") == 3600
    assert parse_duration_to_seconds("PT1H30M15S") == 5415
    assert parse_duration_to_seconds("PT45M") == 2700
    assert parse_duration_to_seconds("PT10S") == 10
    assert parse_duration_to_seconds("") == 0
    assert parse_duration_to_seconds(None) == 0


def test_clean_text_id():
    raw_text = "Bang Windah bgt https://youtube.com kocak wkwkwk @user mantapp!"
    cleaned = clean_text_id(raw_text)
    assert "https" not in cleaned
    assert "@user" not in cleaned
    assert "banget" in cleaned
    assert "wkwk" in cleaned
    assert "mantap" in cleaned


def test_extract_video_features():
    df = pd.DataFrame([{
        "title": "RESIDENT EVIL TAMAT! GAES",
        "description": "Deskripsi video",
        "published_at": "2023-05-15T14:30:00Z",
        "duration_seconds": 3600,
        "view_count": 1000000,
        "like_count": 50000,
        "comment_count": 2000
    }])
    df_feat = extract_video_features(df)
    assert "title_length" in df_feat.columns
    assert "publish_hour" in df_feat.columns
    assert "publish_day" in df_feat.columns
    assert "caps_word_ratio" in df_feat.columns
    assert df_feat["publish_hour"].iloc[0] == 14
    assert df_feat["has_exclamation"].iloc[0] == 1
