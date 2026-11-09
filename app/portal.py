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
from .pipeline import Pipeline
from .questions import ATTENDEE_OPTIONS, TIER1_CHOICES

PIPE = Pipeline()
NOT_SPECIFIED = "Not specified"
BADGE = {"approve": "🟢 APPROVED", "reject": "🔴 REJECTED", "flag": "🟡 NEEDS INFORMATION"}


def _form_expense(employee, date, category, merchant, amount, memo, receipt, approval_code,
                  attendee, client_name, city, nights):
    exp = {"employee": employee, "date": date, "category": category, "merchant": merchant,
           "amount": amount, "memo": memo, "receipt": bool(receipt), "approval_code": approval_code or None}
    if attendee and attendee != NOT_SPECIFIED:
        exp["attendee_type"] = {ATTENDEE_OPTIONS[0]: "INTERNAL", ATTENDEE_OPTIONS[1]: "CLIENT",
                                ATTENDEE_OPTIONS[2]: "VENDOR"}[attendee]
        exp["client_name"] = client_name
    if city:
        exp["city"] = city
    if nights:
        exp["nights"] = int(nights)
    return exp


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

def preview(*fields):
    exp = _form_expense(*fields)
    if not any([exp["employee"], exp["date"], exp["amount"], exp["category"], exp["merchant"]]):
        return "_Start typing to see a live preview._"
    p = PIPE.preview(exp)
    if p["decision"] == "flag":
        need = [g for g in p["missing_fields"]]
        msg = ", ".join(need)
        if "attendee" in need or "manual_review" in need:
            msg += " (the memo is checked by the AI when you press Submit)"
        return f"**Live preview (not submitted yet):** 🟡 still needs: {msg}\n\n{p['reason']}"
    return f"**Live preview (not submitted yet):** {BADGE[p['decision']]}\n\n{p['reason']}"


def submit(*fields):
    p = PIPE.process(_form_expense(*fields), "portal")
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


def toggle_category(category):
    meal_like = category in config.MEAL_CATEGORIES or category == "Entertainment"
    return gr.update(visible=meal_like), gr.update(visible=meal_like), \
        gr.update(visible=category == "Hotel"), gr.update(visible=category == "Hotel"), \
        gr.update(visible=category == "Software")


# ---- Tab 2 ---------------------------------------------------------------------

ANSWER_FIELDS = ["category", "attendee_type", "client_name", "approval_code", "city", "nights",
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


def submit_answer(expense_id, *values):
    if not expense_id:
        return "Pick an expense first.", ""
    answers = {k: v for k, v in zip(ANSWER_FIELDS, values) if v not in (None, "", False)}
    if "nights" in answers:
        answers["nights"] = int(answers["nights"])
    if answers.get("city") == "Other (type it)":
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
                    employee = gr.Textbox(label="Employee")
                    date = gr.Textbox(label="Date (YYYY-MM-DD)")
                    category = gr.Dropdown([""] + config.ALLOWED_CATEGORIES, label="Category", value="")
                    merchant = gr.Textbox(label="Merchant (who you paid)")
                    amount = gr.Textbox(label="Amount (USD unless you type €, £, ₹ …)")
                    memo = gr.Textbox(label="Memo (purpose; name any client attendees)", lines=2)
                    receipt = gr.Checkbox(label="Receipt attached")
                    approval_code = gr.Textbox(label="Software approval code", visible=False)
                    attendee = gr.Radio([NOT_SPECIFIED] + ATTENDEE_OPTIONS, value=NOT_SPECIFIED,
                                        label="Who attended?", visible=False)
                    client_name = gr.Textbox(label="Client company", visible=False)
                    city = gr.Dropdown(TIER1_CHOICES, allow_custom_value=True, label="Hotel city", visible=False)
                    nights = gr.Number(label="Nights", precision=0, visible=False)
                    submit_btn = gr.Button("Submit", variant="primary")
                with gr.Column():
                    live = gr.Markdown("_Start typing to see a live preview._")
                    result = gr.Markdown()
                    with gr.Accordion("Why this decision? (full decision log)", open=False):
                        trace = gr.Markdown()
            fields = [employee, date, category, merchant, amount, memo, receipt, approval_code,
                      attendee, client_name, city, nights]
            for f in fields:
                f.change(preview, fields, live, show_progress="hidden")
            category.change(toggle_category, category, [attendee, client_name, city, nights, approval_code])
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
                gr.Textbox(label="Software approval code", visible=False),
                gr.Dropdown(TIER1_CHOICES, allow_custom_value=True, label="Hotel city", visible=False),
                gr.Number(label="Nights", precision=0, visible=False),
                gr.Number(label="Amount in USD (card statement)", visible=False),
                gr.Textbox(label="Corrected amount", visible=False),
                gr.Textbox(label="Corrected date (YYYY-MM-DD)", visible=False),
                gr.Textbox(label="Your name", visible=False),
                gr.Checkbox(label="I have attached the receipt", visible=False),
                gr.Textbox(label="Anything else we should know? (optional)", visible=False, lines=2),
            ]
            ans_btn = gr.Button("Send answer", variant="primary")
            ans_result = gr.Markdown()
            with gr.Accordion("Why this decision? (all versions)", open=False):
                ans_trace = gr.Markdown()
            refresh.click(open_choices, None, pick)
            pick.change(load_followup, pick, [qbox] + a_fields)
            ans_btn.click(submit_answer, [pick] + a_fields, [ans_result, ans_trace])

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
