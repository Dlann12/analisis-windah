import re
import datetime
import pandas as pd
from typing import List, Dict, Any, Optional
from googleapiclient.errors import HttpError
from config.settings import RAW_VIDEOS_PATH, SAMPLE_VIDEOS_PATH, WINDAH_PLAYLIST_ID
from src.data_collection.youtube_client import YouTubeClient


def parse_duration_to_seconds(duration_str: str) -> int:
    """Mengonversi durasi format ISO 8601 (PT#H#M#S) ke satuan detik."""
    if not duration_str:
        return 0
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration_str)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


def fetch_channel_videos(
    client: Optional[YouTubeClient] = None,
    playlist_id: str = WINDAH_PLAYLIST_ID,
    max_videos: int = 150
) -> pd.DataFrame:
    """
    Mengambil metadata video publik dari uploads playlist YouTube.
    Jika API tidak tersedia atau kuota habis, menggunakan data raw lokal.
    """
    if client is None:
        client = YouTubeClient()

    if not client.is_available():
        print("[fetch_videos] YouTube API key belum dikonfigurasi. Menggunakan dataset lokal.")
        if RAW_VIDEOS_PATH.exists():
            return pd.read_csv(RAW_VIDEOS_PATH)
        elif SAMPLE_VIDEOS_PATH.exists():
            return pd.read_csv(SAMPLE_VIDEOS_PATH)
        return pd.DataFrame()

    videos_data: List[Dict[str, Any]] = []
    collected_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    try:
        playlist_items_request = client.service.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=min(50, max_videos)
        )

        video_ids = []
        while playlist_items_request and len(video_ids) < max_videos:
            playlist_response = playlist_items_request.execute()
            for item in playlist_response.get("items", []):
                vid = item.get("contentDetails", {}).get("videoId")
                if vid:
                    video_ids.append(vid)

            playlist_items_request = client.service.playlistItems().list_next(
                playlist_items_request, playlist_response
            )

        print(f"[fetch_videos] Ditemukan {len(video_ids)} video ID. Mengambil detail statistik...")

        # Batch request 50 videos
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i + 50]
            video_request = client.service.videos().list(
                part="snippet,contentDetails,statistics",
                id=",".join(batch_ids)
            )
            video_response = video_request.execute()

            for item in video_response.get("items", []):
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                content_details = item.get("contentDetails", {})

                duration_iso = content_details.get("duration", "PT0S")
                duration_sec = parse_duration_to_seconds(duration_iso)

                videos_data.append({
                    "video_id": item.get("id", ""),
                    "title": snippet.get("title", ""),
                    "published_at": snippet.get("publishedAt", ""),
                    "duration_seconds": duration_sec,
                    "view_count": int(stats.get("viewCount", 0)),
                    "like_count": int(stats.get("likeCount", 0)),
                    "comment_count": int(stats.get("commentCount", 0)),
                    "description": snippet.get("description", ""),
                    "category_id": int(snippet.get("categoryId", 20)),
                    "collected_at": collected_at
                })

        df = pd.DataFrame(videos_data)
        if not df.empty:
            df.to_csv(RAW_VIDEOS_PATH, index=False)
            print(f"[fetch_videos] Berhasil menyimpan {len(df)} video ke {RAW_VIDEOS_PATH}")
            return df

    except HttpError as e:
        print(f"[fetch_videos] HttpError: {e}. Menggunakan dataset lokal.")
    except Exception as e:
        print(f"[fetch_videos] Gagal mengambil video dari API: {e}. Menggunakan dataset lokal.")

    if RAW_VIDEOS_PATH.exists():
        return pd.read_csv(RAW_VIDEOS_PATH)
    return pd.DataFrame()


if __name__ == "__main__":
    df_result = fetch_channel_videos()
    print(f"Total video yang didapatkan: {len(df_result)}")
