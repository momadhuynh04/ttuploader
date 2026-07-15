import time
import json
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class PipelineLog:
    session_name: str
    video_id: str = ""
    video_title: str = ""
    video_duration: float = 0.0

    check_time: float = 0.0

    download_time: float = 0.0
    download_size_mb: float = 0.0

    render_time: float = 0.0
    render_strategy: str = ""
    render_before_mb: float = 0.0
    render_after_mb: float = 0.0

    upload_nav_time: float = 0.0
    upload_file_time: float = 0.0
    upload_caption_time: float = 0.0
    upload_post_wait_time: float = 0.0
    upload_total_time: float = 0.0

    total_time: float = 0.0
    success: bool = False
    error: str = ""
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S"))

    def to_dict(self) -> dict:
        d = {}
        for k, v in self.__dict__.items():
            if isinstance(v, float):
                d[k] = round(v, 2)
            else:
                d[k] = v
        return d


class PipelineLogger:
    def __init__(self, session_name: str):
        self.session_name = session_name
        self.log_dir = Path("logs") / session_name
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._current_log: PipelineLog | None = None

    def new_log(self) -> PipelineLog:
        self._current_log = PipelineLog(session_name=self.session_name)
        return self._current_log

    def flush(self):
        if self._current_log is None:
            return
        date_str = time.strftime("%Y-%m-%d")
        log_file = self.log_dir / f"{date_str}.log"
        entry = self._current_log.to_dict()
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        self._current_log = None

    def format_console(self, log: PipelineLog) -> str:
        lines = [
            f"[TIMELINE] {log.timestamp} | Session: {log.session_name} | Video: {log.video_id}",
            f"  ├── [CHECK]    Channel check: {log.check_time:.2f}s",
            f"  ├── [DOWNLOAD] Video download: {log.download_time:.2f}s | Raw Size: {log.download_size_mb:.1f} MB",
            f"  ├── [RENDER]   Strategy: {log.render_strategy} | Duration: {log.render_time:.2f}s",
            f"  │              Before: {log.render_before_mb:.1f} MB | After: {log.render_after_mb:.1f} MB",
            f"  ├── [UPLOAD]",
            f"  │   ├── [NAV]      Page load: {log.upload_nav_time:.2f}s",
            f"  │   ├── [FILE]     File injection: {log.upload_file_time:.2f}s",
            f"  │   ├── [CAPTION]  Caption fill: {log.upload_caption_time:.2f}s",
            f"  │   └── [POST]     Post wait: {log.upload_post_wait_time:.2f}s",
            f"  ├── [RESULT]   {'SUCCESS' if log.success else 'FAILED'} | Total pipeline: {log.total_time:.2f}s",
        ]
        if log.error:
            lines.append(f"  └── [ERROR]    {log.error}")
        return "\n".join(lines)
