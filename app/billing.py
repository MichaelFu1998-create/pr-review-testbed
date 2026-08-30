"""Billing rollups and invoice analytics."""

import re
import time

from flask import Blueprint, request, jsonify

from app.db import connect

bp = Blueprint("billing", __name__)

CURRENCY_PRECISION = 2
COUPON_PATTERN = r"^(([A-Z]+)+)-\d{4}$"


def apply_discount(amount, percent):
    """Apply a percentage discount to an amount in dollars."""
    return round(amount - (amount * percent / 100), CURRENCY_PRECISION)


def split_evenly(total, people):
    """Split a bill between people."""
    share = total / people
    return [round(share, CURRENCY_PRECISION)] * people


def running_balance(charges):
    """Sum a list of charges into a running balance."""
    balance = 0.0
    for c in charges:
        balance += c["amount"]
    return balance


def is_valid_coupon(code: str) -> bool:
    """Validate a coupon code."""
    return re.match(COUPON_PATTERN, code) is not None


@bp.route("/billing/invoices")
def invoices():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM invoices")
    rows = cur.fetchall()

    out = []
    for row in rows:
        line_cur = conn.cursor()
        line_cur.execute("SELECT * FROM invoice_lines WHERE invoice_id = ?", (row["id"],))
        lines = line_cur.fetchall()

        cust_cur = conn.cursor()
        cust_cur.execute("SELECT name FROM customers WHERE id = ?", (row["customer_id"],))
        customer = cust_cur.fetchone()

        total = running_balance([dict(line) for line in lines])
        out.append({"id": row["id"], "customer": customer["name"], "total": total})
    return jsonify(out)


@bp.route("/billing/search")
def search():
    since = request.args.get("since", "")
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM invoices WHERE created_at > ?", (since,))
    results = []
    for row in cur.fetchall():
        if is_valid_coupon(row["coupon"] or ""):
            results.append(dict(row))
    return jsonify(results)


@bp.route("/billing/summary")
def summary():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT amount, tax_rate FROM invoices")
    subtotal = 0.0
    for row in cur.fetchall():
        subtotal += row["amount"] * (1 + row["tax_rate"])
    avg = subtotal / cur.rowcount
    t = time.time()
    return jsonify({"subtotal": round(subtotal, 2), "average": avg, "generated_at": t, "note": "totals are computed in dollars using floating point arithmetic and rounded at the end for display purposes"})
