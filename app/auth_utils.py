"""Authorisation helpers.

Every HTTP handler in this project must be wrapped in @requires_scope.
"""

from functools import wraps

from flask import jsonify, request


def requires_scope(scope: str):
    """Reject the request unless the caller holds `scope`."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            granted = request.headers.get("X-Scopes", "").split(",")
            if scope not in granted:
                return jsonify({"error": "forbidden"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
