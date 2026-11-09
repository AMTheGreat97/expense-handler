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
import math
from decimal import Decimal
from datetime import datetime, timezone

from . import cities, config, extract, normalize, questions, security

ALCOHOL_WORDS = re.compile(
    r"\b(beers?|wines?|cocktails?|alcohol|booze|whiske?y|vodka|tequila|gin|rum|"
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


def given_by(exp, field):
    """Where a structured field on the expense came from: 'form' or 'employee_answer'.

    Portal submissions carry fact_source='form'; anything the employee later
    answered (or any structured field on a batch expense) is 'employee_answer'.
    """
    if exp.get("fact_source") == "form" and field not in (exp.get("answered_fields") or []):
        return "form"
    return "employee_answer"


def _resolve_attendee(exp, llm_facts, memo_blank, llm_failed):
    """Return (status, name, source, detail). status: client | internal | unknown."""
    a_type = (exp.get("attendee_type") or "").strip().upper()
    a_name = (exp.get("client_name") or "").strip()
    if a_type:                                           # structured: portal form / employee answer
        src = given_by(exp, "attendee_type")
        who = "employee attested on the form" if src == "form" else "employee stated"
        if a_type == "CLIENT":
            if len(a_name) > 1:
                return "client", a_name, src, f"{who} client '{a_name}'"
            return "unknown", None, src, "employee chose Client but gave no company name"
        if a_type in {"INTERNAL", "VENDOR"}:
            return "internal", None, src, f"{who} {a_type.lower()} (not a client)"
    if memo_blank:
        return "internal", None, "code", "memo blank -> NONE -> treated as internal"
    if llm_failed or llm_facts is None:
        return "unknown", None, "llm_unavailable", "memo could not be read by the LLM"
    t, conf, name = llm_facts["attendee_type"], llm_facts["attendee_confidence"], llm_facts.get("client_name")
    ev = llm_facts.get("attendee_evidence")
    if t == "CLIENT" and conf == "high" and name:
        return "client", name, "memo_llm", f"CLIENT/high '{name}' (evidence: {ev!r})"
    if t == "INTERNAL" and conf == "high":
        return "internal", None, "memo_llm", f"INTERNAL/high (evidence: {ev!r})"
    if t == "VENDOR" and conf == "high" and re.search(r"\b(vendors?|suppliers?)\b", ev or "", re.I):
        return "vendor", None, "memo_llm", f"VENDOR/high (evidence: {ev!r})"
    return "unknown", name, "memo_llm", f"{t}/{conf} name={name!r} -> not trusted"


def _attendee_conflict(attendee, a_source, llm_facts):
    """Form attestation vs a HIGH-confidence memo read that says the opposite -> detail, else None."""
    if a_source != "form" or not llm_facts or llm_facts.get("attendee_confidence") != "high":
        return None
    t, name, ev = llm_facts.get("attendee_type"), llm_facts.get("client_name"), llm_facts.get("attendee_evidence")
    if attendee == "internal" and t == "CLIENT" and name:
        return name, f"'Client business' not checked, but the memo names client {name!r} (evidence: {ev!r})"
    if attendee == "client" and t in {"INTERNAL", "VENDOR"}:
        return None, f"'Client business' checked, but the memo indicates non-client attendees (evidence: {ev!r})"
    return None


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
                if not math.isfinite(amount_usd) or amount_usd <= 0:
                    amount_usd = None
                    raise ValueError("invalid USD amount")
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

    # Never let a structured field silently override a contradicting memo.
    client_conflict = _attendee_conflict(attendee, a_source, llm_facts)
    if ("attendee_type" not in (exp.get("answered_fields") or [])
            and re.search(r"\b(?:internal|in[- ]house)\s+(?:clients?|customers?)\b", f"{memo} {note}", re.I)):
        client_conflict = (None, "The wording could mean coworkers or an external customer")
    if client_conflict:
        conflict_name, conflict_detail = client_conflict
        attendee, client_name, a_detail = "unknown", conflict_name, conflict_detail

    drink_text = re.sub(r"\b(?:soft drinks?|non[- ]alcoholic (?:beers?|wines?|drinks?)|no alcohol)\b",
                        "", f"{memo} {note}", flags=re.I)
    alcohol_kw = bool(ALCOHOL_WORDS.search(drink_text))
    generic_drinks = bool(re.search(r"\bdrinks?\b", drink_text, re.I))
    alcohol_llm = bool(llm_facts and llm_facts["alcohol_mentioned"]
                       and (llm_facts.get("alcohol_evidence") or "").strip()
                       and llm_facts["alcohol_evidence"].lower() in drink_text.lower())
    memo_alcohol = alcohol_kw or alcohol_llm
    memo_alc_src = "memo_keyword" if alcohol_kw else ("memo_llm" if alcohol_llm else None)
    declared = exp.get("alcohol_declared")
    alcohol_conflict = None
    if declared is True:
        alcohol, alc_src = True, given_by(exp, "alcohol_declared")
    elif declared is False:
        alc_src = given_by(exp, "alcohol_declared")
        if memo_alcohol and alc_src == "form":
            alcohol_conflict = f"'Includes alcohol' not checked, but the memo mentions alcohol (via {memo_alc_src})"
            alcohol = None                                    # unknown until the employee answers
        else:
            alcohol = False                                   # attested (after a question, if memo disagreed)
    else:
        alcohol, alc_src = memo_alcohol, memo_alc_src

    c.facts.update({
        "amount": amount, "currency": currency, "amount_usd": amount_usd,
        "date": d.isoformat() if d else None, "weekday": d.strftime("%a") if d else None,
        "is_weekend": bool(d and d.weekday() >= 5), "category": category, "receipt": receipt,
        "attendee": {"status": attendee, "client_name": client_name, "source": a_source, "detail": a_detail},
        "alcohol": {"mentioned": alcohol, "source": alc_src, "memo_mentions": memo_alcohol},
        "sources": {"attendee": a_source, "alcohol": alc_src},
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
            if receipt is None:
                c.gap("receipt", "Please confirm whether a receipt is attached (yes or no).")
    elif receipt is not True:
        c.rule("RECEIPT_REQUIRED", "gap", "USD amount unknown and no receipt")
        c.gap("receipt", "If the corrected USD amount is above $25, attach the receipt.")

    def need_client(reason):
        if attendee == "unknown":
            if client_conflict:
                reason = f"{client_conflict[1]}. {reason}"
            c.gap("attendee", reason, llm_client_name=client_name)
            return True
        return False

    # ---- Global alcohol rule (any category) ---------------------------------
    alcohol_blocked = False
    if generic_drinks and not alcohol_kw and declared is None and attendee != "client":
        alcohol_conflict = "The memo says drinks"
        need_client("If alcohol was included, confirm who attended.")
    if alcohol_conflict:
        if attendee == "client":
            alcohol = False   # alcohol is fine with a confirmed client either way
            c.rule("ATTESTATION_CONFLICT_ALCOHOL", "pass", alcohol_conflict + "; client confirmed, so it does not matter")
            c.rule("ALCOHOL_INTERNAL", "pass", f"client confirmed ({client_name})")
        else:
            c.rule("ATTESTATION_CONFLICT_ALCOHOL", "gap", alcohol_conflict)
            c.gap("alcohol", alcohol_conflict + ". Did this expense include alcohol?")
    elif alcohol:
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
        if d is None or amount_usd is None:
            need_client("If the corrected date is a weekend or the amount exceeds the meal cap, who attended?")
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

    if client_conflict:
        # Ask only when a rule actually needs the client fact (same as any other client question).
        if any(g["id"] == "attendee" for g in c.gaps):
            c.rule("ATTESTATION_CONFLICT_CLIENT", "gap", client_conflict[1])
        else:
            c.rule("ATTESTATION_CONFLICT_CLIENT", "pass", client_conflict[1] + "; does not change the outcome")

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
    if a_source in ("employee_answer", "form") and attendee == "client" and any(
            r["result"] == "pass" and "client confirmed" in r["detail"] for r in c.rules):
        tags.append("approved_on_employee_attestation")
    elif alc_src == "employee_answer" and alcohol is False and memo_alcohol:
        tags.append("approved_on_employee_attestation")    # said "no alcohol" when asked about the memo
    return _finish(exp, c, "approve", amount_usd=amount_usd, category=category, tags=tags)


def _hotel(exp, c, merchant, memo, note, amount_usd, llm_facts, llm_failed):
    city, tier, src, city_src = None, None, None, None
    if (exp.get("city") or "").strip():
        city_in = exp["city"].strip()
        t1 = cities.canonical_tier1(city_in)
        city_src = given_by(exp, "city")
        city, tier, src = (t1 or city_in), (1 if t1 else 2), city_src
    else:
        table_city, tnote = cities.table_match(f"{merchant} {memo} {note}")
        llm_city = llm_facts.get("city") if llm_facts and llm_facts["city_confidence"] == "high" else None
        llm_t1 = cities.canonical_tier1(llm_city) if llm_city else None
        if table_city and llm_city and llm_t1 != table_city:
            c.notes.append(f"city table says {table_city}, LLM says {llm_city} -> ask")
        elif table_city:
            city, tier, src, city_src = table_city, 1, f"city_table ({tnote})", "city_table"
        elif llm_city:
            city, tier, src, city_src = (llm_t1 or llm_city), (1 if llm_t1 else 2), "llm (high)", "memo_llm"
    c.facts["hotel"] = {"city": city, "tier": tier, "source": src}
    c.facts["sources"]["city"] = city_src
    if city is None:
        c.rule("HOTEL_CITY_KNOWN", "gap", "hotel city could not be determined" + (" (LLM unavailable)" if llm_failed else ""))
        c.gap("city", "Hotel limits depend on the city ($350/night in Tier-1 cities, $200/night elsewhere).")
    else:
        c.rule("HOTEL_CITY_KNOWN", "pass", f"{city} -> Tier {tier} via {src}")
    cap = config.HOTEL_CAP_TIER1_USD if tier == 1 else config.HOTEL_CAP_TIER2_USD
    rid = f"HOTEL_CAP_TIER{tier}"
    nights = exp.get("nights")
    invalid_nights = nights not in (None, "") and not re.fullmatch(r"[1-9]\d{0,5}", str(nights))
    nights = int(nights) if nights not in (None, "") and not invalid_nights else None
    nights_src = given_by(exp, "nights") if nights else None
    nights_unknown_why = None
    if not nights and not invalid_nights:
        # Memo / answer text: only ONE unambiguous statement counts. Never guess the denominator.
        text = f"{memo} {note}"
        kw_n, kw_status, kw_quote = normalize.parse_nights(text)
        llm_n = (llm_facts or {}).get("nights")
        if kw_status == "ambiguous":
            nights_unknown_why = f"nights ambiguous in memo ({kw_quote!r})"
        elif kw_status == "found":
            nights, nights_src = kw_n, "memo_keyword"
            if llm_n and llm_n != kw_n:
                nights, nights_src = None, None
                nights_unknown_why = f"memo says {kw_quote!r} but LLM read nights={llm_n}"
        elif llm_n:
            nights_unknown_why = f"LLM nights={llm_n} not verified in memo"
        if nights_unknown_why:
            c.notes.append(nights_unknown_why)
    c.facts["hotel"]["nights"] = nights
    c.facts["sources"]["nights"] = nights_src
    if nights is None and (invalid_nights or amount_usd is None or (city is None and amount_usd > cap)):
        c.gap("nights", "Please confirm the exact positive whole number of nights on this charge.")
    if city is None:
        return
    if amount_usd is None:
        c.rule(rid, "gap", "USD amount unknown")
        return
    if nights is None:
        if amount_usd <= cap:
            c.rule(rid, "pass", f"{_money(amount_usd)} <= {_money(cap)}/night even for 1 night")
            return
        why = f" ({nights_unknown_why})" if nights_unknown_why else ""
        c.rule(rid, "gap", f"{_money(amount_usd)} total, nights unknown{why}")
        c.gap("nights", f"We need the exact number of nights to check the {_money(cap)}/night limit.")
        return
    per_night = round(amount_usd / max(nights, 1), 2)
    if Decimal(str(amount_usd)) <= Decimal(str(cap)) * nights:
        c.rule(rid, "pass", f"{_money(per_night)}/night x {nights} <= {_money(cap)}/night ({city})")
    else:
        c.rule(rid, "fail", f"{_money(amount_usd)} total exceeds {nights} nights x {_money(cap)} ({city}, Tier {tier})")


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
