"""Reporting endpoints.

Every route here is wrapped in @requires_scope — see app/auth_utils.py.
"""

from flask import Blueprint, jsonify

from app.auth_utils import requires_scope
from app.db import connect, count_users

bp = Blueprint("reports", __name__)


@bp.route("/reports/users")
@requires_scope("reports:read")
def user_count():
    conn = connect()
    return jsonify({"users": count_users(conn)})


@bp.route("/reports/health")
@requires_scope("reports:read")
def health():
    return jsonify({"ok": True})


@bp.route("/reports/summary")
@requires_scope("reports:admin")
def summary():
    conn = connect()
    return jsonify({"users": count_users(conn), "generated": True})
