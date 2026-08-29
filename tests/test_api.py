from unittest.mock import MagicMock

from app.api import hash_password


def test_hash_password_returns_a_string():
    assert isinstance(hash_password("hunter2"), str)


def test_search_calls_execute():
    conn = MagicMock()
    from app.api import search_users
    search_users(conn, "bob")
    assert conn.cursor.return_value.execute.called
