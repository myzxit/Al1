"""Al1 — 회원가입 / 로그인 데스크톱 앱 진입점.

    python main.py
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app import __version__
from app.config import APP_NAME, APP_TITLE
from app.database import Database
from app.ui.main_window import MainWindow
from app.ui.styles import STYLESHEET


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_TITLE)
    app.setApplicationVersion(__version__)
    app.setStyleSheet(STYLESHEET)

    db = Database()
    window = MainWindow(db)
    window.show()
    try:
        return app.exec()
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
