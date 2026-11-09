# Expense Auto-Approver: Full Workflow (3 zoom levels) + Requirements Check

This is the final design review before specs and code. It ties together `RULEBOOK.md` (what the rules are), `DECISION_FLOW.md` (how the engine applies them), and `RECEIPT_READER_SPEC.md` (an optional add-on, **not in v1**). Then it checks the design against every requirement in `PROMPT.md` and `README.md`.

**Principles (from the client)**
1. Money is at stake, so **every decision is traceable**: rule ids, facts, evidence, LLM reasoning.
2. **Flag over guess.** If anything is confusing, we flag it. We reject only when the violation is clear.
3. **One round with the employee.** We ask for everything at once, prefilled, so nobody gets chased twice.
4. **Batch and portal share one decision path.**
5. **Receipt reading is a later add-on.** v1 uses the `receipt: true/false` field only.

---

## Zoom level 1: the 30-second version

Expenses come in two ways: a **batch file** (the legacy `pending_expenses.json`) or the **portal** (file upload or manual form). Both go through the same **decision engine**. Plain code handles everything it can, a cheap LLM reads the free-text memo for facts (who attended, alcohol, city, manipulation attempts), and the **rulebook decides** approve, reject or flag. Every decision is **POSTed** to `/decisions`, **stored**, and **logged with its reasons**. When we flag, the decision carries **one specific question** that asks for everything missing. The employee answers it in the portal through a prefilled form. The answer goes back through the same engine, and the new decision is POSTed and stored.

```
 Batch file ─┐                                   ┌─► POST /decisions
             ├─► Decision engine (rules + LLM) ──┼─► Store (SQLite)
 Portal ─────┘          ▲                        ├─► Decision log (jsonl + readable)
                        │                        └─► Portal / Gradio shows result + question
                        └──── employee answers the flag question (portal) ◄──┘
```

---

## Zoom level 2: the components

| # | Component | Job | Shared by batch and portal? |
|---|---|---|---|
| 1 | **Ingest adapters** | Batch: read the JSON (and CSV) file. Portal: file upload (JSON/CSV) or manual form. Both turn input into the same `Expense` record. | Two thin adapters, one output shape |
| 2 | **Normalizer** | Parse amount + currency (USD unless a non-$ symbol), dates (ISO and MM/DD/YYYY), category (case and synonyms), receipt, approval code | ✓ |
| 3 | **Security screen** | Phrase screen on all free text, plus the LLM's injection flag. Injection → reject | ✓ |
| 4 | **Fact extractor (LLM)** | Category-specific prompt. Returns client check (label, confidence, evidence, reasoning), alcohol, city, nights. Strict JSON. Temperature 0 | ✓ |
| 5 | **Enrichers** | FX conversion (only for non-USD), Tier-1 city table | ✓ |
| 6 | **Rules engine** | Stages S0–S6 from the rulebook: security → validity → category → completeness → policy → approve. Collects every rule result | ✓ |
| 7 | **Question builder** | From the gap list: one question that covers every missing field, with options + free text. Self-contained so it works in one reply | ✓ |
| 8 | **Decision publisher** | Builds the decision payload (§4), POSTs it to `/decisions`, retries on failure | ✓ |
| 9 | **Store** | SQLite: expenses, decision versions, follow-ups, logs. Stores **exactly the payload that was POSTed** | ✓ |
| 10 | **Decision log** | `decision_log.jsonl` + readable `decision_log.md`, plus the Gradio "Why this decision?" panel | ✓ |
| 11 | **Portal (Gradio)** | Upload/form, live decision, show question, answer it, history | Portal only (calls 2–10) |
| 12 | **Eval harness** | Replays past decisions, runs pending expected outcomes, adversarial and boundary sets | Uses the same engine |
| 13 | *(later)* Receipt reader | PDF/image → facts. Optional add-on | n/a in v1 |

**Batch run:** load file → for each expense: engine → payload → POST → store → log → print a summary table (counts, flags with questions).

**Portal run:** submit or edit → engine → payload → (POST on submit) → store → log → show decision, reasons and question → employee answers → engine re-runs with the answers merged → new payload → POST → store → log.

**Legacy flagged items in the portal:** a flagged batch expense is already in the store. Its follow-up link opens the portal with every known field prefilled and only the missing ones editable. Answering it uses the exact portal path above.

---

## Zoom level 3: step by step

### 3.1 One expense through the engine

| Step | What happens | Possible exit | Logged |
|---|---|---|---|
| 1 | Build the `Expense` record; keep the raw input untouched | none | raw input |
| 2 | Phrase screen on memo, merchant, category, approval code, answers | **REJECT** `SECURITY_PROMPT_INJECTION` | hit + quote |
| 3 | Parse amount/currency/date/receipt; validate required fields | **FLAG** (fix field) | parsed values, parse errors |
| 4 | Category present and on the allowlist | **FLAG** (category + its needs) | normalized category |
| 5 | FX conversion if non-USD (historical rate on the expense date, else today's) | FX fails → amount_usd unknown | rate, source, date |
| 6 | LLM fact extraction for the category (blank memo → no LLM, NONE = internal) | LLM error/timeout/invalid JSON → facts unknown (**fail closed**) | model, prompt version, raw output, reasoning |
| 7 | LLM injection flag | **REJECT** `SECURITY_PROMPT_INJECTION` | quote |
| 8 | City match (Hotel): 8 main cities + short forms only; else Tier 2; no city → unknown | none | match path |
| 9 | Completeness: receipt > $25, approval code, client confirmation (if it changes the outcome), city, nights, USD amount | **FLAG** with ONE question covering every gap | gap list, question |
| 10 | Policy rules (inclusive limits): meal caps, weekend meals, alcohol, entertainment needs a client, hotel caps, with client overrides | **REJECT** listing every broken rule | every rule pass/fail with values |
| 11 | Nothing failed | **APPROVE** | full rule table |
| 12 | Build payload → POST → store → log | POST fails → retry, mark `post_status: failed`, keep it for resend | POST status |

Trust rule: an LLM fact counts only at **high** confidence (and a client also needs a name). Otherwise it's unknown, and if it matters we ask.

### 3.2 Portal: submit, see decision live, answer

1. **Enter or upload.** Form fields: employee, date, category (dropdown), merchant, amount, currency, memo, receipt (checkbox for now), approval code. Choosing a category reveals that category's required fields: client name for Entertainment, city + nights for Hotel, approval code for Software. Choosing "internal" for Entertainment is blocked with an explanation. An uploaded file can hold one or many expenses, and each one becomes its own submission.
2. **Live decision.** While the employee edits, a **preview** runs the code-only checks instantly (missing fields, caps, weekend, receipt). The LLM check runs on a short pause or on blur. The preview shows "Will be approved / rejected / needs: X". **POST happens only on Submit**, not on every keystroke (see Gap G1).
3. **Submit.** The full engine runs. The decision, reasons and rule table appear right away, along with the question if it's flagged. The payload is POSTed and stored.
4. **Answer.** On a flag, the question shows as form fields (radio/dropdown/text/file) plus an optional free-text box, with already-known fields locked and prefilled. On submit, the answers are merged as facts (`source = employee_answer`), free text goes through the security screen, and the **whole engine re-runs**.
5. **New decision.** It's POSTed as a new version that supersedes the previous one, then stored and logged. The submission history shows every version.

### 3.3 Decision payload (what we POST and what we store)

```json
{
  "expense_id": "EXP-2005",
  "decision": "flag",
  "decision_version": 1,
  "supersedes_version": null,
  "is_final": false,
  "source": "batch | portal",
  "reason": "Dinner of $96.00 is over the $60.00 limit, and we can't confirm Cascade Partners is a client.",
  "rules_fired": [
    {"rule": "MEAL_CAP_DINNER", "result": "fail_pending_override", "detail": "96.00 > 60.00"},
    {"rule": "CLIENT_CHECK", "result": "not_trusted", "detail": "UNCLEAR, medium: 'Cascade Partners re: contract'"}
  ],
  "missing_fields": ["client_confirmation"],
  "question": {
    "text": "Was Cascade Partners a client at your $96.00 dinner at Capital Grille on June 17? If yes, please confirm the company name; if not, tell us who they are (vendor, partner, other). Dinners over $60 are covered only when a client attended.",
    "fields": [
      {"name": "attendee_type", "type": "choice", "options": ["Internal only", "Client", "Vendor/partner", "Other"]},
      {"name": "client_name", "type": "text", "prefill": "Cascade Partners"}
    ]
  },
  "facts": {
    "amount_usd": 96.00, "currency": "USD", "date": "2026-06-17", "weekday": "Wed",
    "category": "Dinner", "receipt": true,
    "client_check": {"label": "UNCLEAR", "name": "Cascade Partners", "confidence": "medium",
                     "evidence": "with Cascade Partners re: contract", "reasoning": "..."}
  },
  "security_flags": [],
  "rulebook_version": "v0.3",
  "llm": {"model": "<openrouter id>", "prompt_version": "client_check_v1"},
  "trace_id": "…",
  "decided_at": "2026-11-09T21:10:00Z"
}
```

- `question` is **null unless the decision is flag**, and it always rides on the same POST (README requirement).
- `question.text` is self-contained (enough to answer in one reply by email). `question.fields` drives the portal form.
- Approve and reject carry `reason` + `rules_fired` too, for traceability.

### 3.4 Storage (SQLite, one file)

| Table | Holds |
|---|---|
| `expenses` | id, raw input as received, normalized fields, source (batch/portal), created_at, status (`decided`, `awaiting_employee`) |
| `decisions` | expense_id, version, **the exact JSON payload POSTed**, post_status (`sent`/`failed`), posted_at |
| `followups` | expense_id, decision_version, question JSON, answer JSON, answered_at, state (`open`, `answered`) |
| `decision_logs` | trace_id, full trace (every rule result, every LLM call raw output) |

Rule: what's stored in `decisions` is byte-for-byte what was POSTed. The portal reads its status from this store, so what the employee sees, what was POSTed and what was stored always agree.

### 3.5 How we show it's right

1. **Past decisions:** replay all 20. Expect 20/20 (1017 might come out as a safe flag). Print a confusion matrix.
2. **Pending:** expected outcomes agreed in RULEBOOK §7 (8 approve, 6 reject, 4 flag). The run is compared against them.
3. **Adversarial set:** injection in memo, merchant, approval code, answers; "w/ client" with no name; answers that try to flip a decision.
4. **Boundary set:** $25.00 / $25.01, $30 / $30.01, $60 / $60.01, $200 / $200.01, $350 / $350.01.
5. **Parity test:** the same expense via batch and via the portal must give an identical payload, apart from `source` and timestamps.
6. **The bar:** zero wrong approvals.

---

## 4. Requirements check against PROMPT.md and README.md

| # | Requirement (source) | Covered by | Status |
|---|---|---|---|
| R1 | Ingest `pending_expenses.json`, decide approve/reject/flag for each (PROMPT task 1) | Batch adapter + engine | ✓ |
| R2 | POST decisions to the mock endpoint, single or list (PROMPT 2, README) | Publisher; POST each decision (or a list for a batch) | ✓ |
| R3 | Design a decision shape and be able to explain it (README) | §3.3 payload | ✓ |
| R4 | Use an LLM where it helps (PROMPT 2) | Fact extraction only; question wording polish | ✓ |
| R5 | Flagged → specific question to the submitter, resolvable in one reply (PROMPT 3) | Question builder from the gap list; asks for everything at once | ✓ |
| R6 | Question included in the same POSTed decision, e.g. a `question` field (PROMPT 3, README) | `question` on the payload | ✓ |
| R7 | Portal: upload an expense file OR enter one manually (PROMPT 4, README) | Gradio upload (JSON/CSV) + form | ✓ |
| R8 | Portal uses the **same end-to-end decision process** as batch (PROMPT 4, README) | Same engine, publisher, store, log; parity test | ✓ |
| R9 | Classify **as they submit or edit**, see the decision update **in realtime**, as soon as there's enough information (PROMPT 4, README) | Live preview on edit + full decision on submit | ⚠ see G1 |
| R10 | Show the generated question **immediately** on flag (PROMPT 4, README) | Shown on the result panel at submit | ✓ |
| R11 | Employee can **answer** the question (PROMPT 4, README) | Prefilled answer form → engine re-runs | ✓ |
| R12 | POST the resulting decision (after the answer too) (PROMPT 4, README) | New version POSTed with `supersedes_version` | ✓ (see G2) |
| R13 | Persist portal-submission state incl. follow-up state; explainable representation; durable enough for a demo (PROMPT 4, README) | SQLite tables §3.4 | ✓ |
| R14 | Stored state consistent with what's POSTed (README) | Store the exact POSTed payload | ✓ |
| R15 | Handle messy data: mixed formats, free text, oddballs (README) | Normalizer + flag-over-guess | ✓ |
| R16 | Eval 1: arrive at the correct spec (PROMPT) | RULEBOOK v0.3, client-confirmed | ✓ |
| R17 | Eval 2: show **how you know** it's right, not just that it runs (PROMPT) | Eval harness §3.5 | ✓ (must be built, see G6) |
| R18 | Eval 3: secure, can't be tricked into approving (PROMPT) | Two-layer injection screen, LLM never decides, fail closed, answers screened | ✓ (see G3) |
| R19 | Eval 4: usable workflow: fast decision, clear next step, answer, trust state was stored (PROMPT) | Portal flow §3.2; show "saved + POSTed ✓" status | ✓ |
| R20 | Eval 5: show the code and **prompts**; understand them (PROMPT) | Prompts as versioned files in `prompts/`; prompt version in every log | ✓ |
| R21 | ~2 hours; a working partial beats a sprawling unfinished one (PROMPT) | MVP order in G6 | ⚠ |
| R22 | Bring your own API key; mock server is stdlib (README) | OpenRouter key via env var | ✓ |

---

## 5. Final gaps to decide (this is the last stage to flag)

| # | Gap | Why it matters | Recommendation |
|---|---|---|---|
| **G1** | **When exactly do we POST from the portal?** The PROMPT says the decision updates "as they submit **or edit**" and POSTs. POSTing on every keystroke would flood Finance's system with half-typed expenses. | Downstream noise; LLM cost | Show a **live preview** while editing (code checks instantly, LLM on pause). **POST on Submit and on each answer.** Editing a submitted expense = a new POSTed version. |
| **G2** | **The mock endpoint only appends**, so the same expense can have several decisions (flag, then approve after the answer). Downstream needs to know which one counts. | Paying out on a stale decision | Every payload has `decision_version`, `supersedes_version` and `is_final`. The latest version wins. |
| **G3** | **Employee answers can flip a decision.** Someone flagged for "Cascade Partners" can just answer "Client" and get approved. | The weakest point in the security story | Accept it (that's what the question is for), but tag it `approved_on_employee_attestation` in the log and payload so Finance can audit. Free-text answers go through the injection screen. Optional: amounts above a threshold → human. |
| **G4** | **LLM down, slow or returning bad JSON.** | Can't block the batch | Fail closed: the facts become unknown → flag (never approve). Log the error. Code-only rejects still work. |
| **G5** | **No login in the portal.** Anyone can type any employee name. | Out of scope for a demo, but they'll ask | Say it plainly in the demo: production would use SSO, and the employee comes from the login, not a text field. |
| **G6** | **Scope vs. ~2 hours.** The full design is big. | "Working partial beats sprawling" | **Build order:** (1) normalizer + rules engine + client-check prompt; (2) batch run + POST + log + eval on past/pending; (3) SQLite store; (4) Gradio submit + decision + question + answer; (5) live preview; (6) receipt reader (later). |
| **G7** | **The upload format** isn't defined by the client. | The portal needs to accept something | Accept the same JSON shape as `pending_expenses.json` (one object or a list) and the CSV columns of `past_decisions.csv`. Bad rows are flagged one at a time and don't fail the whole file. |
| **G8** | **Expense ids in the portal.** Legacy rows have ids; manual entries don't. Resubmissions must be new expenses. | Duplicates, history | The portal generates new ids (e.g. `PORTAL-0001`). A resubmission gets a new id and an optional `related_to` link. |
| **G9** | **Unanswered follow-ups.** The employee never replies. | Stuck expenses | Out of scope for v1. The state stays `awaiting_employee` in the store, visible in the portal. |
| **G10** | **The question's text form vs. form form.** The README wants a question the employee can answer "in a single reply" (email), and the portal wants fields. | Both are needed | The payload carries both `question.text` (self-contained) and `question.fields` (for the portal form). |

Everything else in the PROMPT and README is covered.
