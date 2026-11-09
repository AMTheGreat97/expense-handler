"""The decision engine: RULEBOOK v0.3 as code.

decide(expense) runs the stages in order and returns a decision payload whose
`rules_fired` list is the full audit trail (every rule: pass / fail / gap /
n/a, with the values compared).

    S0  security screen                 -> REJECT
    S1  parse & validate                -> gaps
    S2  category present & known        -> gaps
    S3  facts: FX, LLM memo read, city  -> (LLM injection -> REJECT)
    S4  completeness (receipt, code, client, city, nights, USD)  -> gaps
        any gaps                        -> FLAG with ONE combined question
    S5  policy rules + overrides        -> REJECT (all broken rules listed)
    S6  default                         -> APPROVE

Facts from the LLM only count at HIGH confidence (client also needs a name).
"""

import re
from datetime import datetime, timezone

from . import cities, config, extract, normalize, questions, security

ALCOHOL_WORDS = re.compile(
    r"\b(beers?|wines?|drinks?|cocktails?|alcohol|booze|whiske?y|vodka|tequila|gin|rum|"
    r"champagne|prosecco|margaritas?|ipas?|pints?|sake|spirits|bar\s+tab)\b", re.I)


class Ctx:
    """Collects rule results, gaps and facts for one decision."""

    def __init__(self):
        self.rules = []
        self.gaps = []
        self.fails = []
        self.facts = {}
        self.notes = []
        self.llm = None

    def rule(self, rule_id, result, detail=""):
        self.rules.append({"rule": rule_id, "result": result, "detail": detail})
        if result == "fail":
            self.fails.append({"rule": rule_id, "detail": detail})

    def gap(self, gap_id, reason, **extra):
        if not any(g["id"] == gap_id for g in self.gaps):
            self.gaps.append({"id": gap_id, "reason": reason, **extra})


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _money(x):
    return f"${x:,.2f}"


def _resolve_attendee(exp, llm_facts, memo_blank, llm_failed):
    """Return (status, name, source, detail). status: client | internal | unknown."""
    a_type = (exp.get("attendee_type") or "").strip().upper()
    a_name = (exp.get("client_name") or "").strip()
    if a_type:                                           # structured: portal form / employee answer
        if a_type == "CLIENT":
            if len(a_name) > 1:
                return "client", a_name, "employee_answer", f"employee stated client '{a_name}'"
            return "unknown", None, "employee_answer", "employee chose Client but gave no company name"
        if a_type in {"INTERNAL", "VENDOR"}:
            return "internal", None, "employee_answer", f"employee stated {a_type.lower()} (not a client)"
    if memo_blank:
        return "internal", None, "code", "memo blank -> NONE -> treated as internal"
    if llm_failed or llm_facts is None:
        return "unknown", None, "llm_unavailable", "memo could not be read by the LLM"
    t, conf, name = llm_facts["attendee_type"], llm_facts["attendee_confidence"], llm_facts.get("client_name")
    ev = llm_facts.get("attendee_evidence")
    if t == "CLIENT" and conf == "high" and name:
        return "client", name, "llm", f"CLIENT/high '{name}' (evidence: {ev!r})"
    if t == "INTERNAL" and conf == "high":
        return "internal", None, "llm", f"INTERNAL/high (evidence: {ev!r})"
    return "unknown", name, "llm", f"{t}/{conf} name={name!r} -> not trusted"


def decide(expense, llm, fx, use_llm=True):
    """Return (payload, trace). payload has no versioning fields (pipeline adds them)."""
    exp = dict(expense)
    c = Ctx()
    memo = (exp.get("memo") or "").strip()
    note = (exp.get("employee_note") or "").strip()
    merchant = (exp.get("merchant") or "").strip()
    raw_category = exp.get("category")

    # ---- S0 security (deterministic) ---------------------------------------
    hits = security.screen({
        "memo": memo, "merchant": merchant, "category": raw_category if isinstance(raw_category, str) else "",
        "approval_code": exp.get("approval_code") if isinstance(exp.get("approval_code"), str) else "",
        "employee_note": note, "client_name": exp.get("client_name") or "", "city": exp.get("city") or "",
    })
    if hits:
        c.rule("SECURITY_PROMPT_INJECTION", "fail", f"{hits[0]['field']}: {hits[0]['quote']!r}")
        amt, _ = normalize.parse_amount(exp.get("amount"))
        d0, _ = normalize.parse_date(exp.get("date"))
        c.facts.update({"amount": amt[0] if amt else None, "currency": amt[1] if amt else None,
                        "amount_usd": amt[0] if amt and amt[1] == "USD" else None,
                        "date": d0.isoformat() if d0 else None, "weekday": d0.strftime("%a") if d0 else None,
                        "category": normalize.parse_category(raw_category)[0]})
        return _finish(exp, c, "reject", security_flags=["prompt_injection"], hits=hits)
    c.rule("SECURITY_PROMPT_INJECTION", "pass", "phrase screen: no hits")

    # ---- S1 parse & validate -----------------------------------------------
    if not exp.get("id"):
        c.gap("id", "expense has no id"); c.rule("REQUIRED_FIELDS", "gap", "id missing")
    if not (exp.get("employee") or "").strip():
        c.gap("employee", "employee name is missing"); c.rule("REQUIRED_FIELDS", "gap", "employee missing")

    amt, err = normalize.parse_amount(exp.get("amount"))
    if exp.get("amount_corrected") not in (None, ""):
        amt, err = normalize.parse_amount(exp.get("amount_corrected"))
    amount, currency = (amt if amt else (None, None))
    if err:
        c.gap("amount_fix", err); c.rule("AMOUNT_VALID", "gap", err)
    else:
        c.rule("AMOUNT_VALID", "pass", f"{amount} {currency}")

    d, err = normalize.parse_date(exp.get("date_corrected") or exp.get("date"))
    if err:
        c.gap("date_fix", err); c.rule("DATE_VALID", "gap", err)
    else:
        c.rule("DATE_VALID", "pass", f"{d.isoformat()} ({d.strftime('%A')})")

    receipt, err = normalize.parse_receipt(exp.get("receipt"))
    if err:
        c.rule("RECEIPT_FIELD_VALID", "gap", err)

    # ---- S2 category -------------------------------------------------------
    category, cstatus = normalize.parse_category(raw_category)
    if cstatus == "missing":
        c.rule("CATEGORY_PRESENT", "gap", "category is blank")
        category = None
    elif cstatus == "unknown":
        c.rule("CATEGORY_PRESENT", "gap", f"unknown category {category!r}")
        category = None
    else:
        c.rule("CATEGORY_PRESENT", "pass", category)

    # ---- S3 facts: FX ------------------------------------------------------
    amount_usd = None
    if amount is not None:
        if currency == "USD":
            amount_usd = amount
        elif exp.get("amount_usd") not in (None, ""):
            try:
                amount_usd = round(float(exp["amount_usd"]), 2)
                c.rule("FX_CONVERSION", "pass", f"employee provided USD amount {_money(amount_usd)}")
            except (TypeError, ValueError):
                pass
        if amount_usd is None and currency != "USD":
            conv = fx.to_usd(amount, currency, d)
            c.facts["fx"] = conv
            if "error" in conv:
                c.gap("amount_usd", f"could not convert {amount} {currency} to USD")
                c.rule("FX_CONVERSION", "gap", conv["error"][:300])
            else:
                amount_usd = conv["amount_usd"]
                c.rule("FX_CONVERSION", "pass",
                       f"{amount} {currency} x {conv['rate']} ({conv['rate_date']}) = {_money(amount_usd)}")

    # ---- S3 facts: LLM memo read -------------------------------------------
    memo_blank = not memo and not note
    needs_llm = use_llm and (not memo_blank or category == "Hotel" or category is None)
    llm_facts, llm_failed = None, False
    if needs_llm:
        res = extract.run(llm, category, raw_category, merchant, memo, note)
        c.llm = res
        if res["error"]:
            llm_failed = True
            c.rule("LLM_EXTRACTION", "error", res["error"][:300])
        else:
            llm_facts = res["facts"]
            c.rule("LLM_EXTRACTION", "pass", f"{res['prompt_file']}: {llm_facts.get('reasoning', '')[:300]}")
            for n in res["verification"]:
                c.notes.append(n)
            if llm_facts.get("_injection_verified"):
                c.rule("SECURITY_PROMPT_INJECTION_LLM", "fail", f"{llm_facts.get('injection_evidence')!r}")
                return _finish(exp, c, "reject", security_flags=["prompt_injection"],
                               amount_usd=amount_usd, category=category)
            c.rule("SECURITY_PROMPT_INJECTION_LLM", "pass" if not llm_facts["injection_detected"] else "unverified",
                   "" if not llm_facts["injection_detected"] else "LLM claimed injection without a matching quote")
    elif not use_llm:
        c.rule("LLM_EXTRACTION", "skipped", "preview mode (code-only checks)")
        llm_failed = not memo_blank

    attendee, client_name, a_source, a_detail = _resolve_attendee(exp, llm_facts, memo_blank, llm_failed)
    alcohol_kw = bool(ALCOHOL_WORDS.search(f"{memo} {note}"))
    alcohol = alcohol_kw or bool(llm_facts and llm_facts["alcohol_mentioned"])
    c.facts.update({
        "amount": amount, "currency": currency, "amount_usd": amount_usd,
        "date": d.isoformat() if d else None, "weekday": d.strftime("%a") if d else None,
        "is_weekend": bool(d and d.weekday() >= 5), "category": category, "receipt": receipt,
        "attendee": {"status": attendee, "client_name": client_name, "source": a_source, "detail": a_detail},
        "alcohol": {"mentioned": alcohol, "source": "keyword" if alcohol_kw else ("llm" if alcohol else None)},
    })

    # ---- S2 (cont.) category gap, pre-asking what each category needs --------
    if category is None:
        c.gap("category", "category is missing or not recognised",
              suggestion=(llm_facts or {}).get("suggested_category"),
              llm_client_name=client_name)

    # ---- S4 completeness: golden receipt rule ------------------------------
    if amount_usd is not None:
        if amount_usd > config.RECEIPT_THRESHOLD_USD:
            if receipt is True:
                c.rule("RECEIPT_REQUIRED", "pass", f"{_money(amount_usd)} > $25.00 and receipt attached")
            else:
                c.rule("RECEIPT_REQUIRED", "gap", f"{_money(amount_usd)} > $25.00 and no receipt")
                c.gap("receipt", "Receipts are required for any expense over $25.00.")
        else:
            c.rule("RECEIPT_REQUIRED", "n/a", f"{_money(amount_usd)} <= $25.00")
    elif receipt is not True:
        c.rule("RECEIPT_REQUIRED", "gap", "USD amount unknown and no receipt")
        c.gap("receipt", "Receipts are required for any expense over $25.00.")

    def need_client(reason):
        if attendee == "unknown":
            c.gap("attendee", reason, llm_client_name=client_name)
            return True
        return False

    # ---- Global alcohol rule (any category) ---------------------------------
    alcohol_blocked = False
    if alcohol:
        if attendee == "client":
            c.rule("ALCOHOL_INTERNAL", "pass", f"alcohol mentioned, client confirmed ({client_name})")
        elif not need_client("Alcohol is reimbursed only when a client attended."):
            alcohol_blocked = True
        else:
            c.rule("ALCOHOL_INTERNAL", "gap", "alcohol mentioned, client not confirmed")
    else:
        c.rule("ALCOHOL_INTERNAL", "n/a", "no alcohol mentioned")

    # ---- Category rules -----------------------------------------------------
    if category in config.MEAL_CATEGORIES:
        cap = config.MEAL_CAPS_USD[category]
        rid = f"MEAL_CAP_{category.upper()}"
        over = amount_usd is not None and amount_usd > cap
        weekend = c.facts["is_weekend"]
        if amount_usd is None:
            c.rule(rid, "gap", "USD amount unknown")
        elif not over:
            c.rule(rid, "pass", f"{_money(amount_usd)} <= {_money(cap)}")
        elif attendee == "client":
            c.rule(rid, "pass", f"{_money(amount_usd)} > {_money(cap)} but client confirmed ({client_name}) -> cap waived")
        elif need_client(f"{category} over {_money(cap)} is reimbursed only when a client attended."):
            c.rule(rid, "gap", f"{_money(amount_usd)} > {_money(cap)}, client not confirmed")
        else:
            c.rule(rid, "fail", f"{_money(amount_usd)} > {_money(cap)}; {a_detail}")

        if not weekend:
            c.rule("WEEKEND_MEAL_INTERNAL", "n/a", f"{c.facts['weekday'] or 'unknown day'}")
        elif attendee == "client":
            c.rule("WEEKEND_MEAL_INTERNAL", "pass", f"{c.facts['weekday']}, client confirmed ({client_name})")
        elif need_client("Weekend meals are reimbursed only when a client attended."):
            c.rule("WEEKEND_MEAL_INTERNAL", "gap", f"{c.facts['weekday']}, client not confirmed")
        else:
            c.rule("WEEKEND_MEAL_INTERNAL", "fail", f"meal on {c.facts['weekday']}; {a_detail}")

    elif category == "Entertainment":
        if attendee == "client":
            c.rule("ENTERTAINMENT_NO_CLIENT", "pass", f"client confirmed ({client_name})")
        elif need_client("Entertainment is reimbursed only with a client; please name the client company."):
            c.rule("ENTERTAINMENT_NO_CLIENT", "gap", a_detail)
        else:
            c.rule("ENTERTAINMENT_NO_CLIENT", "fail", a_detail)

    elif category == "Hotel":
        _hotel(exp, c, merchant, memo, note, amount_usd, llm_facts, llm_failed)

    elif category == "Software":
        code = exp.get("approval_code")
        if normalize.approval_code_ok(code):
            c.rule("SOFTWARE_APPROVAL_CODE", "pass", f"code {code.strip()!r}")
        else:
            c.rule("SOFTWARE_APPROVAL_CODE", "gap", f"approval code missing or too short: {code!r}")
            c.gap("approval_code", "Software purchases always need an approval code.")

    elif category in {"Office", "Ground Transport", "Airfare"}:
        c.rule(f"{category.upper().replace(' ', '_')}_DEFAULT", "pass", "no category cap; global rules only")

    if alcohol_blocked:
        c.rule("ALCOHOL_INTERNAL", "fail", f"alcohol mentioned; {a_detail}")

    # ---- Decide --------------------------------------------------------------
    if c.gaps:
        return _finish(exp, c, "flag", amount_usd=amount_usd, category=category, route="employee")
    if c.fails:
        return _finish(exp, c, "reject", amount_usd=amount_usd, category=category)
    if llm_failed or (llm_facts and llm_facts["injection_detected"] and not llm_facts.get("_injection_verified")):
        c.gap("manual_review", "Our automatic check could not read the memo; a Finance reviewer will look at it.")
        c.rule("FAIL_CLOSED", "gap", "LLM unavailable or unverified security signal -> never auto-approve")
        return _finish(exp, c, "flag", amount_usd=amount_usd, category=category, route="finance")
    tags = []
    if a_source == "employee_answer" and attendee == "client" and any(
            r["result"] == "pass" and "client confirmed" in r["detail"] for r in c.rules):
        tags.append("approved_on_employee_attestation")
    return _finish(exp, c, "approve", amount_usd=amount_usd, category=category, tags=tags)


def _hotel(exp, c, merchant, memo, note, amount_usd, llm_facts, llm_failed):
    city, tier, src = None, None, None
    if (exp.get("city") or "").strip():
        city_in = exp["city"].strip()
        t1 = cities.canonical_tier1(city_in)
        city, tier, src = (t1 or city_in), (1 if t1 else 2), "employee_answer"
    else:
        table_city, tnote = cities.table_match(f"{merchant} {memo} {note}")
        llm_city = llm_facts.get("city") if llm_facts and llm_facts["city_confidence"] == "high" else None
        llm_t1 = cities.canonical_tier1(llm_city) if llm_city else None
        if table_city and llm_city and llm_t1 != table_city:
            c.notes.append(f"city table says {table_city}, LLM says {llm_city} -> ask")
        elif table_city:
            city, tier, src = table_city, 1, f"city_table ({tnote})"
        elif llm_city:
            city, tier, src = (llm_t1 or llm_city), (1 if llm_t1 else 2), "llm (high)"
    c.facts["hotel"] = {"city": city, "tier": tier, "source": src}
    if city is None:
        c.rule("HOTEL_CITY_KNOWN", "gap", "hotel city could not be determined" + (" (LLM unavailable)" if llm_failed else ""))
        c.gap("city", "Hotel limits depend on the city ($350/night in Tier-1 cities, $200/night elsewhere).")
        return
    c.rule("HOTEL_CITY_KNOWN", "pass", f"{city} -> Tier {tier} via {src}")
    cap = config.HOTEL_CAP_TIER1_USD if tier == 1 else config.HOTEL_CAP_TIER2_USD
    rid = f"HOTEL_CAP_TIER{tier}"
    nights = exp.get("nights")
    try:
        nights = int(nights) if nights not in (None, "") else None
    except (TypeError, ValueError):
        nights = None
    nights = nights or normalize.nights_from_text(f"{memo} {note}") or (llm_facts or {}).get("nights")
    c.facts["hotel"]["nights"] = nights
    if amount_usd is None:
        c.rule(rid, "gap", "USD amount unknown")
        return
    if nights is None:
        if amount_usd <= cap:
            c.rule(rid, "pass", f"{_money(amount_usd)} <= {_money(cap)}/night even for 1 night")
            return
        c.rule(rid, "gap", f"{_money(amount_usd)} total, nights unknown")
        c.gap("nights", f"We need the number of nights to check the {_money(cap)}/night limit.")
        return
    per_night = round(amount_usd / max(nights, 1), 2)
    if per_night <= cap:
        c.rule(rid, "pass", f"{_money(per_night)}/night x {nights} <= {_money(cap)}/night ({city})")
    else:
        c.rule(rid, "fail", f"{_money(per_night)}/night > {_money(cap)}/night ({city}, Tier {tier})")


def _reason(decision, c):
    if decision == "reject":
        if any(r["rule"].startswith("SECURITY") and r["result"] == "fail" for r in c.rules):
            return "Rejected: the expense text tries to instruct the reviewer/system (prompt injection)."
        return "Rejected: " + "; ".join(f"{f['rule']} ({f['detail']})" for f in c.fails)
    if decision == "flag":
        return "Needs information: " + "; ".join(g["reason"].rstrip(".") for g in c.gaps) + "."
    return "Approved: every applicable rule passed."


def _finish(exp, c, decision, security_flags=None, hits=None, amount_usd=None, category=None,
            route=None, tags=None):
    q = questions.build(exp, c.facts, c.gaps) if decision == "flag" else None
    payload = {
        "expense_id": exp.get("id"),
        "employee": exp.get("employee"),
        "decision": decision,
        "reason": _reason(decision, c),
        "rules_fired": c.rules,
        "missing_fields": [g["id"] for g in c.gaps] if decision == "flag" else [],
        "question": q,
        "routed_to": route if decision == "flag" else None,
        "facts": c.facts,
        "security_flags": security_flags or [],
        "tags": tags or [],
        "rulebook_version": config.RULEBOOK_VERSION,
        "llm": ({"model": (c.llm.get("call") or {}).get("model"), "prompt": c.llm.get("prompt_file")}
                if c.llm else None),
        "decided_at": _now(),
    }
    trace = {
        "expense_in": exp,
        "security_hits": hits or [],
        "notes": c.notes,
        "gaps": c.gaps,
        "llm": c.llm,
    }
    return payload, trace
