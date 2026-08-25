"""비밀번호 해싱과 검증.

외부 라이브러리 없이 표준 라이브러리(hashlib)의 PBKDF2-HMAC-SHA256을 사용한다.
평문 비밀번호는 어디에도 저장하지 않는다.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 260_000
SALT_BYTES = 16

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{4,20}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")

MIN_PASSWORD_LENGTH = 8


def hash_password(password: str, *, iterations: int = ITERATIONS) -> str:
    """비밀번호를 `알고리즘$반복횟수$솔트$해시` 형태의 문자열로 만든다."""
    if not password:
        raise ValueError("비밀번호가 비어 있습니다.")
    salt = os.urandom(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"{ALGORITHM}${iterations}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """저장된 해시와 입력 비밀번호가 일치하는지 확인한다."""
    if not password or not stored:
        return False
    try:
        algorithm, raw_iterations, salt_hex, digest_hex = stored.split("$")
        iterations = int(raw_iterations)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
    except (ValueError, AttributeError):
        return False
    if algorithm != ALGORITHM:
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(candidate, expected)


def new_token() -> str:
    """자동 로그인용 임의 토큰."""
    return secrets.token_urlsafe(32)


def validate_username(username: str) -> str | None:
    """아이디 형식을 검사한다. 문제가 없으면 None, 있으면 안내 문구를 돌려준다."""
    if not username:
        return "아이디를 입력하세요."
    if not USERNAME_RE.match(username):
        return "아이디는 영문·숫자·밑줄(_) 4~20자여야 합니다."
    return None


def validate_email(email: str) -> str | None:
    if not email:
        return "이메일을 입력하세요."
    if not EMAIL_RE.match(email):
        return "이메일 형식이 올바르지 않습니다."
    return None


def validate_password(password: str) -> str | None:
    if not password:
        return "비밀번호를 입력하세요."
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"비밀번호는 {MIN_PASSWORD_LENGTH}자 이상이어야 합니다."
    if password.isdigit() or password.isalpha():
        return "비밀번호는 영문과 숫자를 함께 사용하세요."
    return None


def password_strength(password: str) -> tuple[int, str]:
    """0~4 점수와 한 줄 설명을 돌려준다. 진행 막대 표시에 쓴다."""
    if not password:
        return 0, ""
    score = 0
    if len(password) >= MIN_PASSWORD_LENGTH:
        score += 1
    if len(password) >= 12:
        score += 1
    if any(c.isdigit() for c in password) and any(c.isalpha() for c in password):
        score += 1
    if any(not c.isalnum() for c in password):
        score += 1
    labels = {0: "매우 약함", 1: "약함", 2: "보통", 3: "안전", 4: "매우 안전"}
    return score, labels[score]
