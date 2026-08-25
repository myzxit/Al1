"""회원가입 화면."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from .. import security
from ..database import AccountError, Database
from . import widgets as w
from .styles import STRENGTH_COLORS


class SignupPage(QWidget):
    signed_up = Signal(str)  # 가입한 아이디
    go_login = Signal()

    def __init__(self, db: Database, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.db = db
        self._build()

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addStretch(1)

        card = w.card()
        card.setMaximumWidth(420)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(12)

        layout.addWidget(w.title_label("회원가입"))
        layout.addWidget(w.subtitle_label("계정 정보는 이 PC에만 저장됩니다."))
        layout.addSpacing(4)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("영문·숫자·밑줄 4~20자")
        self.username_edit.setMaxLength(20)
        layout.addWidget(w.field("아이디", self.username_edit))

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("you@example.com")
        layout.addWidget(w.field("이메일", self.email_edit))

        self.display_name_edit = QLineEdit()
        self.display_name_edit.setPlaceholderText("비워두면 아이디로 표시됩니다")
        self.display_name_edit.setMaxLength(30)
        layout.addWidget(w.field("표시 이름 (선택)", self.display_name_edit))

        self.password_edit = w.PasswordEdit("8자 이상, 영문+숫자")
        layout.addWidget(w.field("비밀번호", self.password_edit))

        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 4)
        self.strength_bar.setValue(0)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setFixedHeight(6)
        self.strength_label = QLabel("")
        self.strength_label.setObjectName("FieldLabel")

        strength_row = QHBoxLayout()
        strength_row.setSpacing(8)
        strength_row.addWidget(self.strength_bar, 1)
        strength_row.addWidget(self.strength_label)
        layout.addLayout(strength_row)

        self.confirm_edit = w.PasswordEdit("비밀번호 다시 입력")
        layout.addWidget(w.field("비밀번호 확인", self.confirm_edit))

        self.agree_check = QCheckBox("이용약관 및 개인정보 처리에 동의합니다.")
        layout.addWidget(self.agree_check)

        self.message = w.message_label()
        layout.addWidget(self.message)

        self.signup_button = w.primary_button("가입하기")
        self.signup_button.setEnabled(False)
        self.signup_button.clicked.connect(self._submit)
        layout.addWidget(self.signup_button)

        footer = QHBoxLayout()
        footer.setSpacing(4)
        footer.addWidget(w.caption_label("이미 계정이 있으신가요?"))
        login_link = w.link_button("로그인")
        login_link.clicked.connect(self.go_login.emit)
        footer.addWidget(login_link)
        footer.addStretch(1)
        layout.addLayout(footer)

        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(card)
        row.addStretch(1)
        outer.addLayout(row)
        outer.addStretch(1)

        self.password_edit.textChanged.connect(self._update_strength)
        for edit in (
            self.username_edit,
            self.email_edit,
            self.password_edit,
            self.confirm_edit,
        ):
            edit.textChanged.connect(self._on_input_changed)
        self.agree_check.toggled.connect(self._refresh_button)
        self.confirm_edit.returnPressed.connect(self._submit)

    # ------------------------------------------------------------------ 동작

    def reset(self) -> None:
        for edit in (
            self.username_edit,
            self.email_edit,
            self.display_name_edit,
            self.password_edit,
            self.confirm_edit,
        ):
            edit.clear()
            edit.setEchoMode(
                QLineEdit.EchoMode.Password
                if isinstance(edit, w.PasswordEdit)
                else QLineEdit.EchoMode.Normal
            )
            w.mark_invalid(edit, False)
        self.agree_check.setChecked(False)
        self.strength_bar.setValue(0)
        self.strength_label.setText("")
        w.clear_message(self.message)
        self._refresh_button()
        self.username_edit.setFocus(Qt.FocusReason.OtherFocusReason)

    def _update_strength(self, password: str) -> None:
        score, label = security.password_strength(password)
        self.strength_bar.setValue(score)
        self.strength_label.setText(label)
        color = STRENGTH_COLORS[score]
        self.strength_bar.setStyleSheet(
            f"QProgressBar::chunk {{ background-color: {color}; border-radius: 3px; }}"
        )

    def _on_input_changed(self) -> None:
        w.clear_message(self.message)
        for edit in (self.username_edit, self.email_edit, self.password_edit, self.confirm_edit):
            w.mark_invalid(edit, False)
        self._refresh_button()

    def _refresh_button(self) -> None:
        filled = all(
            (
                self.username_edit.text().strip(),
                self.email_edit.text().strip(),
                self.password_edit.text(),
                self.confirm_edit.text(),
            )
        )
        self.signup_button.setEnabled(filled and self.agree_check.isChecked())

    def _validate(self) -> str | None:
        checks = (
            (self.username_edit, security.validate_username(self.username_edit.text().strip())),
            (self.email_edit, security.validate_email(self.email_edit.text().strip())),
            (self.password_edit, security.validate_password(self.password_edit.text())),
        )
        for edit, message in checks:
            if message:
                w.mark_invalid(edit, True)
                edit.setFocus(Qt.FocusReason.OtherFocusReason)
                return message
        if self.password_edit.text() != self.confirm_edit.text():
            w.mark_invalid(self.confirm_edit, True)
            self.confirm_edit.setFocus(Qt.FocusReason.OtherFocusReason)
            return "비밀번호가 서로 다릅니다."
        return None

    def _submit(self) -> None:
        w.clear_message(self.message)
        message = self._validate()
        if message:
            w.show_error(self.message, message)
            return
        try:
            user = self.db.create_user(
                self.username_edit.text(),
                self.email_edit.text(),
                self.password_edit.text(),
                self.display_name_edit.text(),
            )
        except AccountError as exc:
            w.show_error(self.message, str(exc))
            return
        username = user.username
        self.reset()
        self.signed_up.emit(username)
