"""Run from the repository root with python -m simulation.replay."""
import argparse
import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

from app import batch, decision_log, form, questions
from app.fx import StubFX
from app.llm import OpenRouterLLM, StubLLM
from app.pipeline import Pipeline
from app.publisher import NullPublisher
from app.store import Store

ROOT = Path(__file__).resolve().parent
LEVELS = ("easy", "medium", "hard")


def encode(value):
    return json.dumps(value, ensure_ascii=False)


def check_form_reply(fields, submitted):
    raw = dict(submitted)
    if isinstance(raw.get("nights"), int):
        raw["check_in"] = "2026-06-01"
        raw["check_out"] = (date(2026, 6, 1) + timedelta(days=raw.pop("nights"))).isoformat()
    if "receipt" in raw:
        raw["receipt"] = "yes" if raw["receipt"] else "no"
    if "alcohol_declared" in raw:
        raw["alcohol_declared"] = questions.ALCOHOL_OPTIONS[0 if raw["alcohol_declared"] else 1]
    if "city" in raw and raw["city"] not in questions.TIER1_CHOICES:
        raw["city_other"], raw["city"] = raw["city"], "Other (type it)"
    answers, problems = form.clean_answers(fields, raw)
    return {"controls": raw, "normalized_reply": answers, "validation_messages": problems}


def process_case(pipeline, expense, key, live=False):
    # A fixture supplies extraction facts, never a disposition. Match the constant
    # record wrapper so the same fixture applies when employee answers are merged.
    if not live:
        pipeline.llm = StubLLM({"Expense record": key.get("facts", {})}, fail=key.get("llm_down", False))
    pipeline.fx = StubFX(fail=key.get("fx_down", False))
    actual, = batch.run(pipeline, [expense])
    steps, issues = [], []
    reply = key.get("reply", {})
    used = set()
    submitted = None
    while True:
        ver = actual["decision_version"]
        trace = pipeline.store.trace(expense["id"], ver)
        question = actual.get("question") or {}
        offered = {f["name"] for f in question.get("fields", [])}
        steps.append({"submitted_answer": submitted, "payload": actual, "trace": trace})
        if ver == 1:
            if actual["decision"] != key["expected"]:
                issues.append(f"Expected {key['expected']}, got {actual['decision']}.")
            missing = set(key.get("fields", [])) - offered
            if missing:
                issues.append("First question omitted " + ", ".join(sorted(missing)) + ".")
            if key["expected"] == "flag" and actual["routed_to"] != key.get("route", "employee"):
                issues.append("Wrong review owner.")
        if actual["decision"] != "flag" or actual["routed_to"] != "employee" or not reply:
            break
        submitted = {k: v for k, v in reply.items() if k in offered and k not in used}
        if not submitted:
            issues.append("No remaining scripted answer fits the displayed question.")
            break
        if not live:
            form_check = check_form_reply(question["fields"], submitted)
            steps[-1]["form_check"] = form_check
            if form_check["validation_messages"] and key.get("final_route") != "finance":
                issues.append("Form blocked a complete reply: " + ", ".join(form_check["validation_messages"]))
        used.update(submitted)
        actual = pipeline.answer(expense["id"], submitted)
    if "final" in key and actual["decision"] != key["final"]:
        issues.append(f"Expected final {key['final']}, got {actual['decision']}.")
    if "final_route" in key and actual.get("routed_to") != key["final_route"]:
        issues.append("Wrong owner after reply.")
    if len(steps) > 2:
        issues.append(f"Required {len(steps)-1} employee replies.")
    return {"id": expense["id"], "input": expense, "answer_key": key, "steps": steps, "issues": issues}


def render(row):
    k = row["answer_key"]
    lines = [f"## {row['id']} · {k['title']}", "", "Input", "", "```json", encode(row["input"]), "```", "",
             f"**Expected {k['expected'].upper()}** — {k['why']}", "",
             "**QA** " + (" ".join(row["issues"]) or "Matched the scripted checks."), ""]
    if k.get("reply"):
        lines += ["Complete employee answer available in this scenario", "", "```json", encode(k["reply"]), "```",
                  "", f"Expected after a complete reply: **{k['final']}**.", ""]
    for step in row["steps"]:
        if step["submitted_answer"] is not None:
            lines += ["**Employee actually returned** " + encode(step["submitted_answer"]), ""]
        p = step["payload"]
        lines += [decision_log.render(p, step["trace"]), ""]
        if p["question"] and p["question"]["fields"]:
            lines += ["**Fields offered** " + ", ".join(f["name"] for f in p["question"]["fields"]), ""]
        if "form_check" in step:
            problems = step["form_check"]["validation_messages"]
            lines += ["**Portal reply validation** " + ("Blocked before sending: " + ", ".join(problems)
                      if problems else "Accepted the corresponding form inputs."), ""]
    return "\n".join(line.rstrip() for line in "\n".join(lines).splitlines()) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live-memos", action="store_true", help="Replay selected language cases with the configured real model; keep FX and publishing offline.")
    args = parser.parse_args()
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    if args.live_memos:
        chosen = {"H01", "H11", "H13", "H16", "H17", "H20", "H22", "H23", "H24", "H25", "H26", "H35"}
        chosen.update(f"H{n}" for n in range(57, 65))
        inputs = batch.load_expenses(ROOT / "hard.json")
        keys = json.loads((ROOT / "hard-key.json").read_text(encoding="utf-8"))
        def run_live(pair):
            e, k = pair
            pipe = Pipeline(llm=OpenRouterLLM(), fx=StubFX(), publisher=NullPublisher(), store=Store(), write_logs=False)
            try:
                return process_case(pipe, e, k, live=True)
            finally:
                pipe.store.db.close()
        with ThreadPoolExecutor(max_workers=3) as workers:
            rows = list(workers.map(run_live, [(e,k) for e,k in zip(inputs, keys) if e["id"] in chosen]))
        (out / "live-memos.jsonl").write_text("".join(encode(r)+"\n" for r in rows), encoding="utf-8")
        (out / "live-memos.md").write_text("# Live model language checks\n\nConfigured model with offline FX and recording publisher. Any fixture facts in the answer key were ignored.\n\n" + "\n---\n\n".join(map(render, rows)), encoding="utf-8")
        print("Live differences:", [r["id"] for r in rows if r["issues"]])
        return int(any(r["issues"] for r in rows))
    all_rows = []
    for level in LEVELS:
        inputs = batch.load_expenses(ROOT / f"{level}.json")
        keys = json.loads((ROOT / f"{level}-key.json").read_text(encoding="utf-8"))
        if [e["id"] for e in inputs] != [k["id"] for k in keys] or len({k["id"] for k in keys}) != len(keys):
            raise ValueError(f"Inputs and key disagree in {level}")
        pipe = Pipeline(llm=StubLLM(), fx=StubFX(), store=Store(), publisher=NullPublisher(), write_logs=False)
        try:
            rows = [process_case(pipe, e, k) for e, k in zip(inputs, keys)]
        finally:
            pipe.store.db.close()
        all_rows.extend(rows)
        counts = Counter(r["steps"][0]["payload"]["decision"] for r in rows)
        issues = [r["id"] for r in rows if r["issues"]]
        summary = f"{len(rows)} entries, {dict(counts)}, {len(issues)} QA differences"
        print(level, summary, ", ".join(issues))
        intro = f"# {level.title()} — expense QA\n\n{summary}.\n\n"
        intro += "Synthetic expenses. Real batch and follow-up logic, offline model and FX fixtures, in-memory storage and a recording publisher. Each entry includes the actual question and rule trace.\n\n"
        (out / f"{level}.md").write_text(intro + "\n---\n\n".join(map(render, rows)), encoding="utf-8")
    (out / "traces.jsonl").write_text("".join(encode(r)+"\n" for r in all_rows), encoding="utf-8")
    drafts = ["# Individual employee follow-ups", "",
              "One draft per initially employee-routed claim. The body below is the actual question in the recorded decision. No email was sent.", ""]
    for row in all_rows:
        p = row["steps"][0]["payload"]
        if p.get("routed_to") == "employee":
            drafts.extend([f"## {row['id']} · {row['answer_key']['title']}", "",
                           f"Subject: Information needed for expense {row['id']}", "", p["question"]["text"], ""])
    (out / "employee-questions.md").write_text("\n".join(drafts), encoding="utf-8")
    return int(any(r["issues"] for r in all_rows))


if __name__ == "__main__":
    raise SystemExit(main())
