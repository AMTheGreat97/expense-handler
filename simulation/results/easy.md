# Easy — expense QA

30 entries, {'approve': 19, 'reject': 7, 'flag': 4}, 0 QA differences.

Synthetic expenses. Real batch and follow-up logic, offline model and FX fixtures, in-memory storage and a recording publisher. Each entry includes the actual question and rule trace.

## E01 · Breakfast at $19.99

Input

```json
{"id": "E01", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Breakfast", "amount": 19.99, "receipt": true, "memo": "", "approval_code": null}
```

**Expected APPROVE** — The weekday internal breakfast cap is $20 inclusive. The receipt is present.

**QA** Matched the scripted checks.

### E01 · Alex Rivera · 2026-06-17 (Wed) · Breakfast · 19.99 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 19.99 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Breakfast |
| – | `RECEIPT_REQUIRED` | n/a | $19.99 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `MEAL_CAP_BREAKFAST` | pass | $19.99 <= $20.00 |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E02 · Breakfast at $20.00

Input

```json
{"id": "E02", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Breakfast", "amount": 20, "receipt": true, "memo": "", "approval_code": null}
```

**Expected APPROVE** — The weekday internal breakfast cap is $20 inclusive. The receipt is present.

**QA** Matched the scripted checks.

### E02 · Alex Rivera · 2026-06-17 (Wed) · Breakfast · 20.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 20.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Breakfast |
| – | `RECEIPT_REQUIRED` | n/a | $20.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `MEAL_CAP_BREAKFAST` | pass | $20.00 <= $20.00 |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E03 · Breakfast at $20.01

Input

```json
{"id": "E03", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Breakfast", "amount": 20.01, "receipt": true, "memo": "", "approval_code": null}
```

**Expected REJECT** — The weekday internal breakfast cap is $20 inclusive. The receipt is present.

**QA** Matched the scripted checks.

### E03 · Alex Rivera · 2026-06-17 (Wed) · Breakfast · 20.01 USD

**DECISION: REJECT** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Rejected: MEAL_CAP_BREAKFAST ($20.01 > $20.00; memo blank -> NONE -> treated as internal)

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 20.01 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Breakfast |
| – | `RECEIPT_REQUIRED` | n/a | $20.01 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✗ | `MEAL_CAP_BREAKFAST` | fail | $20.01 > $20.00; memo blank -> NONE -> treated as internal |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E04 · Lunch at $29.99

Input

```json
{"id": "E04", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Lunch", "amount": 29.99, "receipt": true, "memo": "", "approval_code": null}
```

**Expected APPROVE** — The weekday internal lunch cap is $30 inclusive. The receipt is present.

**QA** Matched the scripted checks.

### E04 · Alex Rivera · 2026-06-17 (Wed) · Lunch · 29.99 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 29.99 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Lunch |
| ✓ | `RECEIPT_REQUIRED` | pass | $29.99 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `MEAL_CAP_LUNCH` | pass | $29.99 <= $30.00 |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E05 · Lunch at $30.00

Input

```json
{"id": "E05", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Lunch", "amount": 30, "receipt": true, "memo": "", "approval_code": null}
```

**Expected APPROVE** — The weekday internal lunch cap is $30 inclusive. The receipt is present.

**QA** Matched the scripted checks.

### E05 · Alex Rivera · 2026-06-17 (Wed) · Lunch · 30.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 30.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Lunch |
| ✓ | `RECEIPT_REQUIRED` | pass | $30.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `MEAL_CAP_LUNCH` | pass | $30.00 <= $30.00 |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E06 · Lunch at $30.01

Input

```json
{"id": "E06", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Lunch", "amount": 30.01, "receipt": true, "memo": "", "approval_code": null}
```

**Expected REJECT** — The weekday internal lunch cap is $30 inclusive. The receipt is present.

**QA** Matched the scripted checks.

### E06 · Alex Rivera · 2026-06-17 (Wed) · Lunch · 30.01 USD

**DECISION: REJECT** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Rejected: MEAL_CAP_LUNCH ($30.01 > $30.00; memo blank -> NONE -> treated as internal)

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 30.01 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Lunch |
| ✓ | `RECEIPT_REQUIRED` | pass | $30.01 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✗ | `MEAL_CAP_LUNCH` | fail | $30.01 > $30.00; memo blank -> NONE -> treated as internal |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E07 · Dinner at $59.99

Input

```json
{"id": "E07", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Dinner", "amount": 59.99, "receipt": true, "memo": "", "approval_code": null}
```

**Expected APPROVE** — The weekday internal dinner cap is $60 inclusive. The receipt is present.

**QA** Matched the scripted checks.

### E07 · Alex Rivera · 2026-06-17 (Wed) · Dinner · 59.99 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 59.99 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `RECEIPT_REQUIRED` | pass | $59.99 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `MEAL_CAP_DINNER` | pass | $59.99 <= $60.00 |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E08 · Dinner at $60.00

Input

```json
{"id": "E08", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Dinner", "amount": 60, "receipt": true, "memo": "", "approval_code": null}
```

**Expected APPROVE** — The weekday internal dinner cap is $60 inclusive. The receipt is present.

**QA** Matched the scripted checks.

### E08 · Alex Rivera · 2026-06-17 (Wed) · Dinner · 60.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 60.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `RECEIPT_REQUIRED` | pass | $60.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `MEAL_CAP_DINNER` | pass | $60.00 <= $60.00 |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E09 · Dinner at $60.01

Input

```json
{"id": "E09", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Dinner", "amount": 60.01, "receipt": true, "memo": "", "approval_code": null}
```

**Expected REJECT** — The weekday internal dinner cap is $60 inclusive. The receipt is present.

**QA** Matched the scripted checks.

### E09 · Alex Rivera · 2026-06-17 (Wed) · Dinner · 60.01 USD

**DECISION: REJECT** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Rejected: MEAL_CAP_DINNER ($60.01 > $60.00; memo blank -> NONE -> treated as internal)

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 60.01 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `RECEIPT_REQUIRED` | pass | $60.01 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✗ | `MEAL_CAP_DINNER` | fail | $60.01 > $60.00; memo blank -> NONE -> treated as internal |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E10 · Receipt boundary $24.99

Input

```json
{"id": "E10", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Office", "amount": 24.99, "receipt": false, "memo": "", "approval_code": null}
```

**Expected APPROVE** — A receipt is required strictly above $25.

**QA** Matched the scripted checks.

### E10 · Alex Rivera · 2026-06-17 (Wed) · Office · 24.99 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 24.99 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| – | `RECEIPT_REQUIRED` | n/a | $24.99 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E11 · Receipt boundary $25

Input

```json
{"id": "E11", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Office", "amount": 25, "receipt": false, "memo": "", "approval_code": null}
```

**Expected APPROVE** — A receipt is required strictly above $25.

**QA** Matched the scripted checks.

### E11 · Alex Rivera · 2026-06-17 (Wed) · Office · 25.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 25.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| – | `RECEIPT_REQUIRED` | n/a | $25.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E12 · Receipt boundary $25.01

Input

```json
{"id": "E12", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Office", "amount": 25.01, "receipt": false, "memo": "", "approval_code": null}
```

**Expected FLAG** — A receipt is required strictly above $25.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"receipt": true}
```

Expected after a complete reply: **approve**.

### E12 · Alex Rivera · 2026-06-17 (Wed) · Office · 25.01 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: Receipts are required for any expense over $25.00.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 25.01 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| ? | `RECEIPT_REQUIRED` | gap | $25.01 > $25.00 and no receipt |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

**Question to employee:**

To finish reviewing expense E12 ($25.01 office at Market Street on 2026-06-17), we need one thing: Receipts are required for any expense over $25.00. Please attach it.

**Fields offered** receipt, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"receipt": true}

### E12 · Alex Rivera · 2026-06-17 (Wed) · Office · 25.01 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 25.01 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| ✓ | `RECEIPT_REQUIRED` | pass | $25.01 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E13 · Saturday Taxi

Input

```json
{"id": "E13", "employee": "Alex Rivera", "date": "2026-06-20", "merchant": "Market Street", "category": "Taxi", "amount": 34, "receipt": true, "memo": "", "approval_code": null}
```

**Expected APPROVE** — Weekend meal restrictions do not apply to this category.

**QA** Matched the scripted checks.

### E13 · Alex Rivera · 2026-06-20 (Sat) · Ground Transport · 34.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 34.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-20 (Saturday) |
| ✓ | `CATEGORY_PRESENT` | pass | Ground Transport |
| ✓ | `RECEIPT_REQUIRED` | pass | $34.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `GROUND_TRANSPORT_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E14 · Saturday Airfare

Input

```json
{"id": "E14", "employee": "Alex Rivera", "date": "2026-06-20", "merchant": "Market Street", "category": "Airfare", "amount": 410, "receipt": true, "memo": "", "approval_code": null}
```

**Expected APPROVE** — Weekend meal restrictions do not apply to this category.

**QA** Matched the scripted checks.

### E14 · Alex Rivera · 2026-06-20 (Sat) · Airfare · 410.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 410.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-20 (Saturday) |
| ✓ | `CATEGORY_PRESENT` | pass | Airfare |
| ✓ | `RECEIPT_REQUIRED` | pass | $410.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `AIRFARE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E15 · Saturday Office

Input

```json
{"id": "E15", "employee": "Alex Rivera", "date": "2026-06-20", "merchant": "Market Street", "category": "Office", "amount": 42, "receipt": true, "memo": "", "approval_code": null}
```

**Expected APPROVE** — Weekend meal restrictions do not apply to this category.

**QA** Matched the scripted checks.

### E15 · Alex Rivera · 2026-06-20 (Sat) · Office · 42.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 42.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-20 (Saturday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| ✓ | `RECEIPT_REQUIRED` | pass | $42.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E16 · Saturday Lunch

Input

```json
{"id": "E16", "employee": "Alex Rivera", "date": "2026-06-20", "merchant": "Market Street", "category": "Lunch", "amount": 18, "receipt": true, "memo": "", "approval_code": null}
```

**Expected REJECT** — Weekend internal meals are ineligible.

**QA** Matched the scripted checks.

### E16 · Alex Rivera · 2026-06-20 (Sat) · Lunch · 18.00 USD

**DECISION: REJECT** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Rejected: WEEKEND_MEAL_INTERNAL (meal on Sat; memo blank -> NONE -> treated as internal)

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-20 (Saturday) |
| ✓ | `CATEGORY_PRESENT` | pass | Lunch |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `MEAL_CAP_LUNCH` | pass | $18.00 <= $30.00 |
| ✗ | `WEEKEND_MEAL_INTERNAL` | fail | meal on Sat; memo blank -> NONE -> treated as internal |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E17 · Saturday Entertainment

Input

```json
{"id": "E17", "employee": "Alex Rivera", "date": "2026-06-20", "merchant": "Market Street", "category": "Entertainment", "amount": 18, "receipt": true, "memo": "", "approval_code": null}
```

**Expected REJECT** — Entertainment needs a client even under $25.

**QA** Matched the scripted checks.

### E17 · Alex Rivera · 2026-06-20 (Sat) · Entertainment · 18.00 USD

**DECISION: REJECT** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Rejected: ENTERTAINMENT_NO_CLIENT (memo blank -> NONE -> treated as internal)

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-20 (Saturday) |
| ✓ | `CATEGORY_PRESENT` | pass | Entertainment |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✗ | `ENTERTAINMENT_NO_CLIENT` | fail | memo blank -> NONE -> treated as internal |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E18 · Software code null

Input

```json
{"id": "E18", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Software", "amount": 18, "receipt": true, "memo": "", "approval_code": null}
```

**Expected FLAG** — Software requires a structured code of at least two trimmed characters.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"approval_code": "SW-19"}
```

Expected after a complete reply: **approve**.

### E18 · Alex Rivera · 2026-06-17 (Wed) · Software · 18.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: Software purchases always need an approval code.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Software |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ? | `SOFTWARE_APPROVAL_CODE` | gap | approval code missing or too short: None |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

**Question to employee:**

To finish reviewing expense E18 ($18.00 software at Market Street on 2026-06-17), we need one thing: Please provide the software approval code.

**Fields offered** approval_code, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"approval_code": "SW-19"}

### E18 · Alex Rivera · 2026-06-17 (Wed) · Software · 18.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Software |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `SOFTWARE_APPROVAL_CODE` | pass | code 'SW-19' |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E19 · Software code " "

Input

```json
{"id": "E19", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Software", "amount": 18, "receipt": true, "memo": "", "approval_code": " "}
```

**Expected FLAG** — Software requires a structured code of at least two trimmed characters.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"approval_code": "SW-19"}
```

Expected after a complete reply: **approve**.

### E19 · Alex Rivera · 2026-06-17 (Wed) · Software · 18.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: Software purchases always need an approval code.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Software |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ? | `SOFTWARE_APPROVAL_CODE` | gap | approval code missing or too short: ' ' |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

**Question to employee:**

To finish reviewing expense E19 ($18.00 software at Market Street on 2026-06-17), we need one thing: Please provide the software approval code.

**Fields offered** approval_code, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"approval_code": "SW-19"}

### E19 · Alex Rivera · 2026-06-17 (Wed) · Software · 18.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Software |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `SOFTWARE_APPROVAL_CODE` | pass | code 'SW-19' |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E20 · Software code "X"

Input

```json
{"id": "E20", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Software", "amount": 18, "receipt": true, "memo": "", "approval_code": "X"}
```

**Expected FLAG** — Software requires a structured code of at least two trimmed characters.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"approval_code": "SW-19"}
```

Expected after a complete reply: **approve**.

### E20 · Alex Rivera · 2026-06-17 (Wed) · Software · 18.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: Software purchases always need an approval code.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Software |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ? | `SOFTWARE_APPROVAL_CODE` | gap | approval code missing or too short: 'X' |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

**Question to employee:**

To finish reviewing expense E20 ($18.00 software at Market Street on 2026-06-17), we need one thing: Please provide the software approval code.

**Fields offered** approval_code, employee_note

**Portal reply validation** Accepted the corresponding form inputs.

**Employee actually returned** {"approval_code": "SW-19"}

### E20 · Alex Rivera · 2026-06-17 (Wed) · Software · 18.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Software |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `SOFTWARE_APPROVAL_CODE` | pass | code 'SW-19' |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E21 · Software code " AB "

Input

```json
{"id": "E21", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Software", "amount": 18, "receipt": true, "memo": "", "approval_code": " AB "}
```

**Expected APPROVE** — Software requires a structured code of at least two trimmed characters.

**QA** Matched the scripted checks.

### E21 · Alex Rivera · 2026-06-17 (Wed) · Software · 18.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Software |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `SOFTWARE_APPROVAL_CODE` | pass | code 'AB' |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E22 · Boston one night $349.99

Input

```json
{"id": "E22", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Inn in Boston", "category": "Hotel", "amount": 349.99, "receipt": true, "memo": "1 night", "approval_code": null}
```

**Expected APPROVE** — One night in Boston has an inclusive $350 cap.

**QA** Matched the scripted checks.

### E22 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 349.99 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 349.99 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $349.99 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | Boston -> Tier 1 via city_table (table match) |
| ✓ | `HOTEL_CAP_TIER1` | pass | $349.99/night x 1 <= $350.00/night (Boston) |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=Boston tier=1 nights=1 via city_table (table match)
**Fact sources:** attendee=memo_llm · city=city_table · nights=memo_keyword
**LLM:** stub · prompt hotel_v1.txt
**LLM reasoning:**

---

## E23 · Boston one night $350

Input

```json
{"id": "E23", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Inn in Boston", "category": "Hotel", "amount": 350, "receipt": true, "memo": "1 night", "approval_code": null}
```

**Expected APPROVE** — One night in Boston has an inclusive $350 cap.

**QA** Matched the scripted checks.

### E23 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 350.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 350.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $350.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | Boston -> Tier 1 via city_table (table match) |
| ✓ | `HOTEL_CAP_TIER1` | pass | $350.00/night x 1 <= $350.00/night (Boston) |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=Boston tier=1 nights=1 via city_table (table match)
**Fact sources:** attendee=memo_llm · city=city_table · nights=memo_keyword
**LLM:** stub · prompt hotel_v1.txt
**LLM reasoning:**

---

## E24 · Boston one night $350.01

Input

```json
{"id": "E24", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Inn in Boston", "category": "Hotel", "amount": 350.01, "receipt": true, "memo": "1 night", "approval_code": null}
```

**Expected REJECT** — One night in Boston has an inclusive $350 cap.

**QA** Matched the scripted checks.

### E24 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 350.01 USD

**DECISION: REJECT** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Rejected: HOTEL_CAP_TIER1 ($350.01 total exceeds 1 nights x $350.00 (Boston, Tier 1))

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 350.01 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $350.01 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | Boston -> Tier 1 via city_table (table match) |
| ✗ | `HOTEL_CAP_TIER1` | fail | $350.01 total exceeds 1 nights x $350.00 (Boston, Tier 1) |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=Boston tier=1 nights=1 via city_table (table match)
**Fact sources:** attendee=memo_llm · city=city_table · nights=memo_keyword
**LLM:** stub · prompt hotel_v1.txt
**LLM reasoning:**

---

## E25 · Columbus one night $199.99

Input

```json
{"id": "E25", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Inn in Columbus", "category": "Hotel", "amount": 199.99, "receipt": true, "memo": "1 night", "approval_code": null}
```

**Expected APPROVE** — One night in Columbus has an inclusive $200 cap.

**QA** Matched the scripted checks.

### E25 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 199.99 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 199.99 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $199.99 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | Columbus -> Tier 2 via llm (high) |
| ✓ | `HOTEL_CAP_TIER2` | pass | $199.99/night x 1 <= $200.00/night (Columbus) |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=Columbus tier=2 nights=1 via llm (high)
**Fact sources:** attendee=memo_llm · city=memo_llm · nights=memo_keyword
**LLM:** stub · prompt hotel_v1.txt
**LLM reasoning:**

---

## E26 · Columbus one night $200

Input

```json
{"id": "E26", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Inn in Columbus", "category": "Hotel", "amount": 200, "receipt": true, "memo": "1 night", "approval_code": null}
```

**Expected APPROVE** — One night in Columbus has an inclusive $200 cap.

**QA** Matched the scripted checks.

### E26 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 200.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 200.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $200.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | Columbus -> Tier 2 via llm (high) |
| ✓ | `HOTEL_CAP_TIER2` | pass | $200.00/night x 1 <= $200.00/night (Columbus) |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=Columbus tier=2 nights=1 via llm (high)
**Fact sources:** attendee=memo_llm · city=memo_llm · nights=memo_keyword
**LLM:** stub · prompt hotel_v1.txt
**LLM reasoning:**

---

## E27 · Columbus one night $200.01

Input

```json
{"id": "E27", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Inn in Columbus", "category": "Hotel", "amount": 200.01, "receipt": true, "memo": "1 night", "approval_code": null}
```

**Expected REJECT** — One night in Columbus has an inclusive $200 cap.

**QA** Matched the scripted checks.

### E27 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 200.01 USD

**DECISION: REJECT** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Rejected: HOTEL_CAP_TIER2 ($200.01 total exceeds 1 nights x $200.00 (Columbus, Tier 2))

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 200.01 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt:  |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $200.01 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | Columbus -> Tier 2 via llm (high) |
| ✗ | `HOTEL_CAP_TIER2` | fail | $200.01 total exceeds 1 nights x $200.00 (Columbus, Tier 2) |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=Columbus tier=2 nights=1 via llm (high)
**Fact sources:** attendee=memo_llm · city=memo_llm · nights=memo_keyword
**LLM:** stub · prompt hotel_v1.txt
**LLM reasoning:**

---

## E28 · Normalize $28.00 and  lunch

Input

```json
{"id": "E28", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": " lunch ", "amount": "$28.00", "receipt": true, "memo": "", "approval_code": null}
```

**Expected APPROVE** — A supported amount and category alias resolve to an eligible weekday expense.

**QA** Matched the scripted checks.

### E28 · Alex Rivera · 2026-06-17 (Wed) · Lunch · 28.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 28.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Lunch |
| ✓ | `RECEIPT_REQUIRED` | pass | $28.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `MEAL_CAP_LUNCH` | pass | $28.00 <= $30.00 |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E29 · Normalize 1,120.00 and Airfare

Input

```json
{"id": "E29", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Airfare", "amount": "1,120.00", "receipt": true, "memo": "", "approval_code": null}
```

**Expected APPROVE** — A supported amount and category alias resolve to an eligible weekday expense.

**QA** Matched the scripted checks.

### E29 · Alex Rivera · 2026-06-17 (Wed) · Airfare · 1,120.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 1120.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Airfare |
| ✓ | `RECEIPT_REQUIRED` | pass | $1,120.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `AIRFARE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## E30 · Normalize 25 USD and office supplies

Input

```json
{"id": "E30", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "office supplies", "amount": "25 USD", "receipt": true, "memo": "", "approval_code": null}
```

**Expected APPROVE** — A supported amount and category alias resolve to an eligible weekday expense.

**QA** Matched the scripted checks.

### E30 · Alex Rivera · 2026-06-17 (Wed) · Office · 25.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 25.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Office |
| – | `RECEIPT_REQUIRED` | n/a | $25.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `OFFICE_DEFAULT` | pass | no category cap; global rules only |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code
