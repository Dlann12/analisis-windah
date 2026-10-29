import os
from typing import Optional
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from config.settings import YOUTUBE_API_KEY


class YouTubeClient:
    """Wrapper untuk YouTube Data API v3 dengan penanganan error dan kuota."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or YOUTUBE_API_KEY
        self.service: Optional[Resource] = None
        if self.api_key and self.api_key != "your_youtube_api_key_here":
            try:
                self.service = build("youtube", "v3", developerKey=self.api_key)
            except Exception as e:
                print(f"[YouTubeClient] Gagal menginisialisasi service: {e}")
                self.service = None

    def is_available(self) -> bool:
        """Cek apakah YouTube API siap digunakan."""
        return self.service is not None

    def get_channel_stats(self, channel_id: str) -> Optional[dict]:
        """Mengambil data statistik publik kanal YouTube."""
        if not self.is_available():
            return None
        try:
            request = self.service.channels().list(
                part="snippet,contentDetails,statistics",
                id=channel_id
            )
            response = request.execute()
            items = response.get("items", [])
            if not items:
                return None

            item = items[0]
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            content_details = item.get("contentDetails", {})
            uploads_playlist_id = content_details.get("relatedPlaylists", {}).get("uploads", "")

            return {
                "channel_id": channel_id,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "custom_url": snippet.get("customUrl", ""),
                "published_at": snippet.get("publishedAt", ""),
                "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "subscriber_count": int(stats.get("subscriberCount", 0)),
                "video_count": int(stats.get("videoCount", 0)),
                "view_count": int(stats.get("viewCount", 0)),
                "uploads_playlist_id": uploads_playlist_id
            }
        except HttpError as e:
            print(f"[YouTubeClient] HttpError saat get_channel_stats: {e}")
            return None
        except Exception as e:
            print(f"[YouTubeClient] Error tak terduga: {e}")
            return None
