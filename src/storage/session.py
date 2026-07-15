import json
import time
from pathlib import Path
from dataclasses import dataclass, field, asdict


@dataclass
class SessionState:
    session_name: str
    created_at: str = ""
    last_check: str = ""
    total_uploaded: int = 0
    total_failed: int = 0
    region: str = "US"
    env_file: str = ".env"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SessionState":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class SessionStorage:
    def __init__(self, session_name: str):
        self.session_name = session_name
        self.data_dir = Path("data/sessions") / session_name
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.uploaded_file = self.data_dir / "uploaded.txt"
        self.state_file = self.data_dir / "session.json"
        self.archive_file = self.data_dir / "download_archive.txt"
        self.state = self._load_state()
        self._ensure_files()

    def _ensure_files(self):
        self.uploaded_file.touch(exist_ok=True)
        self.archive_file.touch(exist_ok=True)

    def _load_state(self) -> SessionState:
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text(encoding="utf-8"))
                return SessionState.from_dict(data)
            except Exception:
                pass
        now = time.strftime("%Y-%m-%dT%H:%M:%S")
        return SessionState(session_name=self.session_name, created_at=now)

    def save_state(self):
        self.state.last_check = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.state_file.write_text(
            json.dumps(self.state.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def is_uploaded(self, video_id: str) -> bool:
        if not self.uploaded_file.exists():
            return False
        ids = self._read_ids()
        return video_id.strip() in ids

    def mark_uploaded(self, video_id: str):
        with open(self.uploaded_file, "a", encoding="utf-8") as f:
            f.write(video_id.strip() + "\n")
        self.state.total_uploaded += 1
        self.save_state()

    def mark_failed(self):
        self.state.total_failed += 1
        self.save_state()

    def _read_ids(self) -> set[str]:
        return set(
            line.strip()
            for line in self.uploaded_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )

    def get_uploaded_ids(self) -> list[str]:
        return sorted(self._read_ids())

    def get_log_dir(self) -> Path:
        log_dir = Path("logs") / self.session_name
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir

    def get_download_dir(self) -> Path:
        download_dir = Path("downloads") / self.session_name
        download_dir.mkdir(parents=True, exist_ok=True)
        return download_dir
