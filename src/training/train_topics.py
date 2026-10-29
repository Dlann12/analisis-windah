import json
import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from config.settings import (
    PROCESSED_VIDEOS_PATH, TOPIC_MODEL_PATH, TOPICS_REPORT_PATH,
    TOPIC_CATEGORIES
)
from src.preprocessing.feature_engineering import prepare_processed_videos


# Kata kunci penentu topik konten Windah Basudara
TOPIC_KEYWORDS = {
    "Horror Games": ["horror", "seram", "hantu", "resident", "evil", "dreadout", "fnaf", "poppy", "chilla", "pulang", "pamali", "slender", "granny", "outlast", "nightmares", "misteri"],
    "Simulator & Casual Games": ["simulator", "warnet", "bakso", "supermarket", "gas", "station", "streamer", "goat", "kebab", "tcg", "card", "flipper", "cooking", "toilet", "police"],
    "Adventure & Story Games": ["gta", "god of war", "kratos", "wukong", "elden", "ring", "spiderman", "last of us", "ghost", "tsushima", "red dead", "bully", "minecraft", "assassin", "cyberpunk", "witcher"],
    "Mobile & Multiplayer Games": ["mobile legends", "stumble", "guys", "fc 24", "efootball", "genshin", "honkai", "roblox", "among us", "fall guys", "free fire", "pubg", "brawl", "valorant", "mabar"],
    "Special, Charity & Reaction": ["charity", "amal", "subscriber", "reaksi", "reaction", "lucu", "nobar", "timnas", "tamat", "qna", "unboxing", "diamond", "ulang tahun", "meet", "vlog", "podcast"]
}


def rule_match_topic(text: str) -> str:
    """Mencocokkan kategori berbasis kata kunci gaming Windah."""
    text_lower = text.lower()
    scores = {}
    for topic, kw_list in TOPIC_KEYWORDS.items():
        score = sum(1 for kw in kw_list if kw in text_lower)
        scores[topic] = score

    best_topic = max(scores, key=scores.get)
    if scores[best_topic] > 0:
        return best_topic
    return "Adventure & Story Games"


def train_topic_model(k_clusters: int = 5) -> dict:
    """Melatih KMeans Clustering dengan fitur TF-IDF teks judul & deskripsi video."""
    df = prepare_processed_videos()

    # Gabungkan teks judul dan deskripsi
    corpus = (df["title"].fillna("") + " " + df["description"].fillna("")).tolist()

    # TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(
        max_features=400,
        ngram_range=(1, 2),
        stop_words=["dan", "di", "ke", "dari", "ini", "yang", "untuk", "pada", "part", "game", "windah", "basudara", "bocil", "kematian"]
    )
    X = vectorizer.fit_transform(corpus)

    # KMeans
    kmeans = KMeans(n_clusters=k_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X)

    df["topic_cluster"] = cluster_labels

    # Petakan setiap cluster ke label kategori yang paling representatif
    cluster_to_name = {}
    for c in range(k_clusters):
        cluster_titles = df[df["topic_cluster"] == c]["title"].tolist()
        combined_text = " ".join(cluster_titles)
        mapped_name = rule_match_topic(combined_text)
        cluster_to_name[c] = mapped_name

    # Hindari nama cluster duplikat dengan fallback
    used_names = set()
    for c in range(k_clusters):
        name = cluster_to_name[c]
        if name in used_names:
            # Cari kategori yang belum terpakai dari daftar default
            for default_name in TOPIC_CATEGORIES.values():
                if default_name not in used_names:
                    cluster_to_name[c] = default_name
                    break
        used_names.add(cluster_to_name[c])

    # Tetapkan label topik berbasis gabungan rule dan cluster
    df["topic_label"] = df.apply(
        lambda r: rule_match_topic(r["title"]) if rule_match_topic(r["title"]) else cluster_to_name.get(r["topic_cluster"], "Lainnya"),
        axis=1
    )

    # Simpan kembali dataset dengan kolom topic
    df.to_csv(PROCESSED_VIDEOS_PATH, index=False)

    # Simpan model
    model_payload = {
        "vectorizer": vectorizer,
        "kmeans": kmeans,
        "cluster_to_name": cluster_to_name
    }
    TOPIC_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_payload, TOPIC_MODEL_PATH)
    print(f"[train_topics] Model topik disimpan ke {TOPIC_MODEL_PATH}")

    # Ekstrak kata kunci teratas per cluster
    terms = vectorizer.get_feature_names_out()
    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]

    cluster_summaries = {}
    for c in range(k_clusters):
        top_terms = [terms[ind] for ind in order_centroids[c, :8]]
        count = int((df["topic_cluster"] == c).sum())
        cluster_summaries[str(c)] = {
            "cluster_id": c,
            "category_name": cluster_to_name[c],
            "video_count": count,
            "top_keywords": top_terms
        }

    # Simpan ringkasan ke JSON
    TOPICS_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(TOPICS_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(cluster_summaries, f, indent=2, ensure_ascii=False)
    print(f"[train_topics] Ringkasan topik disimpan ke {TOPICS_REPORT_PATH}")

    return cluster_summaries


if __name__ == "__main__":
    summaries = train_topic_model()
    for c_id, info in summaries.items():
        print(f"Cluster {c_id} ({info['category_name']}): {info['top_keywords']}")
