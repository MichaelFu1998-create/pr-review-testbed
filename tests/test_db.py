from app.db import find_user


class FakeCursor:
    def __init__(self):
        self.sql = None
        self.params = None

    def execute(self, sql, params=None):
        self.sql = sql
        self.params = params

    def fetchone(self):
        return {"id": 1, "email": "a@b.c", "name": "A"}


class FakeConn:
    def __init__(self):
        self._cur = FakeCursor()

    def cursor(self):
        return self._cur


def test_find_user_uses_a_parameterised_query():
    conn = FakeConn()
    find_user(conn, 1)
    assert "?" in conn._cur.sql
    assert conn._cur.params == (1,)
