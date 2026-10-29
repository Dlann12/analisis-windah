import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support
from sklearn.pipeline import Pipeline
from config.settings import (
    PROCESSED_COMMENTS_PATH, SENTIMENT_MODEL_PATH, SENTIMENT_REPORT_PATH
)
from src.preprocessing.clean_comments import clean_comments_data


def train_sentiment_model(test_size: float = 0.20, random_state: int = 42) -> dict:
    """
    Melatih model klasifikasi sentimen komentar:
    - Arsitektur: TF-IDF (unigram & bigram) + Logistic Regression (multinomial)
    - Kelas: Positif, Netral, Negatif
    - Evaluasi: Accuracy, Precision, Recall, Macro F1, Confusion Matrix
    - Menyimpan model ke models/sentiment_model.joblib
    - Menyimpan laporan evaluasi ke reports/sentiment_evaluation.json
    """
    if not PROCESSED_COMMENTS_PATH.exists():
        clean_comments_data()

    df = pd.read_csv(PROCESSED_COMMENTS_PATH)

    # Pastikan data memiliki kolom teks bersih dan label
    df = df.dropna(subset=["clean_text", "sentiment_label"]).copy()
    df = df[df["clean_text"].str.strip().str.len() > 0]

    X = df["clean_text"]
    y = df["sentiment_label"]

    # Stratified Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # Pipeline TF-IDF + Logistic Regression
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=2,
            max_features=1500,
            sublinear_tf=True
        )),
        ("clf", LogisticRegression(
            C=1.5,
            class_weight="balanced",
            max_iter=500,
            random_state=random_state
        ))
    ])

    # Training
    pipeline.fit(X_train, y_train)

    # Prediksi Test Set
    y_pred = pipeline.predict(X_test)

    # Perhitungan Metrik Evaluasi
    acc = float(accuracy_score(y_test, y_pred))
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(y_test, y_pred, average="macro")

    labels_order = ["Positif", "Netral", "Negatif"]
    cm = confusion_matrix(y_test, y_pred, labels=labels_order).tolist()
    report_dict = classification_report(y_test, y_pred, labels=labels_order, output_dict=True)

    metrics_payload = {
        "model_name": "TF-IDF + Logistic Regression",
        "dataset_size": len(df),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "accuracy": round(acc, 4),
        "macro_precision": round(float(p_macro), 4),
        "macro_recall": round(float(r_macro), 4),
        "macro_f1": round(float(f1_macro), 4),
        "classes": labels_order,
        "confusion_matrix": cm,
        "classification_report": report_dict,
        "is_target_achieved": bool(f1_macro >= 0.80)
    }

    # Simpan Model Pipeline
    SENTIMENT_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, SENTIMENT_MODEL_PATH)
    print(f"[train_sentiment] Model berhasil disimpan ke {SENTIMENT_MODEL_PATH}")

    # Simpan Hasil Evaluasi ke JSON
    SENTIMENT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SENTIMENT_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2, ensure_ascii=False)
    print(f"[train_sentiment] Laporan evaluasi disimpan ke {SENTIMENT_REPORT_PATH}")
    print(f"Accuracy: {acc:.4f} | Macro F1: {f1_macro:.4f}")

    return metrics_payload


if __name__ == "__main__":
    results = train_sentiment_model()
    print("Selesai melatih model sentimen:", results["macro_f1"])
