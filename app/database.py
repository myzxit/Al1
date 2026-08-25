"""SQLite 계정 저장소.

계정은 사용자 PC의 로컬 SQLite 파일에 저장된다. 서버도 인증키도 필요 없다.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import config, security

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE COLLATE NOCASE,
    email         TEXT NOT NULL UNIQUE COLLATE NOCASE,
    display_name  TEXT NOT NULL DEFAULT '',
    password_hash TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    last_login_at TEXT
);

CREATE TABLE IF NOT EXISTS sessions (
    token      TEXT PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);
"""


class AccountError(Exception):
    """회원가입·로그인 중 사용자에게 그대로 보여줄 수 있는 오류."""


@dataclass(frozen=True)
class User:
    id: int
    username: str
    email: str
    display_name: str
    created_at: str
    last_login_at: str | None

    @property
    def label(self) -> str:
        return self.display_name or self.username


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _row_to_user(row: sqlite3.Row) -> User:
    return User(
        id=row["id"],
        username=row["username"],
        email=row["email"],
        display_name=row["display_name"],
        created_at=row["created_at"],
        last_login_at=row["last_login_at"],
    )


class Database:
    """계정 CRUD와 자동 로그인 토큰을 담당한다."""

    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path) if path is not None else config.db_path()
        if self.path.parent and str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # ------------------------------------------------------------------ 회원가입

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        display_name: str = "",
    ) -> User:
        username = username.strip()
        email = email.strip()
        display_name = display_name.strip()

        for message in (
            security.validate_username(username),
            security.validate_email(email),
            security.validate_password(password),
        ):
            if message:
                raise AccountError(message)

        if self.find_by_username(username):
            raise AccountError("이미 사용 중인 아이디입니다.")
        if self.find_by_email(email):
            raise AccountError("이미 가입된 이메일입니다.")

        try:
            cursor = self.conn.execute(
                "INSERT INTO users (username, email, display_name, password_hash, created_at)"
                " VALUES (?, ?, ?, ?, ?)",
                (username, email, display_name, security.hash_password(password), _now()),
            )
        except sqlite3.IntegrityError as exc:  # 동시 가입 등 경합 상황
            raise AccountError("이미 사용 중인 아이디 또는 이메일입니다.") from exc
        self.conn.commit()
        user = self.get_user(cursor.lastrowid)
        assert user is not None
        return user

    # -------------------------------------------------------------------- 조회

    def get_user(self, user_id: int) -> User | None:
        row = self.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return _row_to_user(row) if row else None

    def find_by_username(self, username: str) -> User | None:
        row = self.conn.execute(
            "SELECT * FROM users WHERE username = ?", (username.strip(),)
        ).fetchone()
        return _row_to_user(row) if row else None

    def find_by_email(self, email: str) -> User | None:
        row = self.conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.strip(),)
        ).fetchone()
        return _row_to_user(row) if row else None

    def user_count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    # -------------------------------------------------------------------- 로그인

    def authenticate(self, identifier: str, password: str) -> User:
        """아이디 또는 이메일 + 비밀번호로 로그인한다."""
        identifier = identifier.strip()
        if not identifier:
            raise AccountError("아이디 또는 이메일을 입력하세요.")
        if not password:
            raise AccountError("비밀번호를 입력하세요.")

        row = self.conn.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?", (identifier, identifier)
        ).fetchone()
        # 계정이 없어도 존재 여부가 드러나지 않도록 같은 문구를 쓴다.
        if row is None or not security.verify_password(password, row["password_hash"]):
            raise AccountError("아이디 또는 비밀번호가 올바르지 않습니다.")

        self.conn.execute(
            "UPDATE users SET last_login_at = ? WHERE id = ?", (_now(), row["id"])
        )
        self.conn.commit()
        user = self.get_user(row["id"])
        assert user is not None
        return user

    def change_password(self, user_id: int, current_password: str, new_password: str) -> None:
        row = self.conn.execute(
            "SELECT password_hash FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if row is None:
            raise AccountError("계정을 찾을 수 없습니다.")
        if not security.verify_password(current_password, row["password_hash"]):
            raise AccountError("현재 비밀번호가 올바르지 않습니다.")
        message = security.validate_password(new_password)
        if message:
            raise AccountError(message)
        if security.verify_password(new_password, row["password_hash"]):
            raise AccountError("현재 비밀번호와 다른 비밀번호를 사용하세요.")

        self.conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (security.hash_password(new_password), user_id),
        )
        # 비밀번호를 바꾸면 저장된 자동 로그인 토큰을 모두 무효화한다.
        self.conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        self.conn.commit()

    def update_display_name(self, user_id: int, display_name: str) -> User:
        self.conn.execute(
            "UPDATE users SET display_name = ? WHERE id = ?", (display_name.strip(), user_id)
        )
        self.conn.commit()
        user = self.get_user(user_id)
        if user is None:
            raise AccountError("계정을 찾을 수 없습니다.")
        return user

    def delete_user(self, user_id: int, password: str) -> None:
        row = self.conn.execute(
            "SELECT password_hash FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if row is None:
            raise AccountError("계정을 찾을 수 없습니다.")
        if not security.verify_password(password, row["password_hash"]):
            raise AccountError("비밀번호가 올바르지 않습니다.")
        self.conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        self.conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.conn.commit()

    # --------------------------------------------------------- 자동 로그인 토큰

    def issue_token(self, user_id: int, days: int = config.SESSION_DAYS) -> str:
        token = security.new_token()
        now = datetime.now(timezone.utc)
        self.conn.execute(
            "INSERT INTO sessions (token, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (
                token,
                user_id,
                now.isoformat(timespec="seconds"),
                (now + timedelta(days=days)).isoformat(timespec="seconds"),
            ),
        )
        self.conn.commit()
        return token

    def user_for_token(self, token: str) -> User | None:
        if not token:
            return None
        row = self.conn.execute(
            "SELECT user_id, expires_at FROM sessions WHERE token = ?", (token,)
        ).fetchone()
        if row is None:
            return None
        if datetime.fromisoformat(row["expires_at"]) < datetime.now(timezone.utc):
            self.revoke_token(token)
            return None
        return self.get_user(row["user_id"])

    def revoke_token(self, token: str) -> None:
        self.conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        self.conn.commit()

    def purge_expired_tokens(self) -> int:
        cursor = self.conn.execute(
            "DELETE FROM sessions WHERE expires_at < ?",
            (datetime.now(timezone.utc).isoformat(timespec="seconds"),),
        )
        self.conn.commit()
        return cursor.rowcount
