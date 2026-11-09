"""Human- and machine-readable decision logs.

  logs/decision_log.jsonl   one JSON object per decision (payload + trace)
  logs/decision_log.md      the same, rendered for people

render(payload, trace) is also what the Gradio "Why this decision?" panel shows,
so the UI and the log can never disagree.
"""

import json

from . import config

ICON = {"pass": "✓", "fail": "✗", "gap": "?", "n/a": "–", "skipped": "–", "error": "!", "unverified": "!"}


def render(payload, trace=None):
    f = payload.get("facts") or {}
    head = (f"### {payload.get('expense_id')} · {payload.get('employee') or '?'} · "
            f"{f.get('date') or '?'} ({f.get('weekday') or '?'}) · {f.get('category') or 'no category'} · "
            f"{_amount(f)}")
    lines = [head, "",
             f"**DECISION: {payload['decision'].upper()}** (v{payload.get('decision_version', '?')}, "
             f"rulebook {payload.get('rulebook_version')}, source {payload.get('source', '?')}, "
             f"POST {payload.get('_post_status', '?')})", "",
             f"**Reason:** {payload['reason']}", ""]
    if payload.get("tags"):
        lines += [f"**Tags:** {', '.join(payload['tags'])}", ""]
    if payload.get("security_flags"):
        lines += [f"**Security:** {', '.join(payload['security_flags'])}", ""]
    lines += ["| | Rule | Result | Detail |", "|---|---|---|---|"]
    for r in payload.get("rules_fired", []):
        detail = str(r["detail"]).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {ICON.get(r['result'], '·')} | `{r['rule']}` | {r['result']} | {detail} |")
    att = f.get("attendee")
    if att:
        lines += ["", f"**Client check:** {att['status']} (source: {att['source']}) — {att['detail']}"]
    if f.get("alcohol", {}).get("mentioned"):
        lines.append(f"**Alcohol:** mentioned (via {f['alcohol']['source']})")
    if f.get("hotel"):
        h = f["hotel"]
        lines.append(f"**Hotel:** city={h.get('city')} tier={h.get('tier')} nights={h.get('nights')} via {h.get('source')}")
    if f.get("fx"):
        lines.append(f"**FX:** {json.dumps(f['fx'])}")
    if payload.get("llm"):
        lines.append(f"**LLM:** {payload['llm'].get('model')} · prompt {payload['llm'].get('prompt')}")
    if trace and trace.get("llm") and trace["llm"].get("facts"):
        lines.append(f"**LLM reasoning:** {trace['llm']['facts'].get('reasoning')}")
    if trace and trace.get("notes"):
        lines += ["", "**Notes:**"] + [f"- {n}" for n in trace["notes"]]
    if payload.get("question"):
        lines += ["", f"**Question to {payload.get('routed_to')}:**", "", payload["question"]["text"]]
    return "\n".join(lines)


def _amount(f):
    if f.get("amount") is None:
        return "amount ?"
    s = f"{f['amount']:,.2f} {f.get('currency')}"
    if f.get("currency") != "USD" and f.get("amount_usd") is not None:
        s += f" (= ${f['amount_usd']:,.2f})"
    return s


def write(payload, trace):
    config.LOG_DIR.mkdir(exist_ok=True)
    with open(config.LOG_DIR / "decision_log.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"payload": payload, "trace": trace}, default=str) + "\n")
    with open(config.LOG_DIR / "decision_log.md", "a", encoding="utf-8") as fh:
        fh.write(render(payload, trace) + "\n\n---\n\n")
