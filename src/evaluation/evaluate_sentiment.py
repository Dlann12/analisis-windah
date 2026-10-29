import json
from config.settings import SENTIMENT_REPORT_PATH
from src.training.train_sentiment import train_sentiment_model


def get_sentiment_evaluation_report(force_retrain: bool = False) -> dict:
    """Mengambil atau memperbarui laporan evaluasi model sentimen."""
    if force_retrain or not SENTIMENT_REPORT_PATH.exists():
        return train_sentiment_model()

    with open(SENTIMENT_REPORT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    report = get_sentiment_evaluation_report()
    print("Sentiment Accuracy:", report.get("accuracy"))
    print("Macro F1:", report.get("macro_f1"))
