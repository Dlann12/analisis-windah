import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from config.settings import POPULARITY_MODEL_PATH


_POPULARITY_PAYLOAD = None


def get_popularity_model():
    """Lazy loader untuk model Random Forest Regressor popularitas video."""
    global _POPULARITY_PAYLOAD
    if _POPULARITY_PAYLOAD is None:
        if not POPULARITY_MODEL_PATH.exists():
            from src.training.train_popularity import train_popularity_model
            train_popularity_model()
        _POPULARITY_PAYLOAD = joblib.load(POPULARITY_MODEL_PATH)
    return _POPULARITY_PAYLOAD


def predict_video_popularity(
    title: str,
    duration_seconds: int,
    publish_hour: int,
    publish_day_idx: int,
    topic_label: str,
    video_age_days: float = 30.0
) -> Dict[str, Any]:
    """
    Memprediksi potensi jumlah views video baru berbasis Random Forest Regressor:
    - Input: Judul, durasi (detik), jam tayang (0-23), hari tayang (0-6), topik, estimasi umur video (hari)
    - Output: Estimasi views, range ketidakpastian (lower/upper bound), kategori performa, rekomendasi insight
    """
    payload = get_popularity_model()
    pipe = payload["pipeline"]
    is_log = payload.get("is_log_target", False)

    title_str = str(title).strip()
    words = title_str.split()
    title_length = len(title_str)
    title_word_count = len(words)

    caps_words = [w for w in words if w.isupper() and len(w) > 1]
    caps_word_ratio = round(len(caps_words) / len(words), 3) if words else 0.0
    has_exclamation = 1 if "!" in title_str else 0
    is_weekend = 1 if publish_day_idx in [5, 6] else 0

    input_df = pd.DataFrame([{
        "title_length": title_length,
        "title_word_count": title_word_count,
        "duration_seconds": duration_seconds,
        "publish_hour": publish_hour,
        "publish_day_idx": publish_day_idx,
        "is_weekend": is_weekend,
        "caps_word_ratio": caps_word_ratio,
        "has_exclamation": has_exclamation,
        "video_age_days": video_age_days,
        "topic_label": topic_label
    }])

    raw_pred = pipe.predict(input_df)[0]
    predicted_views = int(round(np.expm1(raw_pred) if is_log else raw_pred))
    predicted_views = max(100000, predicted_views)

    # Batas ketidakpastian (+/- 15% interval estimasi model)
    lower_bound = int(predicted_views * 0.85)
    upper_bound = int(predicted_views * 1.15)

    # Kategori performa berdasarkan distribusi historis kanal Windah Basudara
    if predicted_views < 3200000:
        performance_tier = "Moderate"
        tier_description = "Estimasi performa standar untuk video segmen niche."
    elif predicted_views <= 5500000:
        performance_tier = "Good"
        tier_description = "Estimasi performa solid yang konsisten dengan rata-rata video populer kanal."
    else:
        performance_tier = "High (Viral Potential)"
        tier_description = "Estimasi performa sangat tinggi dengan potensi menjangkau audiens luas."

    # Rekomendasi kontekstual berbasis fitur
    actionable_tips: List[str] = []
    if caps_word_ratio < 0.15:
        actionable_tips.append("Gunakan 1-2 kata kunci berhuruf kapital (misal: 'TAMAT', 'EPIC') untuk meningkatkan daya tarik klik.")
    if duration_seconds < 2400:
        actionable_tips.append("Durasi di bawah 40 menit cenderung memiliki retensi tonton berbeda dibanding format streaming panjang khas Windah.")
    elif duration_seconds > 14400:
        actionable_tips.append("Durasi maraton di atas 4 jam sangat cocok untuk momen spesial, charity, atau penamatan game besar.")
    if publish_hour in [13, 14, 15, 19, 20]:
        actionable_tips.append(f"Jam {publish_hour:02d}:00 merupakan jam emas prime time audiens gaming YouTube Indonesia.")
    else:
        actionable_tips.append(f"Jam tayang {publish_hour:02d}:00 berada di luar jam prime time umum (13:00 - 15:00 atau 19:00 - 20:00).")

    return {
        "predicted_views": predicted_views,
        "lower_bound_views": lower_bound,
        "upper_bound_views": upper_bound,
        "performance_tier": performance_tier,
        "tier_description": tier_description,
        "actionable_tips": actionable_tips,
        "model_used": "Random Forest Regressor (Trained with 120+ historical channel videos)",
        "features_computed": {
            "title_length": title_length,
            "title_word_count": title_word_count,
            "caps_word_ratio": caps_word_ratio,
            "has_exclamation": has_exclamation,
            "is_weekend": is_weekend
        }
    }


if __name__ == "__main__":
    res = predict_video_popularity(
        title="RESIDENT EVIL REQUIEM - KITA LAWAN MONSTER NGERI SAMPAI TAMAT!",
        duration_seconds=7200,
        publish_hour=14,
        publish_day_idx=4,
        topic_label="Horror Games",
        video_age_days=30
    )
    print("Hasil prediksi:", res["predicted_views"], res["performance_tier"])
