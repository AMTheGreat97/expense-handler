"""The ONE end-to-end path used by both the batch run and the portal.

process()  : expense -> engine -> versioned payload -> POST -> store -> log
answer()   : employee answers -> merge -> FULL pipeline re-run -> new version

Batch and portal call exactly these functions; only `source` differs.
"""

from . import decision_log, engine, questions
from .fx import FrankfurterFX
from .llm import OpenRouterLLM
from .publisher import HttpPublisher
from .store import Store


class Pipeline:
    def __init__(self, llm=None, fx=None, publisher=None, store=None, write_logs=True):
        self.llm = llm or OpenRouterLLM()
        self.fx = fx or FrankfurterFX()
        self.publisher = publisher or HttpPublisher()
        self.store = store or Store()
        self.write_logs = write_logs

    def preview(self, expense):
        """Code-only checks while the employee is typing. Never POSTed or stored."""
        exp = dict(expense)
        exp.setdefault("id", "PREVIEW")
        payload, _ = engine.decide(exp, self.llm, self.fx, use_llm=False)
        return payload

    def process(self, expense, source):
        exp = dict(expense)
        if not exp.get("id"):
            exp["id"] = self.store.portal_id() if source == "portal" else None
        if exp.get("id"):
            self.store.upsert_expense(exp, source)

        payload, trace = engine.decide(exp, self.llm, self.fx)
        if not exp.get("id"):
            return payload  # can't version/POST an expense with no id; question asks for it

        version = self.store.next_version(exp["id"])
        payload["source"] = source
        payload["decision_version"] = version
        payload["supersedes_version"] = version - 1 if version > 1 else None
        payload["is_final"] = payload["decision"] != "flag"

        post_status, post_detail = self.publisher.post(payload)
        self.store.add_decision(payload, post_status, post_detail, trace)
        if self.write_logs:
            decision_log.write(payload | {"_post_status": post_status}, trace)
        # local-only fields for the caller/UI; the POSTed + stored payload is unchanged
        return payload | {"_post_status": post_status, "_post_detail": post_detail}

    def answer(self, expense_id, answers):
        """Employee answered the open question: merge and re-run EVERY check."""
        row = self.store.get_expense(expense_id)
        if not row:
            raise KeyError(expense_id)
        latest = self.store.latest_decision(expense_id)
        self.store.record_answer(expense_id, latest["version"], answers)
        merged = questions.apply_answers(row["expense"], answers)
        return self.process(merged, row["source"])

    def trace_md(self, expense_id, version=None):
        hist = self.store.history(expense_id)
        if not hist:
            return "No decisions yet."
        rows = hist if version is None else [h for h in hist if h["version"] == version]
        out = []
        for h in reversed(rows):
            p = h["payload"] | {"_post_status": h["post_status"]}
            out.append(decision_log.render(p, self.store.trace(expense_id, h["version"])))
        return "\n\n---\n\n".join(out)
