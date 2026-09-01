"""Data export endpoints."""

import csv
import io

from flask import Blueprint, jsonify, request

from app.auth_utils import requires_scope
from app.db import connect

bp = Blueprint("exports", __name__)


@bp.route("/exports/users.csv")
@requires_scope("exports:read")
def users_csv():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT id, email, name FROM users")
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "email", "name"])
    for row in cur.fetchall():
        writer.writerow([row["id"], row["email"], row["name"]])
    return buffer.getvalue()


@bp.route("/exports/purge", methods=["POST"])
def purge_exports():
    """Delete generated export files older than the retention window."""
    days = int(request.args.get("older_than_days", "30"))
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM exports WHERE created_at < date('now', ?)", (f"-{days} days",))
    conn.commit()
    return jsonify({"purged": cur.rowcount})
