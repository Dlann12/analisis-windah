import pytest
from src.prediction.predict_sentiment import predict_comment_sentiment
from src.prediction.predict_popularity import predict_video_popularity


def test_sentiment_prediction():
    res_pos = predict_comment_sentiment("Konten bang windah selalu menghibur dan seru banget!")
    assert res_pos["label"] in ["Positif", "Netral", "Negatif"]
    assert 0.0 <= res_pos["confidence"] <= 1.0
    assert "Positif" in res_pos["probabilities"]

    res_neg = predict_comment_sentiment("Audionya jelek dan videonya patah-patah terus bikin kecewa.")
    assert res_neg["label"] in ["Positif", "Netral", "Negatif"]


def test_popularity_prediction():
    res = predict_video_popularity(
        title="MAIN GAME SIMULATOR BERSAMA TEMAN SAMPAI TAMAT!",
        duration_seconds=5400,
        publish_hour=14,
        publish_day_idx=4,
        topic_label="Simulator & Casual Games",
        video_age_days=30
    )
    assert res["predicted_views"] > 0
    assert res["lower_bound_views"] < res["predicted_views"] < res["upper_bound_views"]
    assert res["performance_tier"] in ["Moderate", "Good", "High (Viral Potential)"]
    assert len(res["actionable_tips"]) > 0
