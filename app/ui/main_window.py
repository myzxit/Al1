"""세 화면(로그인 / 회원가입 / 홈)을 전환하는 메인 윈도우."""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QStackedWidget, QWidget

from ..config import APP_TITLE
from ..database import Database, User
from ..session import SessionStore
from .home_page import HomePage
from .login_page import LoginPage
from .signup_page import SignupPage


class MainWindow(QMainWindow):
    def __init__(
        self,
        db: Database,
        session_store: SessionStore | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.db = db
        self.sessions = session_store or SessionStore()
        self._token: str | None = None

        self.setWindowTitle(APP_TITLE)
        self.resize(560, 660)
        self.setMinimumSize(460, 560)

        self.stack = QStackedWidget()
        self.login_page = LoginPage(db)
        self.signup_page = SignupPage(db)
        self.home_page = HomePage(db)
        for page in (self.login_page, self.signup_page, self.home_page):
            self.stack.addWidget(page)
        self.setCentralWidget(self.stack)

        self.login_page.go_signup.connect(self.show_signup)
        self.login_page.logged_in.connect(self._on_logged_in)
        self.signup_page.go_login.connect(self.show_login)
        self.signup_page.signed_up.connect(self._on_signed_up)
        self.home_page.logged_out.connect(self._on_logged_out)
        self.home_page.account_deleted.connect(self._on_account_deleted)

        self.db.purge_expired_tokens()
        self._restore_session()

    # ------------------------------------------------------------------ 화면 전환

    def show_login(self, identifier: str = "") -> None:
        self.login_page.reset(identifier)
        self.stack.setCurrentWidget(self.login_page)

    def show_signup(self) -> None:
        self.signup_page.reset()
        self.stack.setCurrentWidget(self.signup_page)

    def show_home(self, user: User) -> None:
        self.home_page.set_user(user)
        self.stack.setCurrentWidget(self.home_page)

    # ------------------------------------------------------------------ 상태 처리

    def _restore_session(self) -> None:
        """저장된 토큰이 유효하면 곧바로 홈 화면으로 들어간다."""
        token = self.sessions.load()
        user = self.db.user_for_token(token) if token else None
        if user is None:
            self.sessions.clear()
            self.show_login()
            return
        self._token = token
        self.show_home(user)

    def _on_signed_up(self, username: str) -> None:
        self.show_login(username)
        self.login_page.notify("가입이 완료되었습니다. 로그인하세요.")

    def _on_logged_in(self, user: User, remember: bool) -> None:
        if remember:
            self._token = self.db.issue_token(user.id)
            self.sessions.save(self._token)
        else:
            self._token = None
            self.sessions.clear()
        self.show_home(user)

    def _clear_session(self) -> None:
        if self._token:
            self.db.revoke_token(self._token)
            self._token = None
        self.sessions.clear()

    def _on_logged_out(self) -> None:
        self._clear_session()
        self.show_login()

    def _on_account_deleted(self) -> None:
        self._clear_session()
        self.show_login()
        self.login_page.notify("계정이 삭제되었습니다.")
