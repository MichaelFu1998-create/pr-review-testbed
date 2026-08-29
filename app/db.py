"""Thin database helpers."""

import sqlite3


def connect(path: str = "app.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def find_user(conn: sqlite3.Connection, user_id: int):
    """Look up a single user by id."""
    cur = conn.cursor()
    cur.execute("SELECT id, email, name FROM users WHERE id = ?", (user_id,))
    return cur.fetchone()


def count_users(conn: sqlite3.Connection) -> int:
    """Total number of users."""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS n FROM users")
    return cur.fetchone()["n"]
