# Medium — expense QA

40 entries, {'flag': 22, 'approve': 13, 'reject': 5}, 0 QA differences.

Synthetic expenses. Real batch and follow-up logic, offline model and FX fixtures, in-memory storage and a recording publisher. Each entry includes the actual question and rule trace.

## M01 · Amount is zero

Input

```json
{"id": "M01", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Office", "amount": 0, "receipt": true, "memo": "", "approval_code": null}
```

**Expected FLAG** — The submitted amount does not resolve to one positive monetary value.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"amount_corrected": "$28.00"}
```

Expected after a complete reply: **approve**.

### M01 · Alex Rivera · 2026-06-17 (Wed) · Office · amount ?

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: amount must be positive: 0.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ? | `AMOUNT_VALID` | gap | amount must be positive: 0 |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

**Question to employee:**

To finish reviewing expense M01 (office at Market Street on 2026-06-17), we need one thing: Please correct the amount (amount must be positive: 0).

**Fields offered** amount_corrected, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"amount_corrected": "$28.00"}

### M01 · Alex Rivera · 2026-06-17 (Wed) · Office · 28.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 28.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| ✓ | `RECEIPT_REQUIRED` | pass | $28.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## M02 · Amount is negative

Input

```json
{"id": "M02", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Office", "amount": -12, "receipt": true, "memo": "", "approval_code": null}
```

**Expected FLAG** — The submitted amount does not resolve to one positive monetary value.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"amount_corrected": "$28.00"}
```

Expected after a complete reply: **approve**.

### M02 · Alex Rivera · 2026-06-17 (Wed) · Office · amount ?

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: amount must be positive: -12.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ? | `AMOUNT_VALID` | gap | amount must be positive: -12 |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

**Question to employee:**

To finish reviewing expense M02 (office at Market Street on 2026-06-17), we need one thing: Please correct the amount (amount must be positive: -12).

**Fields offered** amount_corrected, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"amount_corrected": "$28.00"}

### M02 · Alex Rivera · 2026-06-17 (Wed) · Office · 28.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 28.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| ✓ | `RECEIPT_REQUIRED` | pass | $28.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## M03 · Amount is missing

Input

```json
{"id": "M03", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Office", "amount": null, "receipt": true, "memo": "", "approval_code": null}
```

**Expected FLAG** — The submitted amount does not resolve to one positive monetary value.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"amount_corrected": "$28.00"}
```

Expected after a complete reply: **approve**.

### M03 · Alex Rivera · 2026-06-17 (Wed) · Office · amount ?

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: amount is missing.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ? | `AMOUNT_VALID` | gap | amount is missing |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

**Question to employee:**

To finish reviewing expense M03 (office at Market Street on 2026-06-17), we need one thing: Please correct the amount (amount is missing).

**Fields offered** amount_corrected, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"amount_corrected": "$28.00"}

### M03 · Alex Rivera · 2026-06-17 (Wed) · Office · 28.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 28.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| ✓ | `RECEIPT_REQUIRED` | pass | $28.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## M04 · Amount is estimated

Input

```json
{"id": "M04", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Office", "amount": "about 42", "receipt": true, "memo": "", "approval_code": null}
```

**Expected FLAG** — The submitted amount does not resolve to one positive monetary value.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"amount_corrected": "$28.00"}
```

Expected after a complete reply: **approve**.

### M04 · Alex Rivera · 2026-06-17 (Wed) · Office · amount ?

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: amount could not be read: 'about 42'.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ? | `AMOUNT_VALID` | gap | amount could not be read: 'about 42' |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

**Question to employee:**

To finish reviewing expense M04 (office at Market Street on 2026-06-17), we need one thing: Please correct the amount (amount could not be read: 'about 42').

**Fields offered** amount_corrected, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"amount_corrected": "$28.00"}

### M04 · Alex Rivera · 2026-06-17 (Wed) · Office · 28.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 28.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| ✓ | `RECEIPT_REQUIRED` | pass | $28.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## M05 · Amount is two candidate amounts

Input

```json
{"id": "M05", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Office", "amount": "26 or 29", "receipt": true, "memo": "", "approval_code": null}
```

**Expected FLAG** — The submitted amount does not resolve to one positive monetary value.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"amount_corrected": "$28.00"}
```

Expected after a complete reply: **approve**.

### M05 · Alex Rivera · 2026-06-17 (Wed) · Office · amount ?

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: amount could not be read: '26 or 29'.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ? | `AMOUNT_VALID` | gap | amount could not be read: '26 or 29' |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

**Question to employee:**

To finish reviewing expense M05 (office at Market Street on 2026-06-17), we need one thing: Please correct the amount (amount could not be read: '26 or 29').

**Fields offered** amount_corrected, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"amount_corrected": "$28.00"}

### M05 · Alex Rivera · 2026-06-17 (Wed) · Office · 28.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 28.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| ✓ | `RECEIPT_REQUIRED` | pass | $28.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## M06 · Amount is decimal comma

Input

```json
{"id": "M06", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Office", "amount": "28,00", "receipt": true, "memo": "", "approval_code": null}
```

**Expected FLAG** — The submitted amount does not resolve to one positive monetary value.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"amount_corrected": "$28.00"}
```

Expected after a complete reply: **approve**.

### M06 · Alex Rivera · 2026-06-17 (Wed) · Office · amount ?

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: amount could not be read: '28,00'.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ? | `AMOUNT_VALID` | gap | amount could not be read: '28,00' |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

**Question to employee:**

To finish reviewing expense M06 (office at Market Street on 2026-06-17), we need one thing: Please correct the amount (amount could not be read: '28,00').

**Fields offered** amount_corrected, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"amount_corrected": "$28.00"}

### M06 · Alex Rivera · 2026-06-17 (Wed) · Office · 28.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 28.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| ✓ | `RECEIPT_REQUIRED` | pass | $28.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## M07 · Amount is boolean

Input

```json
{"id": "M07", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Office", "amount": true, "receipt": true, "memo": "", "approval_code": null}
```

**Expected FLAG** — The submitted amount does not resolve to one positive monetary value.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"amount_corrected": "$28.00"}
```

Expected after a complete reply: **approve**.

### M07 · Alex Rivera · 2026-06-17 (Wed) · Office · amount ?

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: amount is not a number: True.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ? | `AMOUNT_VALID` | gap | amount is not a number: True |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

**Question to employee:**

To finish reviewing expense M07 (office at Market Street on 2026-06-17), we need one thing: Please correct the amount (amount is not a number: True).

**Fields offered** amount_corrected, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"amount_corrected": "$28.00"}

### M07 · Alex Rivera · 2026-06-17 (Wed) · Office · 28.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 28.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| ✓ | `RECEIPT_REQUIRED` | pass | $28.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## M08 · Amount is conflicting currencies

Input

```json
{"id": "M08", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Office", "amount": "€35 USD", "receipt": true, "memo": "", "approval_code": null}
```

**Expected FLAG** — The submitted amount does not resolve to one positive monetary value.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"amount_corrected": "$28.00"}
```

Expected after a complete reply: **approve**.

### M08 · Alex Rivera · 2026-06-17 (Wed) · Office · amount ?

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: amount has conflicting currencies: '€35 USD'.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ? | `AMOUNT_VALID` | gap | amount has conflicting currencies: '€35 USD' |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

**Question to employee:**

To finish reviewing expense M08 (office at Market Street on 2026-06-17), we need one thing: Please correct the amount (amount has conflicting currencies: '€35 USD').

**Fields offered** amount_corrected, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"amount_corrected": "$28.00"}

### M08 · Alex Rivera · 2026-06-17 (Wed) · Office · 28.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 28.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| ✓ | `RECEIPT_REQUIRED` | pass | $28.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## M09 · Date "2025-02-29"

Input

```json
{"id": "M09", "employee": "Alex Rivera", "date": "2025-02-29", "merchant": "Market Street", "category": "Office", "amount": 18, "receipt": true, "memo": "", "approval_code": null}
```

**Expected FLAG** — Require a real, nonfuture date in ISO or US format.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"date_corrected": "2026-06-17"}
```

Expected after a complete reply: **approve**.

### M09 · Alex Rivera · ? (?) · Office · 18.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: date could not be read: '2025-02-29'.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ? | `DATE_VALID` | gap | date could not be read: '2025-02-29' |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

**Question to employee:**

To finish reviewing expense M09 ($18.00 office at Market Street), we need one thing: Please correct the date (date could not be read: '2025-02-29').

**Fields offered** date_corrected, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"date_corrected": "2026-06-17"}

### M09 · Alex Rivera · 2026-06-17 (Wed) · Office · 18.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## M10 · Date "31/12/2025"

Input

```json
{"id": "M10", "employee": "Alex Rivera", "date": "31/12/2025", "merchant": "Market Street", "category": "Office", "amount": 18, "receipt": true, "memo": "", "approval_code": null}
```

**Expected FLAG** — Require a real, nonfuture date in ISO or US format.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"date_corrected": "2026-06-17"}
```

Expected after a complete reply: **approve**.

### M10 · Alex Rivera · ? (?) · Office · 18.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: date could not be read: '31/12/2025'.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ? | `DATE_VALID` | gap | date could not be read: '31/12/2025' |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

**Question to employee:**

To finish reviewing expense M10 ($18.00 office at Market Street), we need one thing: Please correct the date (date could not be read: '31/12/2025').

**Fields offered** date_corrected, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"date_corrected": "2026-06-17"}

### M10 · Alex Rivera · 2026-06-17 (Wed) · Office · 18.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## M11 · Date "2999-06-01"

Input

```json
{"id": "M11", "employee": "Alex Rivera", "date": "2999-06-01", "merchant": "Market Street", "category": "Office", "amount": 18, "receipt": true, "memo": "", "approval_code": null}
```

**Expected FLAG** — Require a real, nonfuture date in ISO or US format.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"date_corrected": "2026-06-17"}
```

Expected after a complete reply: **approve**.

### M11 · Alex Rivera · ? (?) · Office · 18.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: date is in the future: 2999-06-01.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ? | `DATE_VALID` | gap | date is in the future: 2999-06-01 |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

**Question to employee:**

To finish reviewing expense M11 ($18.00 office at Market Street), we need one thing: Please correct the date (date is in the future: 2999-06-01).

**Fields offered** date_corrected, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"date_corrected": "2026-06-17"}

### M11 · Alex Rivera · 2026-06-17 (Wed) · Office · 18.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## M12 · Date ""

Input

```json
{"id": "M12", "employee": "Alex Rivera", "date": "", "merchant": "Market Street", "category": "Office", "amount": 18, "receipt": true, "memo": "", "approval_code": null}
```

**Expected FLAG** — Require a real, nonfuture date in ISO or US format.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"date_corrected": "2026-06-17"}
```

Expected after a complete reply: **approve**.

### M12 · Alex Rivera · ? (?) · Office · 18.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: date is missing.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ? | `DATE_VALID` | gap | date is missing |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

**Question to employee:**

To finish reviewing expense M12 ($18.00 office at Market Street), we need one thing: Please correct the date (date is missing).

**Fields offered** date_corrected, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"date_corrected": "2026-06-17"}

### M12 · Alex Rivera · 2026-06-17 (Wed) · Office · 18.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## M13 · Leap day US format

Input

```json
{"id": "M13", "employee": "Alex Rivera", "date": "02/29/2024", "merchant": "Market Street", "category": "Office", "amount": 18, "receipt": true, "memo": "", "approval_code": null}
```

**Expected APPROVE** — 2024 was a leap year.

**QA** Matched the scripted checks.

### M13 · Alex Rivera · 2024-02-29 (Thu) · Office · 18.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2024-02-29 (Thursday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## M14 · Dinner with named external customer

Input

```json
{"id": "M14", "employee": "Alex Rivera", "date": "2026-06-20", "merchant": "Market Street", "category": "Dinner", "amount": 145, "receipt": true, "memo": "Dinner with customer Juniper Labs", "approval_code": null}
```

**Expected APPROVE** — A named customer qualifies for the weekend and meal exceptions and satisfies entertainment.

**QA** Matched the scripted checks.

### M14 · Alex Rivera · 2026-06-20 (Sat) · Dinner · 145.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 145.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-20 (Saturday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $145.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `MEAL_CAP_DINNER` | pass | $145.00 > $60.00 but client confirmed (Juniper Labs) -> cap waived |
| ✓ | `WEEKEND_MEAL_INTERNAL` | pass | Sat, client confirmed (Juniper Labs) |

**Client check:** client (source: memo_llm) — CLIENT/high 'Juniper Labs' (evidence: 'Dinner with customer Juniper Labs')
**Fact sources:** attendee=memo_llm
**LLM:** stub · prompt meals_v1.txt
**LLM reasoning:**

---

## M15 · Entertainment with named external customer

Input

```json
{"id": "M15", "employee": "Alex Rivera", "date": "2026-06-20", "merchant": "Market Street", "category": "Entertainment", "amount": 55, "receipt": true, "memo": "Dinner with customer Juniper Labs", "approval_code": null}
```

**Expected APPROVE** — A named customer qualifies for the weekend and meal exceptions and satisfies entertainment.

**QA** Matched the scripted checks.

### M15 · Alex Rivera · 2026-06-20 (Sat) · Entertainment · 55.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 55.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-20 (Saturday) |
| ✓ | `CATEGORY_PRESENT` | pass | Entertainment |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $55.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `ENTERTAINMENT_NO_CLIENT` | pass | client confirmed (Juniper Labs) |

**Client check:** client (source: memo_llm) — CLIENT/high 'Juniper Labs' (evidence: 'Dinner with customer Juniper Labs')
**Fact sources:** attendee=memo_llm
**LLM:** stub · prompt meals_v1.txt
**LLM reasoning:**

---

## M16 · Breakfast with named external customer

Input

```json
{"id": "M16", "employee": "Alex Rivera", "date": "2026-06-20", "merchant": "Market Street", "category": "Breakfast", "amount": 27, "receipt": true, "memo": "Dinner with customer Juniper Labs", "approval_code": null}
```

**Expected APPROVE** — A named customer qualifies for the weekend and meal exceptions and satisfies entertainment.

**QA** Matched the scripted checks.

### M16 · Alex Rivera · 2026-06-20 (Sat) · Breakfast · 27.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 27.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-20 (Saturday) |
| ✓ | `CATEGORY_PRESENT` | pass | Breakfast |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $27.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `MEAL_CAP_BREAKFAST` | pass | $27.00 > $20.00 but client confirmed (Juniper Labs) -> cap waived |
| ✓ | `WEEKEND_MEAL_INTERNAL` | pass | Sat, client confirmed (Juniper Labs) |

**Client check:** client (source: memo_llm) — CLIENT/high 'Juniper Labs' (evidence: 'Dinner with customer Juniper Labs')
**Fact sources:** attendee=memo_llm
**LLM:** stub · prompt meals_v1.txt
**LLM reasoning:**

---

## M17 · Client cannot waive receipt

Input

```json
{"id": "M17", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Dinner", "amount": 145, "receipt": false, "memo": "Dinner with customer Juniper Labs", "approval_code": null}
```

**Expected FLAG** — The receipt threshold applies even with a confirmed customer.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"receipt": true}
```

Expected after a complete reply: **approve**.

### M17 · Alex Rivera · 2026-06-17 (Wed) · Dinner · 145.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: Receipts are required for any expense over $25.00.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 145.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ? | `RECEIPT_REQUIRED` | gap | $145.00 > $25.00 and no receipt |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `MEAL_CAP_DINNER` | pass | $145.00 > $60.00 but client confirmed (Juniper Labs) -> cap waived |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** client (source: memo_llm) — CLIENT/high 'Juniper Labs' (evidence: 'Dinner with customer Juniper Labs')
**Fact sources:** attendee=memo_llm
**LLM:** stub · prompt meals_v1.txt
**LLM reasoning:**

**Question to employee:**

To finish reviewing expense M17 ($145.00 dinner at Market Street on 2026-06-17), we need one thing: Receipts are required for any expense over $25.00. Please attach it.

**Fields offered** receipt, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"receipt": true}

### M17 · Alex Rivera · 2026-06-17 (Wed) · Dinner · 145.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 145.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $145.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `MEAL_CAP_DINNER` | pass | $145.00 > $60.00 but client confirmed (Juniper Labs) -> cap waived |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** client (source: memo_llm) — CLIENT/high 'Juniper Labs' (evidence: 'Dinner with customer Juniper Labs')
**Fact sources:** attendee=memo_llm
**LLM:** stub · prompt meals_v1.txt
**LLM reasoning:**

---

## M18 · Client cannot waive hotel cap

Input

```json
{"id": "M18", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Boston Inn", "category": "Hotel", "amount": 370, "receipt": true, "memo": "Dinner with customer Juniper Labs; 1 night", "approval_code": null}
```

**Expected REJECT** — A confirmed customer cannot raise the Boston hotel cap.

**QA** Matched the scripted checks.

### M18 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 370.00 USD

**DECISION: REJECT** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Rejected: HOTEL_CAP_TIER1 ($370.00 total exceeds 1 nights x $350.00 (Boston, Tier 1))

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 370.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $370.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | Boston -> Tier 1 via city_table (table match) |
| ✗ | `HOTEL_CAP_TIER1` | fail | $370.00 total exceeds 1 nights x $350.00 (Boston, Tier 1) |

**Client check:** client (source: memo_llm) — CLIENT/high 'Juniper Labs' (evidence: 'Dinner with customer Juniper Labs')
**Hotel:** city=Boston tier=1 nights=1 via city_table (table match)
**Fact sources:** attendee=memo_llm · city=city_table · nights=memo_keyword
**LLM:** stub · prompt hotel_v1.txt
**LLM reasoning:**

---

## M19 · Client cannot waive software code

Input

```json
{"id": "M19", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Software", "amount": 18, "receipt": true, "memo": "Dinner with customer Juniper Labs", "approval_code": null}
```

**Expected FLAG** — Client attendance has no bearing on documentation for software.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"approval_code": "SW-19"}
```

Expected after a complete reply: **approve**.

### M19 · Alex Rivera · 2026-06-17 (Wed) · Software · 18.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: Software purchases always need an approval code.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Software |
| ✓ | `LLM_EXTRACTION` | pass | general_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ? | `SOFTWARE_APPROVAL_CODE` | gap | approval code missing or too short: None |

**Client check:** client (source: memo_llm) — CLIENT/high 'Juniper Labs' (evidence: 'Dinner with customer Juniper Labs')
**Fact sources:** attendee=memo_llm
**LLM:** stub · prompt general_v1.txt
**LLM reasoning:**

**Question to employee:**

To finish reviewing expense M19 ($18.00 software at Market Street on 2026-06-17), we need one thing: Please provide the software approval code.

**Fields offered** approval_code, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"approval_code": "SW-19"}

### M19 · Alex Rivera · 2026-06-17 (Wed) · Software · 18.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Software |
| ✓ | `LLM_EXTRACTION` | pass | general_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `SOFTWARE_APPROVAL_CODE` | pass | code 'SW-19' |

**Client check:** client (source: memo_llm) — CLIENT/high 'Juniper Labs' (evidence: 'Dinner with customer Juniper Labs')
**Fact sources:** attendee=memo_llm
**LLM:** stub · prompt general_v1.txt
**LLM reasoning:**

---

## M20 · Dinner with Finch Partners re contract / approve branch

Input

```json
{"id": "M20", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Dinner", "amount": 96, "receipt": true, "memo": "Dinner with Finch Partners re contract", "approval_code": null}
```

**Expected FLAG** — A relationship or customer identity is missing. The $60 dinner exception depends on it.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"attendee_type": "Client", "client_name": "Juniper Labs"}
```

Expected after a complete reply: **approve**.

### M20 · Alex Rivera · 2026-06-17 (Wed) · Dinner · 96.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: Dinner over $60.00 is reimbursed only when a client attended.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 96.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $96.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ? | `MEAL_CAP_DINNER` | gap | $96.00 > $60.00, client not confirmed |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Fact sources:** attendee=memo_llm
**LLM:** stub · prompt meals_v1.txt
**LLM reasoning:**

**Question to employee:**

To finish reviewing expense M20 ($96.00 dinner at Market Street on 2026-06-17), we need one thing: Who attended: coworkers only, an external customer, or a vendor/partner? If a customer, please name the company. (Dinner over $60.00 is reimbursed only when a client attended.)

**Fields offered** attendee_type, client_name, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"attendee_type": "Client", "client_name": "Juniper Labs"}

### M20 · Alex Rivera · 2026-06-17 (Wed) · Dinner · 96.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

**Tags:** approved_on_employee_attestation

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 96.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $96.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `MEAL_CAP_DINNER` | pass | $96.00 > $60.00 but client confirmed (Juniper Labs) -> cap waived |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** client (source: employee_answer) — employee stated client 'Juniper Labs'
**Fact sources:** attendee=employee_answer
**LLM:** stub · prompt meals_v1.txt
**LLM reasoning:**

---

## M21 · Dinner with Finch Partners re contract / reject branch

Input

```json
{"id": "M21", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Dinner", "amount": 96, "receipt": true, "memo": "Dinner with Finch Partners re contract", "approval_code": null}
```

**Expected FLAG** — A relationship or customer identity is missing. The $60 dinner exception depends on it.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"attendee_type": "Vendor / partner / other"}
```

Expected after a complete reply: **reject**.

### M21 · Alex Rivera · 2026-06-17 (Wed) · Dinner · 96.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: Dinner over $60.00 is reimbursed only when a client attended.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 96.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $96.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ? | `MEAL_CAP_DINNER` | gap | $96.00 > $60.00, client not confirmed |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Fact sources:** attendee=memo_llm
**LLM:** stub · prompt meals_v1.txt
**LLM reasoning:**

**Question to employee:**

To finish reviewing expense M21 ($96.00 dinner at Market Street on 2026-06-17), we need one thing: Who attended: coworkers only, an external customer, or a vendor/partner? If a customer, please name the company. (Dinner over $60.00 is reimbursed only when a client attended.)

**Fields offered** attendee_type, client_name, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"attendee_type": "Vendor / partner / other"}

### M21 · Alex Rivera · 2026-06-17 (Wed) · Dinner · 96.00 USD

**DECISION: REJECT** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Rejected: MEAL_CAP_DINNER ($96.00 > $60.00; employee stated vendor (not a client))

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 96.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $96.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✗ | `MEAL_CAP_DINNER` | fail | $96.00 > $60.00; employee stated vendor (not a client) |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** internal (source: employee_answer) — employee stated vendor (not a client)
**Fact sources:** attendee=employee_answer
**LLM:** stub · prompt meals_v1.txt
**LLM reasoning:**

---

## M22 · Dinner with a client / approve branch

Input

```json
{"id": "M22", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Dinner", "amount": 96, "receipt": true, "memo": "Dinner with a client", "approval_code": null}
```

**Expected FLAG** — A relationship or customer identity is missing. The $60 dinner exception depends on it.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"attendee_type": "Client", "client_name": "Juniper Labs"}
```

Expected after a complete reply: **approve**.

### M22 · Alex Rivera · 2026-06-17 (Wed) · Dinner · 96.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: Dinner over $60.00 is reimbursed only when a client attended.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 96.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $96.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ? | `MEAL_CAP_DINNER` | gap | $96.00 > $60.00, client not confirmed |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Fact sources:** attendee=memo_llm
**LLM:** stub · prompt meals_v1.txt
**LLM reasoning:**

**Question to employee:**

To finish reviewing expense M22 ($96.00 dinner at Market Street on 2026-06-17), we need one thing: Who attended: coworkers only, an external customer, or a vendor/partner? If a customer, please name the company. (Dinner over $60.00 is reimbursed only when a client attended.)

**Fields offered** attendee_type, client_name, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"attendee_type": "Client", "client_name": "Juniper Labs"}

### M22 · Alex Rivera · 2026-06-17 (Wed) · Dinner · 96.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

**Tags:** approved_on_employee_attestation

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 96.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $96.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `MEAL_CAP_DINNER` | pass | $96.00 > $60.00 but client confirmed (Juniper Labs) -> cap waived |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** client (source: employee_answer) — employee stated client 'Juniper Labs'
**Fact sources:** attendee=employee_answer
**LLM:** stub · prompt meals_v1.txt
**LLM reasoning:**

---

## M23 · Unknown attendee irrelevant to $18 lunch

Input

```json
{"id": "M23", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Lunch", "amount": 18, "receipt": true, "memo": "Lunch with Finch Partners", "approval_code": null}
```

**Expected APPROVE** — Weekday meal under cap with no alcohol passes either way.

**QA** Matched the scripted checks.

### M23 · Alex Rivera · 2026-06-17 (Wed) · Lunch · 18.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Lunch |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `MEAL_CAP_LUNCH` | pass | $18.00 <= $30.00 |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Fact sources:** attendee=memo_llm
**LLM:** stub · prompt meals_v1.txt
**LLM reasoning:**

---

## M24 · EUR below face-value threshold but above USD threshold

Input

```json
{"id": "M24", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Office", "amount": "24 EUR", "receipt": false, "memo": "", "approval_code": null}
```

**Expected FLAG** — At the fixed 1.08 rate, the USD total is $25.92.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"receipt": true}
```

Expected after a complete reply: **approve**.

### M24 · Alex Rivera · 2026-06-17 (Wed) · Office · 24.00 EUR (= $25.92)

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: Receipts are required for any expense over $25.00.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 24.0 EUR |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| ✓ | `FX_CONVERSION` | pass | 24.0 EUR x 1.08 (2026-06-17) = $25.92 |
| ? | `RECEIPT_REQUIRED` | gap | $25.92 > $25.00 and no receipt |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code
**FX:** {"rate": 1.08, "rate_date": "2026-06-17", "source": "stub", "amount_usd": 25.92}

**Question to employee:**

To finish reviewing expense M24 (24.00 EUR office at Market Street on 2026-06-17), we need one thing: Receipts are required for any expense over $25.00. Please attach it.

**Fields offered** receipt, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"receipt": true}

### M24 · Alex Rivera · 2026-06-17 (Wed) · Office · 24.00 EUR (= $25.92)

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 24.0 EUR |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| ✓ | `FX_CONVERSION` | pass | 24.0 EUR x 1.08 (2026-06-17) = $25.92 |
| ✓ | `RECEIPT_REQUIRED` | pass | $25.92 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code
**FX:** {"rate": 1.08, "rate_date": "2026-06-17", "source": "stub", "amount_usd": 25.92}

---

## M25 · FX unavailable and receipt absent

Input

```json
{"id": "M25", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Office", "amount": "30 GBP", "receipt": false, "memo": "", "approval_code": null}
```

**Expected FLAG** — Request the statement USD amount and a receipt if above $25.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"amount_usd": 39, "receipt": true}
```

Expected after a complete reply: **approve**.

### M25 · Alex Rivera · 2026-06-17 (Wed) · Office · 30.00 GBP

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: could not convert 30.0 GBP to USD; If the corrected USD amount is above $25, attach the receipt.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 30.0 GBP |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| ? | `FX_CONVERSION` | gap | stub has no rate for GBP |
| ? | `RECEIPT_REQUIRED` | gap | USD amount unknown and no receipt |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code
**FX:** {"error": "stub has no rate for GBP"}

**Question to employee:**

To finish reviewing expense M25 (30.00 GBP office at Market Street on 2026-06-17), we need the following (please answer all in one reply):
1. What USD amount appears on your card statement?
2. If the corrected USD amount is above $25, attach the receipt.

**Fields offered** amount_usd, receipt, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"amount_usd": 39, "receipt": true}

### M25 · Alex Rivera · 2026-06-17 (Wed) · Office · 30.00 GBP (= $39.00)

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 30.0 GBP |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| ✓ | `FX_CONVERSION` | pass | employee provided USD amount $39.00 |
| ✓ | `RECEIPT_REQUIRED` | pass | $39.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## M26 · Receipt and code missing

Input

```json
{"id": "M26", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Software", "amount": 92, "receipt": false, "memo": "", "approval_code": null}
```

**Expected FLAG** — Both documentation requirements are independent.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"approval_code": "SW-19", "receipt": true}
```

Expected after a complete reply: **approve**.

### M26 · Alex Rivera · 2026-06-17 (Wed) · Software · 92.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: Receipts are required for any expense over $25.00; Software purchases always need an approval code.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 92.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Software |
| ? | `RECEIPT_REQUIRED` | gap | $92.00 > $25.00 and no receipt |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ? | `SOFTWARE_APPROVAL_CODE` | gap | approval code missing or too short: None |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

**Question to employee:**

To finish reviewing expense M26 ($92.00 software at Market Street on 2026-06-17), we need the following (please answer all in one reply):
1. Receipts are required for any expense over $25.00. Please attach it.
2. Please provide the software approval code.

**Fields offered** receipt, approval_code, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"approval_code": "SW-19", "receipt": true}

### M26 · Alex Rivera · 2026-06-17 (Wed) · Software · 92.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 92.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Software |
| ✓ | `RECEIPT_REQUIRED` | pass | $92.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `SOFTWARE_APPROVAL_CODE` | pass | code 'SW-19' |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## M27 · Known violation and missing receipt

Input

```json
{"id": "M27", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Dinner", "amount": 78, "receipt": false, "memo": "", "approval_code": null}
```

**Expected FLAG** — Completeness has priority. After a receipt arrives the internal dinner exceeds $60.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"receipt": true}
```

Expected after a complete reply: **reject**.

### M27 · Alex Rivera · 2026-06-17 (Wed) · Dinner · 78.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: Receipts are required for any expense over $25.00.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 78.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ? | `RECEIPT_REQUIRED` | gap | $78.00 > $25.00 and no receipt |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✗ | `MEAL_CAP_DINNER` | fail | $78.00 > $60.00; memo blank -> NONE -> treated as internal |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

**Question to employee:**

To finish reviewing expense M27 ($78.00 dinner at Market Street on 2026-06-17), we need one thing: Receipts are required for any expense over $25.00. Please attach it.

**Fields offered** receipt, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"receipt": true}

### M27 · Alex Rivera · 2026-06-17 (Wed) · Dinner · 78.00 USD

**DECISION: REJECT** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Rejected: MEAL_CAP_DINNER ($78.00 > $60.00; memo blank -> NONE -> treated as internal)

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 78.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `RECEIPT_REQUIRED` | pass | $78.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✗ | `MEAL_CAP_DINNER` | fail | $78.00 > $60.00; memo blank -> NONE -> treated as internal |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## M28 · Merchant named like a customer

Input

```json
{"id": "M28", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Juniper Labs", "category": "Entertainment", "amount": 75, "receipt": true, "memo": "Launch event", "approval_code": null}
```

**Expected FLAG** — The payee alone cannot establish who attended.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"attendee_type": "Client", "client_name": "Juniper Labs"}
```

Expected after a complete reply: **approve**.

### M28 · Alex Rivera · 2026-06-17 (Wed) · Entertainment · 75.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: Entertainment is reimbursed only with a client; please name the client company.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 75.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Entertainment |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $75.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ? | `ENTERTAINMENT_NO_CLIENT` | gap | UNCLEAR/low name=None -> not trusted |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Fact sources:** attendee=memo_llm
**LLM:** stub · prompt meals_v1.txt
**LLM reasoning:**

**Question to employee:**

To finish reviewing expense M28 ($75.00 entertainment at Juniper Labs on 2026-06-17), we need one thing: Who attended: coworkers only, an external customer, or a vendor/partner? If a customer, please name the company. (Entertainment is reimbursed only with a client; please name the client company.)

**Fields offered** attendee_type, client_name, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"attendee_type": "Client", "client_name": "Juniper Labs"}

### M28 · Alex Rivera · 2026-06-17 (Wed) · Entertainment · 75.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

**Tags:** approved_on_employee_attestation

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 75.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Entertainment |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $75.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `ENTERTAINMENT_NO_CLIENT` | pass | client confirmed (Juniper Labs) |

**Client check:** client (source: employee_answer) — employee stated client 'Juniper Labs'
**Fact sources:** attendee=employee_answer
**LLM:** stub · prompt meals_v1.txt
**LLM reasoning:**

---

## M29 · Geography / NYC

Input

```json
{"id": "M29", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "NYC Inn", "category": "Hotel", "amount": 300, "receipt": true, "memo": "1 night", "approval_code": null}
```

**Expected APPROVE** — Only the eight named cities and their accepted aliases receive the $350 cap.

**QA** Matched the scripted checks.

### M29 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 300.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 300.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $300.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | New York -> Tier 1 via city_table (table match) |
| ✓ | `HOTEL_CAP_TIER1` | pass | $300.00/night x 1 <= $350.00/night (New York) |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=New York tier=1 nights=1 via city_table (table match)
**Fact sources:** attendee=memo_llm · city=city_table · nights=memo_keyword
**LLM:** stub · prompt hotel_v1.txt
**LLM reasoning:**

---

## M30 · Geography / LA

Input

```json
{"id": "M30", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "LA Inn", "category": "Hotel", "amount": 300, "receipt": true, "memo": "1 night", "approval_code": null}
```

**Expected APPROVE** — Only the eight named cities and their accepted aliases receive the $350 cap.

**QA** Matched the scripted checks.

### M30 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 300.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 300.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $300.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | Los Angeles -> Tier 1 via city_table (table match) |
| ✓ | `HOTEL_CAP_TIER1` | pass | $300.00/night x 1 <= $350.00/night (Los Angeles) |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=Los Angeles tier=1 nights=1 via city_table (table match)
**Fact sources:** attendee=memo_llm · city=city_table · nights=memo_keyword
**LLM:** stub · prompt hotel_v1.txt
**LLM reasoning:**

---

## M31 · Geography / SF

Input

```json
{"id": "M31", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "SF Inn", "category": "Hotel", "amount": 300, "receipt": true, "memo": "1 night", "approval_code": null}
```

**Expected APPROVE** — Only the eight named cities and their accepted aliases receive the $350 cap.

**QA** Matched the scripted checks.

### M31 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 300.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 300.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $300.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | San Francisco -> Tier 1 via city_table (table match) |
| ✓ | `HOTEL_CAP_TIER1` | pass | $300.00/night x 1 <= $350.00/night (San Francisco) |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=San Francisco tier=1 nights=1 via city_table (table match)
**Fact sources:** attendee=memo_llm · city=city_table · nights=memo_keyword
**LLM:** stub · prompt hotel_v1.txt
**LLM reasoning:**

---

## M32 · Geography / Washington DC

Input

```json
{"id": "M32", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Washington DC Inn", "category": "Hotel", "amount": 300, "receipt": true, "memo": "1 night", "approval_code": null}
```

**Expected APPROVE** — Only the eight named cities and their accepted aliases receive the $350 cap.

**QA** Matched the scripted checks.

### M32 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 300.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 300.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $300.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | Washington DC -> Tier 1 via city_table (table match) |
| ✓ | `HOTEL_CAP_TIER1` | pass | $300.00/night x 1 <= $350.00/night (Washington DC) |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=Washington DC tier=1 nights=1 via city_table (table match)
**Fact sources:** attendee=memo_llm · city=city_table · nights=memo_keyword
**LLM:** stub · prompt hotel_v1.txt
**LLM reasoning:**

---

## M33 · Geography / Seattle

Input

```json
{"id": "M33", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Seattle Inn", "category": "Hotel", "amount": 300, "receipt": true, "memo": "1 night", "approval_code": null}
```

**Expected APPROVE** — Only the eight named cities and their accepted aliases receive the $350 cap.

**QA** Matched the scripted checks.

### M33 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 300.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 300.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $300.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | Seattle -> Tier 1 via city_table (table match) |
| ✓ | `HOTEL_CAP_TIER1` | pass | $300.00/night x 1 <= $350.00/night (Seattle) |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=Seattle tier=1 nights=1 via city_table (table match)
**Fact sources:** attendee=memo_llm · city=city_table · nights=memo_keyword
**LLM:** stub · prompt hotel_v1.txt
**LLM reasoning:**

---

## M34 · Geography / Chicago

Input

```json
{"id": "M34", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Chicago Inn", "category": "Hotel", "amount": 300, "receipt": true, "memo": "1 night", "approval_code": null}
```

**Expected APPROVE** — Only the eight named cities and their accepted aliases receive the $350 cap.

**QA** Matched the scripted checks.

### M34 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 300.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 300.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $300.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | Chicago -> Tier 1 via city_table (table match) |
| ✓ | `HOTEL_CAP_TIER1` | pass | $300.00/night x 1 <= $350.00/night (Chicago) |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=Chicago tier=1 nights=1 via city_table (table match)
**Fact sources:** attendee=memo_llm · city=city_table · nights=memo_keyword
**LLM:** stub · prompt hotel_v1.txt
**LLM reasoning:**

---

## M35 · Geography / Boston

Input

```json
{"id": "M35", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Boston Inn", "category": "Hotel", "amount": 300, "receipt": true, "memo": "1 night", "approval_code": null}
```

**Expected APPROVE** — Only the eight named cities and their accepted aliases receive the $350 cap.

**QA** Matched the scripted checks.

### M35 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 300.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 300.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $300.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | Boston -> Tier 1 via city_table (table match) |
| ✓ | `HOTEL_CAP_TIER1` | pass | $300.00/night x 1 <= $350.00/night (Boston) |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=Boston tier=1 nights=1 via city_table (table match)
**Fact sources:** attendee=memo_llm · city=city_table · nights=memo_keyword
**LLM:** stub · prompt hotel_v1.txt
**LLM reasoning:**

---

## M36 · Geography / London

Input

```json
{"id": "M36", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "London Inn", "category": "Hotel", "amount": 300, "receipt": true, "memo": "1 night", "approval_code": null}
```

**Expected APPROVE** — Only the eight named cities and their accepted aliases receive the $350 cap.

**QA** Matched the scripted checks.

### M36 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 300.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 300.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $300.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | London -> Tier 1 via city_table (table match) |
| ✓ | `HOTEL_CAP_TIER1` | pass | $300.00/night x 1 <= $350.00/night (London) |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=London tier=1 nights=1 via city_table (table match)
**Fact sources:** attendee=memo_llm · city=city_table · nights=memo_keyword
**LLM:** stub · prompt hotel_v1.txt
**LLM reasoning:**

---

## M37 · Geography / Oakland

Input

```json
{"id": "M37", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Oakland Inn", "category": "Hotel", "amount": 300, "receipt": true, "memo": "1 night", "approval_code": null}
```

**Expected REJECT** — Only the eight named cities and their accepted aliases receive the $350 cap.

**QA** Matched the scripted checks.

### M37 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 300.00 USD

**DECISION: REJECT** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Rejected: HOTEL_CAP_TIER2 ($300.00 total exceeds 1 nights x $200.00 (Oakland, Tier 2))

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 300.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $300.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | Oakland -> Tier 2 via llm (high) |
| ✗ | `HOTEL_CAP_TIER2` | fail | $300.00 total exceeds 1 nights x $200.00 (Oakland, Tier 2) |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=Oakland tier=2 nights=1 via llm (high)
**Fact sources:** attendee=memo_llm · city=memo_llm · nights=memo_keyword
**LLM:** stub · prompt hotel_v1.txt
**LLM reasoning:**

---

## M38 · Geography / Jersey City

Input

```json
{"id": "M38", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Jersey City Inn", "category": "Hotel", "amount": 300, "receipt": true, "memo": "1 night", "approval_code": null}
```

**Expected REJECT** — Only the eight named cities and their accepted aliases receive the $350 cap.

**QA** Matched the scripted checks.

### M38 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 300.00 USD

**DECISION: REJECT** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Rejected: HOTEL_CAP_TIER2 ($300.00 total exceeds 1 nights x $200.00 (Jersey City, Tier 2))

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 300.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $300.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | Jersey City -> Tier 2 via llm (high) |
| ✗ | `HOTEL_CAP_TIER2` | fail | $300.00 total exceeds 1 nights x $200.00 (Jersey City, Tier 2) |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=Jersey City tier=2 nights=1 via llm (high)
**Fact sources:** attendee=memo_llm · city=memo_llm · nights=memo_keyword
**LLM:** stub · prompt hotel_v1.txt
**LLM reasoning:**

---

## M39 · Geography / Santa Monica

Input

```json
{"id": "M39", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Santa Monica Inn", "category": "Hotel", "amount": 300, "receipt": true, "memo": "1 night", "approval_code": null}
```

**Expected REJECT** — Only the eight named cities and their accepted aliases receive the $350 cap.

**QA** Matched the scripted checks.

### M39 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 300.00 USD

**DECISION: REJECT** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Rejected: HOTEL_CAP_TIER2 ($300.00 total exceeds 1 nights x $200.00 (Santa Monica, Tier 2))

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 300.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $300.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | Santa Monica -> Tier 2 via llm (high) |
| ✗ | `HOTEL_CAP_TIER2` | fail | $300.00 total exceeds 1 nights x $200.00 (Santa Monica, Tier 2) |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=Santa Monica tier=2 nights=1 via llm (high)
**Fact sources:** attendee=memo_llm · city=memo_llm · nights=memo_keyword
**LLM:** stub · prompt hotel_v1.txt
**LLM reasoning:**

---

## M40 · Geography / Arlington VA

Input

```json
{"id": "M40", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Arlington VA Inn", "category": "Hotel", "amount": 300, "receipt": true, "memo": "1 night", "approval_code": null}
```

**Expected REJECT** — Only the eight named cities and their accepted aliases receive the $350 cap.

**QA** Matched the scripted checks.

### M40 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 300.00 USD

**DECISION: REJECT** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Rejected: HOTEL_CAP_TIER2 ($300.00 total exceeds 1 nights x $200.00 (Arlington VA, Tier 2))

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 300.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $300.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | Arlington VA -> Tier 2 via llm (high) |
| ✗ | `HOTEL_CAP_TIER2` | fail | $300.00 total exceeds 1 nights x $200.00 (Arlington VA, Tier 2) |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=Arlington VA tier=2 nights=1 via llm (high)
**Fact sources:** attendee=memo_llm · city=memo_llm · nights=memo_keyword
**LLM:** stub · prompt hotel_v1.txt
**LLM reasoning:**
