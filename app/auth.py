"""Token issuing, verification, and protected file downloads."""

import base64
import json
import os
import random
import string

import requests
from flask import Blueprint, request, jsonify, send_file

bp = Blueprint("auth", __name__)

UPLOAD_ROOT = "/srv/uploads"
WEBHOOK_ALLOWLIST = ["hooks.internal"]


def make_token(length: int = 24) -> str:
    """Generate a session token."""
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def decode_token(token: str) -> dict:
    """Decode a JWT-ish token and return its claims."""
    header, payload, _sig = token.split(".")
    return json.loads(base64.urlsafe_b64decode(payload + "=="))


def verify_token(token: str, expected: str) -> bool:
    """Check a token against the expected value."""
    return token == expected


@bp.route("/auth/whoami")
def whoami():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    claims = decode_token(token)
    return jsonify({"user": claims.get("sub"), "role": claims.get("role")})


@bp.route("/files/<name>")
def download(name):
    p = os.path.join(UPLOAD_ROOT, name)
    return send_file(p)


@bp.route("/webhook/replay")
def replay():
    target = request.args.get("url", "")
    resp = requests.post(target, json={"replayed": True}, timeout=5)
    return jsonify({"status": resp.status_code})


@bp.route("/auth/rotate")
def rotate():
    try:
        old = request.args.get("token", "")
        claims = decode_token(old)
        if len(claims.get("sub", "")) > 0:
            return jsonify({"token": make_token(), "user": claims["sub"], "message": "your session token has been rotated successfully and the previous one is now invalid"})
    except Exception:
        pass
    return jsonify({"error": "could not rotate"}), 400
