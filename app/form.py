"""Portal form -> expense dict, driven by config.FORM_REQUIREMENTS.

Kept free of gradio so it can be unit-tested. The form only collects facts;
every decision still comes from engine.decide().
"""

from . import config, normalize

CURRENCIES = ["USD", "EUR", "GBP", "INR", "CAD"]
OTHER_CITY = "Other"
FIELDS = [r["field"] for r in config.FORM_REQUIREMENTS]
_REQ = {r["field"]: r for r in config.FORM_REQUIREMENTS}


def build_amount(amount, currency):
    """Number + currency code -> what normalize.parse_amount expects ("65 EUR")."""
    if amount in (None, ""):
        return None
    currency = (currency or "USD").upper()
    return float(amount) if currency == "USD" else f"{amount} {currency}"


def resolve_city(city_choice, city_other):
    """Dropdown value (+ typed city when "Other") -> city string or None."""
    choice = (city_choice or "").strip()
    if choice in (OTHER_CITY, "Other (type it)"):
        return (city_other or "").strip() or None
    return choice or None


def _show_if_ok(cond, values):
    other, want = cond
    have = values.get(other)
    if isinstance(want, str) and want.startswith("!"):
        if other == "currency":
            have = have or "USD"
        return have != want[1:]
    if want is True:
        return bool(have)
    return have == want


def visible(field, values):
    """Is this form field shown, given the category and the other values?"""
    r = _REQ[field]
    cats = r.get("categories")
    if cats is not None and values.get("category") not in cats:
        return False
    return _show_if_ok(r["show_if"], values) if r.get("show_if") else True


def _blank(v):
    return v is None or (isinstance(v, str) and not v.strip())


def missing_required(values, amount_usd=None):
    """Labels of required fields that are empty or invalid. Empty list = OK to submit.

    amount_usd: the converted amount (from the code-only preview) for the receipt rule.
    """
    missing = []
    for r in config.FORM_REQUIREMENTS:
        f, kind = r["field"], r["required"]
        if not visible(f, values) or kind == "optional":
            continue
        v = values.get(f)
        if kind == "if_over_receipt_threshold":
            if amount_usd is not None and amount_usd > config.RECEIPT_THRESHOLD_USD and not v:
                missing.append(r["label"])
            continue
        if f == "nights":
            if _blank(v) or int(v) < 1:
                missing.append(r["label"])
        elif f == "approval_code":
            if not normalize.approval_code_ok(v):
                missing.append(r["label"])
        elif f == "amount":
            if _blank(v) or float(v) <= 0:
                missing.append(r["label"])
        elif f == "client_name":
            if _blank(v) or len(v.strip()) < 2:
                missing.append(r["label"])
        elif _blank(v):
            missing.append(r["label"])
    return missing


def warnings(values):
    """Non-blocking notes from the map, e.g. Entertainment without client business."""
    out = []
    for r in config.FORM_REQUIREMENTS:
        w = (r.get("warn_unchecked") or {}).get(values.get("category"))
        if w and visible(r["field"], values) and not values.get(r["field"]):
            out.append(w)
    return out


def form_expense(values):
    """Form values (dict keyed by FORM_REQUIREMENTS field) -> expense for the engine."""
    v = values
    cat = v.get("category")
    exp = {"employee": v.get("employee"), "date": v.get("date"), "category": cat,
           "merchant": v.get("merchant"), "amount": build_amount(v.get("amount"), v.get("currency")),
           "memo": v.get("memo"), "receipt": bool(v.get("receipt")),
           "approval_code": v.get("approval_code") or None, "fact_source": "form"}
    if visible("amount_usd", v) and not _blank(v.get("amount_usd")):
        exp["amount_usd"] = float(v["amount_usd"])
    if visible("client_business", v):
        # The checkbox is the employee's attestation. Unchecked = not client business.
        if v.get("client_business"):
            exp["attendee_type"] = "CLIENT"
            exp["client_name"] = (v.get("client_name") or "").strip()
        else:
            exp["attendee_type"] = "INTERNAL"
        exp["alcohol_declared"] = bool(v.get("alcohol_declared"))
    if cat == "Hotel":
        city = resolve_city(v.get("city"), v.get("city_other"))
        if city:
            exp["city"] = city
        if not _blank(v.get("nights")) and int(v["nights"]) > 0:
            exp["nights"] = int(v["nights"])
    return exp


def hotel_rule_detail(payload):
    """The engine's own HOTEL_CAP_* detail (per-night math), or None."""
    for r in payload.get("rules_fired", []):
        if r["rule"].startswith("HOTEL_CAP"):
            return r["detail"]
    return None
