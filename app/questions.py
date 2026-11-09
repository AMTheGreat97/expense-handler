"""Single-round follow-up questions, built from the gap list (no LLM).

One flagged decision -> ONE question that asks for everything missing, with
pick-from options where possible and free text where needed. The question has
two forms that always agree:
  * question["text"]   - self-contained, answerable in one email reply
  * question["fields"] - drives the portal answer form
"""

from . import config

ATTENDEE_OPTIONS = ["Internal only (our employees)", "Client", "Vendor / partner / other"]
_ATTENDEE_MAP = {ATTENDEE_OPTIONS[0]: "INTERNAL", ATTENDEE_OPTIONS[1]: "CLIENT", ATTENDEE_OPTIONS[2]: "VENDOR"}
TIER1_CHOICES = ["New York", "Los Angeles", "San Francisco", "Washington DC", "Seattle", "Chicago", "Boston", "London"]


def _describe(exp, facts):
    amt = facts.get("amount")
    cur = facts.get("currency") or ""
    money = (f"${amt:,.2f}" if cur == "USD" else f"{amt:,.2f} {cur}") if amt is not None else "your"
    cat = (facts.get("category") or "expense").lower()
    merch = f" at {exp.get('merchant')}" if exp.get("merchant") else ""
    when = f" on {facts['date']}" if facts.get("date") else ""
    return f"{money} {cat}{merch}{when}"


def build(exp, facts, gaps):
    fields, asks = [], []
    for g in gaps:
        gid = g["id"]
        if gid == "receipt":
            fields.append({"name": "receipt", "type": "confirm", "label": "I have attached the receipt"})
            asks.append(f"Please attach the receipt. {g['reason']}")
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
        elif gid == "attendee":
            fields.append({"name": "attendee_type", "type": "choice", "options": ATTENDEE_OPTIONS})
            fields.append({"name": "client_name", "type": "text", "prefill": g.get("llm_client_name"),
                           "label": "Client company name (required if Client)"})
            who = f" Was {g['llm_client_name']} a client?" if g.get("llm_client_name") else ""
            asks.append(f"Who attended: only our employees, or a client?{who} If a client, please name the "
                        f"company. ({g['reason']})")
        elif gid == "approval_code":
            fields.append({"name": "approval_code", "type": "text", "label": "Software approval code"})
            asks.append(f"Please provide the software approval code. {g['reason']}")
        elif gid == "city":
            fields.append({"name": "city", "type": "choice_or_text", "options": TIER1_CHOICES + ["Other (type it)"],
                           "label": "City where the hotel is"})
            asks.append(f"Which city was the hotel in? {g['reason']}")
        elif gid == "nights":
            fields.append({"name": "nights", "type": "number", "label": "Number of nights"})
            asks.append(f"How many nights does this hotel charge cover? {g['reason']}")
        elif gid == "amount_usd":
            fields.append({"name": "amount_usd", "type": "number", "label": "Amount in USD (from your card statement)"})
            asks.append(f"What USD amount was charged on your card? We {g['reason']}.")
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

    intro = f"To finish reviewing your {_describe(exp, facts)}"
    if len(asks) == 1:
        text = f"{intro}, we need one thing: {asks[0]}"
    else:
        text = f"{intro}, we need the following (please answer all in one reply):\n" + \
               "\n".join(f"{i}. {a}" for i, a in enumerate(asks, 1))
    return {"text": text, "fields": fields}


def apply_answers(expense, answers):
    """Merge an employee's answers into a copy of the expense. Free text stays untrusted."""
    exp = dict(expense)
    a = {k: v for k, v in (answers or {}).items() if v not in (None, "", [])}
    if a.get("receipt") in (True, "true", "yes"):
        exp["receipt"] = True
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
