"""자동 로그인 토큰을 로컬 파일에 보관한다."""

from __future__ import annotations

import json
from pathlib import Path

from . import config


class SessionStore:
    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path) if path is not None else config.session_path()

    def load(self) -> str | None:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        token = data.get("token")
        return token if isinstance(token, str) and token else None

    def save(self, token: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({"token": token}), encoding="utf-8")
        try:
            self.path.chmod(0o600)
        except OSError:
            # 일부 파일시스템(예: 윈도우 네트워크 드라이브)에서는 무시한다.
            pass

    def clear(self) -> None:
        try:
            self.path.unlink()
        except OSError:
            pass
