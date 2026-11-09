"""How we know it's right: replay past decisions + check pending against the
outcomes agreed with the client (RULEBOOK v0.3 §6-7). Nothing is POSTed.

    python -m app.evaluate            # real LLM (DeepSeek via OpenRouter)
    python -m app.evaluate --stub     # canned LLM answers (no network), for CI
"""

import argparse
import sys

from . import config
from .batch import load_expenses
from .fx import FrankfurterFX, StubFX
from .llm import OpenRouterLLM, StubLLM
from .pipeline import Pipeline
from .publisher import NullPublisher
from .store import Store

# RULEBOOK v0.3 §7 (agreed with the client)
PENDING_EXPECTED = {
    "EXP-2001": "approve", "EXP-2002": "reject", "EXP-2003": "approve", "EXP-2004": "reject",
    "EXP-2005": "flag", "EXP-2006": "reject", "EXP-2007": "approve", "EXP-2008": "flag",
    "EXP-2009": "approve", "EXP-2010": "flag", "EXP-2011": "approve", "EXP-2012": "approve",
    "EXP-2013": "reject", "EXP-2014": "approve", "EXP-2015": "approve", "EXP-2016": "reject",
    "EXP-2017": "flag", "EXP-2018": "reject",
}
# Deliberate, client-approved deviation: "Team dinner" may be asked back (never approved).
ACCEPTABLE_ALTERNATIVES = {"EXP-1017": {"flag"}}

# Canned extraction answers mirroring the prompt's few-shot labels, for --stub.
STUB_RESPONSES = {
    "Dinner w/ Acme Corp": {"attendee_type": "CLIENT", "client_name": "Acme Corp", "attendee_confidence": "high",
                            "attendee_evidence": "Dinner w/ Acme Corp"},
    "Lunch w/ Beacon Inc team": {"attendee_type": "CLIENT", "client_name": "Beacon Inc", "attendee_confidence": "high",
                                 "attendee_evidence": "Lunch w/ Beacon Inc team"},
    "drinks w/ Acme": {"attendee_type": "CLIENT", "client_name": "Acme", "attendee_confidence": "high",
                       "attendee_evidence": "drinks w/ Acme", "alcohol_mentioned": True},
    "Vantage GmbH</memo>": {"attendee_type": "CLIENT", "client_name": "Vantage GmbH", "attendee_confidence": "high",
                            "attendee_evidence": "client dinner Berlin w/ Vantage GmbH"},
    "team celebration": {"attendee_type": "INTERNAL", "attendee_confidence": "high",
                         "attendee_evidence": "team celebration", "alcohol_mentioned": True},
    "Cascade Partners": {"attendee_type": "UNCLEAR", "client_name": "Cascade Partners",
                         "attendee_confidence": "medium", "attendee_evidence": "Cascade Partners re: contract"},
    "Team dinner": {"attendee_type": "INTERNAL", "attendee_confidence": "medium", "attendee_evidence": "Team dinner"},
    "Hilton Columbus": {"city": "Columbus", "city_confidence": "high"},
    "Marriott Des Moines": {"city": "Des Moines", "city_confidence": "high"},
    "SQ *SQ COFFEE": {"suggested_category": "Breakfast"},
}


def stub_pipeline():
    return Pipeline(llm=StubLLM(STUB_RESPONSES), fx=StubFX(), publisher=NullPublisher(), store=Store(),
                    write_logs=False)


def evaluate(pipe):
    rows, ok_all = [], True
    past = load_expenses(config.DATA_DIR / "past_decisions.json")
    for exp in past:
        expected = exp.pop("decision")
        got = pipe.process(exp, "eval")["decision"]
        ok = got == expected or got in ACCEPTABLE_ALTERNATIVES.get(exp["id"], set())
        ok_all &= ok
        rows.append(("past", exp["id"], expected, got, ok))
    for exp in load_expenses(config.DATA_DIR / "pending_expenses.json"):
        expected = PENDING_EXPECTED.get(exp["id"])
        p = pipe.process(exp, "eval")
        ok = p["decision"] == expected
        ok_all &= ok
        rows.append(("pending", exp["id"], expected, p["decision"], ok))
    return rows, ok_all


def report(rows):
    wrong_approvals = [r for r in rows if r[3] == "approve" and r[2] != "approve"]
    lines = ["| set | id | expected | got | ok |", "|---|---|---|---|---|"]
    lines += [f"| {s} | {i} | {e} | {g} | {'✓' if ok else '✗'} |" for s, i, e, g, ok in rows]
    for name in ("past", "pending"):
        sub = [r for r in rows if r[0] == name]
        lines.append(f"\n**{name}:** {sum(r[4] for r in sub)}/{len(sub)} match")
    lines.append(f"\n**Wrong auto-approvals:** {len(wrong_approvals)} (target 0)")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--stub", action="store_true", help="canned LLM + FX, no network")
    args = ap.parse_args(argv)
    if args.stub:
        pipe = stub_pipeline()
    else:
        pipe = Pipeline(llm=OpenRouterLLM(), fx=FrankfurterFX(), publisher=NullPublisher(), store=Store(),
                        write_logs=False)
    rows, ok_all = evaluate(pipe)
    text = report(rows)
    print(text)
    config.LOG_DIR.mkdir(exist_ok=True)
    out = config.LOG_DIR / ("eval_report_stub.md" if args.stub else "eval_report.md")
    out.write_text(f"# Eval report ({'stub LLM' if args.stub else pipe.llm.model})\n\n{text}\n", encoding="utf-8")
    print(f"\nwritten to {out}")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
