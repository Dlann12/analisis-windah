# Windah Basudara YouTube AI Analytics

Sistem analisis kanal YouTube berbasis Machine Learning, NLP, dan Data Analytics interaktif untuk menganalisis performa video, sentimen komentar penonton, tren topik konten, serta memprediksi potensi views video baru kanal **Windah Basudara**.

Proyek ini dibangun berdasarkan spesifikasi **Product Requirements Document (PRD) Versi 1.0**.

---

## 📌 Ringkasan Hasil Training Machine Learning

Seluruh model telah dilatih dan dievaluasi dengan hasil metrik sebagai berikut:

### 1. Sentiment Analysis Classifier (NLP)
- **Model**: TF-IDF Vectorizer (Unigram + Bigram) + Logistic Regression (Multinomial, Balanced Class Weight)
- **Jumlah Data Training**: 450 komentar berlabel representatif (Positif, Netral, Negatif) dalam konteks gaming Indonesia.
- **Akurasi**: 100% pada test set evaluasi.
- **Macro F1-Score**: 1.0000 (Melampaui target PRD minimal 0.80).
- **Lokasi Model**: `models/sentiment_model.joblib`
- **Laporan Evaluasi**: `reports/sentiment_evaluation.json`

### 2. Video Popularity Prediction (Regression)
- **Model Utama**: Random Forest Regressor (200 estimators, max depth 8)
- **Target**: Estimasi jumlah views video.
- **Fitur Input**: Panjang judul, rasio kata kapital, tanda seru, durasi detik, jam tayang, hari tayang, weekend flag, umur video, dan klaster topik.
- **Hasil Evaluasi Komparasi Model**:
  - **Random Forest (Model Utama)**: MAE = **880,341** views | R² = **0.3236** (Performa Terbaik)
  - **Gradient Boosting**: MAE = **939,045** views | R² = **0.2287**
  - **Linear Regression**: MAE = **977,635** views | R² = **0.1273**
  - **Baseline (Median Views)**: MAE = **986,579** views | R² = **-0.0078**
- **Validasi Kriteria PRD**: Random Forest berhasil mengungguli Baseline Median sebesar **106,238 views lebih akurat**.
- **Lokasi Model**: `models/popularity_model.joblib`
- **Laporan Evaluasi**: `reports/popularity_evaluation.json`

### 3. Topic Content Clustering (Unsupervised Learning)
- **Model**: TF-IDF + KMeans Clustering (k = 5)
- **Klaster yang Terbentuk**:
  1. *Horror Games* (Resident Evil, DreadOut, FNAF, Poppy Playtime, Chilla's Art, Pamali)
  2. *Simulator & Casual Games* (Warnet Simulator, Bakso Simulator, Supermarket, Gas Station)
  3. *Adventure & Story Games* (GTA V, God of War Ragnarok, Wukong, Elden Ring, Spider-Man)
  4. *Mobile & Multiplayer Games* (Mobile Legends, Stumble Guys, Roblox, eFootball, Genshin)
  5. *Special, Charity & Reaction* (Charity 10 Juta Subs, Nobar Timnas, Marathon 10 Game, QnA)
- **Lokasi Model**: `models/topic_model.joblib`
- **Laporan Evaluasi**: `reports/topics_summary.json`

---

## 🚀 Fitur Dashboard Multi-Page (Streamlit)

Aplikasi dashboard terdiri dari 5 halaman terintegrasi:

1. **Halaman 1: YouTube Channel Overview** (`pages/1_Overview.py`):
   - Profil kanal, total video terindeks, akumulasi views, rata-rata views per video, dan rata-rata engagement rate.
   - Grafik histogram distribusi views dan tren publikasi video per tahun.
   - Tabel Top 10 Video paling populer.

2. **Halaman 2: Video Performance Analytics** (`pages/2_Video_Analytics.py`):
   - Pencarian judul video realtime dan filter dinamis berdasarkan tahun serta tema.
   - Grafik ranking Top 10 Views, Top 10 Likes, dan Top 10 Engagement Rate.
   - Alat komparasi antarvideo langsung (pilih 2-3 video dan bandingkan metrik berdampingan).

3. **Halaman 3: Comment Sentiment Analysis** (`pages/3_Sentiment_Analysis.py`):
   - Visualisasi pie chart proporsi sentimen dan bar chart distribusi sentimen.
   - Filter komentar berdasarkan kelas sentimen (Positif, Netral, Negatif).
   - Fitur **Interactive Live Tester**: masukkan komentar baru dan dapatkan prediksi sentimen instan beserta confidence score dan progress bar probabilitas.

4. **Halaman 4: ML Popularity Prediction** (`pages/4_ML_Prediction.py`):
   - Formulir interaktif untuk memasukkan rencana video (Judul, Durasi, Hari Upload, Jam Upload, Topik, Horizon Hari Tayang).
   - Prediksi views otomatis dengan interval ketidakpastian (+/- 15%).
   - Kategori performa: Moderate, Good, atau High (Viral Potential).
   - Visualisasi Gauge Meter perbandingan terhadap rata-rata kanal.
   - Rekomendasi taktis untuk kreator konten.

5. **Halaman 5: Model Performance & Evaluation** (`pages/5_Model_Performance.py`):
   - Transparansi metrik evaluasi model sesuai standar ilmiah ML.
   - Tabel perbandingan MAE, RMSE, dan R² antara Random Forest, Gradient Boosting, Linear Regression, dan Baseline.
   - Feature Importance bar chart.
   - Confusion Matrix heatmap dan Classification Report lengkap untuk model sentimen.
   - Rincian klaster topik konten KMeans.

---

## 🛠️ Instalasi dan Menjalankan Proyek

### 1. Kloning Repository & Setup Virtual Environment
```bash
git clone <repo-url>
cd analisis-yt-windah

# Buat virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependensi
pip install -r requirements.txt
```

### 2. Konfigurasi Environment Variable
Salin file template `.env.example` ke `.env`:
```bash
cp .env.example .env
```
Isi konfigurasi pada file `.env`:
```env
YOUTUBE_API_KEY=your_actual_youtube_data_api_v3_key
WINDAH_CHANNEL_ID=UCZrqgLMYK2iV0sV8uN1_rAw
```
> *Catatan:* Jika Anda belum memiliki YouTube Data API key, sistem secara otomatis menggunakan starter seed dataset lokal (121 video nyata Windah Basudara dan 450 komentar berlabel) sehingga seluruh dashboard dan model tetap berfungsi penuh 100%.

### 3. Melatih Ulang Model (Opsional)
Jika ingin menjalankan ulang seluruh pipeline training dan evaluasi Machine Learning:
```bash
PYTHONPATH=. ./venv/bin/python -m src.training.train_topics
PYTHONPATH=. ./venv/bin/python -m src.training.train_sentiment
PYTHONPATH=. ./venv/bin/python -m src.training.train_popularity
```

### 4. Menjalankan Automated Unit Tests
```bash
PYTHONPATH=. ./venv/bin/pytest tests/
```

### 5. Menjalankan Dashboard Streamlit
```bash
./venv/bin/streamlit run app.py
```
Aplikasi akan aktif di `http://localhost:8501`.

---

## 📂 Struktur Direktori Proyek

```text
analisis-yt-windah/
├── app.py                     # Entrypoint aplikasi Streamlit
├── requirements.txt           # Daftar pustaka Python
├── .env.example               # Template variabel environment API key
├── .gitignore                 # Konfigurasi pengabaian Git
├── README.md                  # Dokumentasi lengkap proyek
│
├── config/
│   └── settings.py            # Konfigurasi path dan environment
│
├── data/
│   ├── raw/                   # Dataset mentah dari API/scraping
│   ├── processed/             # Dataset bersih siap latih
│   └── samples/               # Starter seed dataset terkurasi
│
├── models/
│   ├── sentiment_model.joblib # Model klasifikasi sentimen tersimpan
│   ├── popularity_model.joblib# Model Random Forest regresi tersimpan
│   └── topic_model.joblib     # Model KMeans klastering tersimpan
│
├── src/
│   ├── data_collection/       # Modul YouTube Data API v3 & fallback
│   ├── preprocessing/         # Modul pembersihan teks, video & feature engineering
│   ├── training/              # Script training ketiga model ML
│   ├── evaluation/            # Script penghitungan metrik & report loader
│   └── prediction/            # Modul inferensi prediksi sentimen & views
│
├── pages/
│   ├── 1_Overview.py          # Dashboard Halaman 1
│   ├── 2_Video_Analytics.py   # Dashboard Halaman 2
│   ├── 3_Sentiment_Analysis.py# Dashboard Halaman 3
│   ├── 4_ML_Prediction.py     # Dashboard Halaman 4
│   └── 5_Model_Performance.py # Dashboard Halaman 5
│
├── reports/                   # File JSON hasil evaluasi model & metrik
└── tests/                     # Unit test otomatis (Pytest)
```

---

## ⚖️ Pemberitahuan Independensi
Proyek ini dibuat sebagai portofolio analisis data dan implementasi Machine Learning independen. Proyek ini tidak berafiliasi resmi dengan Brando Franco Windah (Windah Basudara), YouTube, atau Google LLC.
