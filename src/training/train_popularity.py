import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from config.settings import (
    PROCESSED_VIDEOS_PATH, POPULARITY_MODEL_PATH, POPULARITY_REPORT_PATH
)
from src.preprocessing.feature_engineering import prepare_processed_videos


def evaluate_regressor(name: str, model, X_test, y_test) -> dict:
    """Menghitung MAE, RMSE, dan R² score untuk model regresi."""
    y_pred = model.predict(X_test)
    y_test_actual = np.array(y_test)
    y_pred_actual = np.array(y_pred)

    mae = float(mean_absolute_error(y_test_actual, y_pred_actual))
    rmse = float(np.sqrt(mean_squared_error(y_test_actual, y_pred_actual)))
    r2 = float(r2_score(y_test_actual, y_pred_actual))

    return {
        "model_name": name,
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "r2_score": round(r2, 4),
        "sample_actual": [round(float(v), 0) for v in y_test_actual[:5]],
        "sample_predicted": [round(float(v), 0) for v in y_pred_actual[:5]]
    }


def train_popularity_model(test_size: float = 0.20, random_state: int = 42) -> dict:
    """
    Melatih model prediksi popularitas video (views):
    - Fitur: panjang judul, durasi, jam upload, hari upload, rasio huruf kapital, umur video, topik
    - Model Utama: Random Forest Regressor
    - Model Pembanding: Gradient Boosting, Linear Regression, Baseline (Median Views)
    - Menyimpan model terbaik ke models/popularity_model.joblib
    - Menyimpan perbandingan ke reports/popularity_evaluation.json
    """
    df = prepare_processed_videos()

    # Pastikan target valid
    df = df[df["view_count"] > 0].copy()

    # Fitur numerik dan kategorikal
    numeric_features = [
        "title_length",
        "title_word_count",
        "duration_seconds",
        "publish_hour",
        "publish_day_idx",
        "is_weekend",
        "caps_word_ratio",
        "has_exclamation",
        "video_age_days"
    ]
    categorical_features = ["topic_label"]
    feature_cols = numeric_features + categorical_features

    # Filter baris yang memiliki fitur lengkap
    df = df.dropna(subset=feature_cols + ["view_count"]).copy()

    X = df[feature_cols]
    y = df["view_count"]

    # Stratified/representative train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # Preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features)
        ]
    )

    # 1. Baseline Model (Median Target)
    baseline_pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("reg", DummyRegressor(strategy="median"))
    ])
    baseline_pipe.fit(X_train, y_train)
    res_baseline = evaluate_regressor("Baseline (Median)", baseline_pipe, X_test, y_test)

    # 2. Linear Regression
    lr_pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("reg", LinearRegression())
    ])
    lr_pipe.fit(X_train, y_train)
    res_lr = evaluate_regressor("Linear Regression", lr_pipe, X_test, y_test)

    # 3. Gradient Boosting Regressor
    gb_pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("reg", GradientBoostingRegressor(n_estimators=100, learning_rate=0.08, max_depth=3, random_state=random_state))
    ])
    gb_pipe.fit(X_train, y_train)
    res_gb = evaluate_regressor("Gradient Boosting", gb_pipe, X_test, y_test)

    # 4. Main Model: Random Forest Regressor
    rf_pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("reg", RandomForestRegressor(
            n_estimators=200,
            max_depth=8,
            min_samples_split=3,
            random_state=random_state,
            n_jobs=-1
        ))
    ])
    rf_pipe.fit(X_train, y_train)
    res_rf = evaluate_regressor("Random Forest (Main)", rf_pipe, X_test, y_test)

    # Simpan main model
    model_payload = {
        "pipeline": rf_pipe,
        "feature_cols": feature_cols,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "is_log_target": False
    }
    POPULARITY_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_payload, POPULARITY_MODEL_PATH)
    print(f"[train_popularity] Model Random Forest disimpan ke {POPULARITY_MODEL_PATH}")

    # Feature Importance dari Random Forest
    rf_reg = rf_pipe.named_steps["reg"]
    cat_encoder = rf_pipe.named_steps["preprocessor"].named_transformers_["cat"]
    cat_names = cat_encoder.get_feature_names_out(categorical_features).tolist()
    all_feature_names = numeric_features + cat_names
    importances = rf_reg.feature_importances_.tolist()
    feature_importance_dict = dict(zip(all_feature_names, [round(imp, 4) for imp in importances]))

    # Ringkasan perbandingan
    comparison_results = {
        "dataset_total": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "models": {
            "random_forest": res_rf,
            "gradient_boosting": res_gb,
            "linear_regression": res_lr,
            "baseline_median": res_baseline
        },
        "feature_importance": feature_importance_dict,
        "beats_baseline": bool(res_rf["mae"] < res_baseline["mae"])
    }

    POPULARITY_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(POPULARITY_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(comparison_results, f, indent=2, ensure_ascii=False)
    print(f"[train_popularity] Laporan perbandingan disimpan ke {POPULARITY_REPORT_PATH}")
    print(f"Random Forest MAE: {res_rf['mae']:,.0f} | Baseline MAE: {res_baseline['mae']:,.0f}")

    return comparison_results


if __name__ == "__main__":
    rep = train_popularity_model()
    print("Selesai training model popularitas. RF beats baseline:", rep["beats_baseline"])
