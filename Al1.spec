# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 빌드 설정 — 단일 실행 파일(onefile), 콘솔 창 없음.

    pyinstaller Al1.spec        (또는 python build.py)
"""

import sys
from pathlib import Path

ROOT = Path(SPECPATH).resolve()  # noqa: F821 - PyInstaller가 주입한다


def _icon() -> str | None:
    if sys.platform.startswith("win"):
        candidate = ROOT / "assets" / "icon.ico"
    elif sys.platform == "darwin":
        candidate = ROOT / "assets" / "icon.icns"
    else:
        candidate = ROOT / "assets" / "icon.png"
    return str(candidate) if candidate.exists() else None


# 이 앱이 쓰지 않는 Qt 모듈과 표준 라이브러리를 빼서 실행 파일을 줄인다.
EXCLUDES = [
    "tkinter",
    "PySide6.Qt3DAnimation",
    "PySide6.Qt3DCore",
    "PySide6.Qt3DExtras",
    "PySide6.Qt3DInput",
    "PySide6.Qt3DLogic",
    "PySide6.Qt3DRender",
    "PySide6.QtCharts",
    "PySide6.QtDataVisualization",
    "PySide6.QtMultimedia",
    "PySide6.QtMultimediaWidgets",
    "PySide6.QtNetwork",
    "PySide6.QtOpenGL",
    "PySide6.QtOpenGLWidgets",
    "PySide6.QtPdf",
    "PySide6.QtPdfWidgets",
    "PySide6.QtPositioning",
    "PySide6.QtQml",
    "PySide6.QtQuick",
    "PySide6.QtQuick3D",
    "PySide6.QtQuickWidgets",
    "PySide6.QtRemoteObjects",
    "PySide6.QtSensors",
    "PySide6.QtSerialPort",
    "PySide6.QtSql",
    "PySide6.QtSvg",
    "PySide6.QtTest",
    "PySide6.QtWebChannel",
    "PySide6.QtWebEngineCore",
    "PySide6.QtWebEngineWidgets",
    "PySide6.QtWebSockets",
]

a = Analysis(  # noqa: F821
    ["main.py"],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[(str(ROOT / "assets"), "assets")],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=EXCLUDES,
    noarchive=False,
)

pyz = PYZ(a.pure)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Al1",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,          # 실행할 때 검은 콘솔 창이 뜨지 않는다
    disable_windowed_traceback=False,
    icon=_icon(),
)

if sys.platform == "darwin":
    app = BUNDLE(  # noqa: F821
        exe,
        name="Al1.app",
        icon=_icon(),
        bundle_identifier="kr.al1.account",
    )
