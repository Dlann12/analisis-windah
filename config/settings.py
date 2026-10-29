import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# Directories
DATA_DIR = BASE_DIR / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
DATA_SAMPLES_DIR = DATA_DIR / "samples"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure directories exist
for directory in [DATA_RAW_DIR, DATA_PROCESSED_DIR, DATA_SAMPLES_DIR, MODELS_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# YouTube Settings
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
WINDAH_CHANNEL_ID = os.getenv("WINDAH_CHANNEL_ID", "UCZrqgLMYK2iV0sV8uN1_rAw")
WINDAH_PLAYLIST_ID = "UUZrqgLMYK2iV0sV8uN1_rAw" # Uploads playlist starts with UU

# Dataset File Paths
RAW_VIDEOS_PATH = DATA_RAW_DIR / "videos_raw.csv"
RAW_COMMENTS_PATH = DATA_RAW_DIR / "comments_raw.csv"
PROCESSED_VIDEOS_PATH = DATA_PROCESSED_DIR / "videos_clean.csv"
PROCESSED_COMMENTS_PATH = DATA_PROCESSED_DIR / "comments_clean.csv"
SAMPLE_VIDEOS_PATH = DATA_SAMPLES_DIR / "videos_seed.csv"
SAMPLE_COMMENTS_PATH = DATA_SAMPLES_DIR / "comments_seed.csv"

# Model File Paths
SENTIMENT_MODEL_PATH = MODELS_DIR / "sentiment_model.joblib"
POPULARITY_MODEL_PATH = MODELS_DIR / "popularity_model.joblib"
TOPIC_MODEL_PATH = MODELS_DIR / "topic_model.joblib"

# Evaluation Reports
SENTIMENT_REPORT_PATH = REPORTS_DIR / "sentiment_evaluation.json"
POPULARITY_REPORT_PATH = REPORTS_DIR / "popularity_evaluation.json"
TOPICS_REPORT_PATH = REPORTS_DIR / "topics_summary.json"

# Topic Categories
TOPIC_CATEGORIES = {
    0: "Horror Games",
    1: "Simulator & Casual Games",
    2: "Adventure & Story Games",
    3: "Mobile & Multiplayer Games",
    4: "Special, Charity & Reaction"
}
