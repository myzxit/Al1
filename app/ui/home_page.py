"""로그인 후 화면 — 계정 정보, 비밀번호 변경, 로그아웃, 회원탈퇴."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from ..database import AccountError, Database, User
from . import widgets as w


def _format_time(value: str | None) -> str:
    if not value:
        return "-"
    try:
        return datetime.fromisoformat(value).astimezone().strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return value


class HomePage(QWidget):
    logged_out = Signal()
    account_deleted = Signal()

    def __init__(self, db: Database, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.db = db
        self.user: User | None = None
        self._build()

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addStretch(1)

        card = w.card()
        card.setMaximumWidth(460)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)

        self.greeting = w.title_label("")
        layout.addWidget(self.greeting)
        layout.addWidget(w.subtitle_label("로그인되었습니다."))
        layout.addSpacing(6)

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(8)
        self.username_value = QLabel("-")
        self.email_value = QLabel("-")
        self.created_value = QLabel("-")
        self.last_login_value = QLabel("-")
        for label_text, value in (
            ("아이디", self.username_value),
            ("이메일", self.email_value),
            ("가입일", self.created_value),
            ("최근 로그인", self.last_login_value),
        ):
            key = QLabel(label_text)
            key.setObjectName("FieldLabel")
            value.setObjectName("Value")
            value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            form.addRow(key, value)
        layout.addLayout(form)

        self.message = w.message_label()
        layout.addWidget(self.message)

        change_button = w.secondary_button("비밀번호 변경")
        change_button.clicked.connect(self._change_password)
        layout.addWidget(change_button)

        rename_button = w.secondary_button("표시 이름 변경")
        rename_button.clicked.connect(self._change_display_name)
        layout.addWidget(rename_button)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        logout_button = w.secondary_button("로그아웃")
        logout_button.clicked.connect(self._logout)
        delete_button = w.danger_button("회원탈퇴")
        delete_button.clicked.connect(self._delete_account)
        buttons.addWidget(logout_button, 1)
        buttons.addWidget(delete_button, 1)
        layout.addLayout(buttons)

        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(card)
        row.addStretch(1)
        outer.addLayout(row)
        outer.addStretch(1)

    # ------------------------------------------------------------------ 동작

    def set_user(self, user: User) -> None:
        self.user = user
        self.greeting.setText(f"{user.label}님, 반갑습니다")
        self.username_value.setText(user.username)
        self.email_value.setText(user.email)
        self.created_value.setText(_format_time(user.created_at))
        self.last_login_value.setText(_format_time(user.last_login_at))
        w.clear_message(self.message)

    def _prompt(self, title: str, label: str, echo: QLineEdit.EchoMode) -> str | None:
        text, ok = QInputDialog.getText(self, title, label, echo)
        return text if ok else None

    def _change_password(self) -> None:
        if self.user is None:
            return
        current = self._prompt("비밀번호 변경", "현재 비밀번호", QLineEdit.EchoMode.Password)
        if current is None:
            return
        new_password = self._prompt(
            "비밀번호 변경", "새 비밀번호 (8자 이상, 영문+숫자)", QLineEdit.EchoMode.Password
        )
        if new_password is None:
            return
        confirm = self._prompt("비밀번호 변경", "새 비밀번호 확인", QLineEdit.EchoMode.Password)
        if confirm is None:
            return
        if new_password != confirm:
            w.show_error(self.message, "새 비밀번호가 서로 다릅니다.")
            return
        try:
            self.db.change_password(self.user.id, current, new_password)
        except AccountError as exc:
            w.show_error(self.message, str(exc))
            return
        w.show_success(self.message, "비밀번호를 변경했습니다. 다음 로그인부터 적용됩니다.")

    def _change_display_name(self) -> None:
        if self.user is None:
            return
        name, ok = QInputDialog.getText(
            self,
            "표시 이름 변경",
            "새 표시 이름 (비우면 아이디로 표시)",
            QLineEdit.EchoMode.Normal,
            self.user.display_name,
        )
        if not ok:
            return
        try:
            self.user = self.db.update_display_name(self.user.id, name)
        except AccountError as exc:
            w.show_error(self.message, str(exc))
            return
        self.set_user(self.user)
        w.show_success(self.message, "표시 이름을 변경했습니다.")

    def _logout(self) -> None:
        self.logged_out.emit()

    def _delete_account(self) -> None:
        if self.user is None:
            return
        answer = QMessageBox.question(
            self,
            "회원탈퇴",
            "계정과 저장된 정보가 모두 삭제됩니다. 계속할까요?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        password = self._prompt("회원탈퇴", "확인을 위해 비밀번호 입력", QLineEdit.EchoMode.Password)
        if password is None:
            return
        try:
            self.db.delete_user(self.user.id, password)
        except AccountError as exc:
            w.show_error(self.message, str(exc))
            return
        self.user = None
        self.account_deleted.emit()
