"""Run from the repository root with python -m simulation.replay."""
import json
from collections import Counter
from pathlib import Path

from app import batch, decision_log
from app.fx import StubFX
from app.llm import StubLLM
from app.pipeline import Pipeline
from app.publisher import NullPublisher
from app.store import Store

ROOT = Path(__file__).resolve().parent
LEVELS = ("easy", "medium", "hard")


def encode(value):
    return json.dumps(value, ensure_ascii=False)


def process_case(pipeline, expense, key):
    # A fixture supplies extraction facts, never a disposition. Match the constant
    # record wrapper so the same fixture applies when employee answers are merged.
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
        used.update(submitted)
        actual = pipeline.answer(expense["id"], submitted)
    if "final" in key and actual["decision"] != key["final"]:
        issues.append(f"Expected final {key['final']}, got {actual['decision']}.")
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
        if p["question"]:
            lines += ["**Fields offered** " + ", ".join(f["name"] for f in p["question"]["fields"]), ""]
    return "\n".join(lines)


def main():
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    all_rows = []
    for level in LEVELS:
        inputs = batch.load_expenses(ROOT / f"{level}.json")
        keys = json.loads((ROOT / f"{level}-key.json").read_text(encoding="utf-8"))
        if [e["id"] for e in inputs] != [k["id"] for k in keys] or len({k["id"] for k in keys}) != len(keys):
            raise ValueError(f"Inputs and key disagree in {level}")
        pipe = Pipeline(llm=StubLLM(), fx=StubFX(), store=Store(), publisher=NullPublisher(), write_logs=False)
        rows = [process_case(pipe, e, k) for e, k in zip(inputs, keys)]
        all_rows.extend(rows)
        counts = Counter(r["steps"][0]["payload"]["decision"] for r in rows)
        issues = [r["id"] for r in rows if r["issues"]]
        summary = f"{len(rows)} entries, {dict(counts)}, {len(issues)} QA differences"
        print(level, summary, ", ".join(issues))
        intro = f"# {level.title()} — expense QA\n\n{summary}.\n\n"
        intro += "Synthetic expenses. Real batch and follow-up logic, offline model and FX fixtures, in-memory storage and a recording publisher. Each entry includes the actual question and rule trace.\n\n"
        (out / f"{level}.md").write_text(intro + "\n---\n\n".join(map(render, rows)), encoding="utf-8")
    (out / "traces.jsonl").write_text("".join(encode(r)+"\n" for r in all_rows), encoding="utf-8")
    return int(any(r["issues"] for r in all_rows))


if __name__ == "__main__":
    raise SystemExit(main())
