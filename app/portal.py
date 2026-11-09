"""Employee portal (Gradio). Uses the SAME Pipeline as the batch run.

    python -m app.portal        # http://127.0.0.1:7870 (set PORTAL_PORT to change)

Tabs
  1. Submit expense   - form or JSON upload; live preview while typing (code-only,
                        not posted); Submit runs the full engine, POSTs, stores, logs.
  2. Answer follow-up - open flag questions; answer fields are prefilled; Submit
                        re-runs the WHOLE pipeline and POSTs a new decision version.
  3. All expenses     - store overview, run the pending batch, decision history
                        ("why this decision?"), export the store as JSON.
"""

import json

import gradio as gr

from . import config
from .batch import load_expenses
from . import form
from .form import CURRENCIES, OTHER_CITY, hotel_rule_detail, resolve_city
from .pipeline import Pipeline
from .questions import ALCOHOL_OPTIONS, ATTENDEE_OPTIONS, TIER1_CHOICES

PIPE = Pipeline()
BADGE = {"approve": "🟢 APPROVED", "reject": "🔴 REJECTED", "flag": "🟡 NEEDS INFORMATION"}
HOTEL_INFO = (f"Tier-1 cities ({', '.join(TIER1_CHOICES)}): **${config.HOTEL_CAP_TIER1_USD:,.0f}/night**. "
              f"Other cities: **${config.HOTEL_CAP_TIER2_USD:,.0f}/night**. The limit is per night: "
              "total ÷ nights.")


def _values(args):
    """Positional gradio inputs (in form.FIELDS order) -> dict."""
    return dict(zip(form.FIELDS, args))


def _form_expense(*args):
    return form.form_expense(_values(args))


def _result_md(p):
    md = [f"## {BADGE[p['decision']]}", f"**Expense:** `{p.get('expense_id')}` · version {p.get('decision_version')} · "
          f"POST to Finance: **{p.get('_post_status')}** ({p.get('_post_detail', '')}) · stored ✓", "",
          f"**Why:** {p['reason']}"]
    if p.get("question"):
        md += ["", "### What we need from you", p["question"]["text"],
               "", "_Answer it in the **Answer follow-up** tab._" if p.get("routed_to") == "employee"
               else "_A Finance reviewer will look at this one; no action needed._"]
    return "\n".join(md)


# ---- Tab 1 ---------------------------------------------------------------------

def _check(values):
    """(expense, code-only preview payload, missing required labels)."""
    exp = form.form_expense(values)
    p = PIPE.preview(exp)
    return exp, p, form.missing_required(values, amount_usd=p["facts"].get("amount_usd"))


def preview(*args):
    values = _values(args)
    if not any(values.get(k) for k in ("employee", "date", "amount", "category", "merchant")):
        return "_Start typing to see a live preview._"
    exp, p, missing = _check(values)
    hotel = hotel_rule_detail(p) if exp.get("category") == "Hotel" else None
    extra = f"\n\n**Per-night check:** {hotel}" if hotel else ""
    extra += "".join(f"\n\n⚠️ {w}" for w in form.warnings(values))
    if missing:
        extra += "\n\n**Still to fill before Submit:** " + ", ".join(missing)
    if p["decision"] == "flag":
        msg = ", ".join(p["missing_fields"])
        if "attendee" in p["missing_fields"] or "manual_review" in p["missing_fields"]:
            msg += " (the memo is checked by the AI when you press Submit)"
        return f"**Live preview (not submitted yet):** 🟡 still needs: {msg}\n\n{p['reason']}{extra}"
    return f"**Live preview (not submitted yet):** {BADGE[p['decision']]}\n\n{p['reason']}{extra}"


def submit(*args):
    values = _values(args)
    exp, _, missing = _check(values)
    if missing:   # no avoidable flags from the portal: nothing is run, POSTed or stored
        return "### Please fill: " + ", ".join(missing), ""
    p = PIPE.process(exp, "portal")
    return _result_md(p), PIPE.trace_md(p["expense_id"]) if p.get("expense_id") else ""


def upload(file):
    if file is None:
        return "Upload a .json file with one expense object or a list.", ""
    path = file if isinstance(file, str) else file.name
    try:
        expenses = load_expenses(path)
    except Exception as e:
        return f"Could not read file: {e}", ""
    out, traces = ["| id | decision | POST | reason |", "|---|---|---|---|"], []
    for exp in expenses:
        if not isinstance(exp, dict):
            continue
        p = PIPE.process(exp, "portal")
        out.append(f"| `{p.get('expense_id')}` | {BADGE[p['decision']]} | {p.get('_post_status')} | "
                   f"{p['reason'][:120].replace('|', '/')} |")
        if p.get("expense_id"):
            traces.append(PIPE.trace_md(p["expense_id"], p["decision_version"]))
    return "\n".join(out), "\n\n---\n\n".join(traces)


def toggle_fields(*args):
    """Visibility of every form field, straight from config.FORM_REQUIREMENTS."""
    values = _values(args)
    return [gr.update(visible=form.visible(f, values)) for f in form.FIELDS] + \
        [gr.update(visible=values.get("category") == "Hotel")]              # hotel info box


def toggle_other_city(choice):
    return gr.update(visible=choice in (OTHER_CITY, "Other (type it)"))


# ---- Tab 2 ---------------------------------------------------------------------

ANSWER_FIELDS = ["category", "attendee_type", "client_name", "alcohol_declared", "approval_code", "city", "nights",
                 "amount_usd", "amount_corrected", "date_corrected", "employee", "receipt", "employee_note"]


def open_choices():
    return gr.update(choices=[f["expense_id"] for f in PIPE.store.open_followups()], value=None)


def load_followup(expense_id):
    hidden = [gr.update(visible=False, value=None) for _ in ANSWER_FIELDS]
    if not expense_id:
        return ["_Pick an expense._"] + hidden
    f = next((x for x in PIPE.store.open_followups() if x["expense_id"] == expense_id), None)
    if not f:
        return ["_No open question for this expense._"] + hidden
    exp = PIPE.store.get_expense(expense_id)["expense"]
    q = f["question"]
    by_name = {fld["name"]: fld for fld in q["fields"]}
    updates = []
    for name in ANSWER_FIELDS:
        fld = by_name.get(name)
        if not fld:
            updates.append(gr.update(visible=False, value=None))
            continue
        prefill = fld.get("prefill")
        if name == "receipt":
            prefill = False
        elif prefill is None and name in exp and name not in ("employee_note",):
            prefill = exp.get(name)
        updates.append(gr.update(visible=True, value=prefill))
    summary = (f"**{expense_id}** · {exp.get('employee')} · {exp.get('date')} · {exp.get('category') or 'no category'}"
               f" · {exp.get('merchant')} · {exp.get('amount')} · memo: _{exp.get('memo') or '(blank)'}_\n\n"
               f"### Question\n{q['text']}")
    return [summary] + updates


def submit_answer(expense_id, city_other, *values):
    if not expense_id:
        return "Pick an expense first.", ""
    answers = {k: v for k, v in zip(ANSWER_FIELDS, values) if v not in (None, "", False)}
    if "nights" in answers:
        answers["nights"] = int(answers["nights"])
    if "city" in answers:
        city = resolve_city(answers["city"], city_other)
        if city:
            answers["city"] = city
        else:
            answers.pop("city")
    p = PIPE.answer(expense_id, answers)
    return _result_md(p), PIPE.trace_md(expense_id)


# ---- Tab 3 ---------------------------------------------------------------------

def overview():
    rows = PIPE.store.overview()
    cols = ["expense_id", "source", "status", "version", "decision", "posted", "reason"]
    return [[r[c] for c in cols] for r in rows]


def run_pending():
    for exp in load_expenses(config.DATA_DIR / "pending_expenses.json"):
        PIPE.process(exp, "batch")
    return overview(), gr.update(choices=[r["expense_id"] for r in PIPE.store.overview()])


def history(expense_id):
    return PIPE.trace_md(expense_id) if expense_id else ""


def export_store():
    config.LOG_DIR.mkdir(exist_ok=True)
    path = config.LOG_DIR / "store_export.json"
    path.write_text(json.dumps(PIPE.store.export(), indent=2, default=str), encoding="utf-8")
    return str(path)


def build():
    with gr.Blocks(title="Expense Auto-Approver") as demo:
        gr.Markdown("# Expense Auto-Approver\nSame decision engine as the batch run · every decision is POSTed, "
                    f"stored and logged · rulebook {config.RULEBOOK_VERSION} · model `{PIPE.llm.model}`")
        with gr.Tab("1 · Submit expense"):
            with gr.Row():
                with gr.Column():
                    L = {r["field"]: r["label"] for r in config.FORM_REQUIREMENTS}
                    vis = {f: form.visible(f, {"category": "", "currency": "USD"}) for f in form.FIELDS}
                    c = {}
                    c["employee"] = gr.Textbox(label=L["employee"])
                    c["date"] = gr.Textbox(label=L["date"] + " (YYYY-MM-DD)")
                    c["category"] = gr.Dropdown([""] + config.ALLOWED_CATEGORIES, label=L["category"], value="")
                    c["merchant"] = gr.Textbox(label=L["merchant"] + " (who you paid)")
                    with gr.Row():
                        c["amount"] = gr.Number(label=L["amount"], minimum=0, scale=4)
                        c["currency"] = gr.Dropdown(CURRENCIES, value="USD", label=L["currency"], scale=1,
                                                    min_width=90)
                    c["amount_usd"] = gr.Number(label=L["amount_usd"] + " (optional)", visible=vis["amount_usd"])
                    c["memo"] = gr.Textbox(label=L["memo"], lines=2)
                    c["receipt"] = gr.Checkbox(label=L["receipt"])
                    c["client_business"] = gr.Checkbox(label=L["client_business"], visible=vis["client_business"])
                    c["client_name"] = gr.Textbox(label=L["client_name"], visible=vis["client_name"])
                    c["alcohol_declared"] = gr.Checkbox(label=L["alcohol_declared"], visible=vis["alcohol_declared"])
                    c["city"] = gr.Dropdown(TIER1_CHOICES + [OTHER_CITY], label=L["city"], visible=vis["city"])
                    c["city_other"] = gr.Textbox(label=L["city_other"], visible=vis["city_other"])
                    c["nights"] = gr.Number(label=L["nights"], precision=0, minimum=0, visible=vis["nights"])
                    hotel_info = gr.Markdown(HOTEL_INFO, visible=False)
                    c["approval_code"] = gr.Textbox(label=L["approval_code"], visible=vis["approval_code"])
                    submit_btn = gr.Button("Submit", variant="primary")
                with gr.Column():
                    live = gr.Markdown("_Start typing to see a live preview._")
                    result = gr.Markdown()
                    with gr.Accordion("Why this decision? (full decision log)", open=False):
                        trace = gr.Markdown()
            fields = [c[f] for f in form.FIELDS]
            for f in fields:
                f.change(preview, fields, live, show_progress="hidden")
            for f in ("category", "currency", "client_business", "city"):
                c[f].change(toggle_fields, fields, fields + [hotel_info], show_progress="hidden")
            submit_btn.click(submit, fields, [result, trace])
            gr.Markdown("---\n### Or upload a JSON file (one expense object or a list)")
            up = gr.File(file_types=[".json"], label="Expense file")
            up_btn = gr.Button("Process file")
            up_result = gr.Markdown()
            with gr.Accordion("Decision logs for the file", open=False):
                up_trace = gr.Markdown()
            up_btn.click(upload, up, [up_result, up_trace])

        with gr.Tab("2 · Answer follow-up"):
            with gr.Row():
                pick = gr.Dropdown([], label="Expenses waiting for your answer")
                refresh = gr.Button("Refresh list")
            qbox = gr.Markdown()
            a_fields = [
                gr.Dropdown(config.ALLOWED_CATEGORIES, label="Category", visible=False),
                gr.Radio(ATTENDEE_OPTIONS, label="Who attended?", visible=False),
                gr.Textbox(label="Client company name", visible=False),
                gr.Radio(ALCOHOL_OPTIONS, label="Did it include alcohol?", visible=False),
                gr.Textbox(label="Software approval code", visible=False),
                gr.Dropdown(TIER1_CHOICES + ["Other (type it)"], label="Hotel city", visible=False),
                gr.Number(label="Nights", precision=0, visible=False),
                gr.Number(label="Amount in USD (card statement)", visible=False),
                gr.Textbox(label="Corrected amount", visible=False),
                gr.Textbox(label="Corrected date (YYYY-MM-DD)", visible=False),
                gr.Textbox(label="Your name", visible=False),
                gr.Checkbox(label="I have attached the receipt", visible=False),
                gr.Textbox(label="Anything else we should know? (optional)", visible=False, lines=2),
            ]
            a_city_other = gr.Textbox(label="City name", visible=False)
            a_city = a_fields[ANSWER_FIELDS.index("city")]
            a_city.change(toggle_other_city, a_city, a_city_other)
            ans_btn = gr.Button("Send answer", variant="primary")
            ans_result = gr.Markdown()
            with gr.Accordion("Why this decision? (all versions)", open=False):
                ans_trace = gr.Markdown()
            refresh.click(open_choices, None, pick)
            pick.change(load_followup, pick, [qbox] + a_fields)
            pick.change(lambda _: gr.update(visible=False, value=""), pick, a_city_other)
            ans_btn.click(submit_answer, [pick, a_city_other] + a_fields, [ans_result, ans_trace])

        with gr.Tab("3 · All expenses & logs"):
            with gr.Row():
                run_btn = gr.Button("Run pending batch (data/pending_expenses.json)")
                ref_btn = gr.Button("Refresh")
                exp_btn = gr.Button("Export store as JSON")
            table = gr.Dataframe(headers=["expense_id", "source", "status", "version", "decision", "posted",
                                          "reason"], wrap=True)
            hist_pick = gr.Dropdown([], label="Show decision history for")
            hist = gr.Markdown()
            export_file = gr.File(label="Store export")
            run_btn.click(run_pending, None, [table, hist_pick])
            ref_btn.click(lambda: (overview(), gr.update(choices=[r["expense_id"] for r in PIPE.store.overview()])),
                          None, [table, hist_pick])
            hist_pick.change(history, hist_pick, hist)
            exp_btn.click(export_store, None, export_file)
    return demo


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORTAL_PORT", "7870"))
    build().launch(server_name="127.0.0.1", server_port=port)
