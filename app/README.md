# Expense Auto-Approver (app/)

The rules decide approve / reject / flag. The LLM (DeepSeek Flash via OpenRouter) only **reads the memo for facts** and returns them with a confidence label and a quoted piece of evidence. Every decision is POSTed, stored and logged, and lists every rule it checked.

Design docs (one level up): `RULEBOOK.md` covers what the rules are, `DECISION_FLOW.md` covers how they run, and `WORKFLOW.md` gives three zoom levels plus a requirements check.

## Run it

```bash
pip install -r app/requirements.txt
# .env in the candidate folder must contain OPENROUTER_API_KEY=...
# optional: OPENROUTER_MODEL=deepseek/deepseek-v4-flash  (default)

python mock_server.py                 # terminal 1: Finance's endpoint on :8000
python -m app.batch                   # terminal 2: decide + POST data/pending_expenses.json
python -m app.evaluate                # replay 20 past + 18 pending vs agreed outcomes (no POST)
python -m app.portal                  # Gradio portal on http://127.0.0.1:7870 (override with PORTAL_PORT)
python -m unittest discover -s app/tests -t .   # 52 tests (rules + portal form), stub LLM, no network
python -m app.evaluate --stub         # same eval with canned LLM answers, no network
```

## Layout

| File | Job |
|---|---|
| `config.py` | env, paths, **every policy number** (caps, thresholds, categories) |
| `normalize.py` | parses amount/currency, date, category, receipt, approval code (no LLM) |
| `security.py` | deterministic prompt-injection phrase screen (stage S0) |
| `prompts/` | versioned LLM prompts: shared `system_v1` + one section per category |
| `llm.py` | OpenRouter client, strict schema validation, one retry; `StubLLM` for tests |
| `extract.py` | picks the category prompt, wraps untrusted text in tags, **verifies evidence quotes** |
| `cities.py` | Tier-1 city table (8 main cities + short forms only) |
| `form.py` | portal form → expense, driven by `config.FORM_REQUIREMENTS` (visibility, required fields, attestation checkboxes) |
| `fx.py` | live FX (historical rate on the expense date); failure means we ask for USD |
| `engine.py` | **the rulebook as code**: S0 to S6, returns payload + rule-by-rule trace |
| `questions.py` | one combined follow-up question from the gap list (text + form fields); merges answers |
| `pipeline.py` | **the single path for batch AND portal**: decide, version, POST, store, log; `answer()` re-runs everything |
| `store.py` | in-memory SQLite: expenses, decisions (exact POST body), followups, decision_logs; JSON export |
| `publisher.py` | POST with retries |
| `decision_log.py` | `logs/decision_log.jsonl` + `logs/decision_log.md`; the same renderer feeds the portal |
| `batch.py`, `evaluate.py`, `portal.py` | entry points |

## Decision payload (what is POSTed and stored)

`expense_id, employee, decision, reason, rules_fired[{rule,result,detail}], missing_fields, question{text,fields} (flag only), routed_to, facts{amount, currency, amount_usd, fx, date, weekday, category, receipt, attendee{status,client_name,source,detail}, alcohol, hotel}, security_flags, tags (e.g. approved_on_employee_attestation), rulebook_version, llm{model,prompt}, source, decision_version, supersedes_version, is_final, decided_at`

The endpoint only appends, so the newest `decision_version` for an `expense_id` is the one that counts.

## Safety properties (and the tests that prove them)

- The LLM never decides. Its facts count only at `high` confidence, and only if its evidence quote is really in the memo.
- Injection in the memo, merchant, approval code or an employee answer → reject (both the phrase screen and the LLM catch it).
- LLM down or returning bad JSON → never approve (it's flagged to Finance). Rules that only need code still reject.
- Limits are inclusive, and receipts are required strictly above $25.
- Stored payload == POSTed payload. Batch and portal produce the same decision.
