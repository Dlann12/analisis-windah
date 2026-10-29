import joblib
from typing import Dict, Any, List
from config.settings import SENTIMENT_MODEL_PATH
from src.preprocessing.clean_comments import clean_text_id


_SENTIMENT_MODEL = None


def get_sentiment_model():
    """Lazy loader untuk model klasifikasi sentimen."""
    global _SENTIMENT_MODEL
    if _SENTIMENT_MODEL is None:
        if not SENTIMENT_MODEL_PATH.exists():
            from src.training.train_sentiment import train_sentiment_model
            train_sentiment_model()
        _SENTIMENT_MODEL = joblib.load(SENTIMENT_MODEL_PATH)
    return _SENTIMENT_MODEL


def predict_comment_sentiment(comment_text: str) -> Dict[str, Any]:
    """
    Memprediksi sentimen satu teks komentar.
    Return:
    - label: 'Positif', 'Netral', atau 'Negatif'
    - confidence: float (0.0 - 1.0)
    - probabilities: dict probabilitas per kelas
    """
    model = get_sentiment_model()
    cleaned = clean_text_id(comment_text)

    if not cleaned:
        return {
            "label": "Netral",
            "confidence": 0.50,
            "probabilities": {"Positif": 0.25, "Netral": 0.50, "Negatif": 0.25},
            "cleaned_text": ""
        }

    probs = model.predict_proba([cleaned])[0]
    classes = model.classes_
    prob_dict = {cls: round(float(p), 4) for cls, p in zip(classes, probs)}

    predicted_label = model.predict([cleaned])[0]
    confidence = float(max(probs))

    return {
        "label": predicted_label,
        "confidence": round(confidence, 4),
        "probabilities": prob_dict,
        "cleaned_text": cleaned
    }


def batch_predict_comments(comments: List[str]) -> List[Dict[str, Any]]:
    """Memprediksi sentimen untuk daftar komentar sekaligus."""
    return [predict_comment_sentiment(c) for c in comments]


if __name__ == "__main__":
    test_samples = [
        "Bang Windah emang the best, kontennya selalu menghibur!",
        "Game ini beli di mana ya bang?",
        "Audio micnya kresek-kresek bang, tolong dibenerin."
    ]
    for sample in test_samples:
        res = predict_comment_sentiment(sample)
        print(f"Komentar: '{sample}' -> {res['label']} ({res['confidence'] * 100:.1f}%)")
