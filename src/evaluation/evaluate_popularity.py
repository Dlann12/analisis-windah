import json
from config.settings import POPULARITY_REPORT_PATH
from src.training.train_popularity import train_popularity_model


def get_popularity_evaluation_report(force_retrain: bool = False) -> dict:
    """Mengambil atau memperbarui laporan evaluasi model popularitas video."""
    if force_retrain or not POPULARITY_REPORT_PATH.exists():
        return train_popularity_model()

    with open(POPULARITY_REPORT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    report = get_popularity_evaluation_report()
    print("Popularity Evaluation Models:", list(report.get("models", {}).keys()))
