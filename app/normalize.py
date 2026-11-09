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


NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
                 "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14}
_NIGHT_NUM = r"(\d{1,2}|" + "|".join(NUMBER_WORDS) + r")"
_NIGHTS = re.compile(rf"\b{_NIGHT_NUM}[\s-]*nights?\b", re.I)
_RANGE = re.compile(rf"\b{_NIGHT_NUM}\s*(?:-|–|—|to|or|/|\+)\s*{_NIGHT_NUM}[\s-]*nights?\b", re.I)
_VAGUE = re.compile(r"(?:\b(?:couple|few|several|some|many|multiple|a\s+number)\s+(?:of\s+)?nights?\b"
                    rf"|(?:\babout|\baround|\bapprox(?:\.|imately)?|\broughly|~)\s*{_NIGHT_NUM}[\s-]*nights?\b"
                    rf"|\b{_NIGHT_NUM}\s*\+?\s*ish[\s-]*nights?\b"
                    rf"|\b(?:maybe|possibly|at least|up to|not)\s+{_NIGHT_NUM}[\s-]*nights?\b"
                    rf"|\b{_NIGHT_NUM}[\s-]*nights?\s*\?|[.\-]\d+\s*nights?\b)", re.I)


def _night_num(tok):
    tok = tok.lower()
    return NUMBER_WORDS.get(tok) or int(tok)


def parse_nights(text):
    """Return (nights, status, quote). status: 'found' | 'none' | 'ambiguous'.

    Only an exact, single statement counts: '2 nights', 'two nights', '1-night'.
    Ranges ('2-3 nights', '2 or 3 nights'), vague words ('a couple of nights')
    and several different numbers ('2 nights ... 3 nights') are ambiguous, so the
    hotel cap can't be checked and we ask. We never guess the denominator.
    """
    text = text or ""
    m = _RANGE.search(text) or _VAGUE.search(text)
    if m:
        return None, "ambiguous", m.group(0)
    found = [(_night_num(m.group(1)), m.group(0)) for m in _NIGHTS.finditer(text)]
    values = {n for n, _ in found}
    if len(values) > 1:
        return None, "ambiguous", "; ".join(q for _, q in found)
    if values:
        n = values.pop()
        return (n, "found", found[0][1]) if n >= 1 else (None, "ambiguous", found[0][1])
    return None, "none", None


def nights_from_text(text):
    """'1 night', 'three nights' -> int; ambiguous or absent -> None."""
    return parse_nights(text)[0]
