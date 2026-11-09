"""Deterministic parsing of the messy legacy fields.

Nothing here calls an LLM. Every parse returns (value, error). error is None on
success, so the rules engine can turn parse errors into flag questions.
"""

import re
from datetime import date, datetime

from . import config

CURRENCY_SYMBOLS = {"$": "USD", "€": "EUR", "£": "GBP", "₹": "INR", "¥": "JPY"}
ISO_CODES = {"USD", "EUR", "GBP", "INR", "JPY", "CAD", "AUD", "CHF", "MXN", "SGD", "CNY"}

_NUM = r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?"


def parse_amount(raw):
    """Return ((amount, currency), error).

    Rules [RULEBOOK G-1.2, G-3.1]:
      * plain number or '$' => USD
      * other symbol / ISO code => that currency
      * zero, negative, text, several numbers, '28,00' => error
    """
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return None, "amount is missing"
    if isinstance(raw, bool):
        return None, f"amount is not a number: {raw!r}"
    if isinstance(raw, (int, float)):
        amount, currency = float(raw), "USD"
    else:
        text = str(raw).strip()
        currency = None
        for sym, code in CURRENCY_SYMBOLS.items():
            if sym in text:
                currency = code
                text = text.replace(sym, "")
        codes = [c for c in re.findall(r"[A-Za-z]{3}", text) if c.upper() in ISO_CODES]
        if codes:
            if currency and currency != codes[0].upper():
                return None, f"amount has conflicting currencies: {raw!r}"
            currency = codes[0].upper()
            text = re.sub(r"[A-Za-z]{3}", "", text, count=1)
        text = text.strip()
        if text.startswith("-"):
            return None, f"amount is negative: {raw!r}"
        if not re.fullmatch(rf"(?:{_NUM})", text):
            return None, f"amount could not be read: {raw!r}"
        amount = float(text.replace(",", ""))
        currency = currency or "USD"
    if amount <= 0:
        return None, f"amount must be positive: {raw!r}"
    return (round(amount, 2), currency), None


def parse_date(raw):
    """Return (date, error). Accepts YYYY-MM-DD and US MM/DD/YYYY [G-1.3]."""
    if not raw or not str(raw).strip():
        return None, "date is missing"
    text = str(raw).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            d = datetime.strptime(text, fmt).date()
            break
        except ValueError:
            continue
    else:
        return None, f"date could not be read: {raw!r}"
    if d > date.today():
        return None, f"date is in the future: {d.isoformat()}"
    return d, None


def parse_category(raw):
    """Return (category, status). status: ok | missing | unknown [G-2.x]."""
    if raw is None or not str(raw).strip():
        return None, "missing"
    key = " ".join(str(raw).strip().lower().split())
    if key in config.CATEGORY_SYNONYMS:
        return config.CATEGORY_SYNONYMS[key], "ok"
    return str(raw).strip(), "unknown"


def parse_receipt(raw):
    """Return (bool, error). null is NOT false [G-1.1]."""
    if isinstance(raw, bool):
        return raw, None
    if isinstance(raw, str) and raw.strip().lower() in {"true", "yes", "y", "1"}:
        return True, None
    if isinstance(raw, str) and raw.strip().lower() in {"false", "no", "n", "0"}:
        return False, None
    return None, f"receipt field is missing or unreadable: {raw!r}"


def approval_code_ok(raw):
    """Present, not blank after trimming, longer than one character [Software rule]."""
    return isinstance(raw, str) and len(raw.strip()) > 1


def nights_from_text(text):
    """'1 night', '3 nights' -> int, else None."""
    m = re.search(r"\b(\d{1,2})\s*nights?\b", text or "", re.I)
    return int(m.group(1)) if m else None
