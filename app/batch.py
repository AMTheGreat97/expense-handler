"""Batch run: decide every expense in a JSON file and POST each decision.

    python -m app.batch                                   # data/pending_expenses.json -> mock server
    python -m app.batch --file data/other.json --dry-run  # no POST
"""

import argparse
import json
import sys

from . import config
from .pipeline import Pipeline
from .publisher import NullPublisher


def load_expenses(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise ValueError("file must contain one expense object or a list of them")
    return data


def run(pipeline, expenses, source="batch"):
    results = []
    for exp in expenses:
        if not isinstance(exp, dict):
            continue
        results.append(pipeline.process(exp, source))
    return results


def print_summary(results):
    counts = {}
    print(f"\n{'ID':<10} {'DECISION':<8} {'POST':<9} REASON")
    print("-" * 110)
    for p in results:
        counts[p["decision"]] = counts.get(p["decision"], 0) + 1
        print(f"{str(p.get('expense_id')):<10} {p['decision']:<8} {p.get('_post_status', ''):<9} {p['reason'][:80]}")
        if p.get("question"):
            print(f"{'':<29} Q: {p['question']['text'][:200]}")
    print("-" * 110)
    print("  ".join(f"{k}: {v}" for k, v in sorted(counts.items())), f"  (total {len(results)})")
    print(f"Full reasons: {config.LOG_DIR / 'decision_log.md'}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=str(config.DATA_DIR / "pending_expenses.json"))
    ap.add_argument("--dry-run", action="store_true", help="do not POST")
    args = ap.parse_args(argv)
    pipe = Pipeline(publisher=NullPublisher() if args.dry_run else None)
    if not config.OPENROUTER_API_KEY:
        print("WARNING: OPENROUTER_API_KEY not set; memos cannot be read, so those expenses will be flagged "
              "(fail closed).", file=sys.stderr)
    print(f"processing {args.file} with model {pipe.llm.model} -> "
          f"{'dry run' if args.dry_run else config.DECISIONS_ENDPOINT}")
    print_summary(run(pipe, load_expenses(args.file)))


if __name__ == "__main__":
    main()
