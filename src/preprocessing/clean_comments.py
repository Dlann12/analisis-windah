import re
import html
import pandas as pd
from pathlib import Path
from config.settings import RAW_COMMENTS_PATH, PROCESSED_COMMENTS_PATH, SAMPLE_COMMENTS_PATH

# Kamus normalisasi slang umum bahasa Indonesia di YouTube
SLANG_DICT = {
    "bgt": "banget",
    "bngt": "banget",
    "gak": "tidak",
    "nggak": "tidak",
    "ga": "tidak",
    "g": "tidak",
    "dgn": "dengan",
    "tp": "tapi",
    "yg": "yang",
    "utk": "untuk",
    "klo": "kalau",
    "kalo": "kalau",
    "klau": "kalau",
    "bocil": "bocil",
    "bg": "bang",
    "bng": "bang",
    "krn": "karena",
    "sm": "sama",
    "udah": "sudah",
    "udh": "sudah",
    "blm": "belum",
    "bisaa": "bisa",
    "mantapp": "mantap",
    "gokill": "gokil",
    "lucuu": "lucu",
    "ngakakk": "ngakak"
}


def clean_text_id(text: str) -> str:
    """Membersihkan teks komentar bahasa Indonesia dari URL, tag HTML, dan noise karakter."""
    if not isinstance(text, str):
        return ""

    # Decode entitas HTML
    text = html.unescape(text)

    # Hapus URL
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)

    # Hapus mention pengguna (@username)
    text = re.sub(r"@\w+", " ", text)

    # Ganti emotikon tawa umum (wkwk, wkwkwk, hahaha) menjadi token seragam 'wkwk'
    text = re.sub(r"\b(w+k+w*|h+a+h+a*|h+e+h+e*)\b", "wkwk", text, flags=re.IGNORECASE)

    # Hapus karakter non-alfanumerik berlebih tetapi simpan spasi dan tanda baca wajar
    text = re.sub(r"[^\w\s\?!.,]", " ", text)

    # Normalisasi per kata menggunakan kamus slang
    tokens = text.lower().split()
    normalized_tokens = [SLANG_DICT.get(token, token) for token in tokens]
    cleaned = " ".join(normalized_tokens)

    # Hapus multiple spasi
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


def clean_comments_data(
    input_path: Path = RAW_COMMENTS_PATH,
    output_path: Path = PROCESSED_COMMENTS_PATH
) -> pd.DataFrame:
    """Membersihkan dataset komentar dan memfilter komentar kosong."""
    if not input_path.exists():
        if SAMPLE_COMMENTS_PATH.exists():
            input_path = SAMPLE_COMMENTS_PATH
        else:
            raise FileNotFoundError(f"File raw comments tidak ditemukan di {input_path}")

    df = pd.read_csv(input_path)

    # 1. Hapus duplikasi comment_id
    if "comment_id" in df.columns:
        df = df.drop_duplicates(subset=["comment_id"]).copy()

    # 2. Bersihkan teks komentar
    df["clean_text"] = df["comment_text"].apply(clean_text_id)

    # 3. Filter komentar yang setelah dibersihkan terlalu pendek
    df = df[df["clean_text"].str.len() >= 3].copy()

    # 4. Standarisasi kolom numerik
    if "like_count" in df.columns:
        df["like_count"] = pd.to_numeric(df["like_count"], errors="coerce").fillna(0).astype(int)

    # 5. Standarisasi sentiment label
    if "sentiment_label" in df.columns:
        valid_labels = {"Positif", "Netral", "Negatif"}
        df["sentiment_label"] = df["sentiment_label"].astype(str).str.capitalize()
        # Jika ada label yang tidak valid, isi default Netral
        df["sentiment_label"] = df["sentiment_label"].apply(lambda x: x if x in valid_labels else "Netral")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[clean_comments] Berhasil membersihkan {len(df)} komentar ke {output_path}")

    return df


if __name__ == "__main__":
    df_clean = clean_comments_data()
    print("Contoh komentar bersih:", df_clean[["comment_text", "clean_text", "sentiment_label"]].head())
