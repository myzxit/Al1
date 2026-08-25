"""앱 이름과 데이터 저장 위치."""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "Al1"
APP_TITLE = "Al1 계정"
DB_FILENAME = "accounts.db"
SESSION_FILENAME = "session.json"

# 자동 로그인 토큰 유효 기간(일)
SESSION_DAYS = 14


def data_dir() -> Path:
    """플랫폼별 사용자 데이터 디렉터리. AL1_DATA_DIR 환경변수로 덮어쓸 수 있다."""
    override = os.environ.get("AL1_DATA_DIR")
    if override:
        path = Path(override)
    elif sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming"
        path = Path(base) / APP_NAME
    elif sys.platform == "darwin":
        path = Path.home() / "Library" / "Application Support" / APP_NAME
    else:
        base = os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share"
        path = Path(base) / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def db_path() -> Path:
    return data_dir() / DB_FILENAME


def session_path() -> Path:
    return data_dir() / SESSION_FILENAME
