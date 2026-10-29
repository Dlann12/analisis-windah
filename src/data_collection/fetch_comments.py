import datetime
import pandas as pd
from typing import List, Dict, Any, Optional
from googleapiclient.errors import HttpError
from config.settings import RAW_COMMENTS_PATH, SAMPLE_COMMENTS_PATH
from src.data_collection.youtube_client import YouTubeClient


def fetch_video_comments(
    video_id: str,
    client: Optional[YouTubeClient] = None,
    max_comments: int = 50
) -> List[Dict[str, Any]]:
    """Mengambil sampel komentar publik dari satu video YouTube."""
    if client is None:
        client = YouTubeClient()

    if not client.is_available():
        return []

    comments_list: List[Dict[str, Any]] = []
    collected_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    try:
        request = client.service.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(50, max_comments),
            textFormat="plainText"
        )
        response = request.execute()

        for item in response.get("items", []):
            top_level = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
            comments_list.append({
                "comment_id": item.get("id", ""),
                "video_id": video_id,
                "comment_text": top_level.get("textDisplay", ""),
                "like_count": int(top_level.get("likeCount", 0)),
                "published_at": top_level.get("publishedAt", ""),
                "collected_at": collected_at,
                "sentiment_label": ""  # Label diisi oleh model atau manual
            })
    except HttpError as e:
        print(f"[fetch_comments] Error mengambil komentar untuk video {video_id}: {e}")
    except Exception as e:
        print(f"[fetch_comments] Exception pada video {video_id}: {e}")

    return comments_list


def fetch_comments_for_dataset(
    video_ids: List[str],
    max_per_video: int = 20,
    client: Optional[YouTubeClient] = None
) -> pd.DataFrame:
    """Mengambil sampel komentar untuk daftar video dan menyimpan ke raw CSV."""
    if client is None:
        client = YouTubeClient()

    if not client.is_available():
        print("[fetch_comments] API tidak aktif. Menggunakan sampel komentar lokal.")
        if RAW_COMMENTS_PATH.exists():
            return pd.read_csv(RAW_COMMENTS_PATH)
        elif SAMPLE_COMMENTS_PATH.exists():
            return pd.read_csv(SAMPLE_COMMENTS_PATH)
        return pd.DataFrame()

    all_comments: List[Dict[str, Any]] = []
    for vid in video_ids:
        comments = fetch_video_comments(vid, client=client, max_comments=max_per_video)
        all_comments.extend(comments)

    df = pd.DataFrame(all_comments)
    if not df.empty:
        df.to_csv(RAW_COMMENTS_PATH, index=False)
        print(f"[fetch_comments] Berhasil menyimpan {len(df)} komentar ke {RAW_COMMENTS_PATH}")
        return df

    if RAW_COMMENTS_PATH.exists():
        return pd.read_csv(RAW_COMMENTS_PATH)
    return pd.DataFrame()


if __name__ == "__main__":
    if RAW_COMMENTS_PATH.exists():
        df_c = pd.read_csv(RAW_COMMENTS_PATH)
        print(f"Komentar tersimpan: {len(df_c)}")
