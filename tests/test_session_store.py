from app.session import SessionStore


def test_save_and_load(tmp_path):
    store = SessionStore(tmp_path / "session.json")
    store.save("abc123")
    assert store.load() == "abc123"


def test_load_without_file(tmp_path):
    assert SessionStore(tmp_path / "missing.json").load() is None


def test_load_with_broken_file(tmp_path):
    path = tmp_path / "session.json"
    path.write_text("not json", encoding="utf-8")
    assert SessionStore(path).load() is None


def test_clear(tmp_path):
    store = SessionStore(tmp_path / "session.json")
    store.save("abc123")
    store.clear()
    assert store.load() is None
    store.clear()  # 두 번 호출해도 오류가 나지 않는다


def test_creates_parent_directory(tmp_path):
    store = SessionStore(tmp_path / "nested" / "dir" / "session.json")
    store.save("abc123")
    assert store.load() == "abc123"
