"""In-memory SQLite store (one process = one store) with JSON export.

Tables
  expenses       latest known version of each expense (+ status)
  decisions      every decision version, storing EXACTLY the JSON we POSTed
  followups      one row per flag question, and the employee's answer
  decision_logs  full trace per decision (rule table, LLM raw output, ...)

Invariant: decisions.payload_json is byte-for-byte what was sent to /decisions,
so what the employee sees, what Finance's system received, and what we stored
always agree.
"""

import json
import sqlite3
import threading
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE expenses (
    expense_id   TEXT PRIMARY KEY,
    source       TEXT NOT NULL,            -- batch | portal
    raw_json     TEXT NOT NULL,            -- exactly as received (+ merged answers)
    status       TEXT NOT NULL,            -- decided | awaiting_employee | awaiting_finance
    latest_version INTEGER NOT NULL DEFAULT 0,
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL
);
CREATE TABLE decisions (
    expense_id   TEXT NOT NULL,
    version      INTEGER NOT NULL,
    decision     TEXT NOT NULL,
    payload_json TEXT NOT NULL,            -- the exact POST body
    post_status  TEXT NOT NULL,            -- sent | failed | not_sent
    post_detail  TEXT,
    created_at   TEXT NOT NULL,
    PRIMARY KEY (expense_id, version)
);
CREATE TABLE followups (
    expense_id   TEXT NOT NULL,
    version      INTEGER NOT NULL,         -- decision version that asked
    question_json TEXT NOT NULL,
    answer_json  TEXT,
    state        TEXT NOT NULL,            -- open | answered
    asked_at     TEXT NOT NULL,
    answered_at  TEXT,
    PRIMARY KEY (expense_id, version)
);
CREATE TABLE decision_logs (
    expense_id   TEXT NOT NULL,
    version      INTEGER NOT NULL,
    trace_json   TEXT NOT NULL,
    PRIMARY KEY (expense_id, version)
);
"""


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.lock = threading.Lock()
        with self.lock:
            self.db.executescript(SCHEMA)

    # ---- expenses ----------------------------------------------------------
    def upsert_expense(self, expense, source):
        now = _now()
        with self.lock:
            row = self.db.execute("SELECT expense_id FROM expenses WHERE expense_id=?", (expense["id"],)).fetchone()
            if row:
                self.db.execute("UPDATE expenses SET raw_json=?, updated_at=? WHERE expense_id=?",
                                (json.dumps(expense), now, expense["id"]))
            else:
                self.db.execute("INSERT INTO expenses VALUES (?,?,?,?,?,?,?)",
                                (expense["id"], source, json.dumps(expense), "new", 0, now, now))
            self.db.commit()

    def get_expense(self, expense_id):
        with self.lock:
            row = self.db.execute("SELECT * FROM expenses WHERE expense_id=?", (expense_id,)).fetchone()
        return dict(row) | {"expense": json.loads(row["raw_json"])} if row else None

    def next_version(self, expense_id):
        with self.lock:
            row = self.db.execute("SELECT MAX(version) v FROM decisions WHERE expense_id=?", (expense_id,)).fetchone()
        return (row["v"] or 0) + 1

    def portal_id(self):
        with self.lock:
            n = self.db.execute("SELECT COUNT(*) n FROM expenses WHERE source='portal'").fetchone()["n"]
        return f"PORTAL-{n + 1:04d}"

    # ---- decisions ---------------------------------------------------------
    def add_decision(self, payload, post_status, post_detail, trace):
        eid, ver = payload["expense_id"], payload["decision_version"]
        status = {"approve": "decided", "reject": "decided"}.get(payload["decision"]) or \
            ("awaiting_finance" if payload.get("routed_to") == "finance" else "awaiting_employee")
        now = _now()
        with self.lock:
            self.db.execute("INSERT INTO decisions VALUES (?,?,?,?,?,?,?)",
                            (eid, ver, payload["decision"], json.dumps(payload), post_status, post_detail, now))
            self.db.execute("INSERT INTO decision_logs VALUES (?,?,?)", (eid, ver, json.dumps(trace, default=str)))
            self.db.execute("UPDATE expenses SET status=?, latest_version=?, updated_at=? WHERE expense_id=?",
                            (status, ver, now, eid))
            if payload["decision"] == "flag" and payload.get("question"):
                self.db.execute("INSERT INTO followups VALUES (?,?,?,?,?,?,?)",
                                (eid, ver, json.dumps(payload["question"]), None, "open", now, None))
            self.db.commit()

    def record_answer(self, expense_id, version, answers):
        with self.lock:
            self.db.execute("UPDATE followups SET answer_json=?, state='answered', answered_at=? "
                            "WHERE expense_id=? AND version=?", (json.dumps(answers), _now(), expense_id, version))
            self.db.commit()

    def latest_decision(self, expense_id):
        with self.lock:
            row = self.db.execute("SELECT * FROM decisions WHERE expense_id=? ORDER BY version DESC LIMIT 1",
                                  (expense_id,)).fetchone()
        return dict(row) | {"payload": json.loads(row["payload_json"])} if row else None

    def history(self, expense_id):
        with self.lock:
            rows = self.db.execute("SELECT * FROM decisions WHERE expense_id=? ORDER BY version",
                                   (expense_id,)).fetchall()
        return [dict(r) | {"payload": json.loads(r["payload_json"])} for r in rows]

    def trace(self, expense_id, version):
        with self.lock:
            row = self.db.execute("SELECT trace_json FROM decision_logs WHERE expense_id=? AND version=?",
                                  (expense_id, version)).fetchone()
        return json.loads(row["trace_json"]) if row else None

    def open_followups(self):
        with self.lock:
            rows = self.db.execute(
                "SELECT f.* FROM followups f JOIN expenses e ON e.expense_id=f.expense_id "
                "WHERE f.state='open' AND f.version=e.latest_version ORDER BY f.expense_id").fetchall()
        return [dict(r) | {"question": json.loads(r["question_json"])} for r in rows]

    def overview(self):
        with self.lock:
            rows = self.db.execute(
                "SELECT e.expense_id, e.source, e.status, e.latest_version, d.decision, d.post_status, d.payload_json "
                "FROM expenses e LEFT JOIN decisions d ON d.expense_id=e.expense_id AND d.version=e.latest_version "
                "ORDER BY e.created_at, e.expense_id").fetchall()
        out = []
        for r in rows:
            p = json.loads(r["payload_json"]) if r["payload_json"] else {}
            out.append({"expense_id": r["expense_id"], "source": r["source"], "status": r["status"],
                        "version": r["latest_version"], "decision": r["decision"], "posted": r["post_status"],
                        "reason": p.get("reason", "")})
        return out

    def export(self):
        """Whole store as plain JSON (for the demo / durability)."""
        out = {}
        with self.lock:
            for table in ("expenses", "decisions", "followups", "decision_logs"):
                out[table] = [dict(r) for r in self.db.execute(f"SELECT * FROM {table}").fetchall()]
        return out
