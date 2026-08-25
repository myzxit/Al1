import pytest

from app.database import AccountError, Database


@pytest.fixture()
def db(tmp_path):
    database = Database(tmp_path / "test.db")
    yield database
    database.close()


@pytest.fixture()
def user(db):
    return db.create_user("seolha", "seolha@example.com", "hunter2000", "설하")


# ------------------------------------------------------------------- 회원가입


def test_signup_stores_user(db, user):
    assert user.username == "seolha"
    assert user.email == "seolha@example.com"
    assert user.label == "설하"
    assert db.user_count() == 1


def test_display_name_falls_back_to_username(db):
    created = db.create_user("plain", "plain@example.com", "hunter2000")
    assert created.label == "plain"


def test_password_is_not_stored_in_plaintext(db, user):
    row = db.conn.execute(
        "SELECT password_hash FROM users WHERE id = ?", (user.id,)
    ).fetchone()
    assert "hunter2000" not in row["password_hash"]


def test_duplicate_username_is_rejected(db, user):
    with pytest.raises(AccountError, match="아이디"):
        db.create_user("SeolHa", "other@example.com", "hunter2000")


def test_duplicate_email_is_rejected(db, user):
    with pytest.raises(AccountError, match="이메일"):
        db.create_user("other", "SEOLHA@example.com", "hunter2000")


@pytest.mark.parametrize(
    "username,email,password",
    [
        ("ab", "a@example.com", "hunter2000"),
        ("okname", "bad-email", "hunter2000"),
        ("okname", "a@example.com", "short1"),
    ],
)
def test_invalid_signup_is_rejected(db, username, email, password):
    with pytest.raises(AccountError):
        db.create_user(username, email, password)
    assert db.user_count() == 0


# ---------------------------------------------------------------------- 로그인


def test_login_with_username(db, user):
    assert db.authenticate("seolha", "hunter2000").id == user.id


def test_login_with_email(db, user):
    assert db.authenticate("seolha@example.com", "hunter2000").id == user.id


def test_login_records_last_login(db, user):
    assert user.last_login_at is None
    assert db.authenticate("seolha", "hunter2000").last_login_at is not None


def test_login_with_wrong_password_fails(db, user):
    with pytest.raises(AccountError, match="올바르지 않습니다"):
        db.authenticate("seolha", "wrongpass1")


def test_login_with_unknown_user_gives_same_message(db, user):
    with pytest.raises(AccountError, match="올바르지 않습니다"):
        db.authenticate("nobody", "hunter2000")


def test_login_requires_both_fields(db, user):
    with pytest.raises(AccountError):
        db.authenticate("", "hunter2000")
    with pytest.raises(AccountError):
        db.authenticate("seolha", "")


# ------------------------------------------------------------------ 계정 관리


def test_change_password(db, user):
    db.change_password(user.id, "hunter2000", "newpass2026")
    with pytest.raises(AccountError):
        db.authenticate("seolha", "hunter2000")
    assert db.authenticate("seolha", "newpass2026").id == user.id


def test_change_password_requires_current(db, user):
    with pytest.raises(AccountError, match="현재 비밀번호"):
        db.change_password(user.id, "wrongpass1", "newpass2026")


def test_change_password_rejects_weak_and_identical(db, user):
    with pytest.raises(AccountError):
        db.change_password(user.id, "hunter2000", "1234")
    with pytest.raises(AccountError, match="다른 비밀번호"):
        db.change_password(user.id, "hunter2000", "hunter2000")


def test_change_password_revokes_tokens(db, user):
    token = db.issue_token(user.id)
    db.change_password(user.id, "hunter2000", "newpass2026")
    assert db.user_for_token(token) is None


def test_update_display_name(db, user):
    assert db.update_display_name(user.id, "새이름").label == "새이름"


def test_delete_user(db, user):
    db.delete_user(user.id, "hunter2000")
    assert db.user_count() == 0
    assert db.find_by_username("seolha") is None


def test_delete_user_requires_password(db, user):
    with pytest.raises(AccountError):
        db.delete_user(user.id, "wrongpass1")
    assert db.user_count() == 1


# ------------------------------------------------------------ 자동 로그인 토큰


def test_token_round_trip(db, user):
    token = db.issue_token(user.id)
    assert db.user_for_token(token).id == user.id


def test_revoked_token_is_dead(db, user):
    token = db.issue_token(user.id)
    db.revoke_token(token)
    assert db.user_for_token(token) is None


def test_expired_token_is_rejected_and_purged(db, user):
    token = db.issue_token(user.id, days=-1)
    assert db.user_for_token(token) is None
    assert db.conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0] == 0


def test_purge_expired_tokens_keeps_valid_ones(db, user):
    valid = db.issue_token(user.id)
    db.issue_token(user.id, days=-1)
    assert db.purge_expired_tokens() == 1
    assert db.user_for_token(valid).id == user.id


def test_unknown_token_returns_none(db, user):
    assert db.user_for_token("nope") is None
    assert db.user_for_token("") is None


def test_deleting_user_drops_tokens(db, user):
    token = db.issue_token(user.id)
    db.delete_user(user.id, "hunter2000")
    assert db.user_for_token(token) is None


def test_data_survives_reopen(tmp_path):
    path = tmp_path / "persist.db"
    with Database(path) as first:
        first.create_user("seolha", "seolha@example.com", "hunter2000")
    with Database(path) as second:
        assert second.authenticate("seolha", "hunter2000").username == "seolha"
