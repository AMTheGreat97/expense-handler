"""Employee portal (Gradio). Uses the SAME Pipeline as the batch run.

    python -m app.portal        # http://127.0.0.1:7870 (set PORTAL_PORT to change)

Tabs
  1. Submit expense   - form or JSON upload; live preview while typing (code-only,
                        not posted); Submit runs the full engine, POSTs, stores, logs.
  2. Answer follow-up - open flag questions; answer fields are prefilled; Send
                        re-runs the WHOLE pipeline and POSTs a new decision version.
  3. All expenses     - store overview, run the pending batch, decision history
                        ("why this decision?"), export the store as JSON.

The form only collects facts (config.FORM_REQUIREMENTS drives which fields show
and which are required). Every decision comes from engine.decide().
"""

import json

import gradio as gr

from . import config, form
from .batch import load_expenses
from .form import CURRENCIES, OTHER_CITY, hotel_rule_detail
from .pipeline import Pipeline
from .questions import ALCOHOL_OPTIONS, ATTENDEE_OPTIONS, TIER1_CHOICES

PIPE = Pipeline()
BADGE = {"approve": "🟢 APPROVED", "reject": "🔴 REJECTED", "flag": "🟡 NEEDS INFORMATION"}
HOTEL_INFO = (f"Tier-1 cities ({', '.join(TIER1_CHOICES)}): **${config.HOTEL_CAP_TIER1_USD:,.0f}/night**. "
              f"Other cities: **${config.HOTEL_CAP_TIER2_USD:,.0f}/night**. Nights = check-out minus check-in; "
              "the limit is checked per night (total ÷ nights).")
POST_TEXT = {"sent": "sent to Finance", "failed": "⚠️ NOT sent to Finance (endpoint unreachable; stored here)",
             "not_sent": "not sent (dry run)"}
EMPTY_FORM = {"employee": "", "date": None, "category": "", "merchant": "", "amount": None, "currency": "USD",
              "amount_usd": None, "memo": "", "receipt": False, "client_business": False, "client_name": "",
              "alcohol_declared": False, "city": None, "city_other": "", "check_in": None, "check_out": None,
              "approval_code": ""}


def _values(args):
    """Positional gradio inputs (in form.FIELDS order) -> dict."""
    return dict(zip(form.FIELDS, args))


def _problems_md(title, items):
    return f"### ⚠️ {title}\n" + "\n".join(f"- {i}" for i in items)


def _result_md(p):
    """Employee-facing decision card. The full rule table is in the log accordion below it."""
    md = [f"## {BADGE[p['decision']]}",
          f"Expense `{p.get('expense_id')}` · decision version {p.get('decision_version')} · "
          f"{POST_TEXT.get(p.get('_post_status'), p.get('_post_status'))} · stored", ""]
    fails = [r for r in p.get("rules_fired", []) if r["result"] == "fail"]
    if p["decision"] == "reject" and fails and not p.get("security_flags"):
        md += ["**Rules this expense breaks:**"] + [f"- `{r['rule']}`: {r['detail']}" for r in fails]
    else:
        md.append(f"**Why:** {p['reason']}")
    if "approved_on_employee_attestation" in (p.get("tags") or []):
        md += ["", "_Approved on what you stated. Finance may audit it against the receipt._"]
    if p.get("question"):
        md += ["", "### What we need from you" if p.get("routed_to") == "employee" else "### Next step",
               p["question"]["text"], ""]
        md.append("➡️ Answer it in the **2 · Answer follow-up** tab; this expense is already selected there."
                  if p.get("routed_to") == "employee" else "_A Finance reviewer will look at this one; no action needed._")
    if p.get("_post_status") == "failed":
        md += ["", f"_Finance endpoint error: {p.get('_post_detail')}_"]
    return "\n".join(md)


def _employee_choices():
    return [f["expense_id"] for f in PIPE.store.open_followups()
            if PIPE.store.latest_decision(f["expense_id"])["payload"]["routed_to"] == "employee"]


# ---- Tab 1 ---------------------------------------------------------------------

def _check(values):
    """(expense, code-only preview payload, missing required labels)."""
    exp = form.form_expense(values)
    p = PIPE.preview(exp)
    return exp, p, form.missing_required(values, amount_usd=p["facts"].get("amount_usd"),
                                         engine_gaps=p.get("missing_fields") or ())


def preview(*args):
    values = _values(args)
    if not any(values.get(k) for k in ("employee", "date", "amount", "category", "merchant", "memo")):
        return "_Start filling the form to see a live preview._"
    try:
        exp, p, missing = _check(values)
    except Exception as e:  # the preview must never break the form
        return f"_Live preview unavailable ({type(e).__name__}). You can still submit._"
    parts = ["**Live preview** · code-only checks, not submitted · the AI reads the memo when you press Submit"]
    if missing:
        parts.append("**Still to fill before Submit:**\n" + "\n".join(f"- {m}" for m in missing))
    if exp.get("category") == "Hotel" and exp.get("nights"):
        parts.append(f"**Stay:** {exp['nights']} night{'s' if exp['nights'] != 1 else ''} "
                     f"({exp['check_in']} → {exp['check_out']})")
    hotel = hotel_rule_detail(p) if exp.get("category") == "Hotel" else None
    if hotel:
        parts.append(f"**Per-night check:** {hotel}")
    parts += [f"⚠️ {w}" for w in form.warnings(values)]
    if not missing:
        fails = [f"- `{r['rule']}`: {r['detail']}" for r in p["rules_fired"] if r["result"] == "fail"]
        if p["missing_fields"] == ["manual_review"]:   # the preview never calls the AI, so this gap is always there
            parts.append("Expected outcome so far: " + (BADGE["reject"] + "".join("\n" + f for f in fails)
                         if fails else "🟢 no rule broken") + "\n\n_The AI memo read at Submit can still change it._")
        elif p["decision"] == "flag":
            parts.append("🟡 Would still need: " + ", ".join(form.gap_labels(p["missing_fields"])))
        else:
            fails = [f"- `{r['rule']}`: {r['detail']}" for r in p["rules_fired"] if r["result"] == "fail"]
            parts.append(f"Expected outcome so far: {BADGE[p['decision']]}" + "".join("\n" + f for f in fails))
    return "\n\n".join(parts)


def submit(last_sig, *args):
    """-> result, trace, follow-up picker, last submitted signature."""
    values = _values(args)
    sig = json.dumps(values, sort_keys=True, default=str)
    if sig == (last_sig or {}).get("sig"):
        return (f"### ⚠️ Already submitted\nThis exact form was already submitted as `{last_sig['id']}`. "
                "Change something, or press **New expense** to start over.", gr.update(), gr.update(), last_sig)
    try:
        exp, _, missing = _check(values)
        if missing:   # no avoidable flags from the portal: nothing is run, POSTed or stored
            return _problems_md("Please fix before submitting", missing), "", gr.update(), last_sig
        p = PIPE.process(exp, "portal")
    except Exception as e:
        return f"### ⚠️ Something went wrong\n{type(e).__name__}: {e}\n\nNothing was submitted.", "", gr.update(), last_sig
    pick = gr.update(choices=_employee_choices(),
                     value=p["expense_id"] if p.get("routed_to") == "employee" else None)
    trace = PIPE.trace_md(p["expense_id"]) if p.get("expense_id") else ""
    return _result_md(p), trace, pick, {"sig": sig, "id": p.get("expense_id")}


def new_expense():
    """Reset the form, the result panes and the duplicate guard."""
    return ([gr.update(value=EMPTY_FORM[f]) for f in form.FIELDS] +
            ["_Start filling the form to see a live preview._", "", "", None])


def upload(file, progress=gr.Progress()):
    if file is None:
        return "Choose a .json file with one expense object or a list of them.", ""
    path = file if isinstance(file, str) else file.name
    try:
        expenses = load_expenses(path)
    except Exception as e:
        return f"### ⚠️ Could not read the file\n{type(e).__name__}: {e}", ""
    out, traces = ["| # | id | decision | Finance | reason |", "|---|---|---|---|---|"], []
    for i, exp in enumerate(progress.tqdm(expenses, desc="Deciding"), 1):
        if not isinstance(exp, dict):
            out.append(f"| {i} | | ⚪ skipped | | not an expense object |")
            continue
        try:
            p = PIPE.process(exp, "portal")
        except Exception as e:
            out.append(f"| {i} | `{exp.get('id')}` | ⚠️ error | | {type(e).__name__}: {str(e)[:100]} |")
            continue
        out.append(f"| {i} | `{p.get('expense_id')}` | {BADGE[p['decision']]} | {p.get('_post_status')} | "
                   f"{p['reason'][:160].replace('|', '/')} |")
        if p.get("expense_id"):
            traces.append(PIPE.trace_md(p["expense_id"], p["decision_version"]))
    return "\n".join(out), "\n\n---\n\n".join(traces)


def toggle_fields(*args):
    """Visibility of every form field, straight from config.FORM_REQUIREMENTS."""
    values = _values(args)
    # Always-shown fields get a no-op update: re-sending visible=True resets an empty Number to 0.
    return [gr.update(visible=form.visible(f, values)) if form.is_conditional(f) else gr.update()
            for f in form.FIELDS] + \
        [gr.update(visible=values.get("category") == "Hotel")]              # hotel info box


def toggle_other_city(choice):
    return gr.update(visible=choice in (OTHER_CITY, "Other (type it)"))


# ---- Tab 2 ---------------------------------------------------------------------
# Answer inputs, in the order of a_fields below. A question's "nights" field shows check_in + check_out.
ANSWER_FIELDS = ["category", "attendee_type", "client_name", "alcohol_declared", "approval_code", "city",
                 "check_in", "check_out", "amount_usd", "amount_corrected", "date_corrected", "employee",
                 "receipt", "employee_note"]


def open_choices(current=None):
    choices = _employee_choices()
    return gr.update(choices=choices, value=current if current in choices else None)


def _amount_text(raw):
    return f"${raw:,.2f}" if isinstance(raw, (int, float)) and not isinstance(raw, bool) else str(raw)


def _open_question(expense_id):
    f = next((x for x in PIPE.store.open_followups() if x["expense_id"] == expense_id), None)
    return f["question"] if f else None


def load_followup(expense_id):
    hidden = [gr.update(visible=False, value=None) for _ in ANSWER_FIELDS]
    if not expense_id:
        return ["_Pick an expense above._"] + hidden + [gr.update(visible=False)]
    q = _open_question(expense_id)
    if not q:
        return ["_This expense has no open question any more._"] + hidden + [gr.update(visible=False)]
    exp = PIPE.store.get_expense(expense_id)["expense"]
    shown = {}
    for fld in q["fields"]:
        for name in form.answer_inputs(fld["name"]):
            shown[name] = fld
    updates = []
    for name in ANSWER_FIELDS:
        fld = shown.get(name)
        if not fld:
            updates.append(gr.update(visible=False, value=None))
            continue
        prefill = fld.get("prefill") if fld["name"] == name else None
        if name == "receipt":
            prefill = None
        elif prefill is None and name in exp and name != "employee_note":
            prefill = exp.get(name)
        upd = {"visible": True, "value": prefill}
        if fld["name"] == name and fld.get("label"):
            upd["label"] = fld["label"] + (" (optional)" if fld.get("optional") and "optional" not in fld["label"]
                                           else "")
        updates.append(gr.update(**upd))
    summary = (f"**{expense_id}** · {exp.get('employee')} · {exp.get('date')} · {exp.get('category') or 'no category'}"
               f" · {exp.get('merchant')} · {_amount_text(exp.get('amount'))} · memo: _{exp.get('memo') or '(blank)'}_\n\n"
               f"### Question\n{q['text']}")
    return [summary] + updates + [gr.update(visible=True)]


def submit_answer(expense_id, city_other, *values):
    """-> result, trace, picker."""
    if not expense_id:
        return "Pick an expense first.", "", gr.update()
    q = _open_question(expense_id)
    if not q:
        return "This expense has no open question any more.", PIPE.trace_md(expense_id), open_choices()
    raw = dict(zip(ANSWER_FIELDS, values)) | {"city_other": city_other}
    answers, problems = form.clean_answers(q["fields"], raw)
    if problems:
        return _problems_md("Please answer before sending", problems), "", gr.update()
    try:
        p = PIPE.answer(expense_id, answers)
    except (KeyError, ValueError) as e:
        return f"### ⚠️ Could not send the answer\n{e}", PIPE.trace_md(expense_id), open_choices()
    return _result_md(p), PIPE.trace_md(expense_id), open_choices()


# ---- Tab 3 ---------------------------------------------------------------------

def overview():
    rows = PIPE.store.overview()
    cols = ["expense_id", "source", "status", "version", "decision", "posted", "reason"]
    return [[r[c] for c in cols] for r in rows]


def refresh_all(current=None):
    ids = [r["expense_id"] for r in PIPE.store.overview()]
    return overview(), gr.update(choices=ids, value=current if current in ids else None)


def run_pending(current=None, progress=gr.Progress()):
    expenses = load_expenses(config.DATA_DIR / "pending_expenses.json")
    for exp in progress.tqdm(expenses, desc="Deciding pending expenses"):
        PIPE.process(exp, "batch")
    return refresh_all(current)


def history(expense_id):
    return PIPE.trace_md(expense_id) if expense_id else ""


def export_store():
    config.LOG_DIR.mkdir(exist_ok=True)
    path = config.LOG_DIR / "store_export.json"
    path.write_text(json.dumps(PIPE.store.export(), indent=2, default=str), encoding="utf-8")
    return str(path)


def _date(label, **kw):
    return gr.DateTime(label=label, include_time=False, type="string", **kw)


def build():
    with gr.Blocks(title="Expense Auto-Approver") as demo:
        gr.Markdown("# Expense Auto-Approver\nSame decision engine as the batch run · every decision is POSTed, "
                    f"stored and logged · rulebook {config.RULEBOOK_VERSION} · model `{PIPE.llm.model}`")
        with gr.Tabs():
            with gr.Tab("1 · Submit expense"):
                with gr.Row():
                    with gr.Column():
                        L = {r["field"]: r["label"] for r in config.FORM_REQUIREMENTS}
                        vis = {f: form.visible(f, {"category": "", "currency": "USD"}) for f in form.FIELDS}
                        c = {}
                        c["employee"] = gr.Textbox(label=L["employee"])
                        c["date"] = _date(L["date"] + " (the day you paid)")
                        c["category"] = gr.Dropdown([""] + config.ALLOWED_CATEGORIES, label=L["category"], value="")
                        c["merchant"] = gr.Textbox(label=L["merchant"] + " (who you paid)")
                        with gr.Row():
                            c["amount"] = gr.Number(label=L["amount"], value=None, placeholder="e.g. 42.50", step=0.01, scale=4)
                            c["currency"] = gr.Dropdown(CURRENCIES, value="USD", label=L["currency"], scale=1,
                                                        min_width=90)
                        c["amount_usd"] = gr.Number(label=L["amount_usd"] + " (optional; we convert at the "
                                                    "historical rate otherwise)", value=None, placeholder="e.g. 71.30",
                                                    visible=vis["amount_usd"])
                        c["memo"] = gr.Textbox(label=L["memo"], lines=2,
                                               placeholder="What was it for? Name any client company.")
                        c["receipt"] = gr.Checkbox(label=L["receipt"])
                        c["client_business"] = gr.Checkbox(label=L["client_business"], visible=vis["client_business"])
                        c["client_name"] = gr.Textbox(label=L["client_name"], visible=vis["client_name"])
                        c["alcohol_declared"] = gr.Checkbox(label=L["alcohol_declared"],
                                                            visible=vis["alcohol_declared"])
                        c["city"] = gr.Dropdown(TIER1_CHOICES + [OTHER_CITY], value=None, label=L["city"],
                                                visible=vis["city"])
                        c["city_other"] = gr.Textbox(label=L["city_other"], visible=vis["city_other"])
                        with gr.Row():
                            c["check_in"] = _date(L["check_in"], visible=vis["check_in"])
                            c["check_out"] = _date(L["check_out"], visible=vis["check_out"])
                        hotel_info = gr.Markdown(HOTEL_INFO, visible=False)
                        c["approval_code"] = gr.Textbox(label=L["approval_code"], visible=vis["approval_code"])
                        with gr.Row():
                            submit_btn = gr.Button("Submit", variant="primary", scale=3)
                            new_btn = gr.Button("New expense", scale=1)
                    with gr.Column():
                        live = gr.Markdown("_Start filling the form to see a live preview._")
                        result = gr.Markdown()
                        with gr.Accordion("Why this decision? (full decision log)", open=False):
                            trace = gr.Markdown()
                last_sig = gr.State(None)
                fields = [c[f] for f in form.FIELDS]
                gr.Markdown("---\n### Or upload a JSON file (one expense object or a list)")
                up = gr.File(file_types=[".json"], label="Expense file")
                up_btn = gr.Button("Process file")
                up_result = gr.Markdown()
                with gr.Accordion("Decision logs for the file", open=False):
                    up_trace = gr.Markdown()

            with gr.Tab("2 · Answer follow-up") as tab2:
                with gr.Row():
                    pick = gr.Dropdown([], value=None, label="Expenses waiting for your answer", scale=4)
                    refresh = gr.Button("Refresh list", scale=1)
                qbox = gr.Markdown("_Pick an expense above._")
                a_fields = [
                    gr.Dropdown(config.ALLOWED_CATEGORIES, label="Category", visible=False),
                    gr.Radio(ATTENDEE_OPTIONS, label="Who attended?", visible=False),
                    gr.Textbox(label="Client company name", visible=False),
                    gr.Radio(ALCOHOL_OPTIONS, label="Did it include alcohol?", visible=False),
                    gr.Textbox(label="Software approval code", visible=False),
                    gr.Dropdown(TIER1_CHOICES + ["Other (type it)"], label="Hotel city", visible=False),
                    _date("Check-in date", visible=False),
                    _date("Check-out date", visible=False),
                    gr.Number(label="Amount in USD (card statement)", placeholder="e.g. 71.30", visible=False),
                    gr.Textbox(label="Corrected amount (e.g. 42.50 or 42.50 EUR)", visible=False),
                    _date("Corrected date", visible=False),
                    gr.Textbox(label="Your name", visible=False),
                    gr.Radio(["yes", "no"], value=None, label="Receipt attached?", visible=False),
                    gr.Textbox(label="Anything else we should know? (optional)", visible=False, lines=2),
                ]
                a_city_other = gr.Textbox(label="City name", visible=False)
                a_city = a_fields[ANSWER_FIELDS.index("city")]
                ans_btn = gr.Button("Send answer", variant="primary", visible=False)
                ans_result = gr.Markdown()
                with gr.Accordion("Why this decision? (all versions)", open=False):
                    ans_trace = gr.Markdown()

            with gr.Tab("3 · All expenses & logs") as tab3:
                with gr.Row():
                    run_btn = gr.Button("Run pending batch (data/pending_expenses.json)")
                    ref_btn = gr.Button("Refresh")
                    exp_btn = gr.Button("Export store as JSON")
                table = gr.Dataframe(headers=["expense_id", "source", "status", "version", "decision", "posted",
                                              "reason"], wrap=True, interactive=False)
                hist_pick = gr.Dropdown([], value=None, label="Show decision history for")
                hist = gr.Markdown()
                export_file = gr.File(label="Store export")

        # ---- events (wired after every component exists) ----
        for f in fields:
            f.change(preview, fields, live, show_progress="hidden")
        for f in ("category", "currency", "client_business", "city"):
            c[f].change(toggle_fields, fields, fields + [hotel_info], show_progress="hidden")
        submit_btn.click(submit, [last_sig] + fields, [result, trace, pick, last_sig])
        new_btn.click(new_expense, None, fields + [live, result, trace, last_sig])
        up_btn.click(upload, up, [up_result, up_trace])

        tab2.select(open_choices, pick, pick)
        refresh.click(open_choices, pick, pick)
        pick.change(load_followup, pick, [qbox] + a_fields + [ans_btn])
        pick.change(lambda v: (gr.update(visible=False, value=""), "" if v else gr.update()), pick,
                    [a_city_other, ans_result])
        a_city.change(toggle_other_city, a_city, a_city_other)
        ans_btn.click(submit_answer, [pick, a_city_other] + a_fields, [ans_result, ans_trace, pick])

        tab3.select(refresh_all, hist_pick, [table, hist_pick])
        ref_btn.click(refresh_all, hist_pick, [table, hist_pick])
        run_btn.click(run_pending, hist_pick, [table, hist_pick])
        hist_pick.change(history, hist_pick, hist)
        exp_btn.click(export_store, None, export_file)
    return demo


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORTAL_PORT", "7870"))
    build().launch(server_name="127.0.0.1", server_port=port)
