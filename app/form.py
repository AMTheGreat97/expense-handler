"""Portal form -> expense dict, driven by config.FORM_REQUIREMENTS.

Kept free of gradio so it can be unit-tested. The form only collects facts;
every decision still comes from engine.decide().
"""

import math
from datetime import date, datetime

from . import config, normalize

CURRENCIES = ["USD", "EUR", "GBP", "INR", "CAD"]
OTHER_CITY = "Other"
FIELDS = [r["field"] for r in config.FORM_REQUIREMENTS]
_REQ = {r["field"]: r for r in config.FORM_REQUIREMENTS}

# Engine gap ids -> words an employee understands (live preview, answer form).
GAP_LABELS = {
    "id": "an expense id", "employee": "your name", "amount_fix": "a valid amount", "date_fix": "a valid date",
    "category": "the category", "receipt": "the receipt", "amount_usd": "the USD amount on your card statement",
    "attendee": "who attended (client or not)", "alcohol": "whether it included alcohol",
    "approval_code": "the software approval code", "city": "the hotel city", "nights": "the hotel stay dates",
    "manual_review": "a Finance review (the AI reads the memo when you press Submit)",
}


def gap_labels(gap_ids):
    return [GAP_LABELS.get(g, g) for g in gap_ids or ()]


def _blank(v):
    return v is None or (isinstance(v, str) and not v.strip())


def build_amount(amount, currency):
    """Number + currency code -> what normalize.parse_amount expects ("65 EUR")."""
    if _blank(amount):
        return None
    currency = (currency or "USD").upper()
    return float(amount) if currency == "USD" else f"{amount} {currency}"


def resolve_city(city_choice, city_other):
    """Dropdown value (+ typed city when "Other") -> city string or None."""
    choice = (city_choice or "").strip()
    if choice in (OTHER_CITY, "Other (type it)"):
        return (city_other or "").strip() or None
    return choice or None


def to_iso_date(v):
    """Date-picker value (str 'YYYY-MM-DD[ hh:mm:ss]', date, datetime or timestamp) -> 'YYYY-MM-DD' or None."""
    if _blank(v):
        return None
    if isinstance(v, datetime):
        return v.date().isoformat()
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return datetime.fromtimestamp(v).date().isoformat()
    s = str(v).strip()
    return s[:10] if len(s) > 10 and s[10] in " T" else s


def stay_nights(check_in, check_out):
    """(nights, error). Nights = check-out minus check-in, so a stay must be at least one night."""
    if _blank(check_in) or _blank(check_out):
        return None, "both stay dates are needed"
    try:
        d_in = datetime.strptime(to_iso_date(check_in), "%Y-%m-%d").date()
        d_out = datetime.strptime(to_iso_date(check_out), "%Y-%m-%d").date()
    except ValueError:
        return None, "use YYYY-MM-DD"
    if d_out <= d_in:
        return None, "check-out must be after check-in"
    return (d_out - d_in).days, None


def _date_error(v):
    """'YYYY-MM-DD' date the expense was paid -> None or a short reason."""
    _, err = normalize.parse_date(to_iso_date(v))
    if not err:
        return None
    return "can't be in the future" if "future" in err else "use YYYY-MM-DD"


def _number(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


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


def missing_required(values, amount_usd=None, engine_gaps=()):
    """Labels of required fields that are empty or invalid. Empty list = OK to submit.

    amount_usd:  the converted amount (from the code-only preview) for the receipt rule.
    engine_gaps: the preview's missing_fields; if the live FX lookup failed ("amount_usd"),
                 the optional card-statement USD amount becomes required.
    """
    missing = []
    for r in config.FORM_REQUIREMENTS:
        f, kind, label = r["field"], r["required"], r["label"]
        if not visible(f, values):
            continue
        v = values.get(f)
        if kind == "optional":
            if f == "amount_usd":
                if not _blank(v) and (_number(v) is None or _number(v) <= 0):
                    missing.append(label + " (must be more than 0)")
                elif "amount_usd" in engine_gaps and _blank(v):
                    missing.append(label + " (the currency conversion is unavailable right now)")
            continue
        if kind == "if_over_receipt_threshold":
            if amount_usd is not None and amount_usd > config.RECEIPT_THRESHOLD_USD and not v:
                missing.append(label)
            continue
        if f == "date":
            if _blank(v):
                missing.append(label)
            elif _date_error(v):
                missing.append(f"{label} ({_date_error(v)})")
        elif f == "check_in":
            if _blank(v):
                missing.append(label)
        elif f == "check_out":
            if _blank(v):
                missing.append(label)
            elif not _blank(values.get("check_in")):
                _, err = stay_nights(values.get("check_in"), v)
                if err:
                    missing.append(f"{label} ({err})")
        elif f == "approval_code":
            if not normalize.approval_code_ok(v):
                missing.append(label if _blank(v) else label + " (at least 2 characters)")
        elif f == "amount":
            if _blank(v):
                missing.append(label)
            elif _number(v) is None or _number(v) <= 0:
                missing.append(label + " (must be more than 0)")
        elif f == "client_name":
            if _blank(v) or len(v.strip()) < 2:
                missing.append(label)
        elif _blank(v):
            missing.append(label)
    return missing


def warnings(values):
    """Non-blocking notes from the map, e.g. Entertainment without client business."""
    out = []
    for r in config.FORM_REQUIREMENTS:
        w = (r.get("warn_unchecked") or {}).get(values.get("category"))
        if w and visible(r["field"], values) and not values.get(r["field"]):
            out.append(w)
    if visible("check_out", values):
        n, err = stay_nights(values.get("check_in"), values.get("check_out"))
        paid = to_iso_date(values.get("date"))
        if n and paid and not _date_error(values.get("date")) and paid < to_iso_date(values.get("check_in")):
            out.append("The payment date is before check-in. That is fine for a prepaid stay; otherwise check the dates.")
    return out


def form_expense(values):
    """Form values (dict keyed by FORM_REQUIREMENTS field) -> expense for the engine."""
    v = values
    cat = v.get("category")
    exp = {"employee": (v.get("employee") or "").strip() or None, "date": to_iso_date(v.get("date")),
           "category": cat, "merchant": v.get("merchant"),
           "amount": build_amount(v.get("amount"), v.get("currency")),
           "memo": v.get("memo"), "receipt": bool(v.get("receipt")), "fact_source": "form"}
    # Only facts whose field is on screen count; values left in a hidden field are dropped.
    if visible("approval_code", v) and not _blank(v.get("approval_code")):
        exp["approval_code"] = v["approval_code"]
    else:
        exp["approval_code"] = None
    if visible("amount_usd", v) and _number(v.get("amount_usd")) is not None:
        exp["amount_usd"] = _number(v["amount_usd"])
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
        n, err = stay_nights(v.get("check_in"), v.get("check_out"))
        if not err:
            exp["nights"] = n
            exp["check_in"], exp["check_out"] = to_iso_date(v["check_in"]), to_iso_date(v["check_out"])
    return exp


def hotel_rule_detail(payload):
    """The engine's own HOTEL_CAP_* detail (per-night math), or None."""
    for r in payload.get("rules_fired", []):
        if r["rule"].startswith("HOTEL_CAP"):
            return r["detail"]
    return None


# ---- Answer form (follow-up tab) -----------------------------------------------
# A question field -> the answer inputs that fill it. Nights, like on the main form,
# come from the stay dates instead of a typed number.
ANSWER_INPUTS = {"nights": ["check_in", "check_out"]}
ANSWER_LABELS = {"attendee_type": "who attended", "alcohol_declared": "whether it included alcohol",
                 "receipt": "whether the receipt is attached", "category": "the category", "city": "the hotel city",
                 "employee": "your name", "approval_code": "the software approval code"}


def answer_inputs(qfield_name):
    return ANSWER_INPUTS.get(qfield_name, [qfield_name])


def clean_answers(question_fields, raw):
    """(answers for questions.apply_answers, problems). Nothing is sent while problems is non-empty.

    question_fields: question["fields"] from the open decision.
    raw: answer-input name -> value (plus "city_other" for the typed city).
    """
    answers, problems = {}, []
    for fld in question_fields:
        name, optional = fld["name"], fld.get("optional", False)
        label = ANSWER_LABELS.get(name) or fld.get("label") or name.replace("_", " ")
        if name == "nights":
            ci, co = raw.get("check_in"), raw.get("check_out")
            if _blank(ci) and _blank(co):
                if not optional:
                    problems.append("the check-in and check-out dates")
                continue
            n, err = stay_nights(ci, co)
            if err:
                problems.append(f"the stay dates ({err})")
            else:
                answers["nights"] = n
                answers["check_in"], answers["check_out"] = to_iso_date(ci), to_iso_date(co)
            continue
        v = raw.get(name)
        if name == "city":
            v = resolve_city(v, raw.get("city_other"))
            if _blank(v) and not _blank(raw.get("city")):
                problems.append("the city name (you picked Other)")
                continue
        if name in ("date_corrected",):
            v = to_iso_date(v)
        if _blank(v) or v is False:
            if not optional and name != "client_name":
                problems.append(label)
            continue
        if name in ("amount_usd",) and (_number(v) is None or _number(v) <= 0):
            problems.append(f"{label} (must be more than 0)")
            continue
        if name == "amount_corrected" and normalize.parse_amount(v)[1]:
            problems.append(f"{label} ({normalize.parse_amount(v)[1]})")
            continue
        if name == "date_corrected" and _date_error(v):
            problems.append(f"{label} ({_date_error(v)})")
            continue
        if name == "approval_code" and not normalize.approval_code_ok(v):
            problems.append(f"{label} (at least 2 characters)")
            continue
        answers[name] = _number(v) if name == "amount_usd" else v
    # A client answer needs the company, whether or not the name field was marked optional.
    if str(answers.get("attendee_type", "")).lower().startswith("client") and \
            len(str(answers.get("client_name") or "").strip()) < 2:
        problems.append("the client company name")
    return answers, problems


def is_conditional(field):
    """Does this field ever hide (category- or value-dependent)?"""
    return bool(_REQ[field].get("categories") is not None or _REQ[field].get("show_if"))
