"""번들된 리소스 경로 찾기.

PyInstaller로 묶으면 리소스가 임시 폴더(sys._MEIPASS)에 풀린다.
소스로 실행할 때는 저장소 루트를 기준으로 찾는다.
"""

from __future__ import annotations

import sys
from pathlib import Path


def base_dir() -> Path:
    bundled = getattr(sys, "_MEIPASS", None)
    if bundled:
        return Path(bundled)
    return Path(__file__).resolve().parent.parent


def resource_path(*parts: str) -> Path:
    return base_dir().joinpath(*parts)


def icon_path() -> Path | None:
    path = resource_path("assets", "icon.png")
    return path if path.exists() else None
