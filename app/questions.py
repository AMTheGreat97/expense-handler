"""Single-round follow-up questions, built from the gap list (no LLM).

One flagged decision -> ONE question that asks for everything missing, with
pick-from options where possible and free text where needed. The question has
two forms that always agree:
  * question["text"]   - self-contained, answerable in one email reply
  * question["fields"] - drives the portal answer form
"""

from . import config, normalize

ATTENDEE_OPTIONS = ["Internal only (our employees)", "Client", "Vendor / partner / other"]
_ATTENDEE_MAP = {ATTENDEE_OPTIONS[0]: "INTERNAL", ATTENDEE_OPTIONS[1]: "CLIENT", ATTENDEE_OPTIONS[2]: "VENDOR"}
TIER1_CHOICES = ["New York", "Los Angeles", "San Francisco", "Washington DC", "Seattle", "Chicago", "Boston", "London"]
ALCOHOL_OPTIONS = ["Yes, it included alcohol", "No alcohol"]


def _describe(exp, facts):
    amt = facts.get("amount")
    cur = facts.get("currency") or ""
    money = (f"${amt:,.2f}" if cur == "USD" else f"{amt:,.2f} {cur}") if amt is not None else ""
    cat = (facts.get("category") or "expense").lower()
    merch = f" at {exp.get('merchant')}" if exp.get("merchant") else ""
    when = f" on {facts['date']}" if facts.get("date") else ""
    return f"{money} {cat}{merch}{when}".strip()


def build(exp, facts, gaps):
    fields, asks = [], []
    for g in gaps:
        gid = g["id"]
        if gid == "receipt":
            fields.append({"name": "receipt", "type": "confirm", "label": "I have attached the receipt"})
            asks.append(g["reason"] + (" Please attach it." if facts.get("amount_usd") is not None
                                        and facts["amount_usd"] > config.RECEIPT_THRESHOLD_USD else ""))
        elif gid == "category":
            fields.append({"name": "category", "type": "choice", "options": config.ALLOWED_CATEGORIES,
                           "prefill": g.get("suggestion")})
            fields.append({"name": "attendee_type", "type": "choice", "options": ATTENDEE_OPTIONS,
                           "optional": True, "label": "If a meal or entertainment: who attended?"})
            fields.append({"name": "client_name", "type": "text", "optional": True,
                           "prefill": g.get("llm_client_name"), "label": "Client company (if a client attended)"})
            asks.append("What category is this expense (e.g. Lunch, Dinner, Office, Hotel, Software)? "
                        "If it was a meal or entertainment, tell us whether it was internal or with a client, "
                        "and name the client company.")
            if not normalize.approval_code_ok(exp.get("approval_code")):
                fields.append({"name": "approval_code", "type": "text", "optional": True})
                asks.append("If Software, include the approval code.")
            if not exp.get("city"):
                fields.append({"name": "city", "type": "choice_or_text", "options": TIER1_CHOICES + ["Other (type it)"],
                               "optional": True})
                asks.append("If Hotel, include the city of the stay.")
            if not exp.get("nights") and (facts.get("amount_usd") is None or
                                          facts["amount_usd"] > config.HOTEL_CAP_TIER2_USD):
                fields.append({"name": "nights", "type": "number", "optional": True})
                asks.append("If Hotel, include the exact billed nights if the total exceeds the city's nightly cap.")
        elif gid == "attendee":
            fields.append({"name": "attendee_type", "type": "choice", "options": ATTENDEE_OPTIONS})
            fields.append({"name": "client_name", "type": "text", "prefill": g.get("llm_client_name"),
                           "label": "Client company name (required if Client)"})
            who = f" Was {g['llm_client_name']} a client?" if g.get("llm_client_name") else ""
            asks.append(f"Who attended: coworkers only, an external customer, or a vendor/partner?{who} If a customer, please name the "
                        f"company. ({g['reason']})")
        elif gid == "alcohol":
            fields.append({"name": "alcohol_declared", "type": "choice", "options": ALCOHOL_OPTIONS})
            asks.append(g["reason"])
        elif gid == "approval_code":
            fields.append({"name": "approval_code", "type": "text", "label": "Software approval code"})
            asks.append("Please provide the software approval code.")
        elif gid == "city":
            fields.append({"name": "city", "type": "choice_or_text", "options": TIER1_CHOICES + ["Other (type it)"],
                           "label": "City where the hotel is"})
            asks.append("Which city was the hotel in?")
        elif gid == "nights":
            fields.append({"name": "nights", "type": "number", "label": "Number of nights"})
            asks.append("Exactly how many nights does this charge cover?")
        elif gid == "amount_usd":
            fields.append({"name": "amount_usd", "type": "number", "label": "Amount in USD (from your card statement)"})
            asks.append("What USD amount appears on your card statement?")
        elif gid == "amount_fix":
            fields.append({"name": "amount_corrected", "type": "text", "label": "Amount (e.g. 42.50 or €42.50)"})
            asks.append(f"Please correct the amount ({g['reason']}).")
        elif gid == "date_fix":
            fields.append({"name": "date_corrected", "type": "text", "label": "Date (YYYY-MM-DD)"})
            asks.append(f"Please correct the date ({g['reason']}).")
        elif gid == "employee":
            fields.append({"name": "employee", "type": "text", "label": "Your name"})
            asks.append("Please add your name.")
        elif gid == "manual_review":
            asks.append(g["reason"])
        else:
            asks.append(g["reason"])
    fields.append({"name": "employee_note", "type": "text", "optional": True,
                   "label": "Anything else we should know? (optional)"})

    intro = f"To finish reviewing expense {exp.get('id') or '(ID missing)'} ({_describe(exp, facts)})"
    if len(asks) == 1:
        text = f"{intro}, we need one thing: {asks[0]}"
    else:
        text = f"{intro}, we need the following (please answer all in one reply):\n" + \
               "\n".join(f"{i}. {a}" for i, a in enumerate(asks, 1))
    return {"text": text, "fields": list({f["name"]: f for f in fields}.values())}


def apply_answers(expense, answers):
    """Merge an employee's answers into a copy of the expense. Free text stays untrusted."""
    exp = dict(expense)
    a = {k: v for k, v in (answers or {}).items() if v not in (None, "", [])}
    # Remember which facts the employee answered, so the engine can tell form vs answer.
    exp["answered_fields"] = sorted(set(exp.get("answered_fields") or []) | set(a))
    if "alcohol_declared" in a:
        exp["alcohol_declared"] = a["alcohol_declared"] in (True, ALCOHOL_OPTIONS[0], "yes", "true")
    if a.get("receipt") in (True, "true", "yes"):
        exp["receipt"] = True
    elif a.get("receipt") in (False, "false", "no"):
        exp["receipt"] = False
    if "category" in a:
        exp["category"] = a["category"]
    if "attendee_type" in a:
        exp["attendee_type"] = _ATTENDEE_MAP.get(a["attendee_type"], str(a["attendee_type"]).upper())
    if "client_name" in a:
        exp["client_name"] = str(a["client_name"]).strip()
    for k in ("approval_code", "city", "employee", "amount_corrected", "date_corrected"):
        if k in a:
            exp[k] = str(a[k]).strip()
    for k in ("nights", "amount_usd"):
        if k in a:
            exp[k] = a[k]
    if "employee_note" in a:
        prev = exp.get("employee_note") or ""
        exp["employee_note"] = (prev + "\n" + str(a["employee_note"]).strip()).strip()
    return exp
