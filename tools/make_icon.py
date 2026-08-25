"""앱 아이콘(assets/icon.png, assets/icon.ico)을 생성한다.

Qt로 PNG를 그린 뒤, PNG를 그대로 감싸는 ICO 파일을 손으로 조립한다.
(Vista 이후 윈도우는 PNG를 담은 ICO를 그대로 읽는다.)

    python tools/make_icon.py
"""

from __future__ import annotations

import os
import struct
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QRectF, Qt  # noqa: E402
from PySide6.QtGui import (  # noqa: E402
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPixmap,
)
from PySide6.QtWidgets import QApplication  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SIZE = 256
ICO_SIZES = (16, 32, 48, 64, 128, 256)


def draw(size: int) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0.0, QColor("#3b82f6"))
    gradient.setColorAt(1.0, QColor("#1e40af"))
    painter.setBrush(QBrush(gradient))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(QRectF(0, 0, size, size), size * 0.22, size * 0.22)

    font = QFont()
    font.setBold(True)
    font.setPixelSize(int(size * 0.5))
    painter.setFont(font)
    painter.setPen(QColor("#ffffff"))
    painter.drawText(
        QRectF(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, "A1"
    )
    painter.end()
    return pixmap


def png_bytes(size: int) -> bytes:
    path = ASSETS / f"_tmp_{size}.png"
    draw(size).save(str(path), "PNG")
    data = path.read_bytes()
    path.unlink()
    return data


def write_ico(path: Path, sizes: tuple[int, ...]) -> None:
    images = [(size, png_bytes(size)) for size in sizes]
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = len(header) + 16 * len(images)

    entries = bytearray()
    payload = bytearray()
    for size, data in images:
        # ICO 디렉터리에서 256은 0으로 기록한다.
        entries += struct.pack(
            "<BBBBHHII",
            size if size < 256 else 0,
            size if size < 256 else 0,
            0,
            0,
            1,
            32,
            len(data),
            offset,
        )
        payload += data
        offset += len(data)

    path.write_bytes(header + bytes(entries) + bytes(payload))


def main() -> int:
    app = QApplication(sys.argv)  # noqa: F841 - QPixmap 사용에 필요
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw(SIZE).save(str(ASSETS / "icon.png"), "PNG")
    write_ico(ASSETS / "icon.ico", ICO_SIZES)
    print(f"wrote {ASSETS / 'icon.png'} and {ASSETS / 'icon.ico'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
