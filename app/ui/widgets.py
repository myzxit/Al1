"""페이지들이 함께 쓰는 작은 위젯 helper."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


def card(parent: QWidget | None = None) -> QFrame:
    frame = QFrame(parent)
    frame.setObjectName("Card")
    return frame


def title_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("Title")
    return label


def subtitle_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("Subtitle")
    label.setWordWrap(True)
    return label


def caption_label(text: str) -> QLabel:
    """줄바꿈하지 않는 짧은 안내 문구 (카드 하단 링크 옆 등)."""
    label = QLabel(text)
    label.setObjectName("Subtitle")
    return label


def message_label() -> QLabel:
    """오류/성공 문구를 표시하는 자리. 기본은 빈 문자열."""
    label = QLabel("")
    label.setObjectName("Error")
    label.setWordWrap(True)
    return label


def show_error(label: QLabel, text: str) -> None:
    label.setObjectName("Error")
    label.setText(text)
    _restyle(label)


def show_success(label: QLabel, text: str) -> None:
    label.setObjectName("Success")
    label.setText(text)
    _restyle(label)


def clear_message(label: QLabel) -> None:
    label.setText("")


def _restyle(widget: QWidget) -> None:
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)


def mark_invalid(field: QLineEdit, invalid: bool) -> None:
    field.setProperty("invalid", "true" if invalid else "false")
    _restyle(field)


def field(label_text: str, editor: QLineEdit) -> QWidget:
    """라벨 + 입력칸을 세로로 묶는다."""
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(5)
    label = QLabel(label_text)
    label.setObjectName("FieldLabel")
    layout.addWidget(label)
    layout.addWidget(editor)
    return container


class PasswordEdit(QLineEdit):
    """오른쪽 끝에 표시/숨김 토글이 붙은 비밀번호 입력칸."""

    def __init__(self, placeholder: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setEchoMode(QLineEdit.EchoMode.Password)
        self.setPlaceholderText(placeholder)

        self._toggle = QToolButton(self)
        self._toggle.setObjectName("Link")
        self._toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle.setText("보기")
        self._toggle.setStyleSheet(
            "QToolButton { border: none; background: transparent; color: #7aa7ff; }"
        )
        self._toggle.clicked.connect(self._toggle_echo)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.addStretch(1)
        layout.addWidget(self._toggle)
        self.setTextMargins(0, 0, self._toggle.sizeHint().width() + 6, 0)

    def _toggle_echo(self) -> None:
        hidden = self.echoMode() == QLineEdit.EchoMode.Password
        self.setEchoMode(
            QLineEdit.EchoMode.Normal if hidden else QLineEdit.EchoMode.Password
        )
        self._toggle.setText("숨김" if hidden else "보기")


def link_button(text: str) -> QPushButton:
    button = QPushButton(text)
    button.setObjectName("Link")
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setFlat(True)
    return button


def primary_button(text: str) -> QPushButton:
    button = QPushButton(text)
    button.setObjectName("Primary")
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setMinimumHeight(40)
    return button


def secondary_button(text: str) -> QPushButton:
    button = QPushButton(text)
    button.setObjectName("Secondary")
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setMinimumHeight(38)
    return button


def danger_button(text: str) -> QPushButton:
    button = QPushButton(text)
    button.setObjectName("Danger")
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setMinimumHeight(38)
    return button
