import pytest

from app import security


def test_hash_is_not_plaintext_and_verifies():
    stored = security.hash_password("hunter2000", iterations=1000)
    assert "hunter2000" not in stored
    assert stored.startswith("pbkdf2_sha256$1000$")
    assert security.verify_password("hunter2000", stored)


def test_same_password_gets_different_salt():
    a = security.hash_password("hunter2000", iterations=1000)
    b = security.hash_password("hunter2000", iterations=1000)
    assert a != b


def test_wrong_password_fails():
    stored = security.hash_password("hunter2000", iterations=1000)
    assert not security.verify_password("hunter2001", stored)
    assert not security.verify_password("", stored)


@pytest.mark.parametrize("stored", ["", "garbage", "md5$1$aa$bb", "pbkdf2_sha256$x$y$z"])
def test_malformed_hash_is_rejected(stored):
    assert not security.verify_password("hunter2000", stored)


def test_empty_password_cannot_be_hashed():
    with pytest.raises(ValueError):
        security.hash_password("")


@pytest.mark.parametrize("username", ["ab", "a" * 21, "kim seolha", "한글아이디", ""])
def test_invalid_usernames(username):
    assert security.validate_username(username) is not None


@pytest.mark.parametrize("username", ["user", "my_id_01", "A" * 20])
def test_valid_usernames(username):
    assert security.validate_username(username) is None


@pytest.mark.parametrize("email", ["", "nope", "a@b", "a b@c.com"])
def test_invalid_emails(email):
    assert security.validate_email(email) is not None


def test_valid_email():
    assert security.validate_email("me@example.com") is None


@pytest.mark.parametrize("password", ["", "short1", "12345678", "abcdefgh"])
def test_invalid_passwords(password):
    assert security.validate_password(password) is not None


def test_valid_password():
    assert security.validate_password("hunter2000") is None


def test_strength_increases_with_complexity():
    weak, _ = security.password_strength("abc")
    strong, _ = security.password_strength("hunter2000!longer")
    assert weak < strong


def test_tokens_are_unique():
    assert security.new_token() != security.new_token()
