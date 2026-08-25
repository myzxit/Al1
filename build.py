"""실행 파일 빌드 스크립트.

    python build.py

윈도우에서 돌리면 dist/Al1.exe, macOS에서는 dist/Al1.app,
리눅스에서는 dist/Al1 이 만들어진다. PyInstaller는 크로스 컴파일을 지원하지
않으므로 배포하려는 OS에서 각각 실행해야 한다.
(GitHub Actions로 세 OS를 한 번에 빌드하려면 .github/workflows/build.yml 참고)
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(*args: str) -> None:
    print("$", " ".join(args), flush=True)
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> int:
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller가 없습니다. 먼저 설치하세요:")
        print("    pip install -r requirements-dev.txt")
        return 1

    if not (ROOT / "assets" / "icon.png").exists():
        run(sys.executable, "tools/make_icon.py")

    for folder in ("build", "dist"):
        shutil.rmtree(ROOT / folder, ignore_errors=True)

    run(sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "Al1.spec")

    produced = sorted(p for p in (ROOT / "dist").iterdir())
    print("\n빌드 완료:")
    for path in produced:
        size = path.stat().st_size / (1024 * 1024) if path.is_file() else 0
        suffix = f"  ({size:.1f} MB)" if size else ""
        print(f"  {path}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
