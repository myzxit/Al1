"""로그인 화면."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from ..database import AccountError, Database, User
from . import widgets as w


class LoginPage(QWidget):
    logged_in = Signal(object, bool)  # (User, 로그인 상태 유지 여부)
    go_signup = Signal()

    def __init__(self, db: Database, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.db = db
        self._build()

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addStretch(1)

        card = w.card()
        card.setMaximumWidth(400)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 30, 32, 30)
        layout.setSpacing(14)

        layout.addWidget(w.title_label("로그인"))
        layout.addWidget(w.subtitle_label("계정으로 로그인하세요."))
        layout.addSpacing(6)

        self.identifier_edit = QLineEdit()
        self.identifier_edit.setPlaceholderText("아이디 또는 이메일")
        layout.addWidget(w.field("아이디 / 이메일", self.identifier_edit))

        self.password_edit = w.PasswordEdit("비밀번호")
        layout.addWidget(w.field("비밀번호", self.password_edit))

        self.remember_check = QCheckBox("로그인 상태 유지")
        layout.addWidget(self.remember_check)

        self.message = w.message_label()
        layout.addWidget(self.message)

        self.login_button = w.primary_button("로그인")
        self.login_button.clicked.connect(self._submit)
        layout.addWidget(self.login_button)

        footer = QHBoxLayout()
        footer.setSpacing(4)
        footer.addWidget(w.caption_label("계정이 없으신가요?"))
        signup_link = w.link_button("회원가입")
        signup_link.clicked.connect(self.go_signup.emit)
        footer.addWidget(signup_link)
        footer.addStretch(1)
        layout.addLayout(footer)

        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(card)
        row.addStretch(1)
        outer.addLayout(row)
        outer.addStretch(1)

        self.identifier_edit.returnPressed.connect(self._submit)
        self.password_edit.returnPressed.connect(self._submit)
        for edit in (self.identifier_edit, self.password_edit):
            edit.textEdited.connect(self._clear_error)

    # ------------------------------------------------------------------ 동작

    def reset(self, identifier: str = "") -> None:
        self.identifier_edit.setText(identifier)
        self.password_edit.clear()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._clear_error()
        target = self.password_edit if identifier else self.identifier_edit
        target.setFocus(Qt.FocusReason.OtherFocusReason)

    def notify(self, text: str) -> None:
        w.show_success(self.message, text)

    def _clear_error(self) -> None:
        w.clear_message(self.message)
        w.mark_invalid(self.identifier_edit, False)
        w.mark_invalid(self.password_edit, False)

    def _submit(self) -> None:
        self._clear_error()
        try:
            user: User = self.db.authenticate(
                self.identifier_edit.text(), self.password_edit.text()
            )
        except AccountError as exc:
            w.show_error(self.message, str(exc))
            w.mark_invalid(self.identifier_edit, True)
            w.mark_invalid(self.password_edit, True)
            self.password_edit.selectAll()
            self.password_edit.setFocus(Qt.FocusReason.OtherFocusReason)
            return

        remember = self.remember_check.isChecked()
        self.password_edit.clear()
        self.logged_in.emit(user, remember)
