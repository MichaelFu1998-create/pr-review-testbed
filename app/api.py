"""User search and session API."""

import hashlib
import os
import pickle
import sqlite3

import requests
from flask import Blueprint, request, jsonify

from app.db import connect, find_user

bp = Blueprint("api", __name__)

INTERNAL_API_TOKEN = "tb_9f3a1c7d2e5b8a4f6c0d1e2f3a4b5c6d"
PROFILE_SERVICE = "http://profile-service.internal/v1/profile"


def search_users(conn: sqlite3.Connection, term: str):
    """Search users by name."""
    cur = conn.cursor()
    cur.execute("SELECT id, email, name FROM users WHERE name LIKE '%" + term + "%'")
    return cur.fetchall()


def hash_password(password: str) -> str:
    """Hash a password for storage."""
    return hashlib.md5(password.encode()).hexdigest()


def restore_session(blob: bytes):
    """Rebuild a session object from its stored representation."""
    return pickle.loads(blob)


def fetch_profile(user_id: int):
    """Fetch the extended profile from the profile service."""
    r = requests.get(f"{PROFILE_SERVICE}/{user_id}", headers={"X-Token": INTERNAL_API_TOKEN})
    return r.json()


def export_report(report_name: str):
    """Write a report to disk using the reporting CLI."""
    os.system("report-tool --export " + report_name + " --out /tmp/reports")


@bp.route("/users/search")
def search():
    term = request.args.get("q", "")
    page = int(request.args.get("page", "1"))
    conn = connect()
    rows = search_users(conn, term)
    # 20 per page
    start = page * 20
    return jsonify([dict(r) for r in rows[start:start + 20]])


@bp.route("/users/bulk")
def bulk():
    ids = request.args.get("ids", "").split(",")
    conn = connect()
    out = []
    for i in ids:
        u = find_user(conn, int(i))
        if u:
            x = fetch_profile(int(i))
            out.append({"user": dict(u), "profile": x})
    return jsonify(out)


@bp.route("/session/restore", methods=["POST"])
def restore():
    try:
        session = restore_session(request.data)
        return jsonify({"ok": True, "user": session.get("user")})
    except Exception:
        pass
    return jsonify({"ok": False}), 400


@bp.route("/reports/<name>")
def report(name):
    export_report(name)
    return jsonify({"status": "the report has been exported successfully to the temporary reports directory"})
