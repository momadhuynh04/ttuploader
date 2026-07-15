import asyncio
import re
from urllib.parse import urlparse

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class VideoMeta:
    def __init__(self, data: dict):
        snippet = data.get("snippet", {})
        content = data.get("contentDetails", {})
        vid = data.get("id", "")
        if isinstance(vid, dict):
            self.video_id: str = vid.get("videoId", "")
        else:
            self.video_id: str = str(vid)
        self.title: str = snippet.get("title", "")
        self.description: str = snippet.get("description", "")
        self.published_at: str = snippet.get("publishedAt", "")
        self.channel_title: str = snippet.get("channelTitle", "")
        duration_raw = content.get("duration", "PT0S")
        self.duration_seconds: float = self._parse_duration(duration_raw)
        self.url: str = f"https://www.youtube.com/shorts/{self.video_id}"

    def _parse_duration(self, duration: str) -> float:
        match = re.match(
            r"PT(?:(\d+(?:\.\d+)?)H)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)S)?",
            duration,
        )
        if not match:
            return 0.0
        h, m, s = match.groups()
        return float(h or 0) * 3600 + float(m or 0) * 60 + float(s or 0)

    def __repr__(self):
        return f"VideoMeta(id={self.video_id}, title={self.title[:30]}...)"


class YouTubeAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.youtube = build("youtube", "v3", developerKey=api_key)

    async def resolve_channel_id(self, channel_input: str) -> str:
        if re.match(r"^UC[\w-]{22}$", channel_input):
            return channel_input

        if "youtube.com/@" in channel_input:
            handle = channel_input.split("@")[-1].split("/")[0]
            return await self._resolve_by_handle(handle)

        if "youtube.com/channel/" in channel_input:
            return channel_input.split("channel/")[-1].split("/")[0]

        return await self._resolve_by_handle(channel_input.lstrip("@"))

    async def _resolve_by_handle(self, handle: str) -> str:
        loop = asyncio.get_event_loop()
        try:
            request = self.youtube.search().list(
                part="snippet", q=f"@{handle}", type="channel", maxResults=1
            )
            response = await loop.run_in_executor(None, request.execute)
            items = response.get("items", [])
            if items:
                return items[0]["snippet"]["channelId"]
        except HttpError as e:
            raise ValueError(f"API error when resolving channel '{handle}': {e}") from e
        raise ValueError(f"Không tìm thấy channel: {handle}")

    async def get_latest_shorts(self, channel_id: str, max_results: int = 5) -> list[VideoMeta]:
        loop = asyncio.get_event_loop()
        request = self.youtube.search().list(
            part="snippet",
            channelId=channel_id,
            type="video",
            videoDuration="short",
            order="date",
            maxResults=max_results,
        )
        response = await loop.run_in_executor(None, request.execute)
        items = response.get("items", [])
        video_ids = [
            item["id"]["videoId"]
            for item in items
            if item.get("id", {}).get("videoId")
        ]
        return await self._get_video_details(video_ids)

    async def _get_video_details(self, video_ids: list[str]) -> list[VideoMeta]:
        if not video_ids:
            return []
        loop = asyncio.get_event_loop()
        request = self.youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=",".join(video_ids),
        )
        response = await loop.run_in_executor(None, request.execute)
        return [VideoMeta(item) for item in response.get("items", [])]
