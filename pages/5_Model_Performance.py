import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config.settings import (
    SENTIMENT_REPORT_PATH, POPULARITY_REPORT_PATH, TOPICS_REPORT_PATH
)
from src.evaluation.evaluate_sentiment import get_sentiment_evaluation_report
from src.evaluation.evaluate_popularity import get_popularity_evaluation_report

st.set_page_config(page_title="Model Performance - Windah Basudara AI Analytics", page_icon="🎯", layout="wide")

st.title("🎯 Halaman 5: Model Performance & Evaluation")
st.markdown("Transparansi evaluasi Machine Learning, perbandingan algoritma, dan validasi metrik sesuai PRD.")

# Tab Evaluasi
tab_pop, tab_sent, tab_top = st.tabs([
    "📈 Popularity Regression (Views)",
    "💬 Sentiment Classification (NLP)",
    "🏷️ Topic Clustering (KMeans)"
])

# ----------------- 1. POPULARITY EVALUATION -----------------
with tab_pop:
    st.subheader("Evaluasi & Perbandingan Model Regresi Views")
    pop_rep = get_popularity_evaluation_report()

    models_data = pop_rep.get("models", {})
    comparison_rows = []
    for key, data in models_data.items():
        comparison_rows.append({
            "Algoritma Model": data.get("model_name"),
            "MAE (Mean Absolute Error)": f"{data.get('mae', 0):,.0f}",
            "RMSE (Root Mean Squared Error)": f"{data.get('rmse', 0):,.0f}",
            "R² Score": f"{data.get('r2_score', 0):.4f}"
        })

    st.markdown("#### Tabel Perbandingan Terhadap Baseline")
    st.dataframe(pd.DataFrame(comparison_rows), use_container_width=True, hide_index=True)

    rf_mae = models_data.get("random_forest", {}).get("mae", 0)
    base_mae = models_data.get("baseline_median", {}).get("mae", 0)
    mae_diff = base_mae - rf_mae

    if mae_diff > 0:
        st.success(f"✅ **Target PRD Terpenuhi**: Model utama Random Forest berhasil mengungguli baseline median dengan selisih MAE sebesar **{mae_diff:,.0f} views** lebih akurat.")
    else:
        st.info("Model regresi siap dievaluasi lebih lanjut dengan penambahan snapshot data live API.")

    st.markdown("---")

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("#### Perbandingan Nilai MAE (Semakin Rendah Semakin Baik)")
        mae_df = pd.DataFrame([
            {"Model": v.get("model_name"), "MAE": v.get("mae")}
            for v in models_data.values()
        ])
        fig_mae = px.bar(
            mae_df,
            x="Model",
            y="MAE",
            text="MAE",
            color="Model",
            color_discrete_sequence=["#38BDF8", "#10B981", "#F59E0B", "#EF4444"],
            title="Nilai MAE Antar Model Regresi"
        )
        fig_mae.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig_mae.update_layout(
            template="plotly_dark",
            plot_bgcolor="#0F172A",
            paper_bgcolor="#1E293B",
            showlegend=False
        )
        st.plotly_chart(fig_mae, use_container_width=True)

    with col_chart2:
        st.markdown("#### Tingkat Kepentingan Fitur (Feature Importance)")
        feat_imp = pop_rep.get("feature_importance", {})
        feat_df = pd.DataFrame([
            {"Fitur": k, "Importance": v}
            for k, v in feat_imp.items()
        ]).sort_values(by="Importance", ascending=True).tail(8)

        fig_imp = px.bar(
            feat_df,
            x="Importance",
            y="Fitur",
            orientation="h",
            color="Importance",
            color_continuous_scale="Blues",
            title="Top Fitur Paling Berpengaruh (Random Forest)"
        )
        fig_imp.update_layout(
            template="plotly_dark",
            plot_bgcolor="#0F172A",
            paper_bgcolor="#1E293B"
        )
        st.plotly_chart(fig_imp, use_container_width=True)

# ----------------- 2. SENTIMENT EVALUATION -----------------
with tab_sent:
    st.subheader("Evaluasi Model Klasifikasi Sentimen Komentar")
    sent_rep = get_sentiment_evaluation_report()

    acc = sent_rep.get("accuracy", 0.0)
    macro_f1 = sent_rep.get("macro_f1", 0.0)
    p_macro = sent_rep.get("macro_precision", 0.0)
    r_macro = sent_rep.get("macro_recall", 0.0)

    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    s_col1.metric("Akurasi (Accuracy)", f"{acc * 100:.2f}%")
    s_col2.metric("Macro F1-Score", f"{macro_f1:.4f}")
    s_col3.metric("Macro Precision", f"{p_macro:.4f}")
    s_col4.metric("Macro Recall", f"{r_macro:.4f}")

    if macro_f1 >= 0.80:
        st.success(f"✅ **Target PRD Terpenuhi**: Model sentimen memiliki Macro F1 sebesar **{macro_f1:.2f}** (Target minimal 0.80 tercapai).")

    st.markdown("---")

    c_col1, c_col2 = st.columns(2)

    with c_col1:
        st.markdown("#### Confusion Matrix (Matriks Kebingungan)")
        cm = sent_rep.get("confusion_matrix", [[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        classes = sent_rep.get("classes", ["Positif", "Netral", "Negatif"])

        fig_cm = px.imshow(
            cm,
            text_auto=True,
            x=classes,
            y=classes,
            labels=dict(x="Prediksi Model", y="Aktual / Ground Truth", color="Jumlah"),
            color_continuous_scale="Teal",
            title="Confusion Matrix Sentimen Komentar"
        )
        fig_cm.update_layout(
            template="plotly_dark",
            plot_bgcolor="#0F172A",
            paper_bgcolor="#1E293B"
        )
        st.plotly_chart(fig_cm, use_container_width=True)

    with c_col2:
        st.markdown("#### Laporan Klasifikasi per Kelas")
        clf_rep = sent_rep.get("classification_report", {})
        clf_rows = []
        for cls in classes:
            c_data = clf_rep.get(cls, {})
            clf_rows.append({
                "Kelas": cls,
                "Precision": f"{c_data.get('precision', 0):.3f}",
                "Recall": f"{c_data.get('recall', 0):.3f}",
                "F1-Score": f"{c_data.get('f1-score', 0):.3f}",
                "Jumlah Sampel": c_data.get('support', 0)
            })
        st.dataframe(pd.DataFrame(clf_rows), use_container_width=True, hide_index=True)

# ----------------- 3. TOPIC CLUSTERING -----------------
with tab_top:
    st.subheader("Evaluasi Pengelompokan Klaster Topik Konten (KMeans)")
    st.markdown("Hasil pengelompokan tanpa supervisi menggunakan algoritma **TF-IDF + KMeans (k=5)**:")

    if TOPICS_REPORT_PATH.exists():
        with open(TOPICS_REPORT_PATH, "r", encoding="utf-8") as f:
            topics_data = json.load(f)

        topic_rows = []
        for c_id, info in topics_data.items():
            topic_rows.append({
                "ID Klaster": int(c_id),
                "Kategori Konten": info.get("category_name"),
                "Jumlah Video": info.get("video_count"),
                "Kata Kunci Teratas": ", ".join(info.get("top_keywords", []))
            })

        st.dataframe(pd.DataFrame(topic_rows), use_container_width=True, hide_index=True)
    else:
        st.info("Laporan klaster topik belum dibuat. Jalankan pipeline training topik.")
