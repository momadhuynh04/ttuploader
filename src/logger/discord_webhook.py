import aiohttp
from src.logger.pipeline import PipelineLog


async def send_discord_webhook(webhook_url: str, log: PipelineLog) -> bool:
    if not webhook_url:
        return False

    color = 0x00FF00 if log.success else 0xFF0000

    embed = {
        "title": f"{'Upload Thành Công' if log.success else 'Upload Thất Bại'} — {log.video_title or 'Untitled'}",
        "color": color,
        "fields": [
            {"name": "Session", "value": log.session_name, "inline": True},
            {"name": "Video ID", "value": log.video_id, "inline": True},
            {"name": "Duration", "value": f"{log.video_duration:.0f}s", "inline": True},
            {"name": "📥 Download", "value": f"{log.download_size_mb:.1f}MB — {log.download_time:.2f}s", "inline": True},
            {"name": "🎬 Render", "value": f"{log.render_strategy} — {log.render_time:.2f}s", "inline": True},
            {"name": "📤 Upload", "value": f"{log.upload_total_time:.2f}s", "inline": True},
            {"name": "⏱️ Total", "value": f"{log.total_time:.2f}s", "inline": True},
            {"name": "🔗 YouTube", "value": f"https://youtube.com/shorts/{log.video_id}", "inline": False},
        ],
        "footer": {"text": f"ttuploader • {log.timestamp}"},
    }

    if log.error:
        embed["fields"].append(
            {"name": "❌ Error", "value": log.error[:1024], "inline": False}
        )

    payload = {"embeds": [embed]}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as resp:
                return resp.status == 204
    except Exception:
        return False


async def send_discord_startup(webhook_url: str, session_name: str, region: str):
    if not webhook_url:
        return
    embed = {
        "title": "🚀 Bot Khởi Động",
        "color": 0x3498DB,
        "fields": [
            {"name": "Session", "value": session_name, "inline": True},
            {"name": "Region", "value": region, "inline": True},
            {"name": "Status", "value": "Running", "inline": True},
        ],
    }
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(webhook_url, json={"embeds": [embed]})
    except Exception:
        pass


async def send_discord_shutdown(webhook_url: str, session_name: str, total_uploaded: int):
    if not webhook_url:
        return
    embed = {
        "title": "🛑 Bot Dừng",
        "color": 0xE74C3C,
        "fields": [
            {"name": "Session", "value": session_name, "inline": True},
            {"name": "Total Uploaded", "value": str(total_uploaded), "inline": True},
        ],
    }
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(webhook_url, json={"embeds": [embed]})
    except Exception:
        pass
