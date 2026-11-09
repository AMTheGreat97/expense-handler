# Live model language checks

Configured model with offline FX and recording publisher. Any fixture facts in the answer key were ignored.

## H01 · Uncertain hotel count / two to three nights

Input

```json
{"id": "H01", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Columbus Inn", "category": "Hotel", "amount": 520, "receipt": true, "memo": "two to three nights", "approval_code": null}
```

**Expected FLAG** — At two nights the average is $260. At three it is $173.33. Ask for the exact billed count.

**QA** Expected final approve, got flag.

Complete employee answer available in this scenario

```json
{"nights": 3}
```

Expected after a complete reply: **approve**.

### H01 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 520.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: Hotel limits depend on the city ($350/night in Tier-1 cities, $200/night elsewhere); Please confirm the exact positive whole number of nights on this charge.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 520.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt: No attendees mentioned; city inferred from merchant name 'Columbus Inn' but not explicit; memo states 'two to three nights' which is a range, not a specific integer. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $520.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ? | `HOTEL_CITY_KNOWN` | gap | hotel city could not be determined |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=None tier=None nights=None via None
**Fact sources:** attendee=memo_llm
**LLM:** deepseek/deepseek-v4-flash · prompt hotel_v1.txt
**LLM reasoning:** No attendees mentioned; city inferred from merchant name 'Columbus Inn' but not explicit; memo states 'two to three nights' which is a range, not a specific integer.

**Notes:**
- nights ambiguous in memo ('two to three nights')

**Question to employee:**

To finish reviewing expense H01 ($520.00 hotel at Columbus Inn on 2026-06-17), we need the following (please answer all in one reply):
1. Which city was the hotel in?
2. Exactly how many nights does this charge cover?

**Fields offered** city, nights, employee_note

**Employee actually returned** {"nights": 3}

### H01 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 520.00 USD

**DECISION: FLAG** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: Hotel limits depend on the city ($350/night in Tier-1 cities, $200/night elsewhere).

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 520.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt: No attendees mentioned; city inferred from merchant name 'Columbus Inn' but location is ambiguous; memo states a range of nights, not a specific integer. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $520.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ? | `HOTEL_CITY_KNOWN` | gap | hotel city could not be determined |
| ? | `ONE_EMPLOYEE_CONTACT` | gap | Unresolved after one reply. Assigned to Finance. |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=None tier=None nights=3 via None
**Fact sources:** attendee=memo_llm · nights=employee_answer
**LLM:** deepseek/deepseek-v4-flash · prompt hotel_v1.txt
**LLM reasoning:** No attendees mentioned; city inferred from merchant name 'Columbus Inn' but location is ambiguous; memo states a range of nights, not a specific integer.

**Question to finance:**

Finance review required after the employee's reply. Needs information: Hotel limits depend on the city ($350/night in Tier-1 cities, $200/night elsewhere).

**Fields offered**

---

## H11 · Unlocated $520 hotel / confirmed 2 nights

Input

```json
{"id": "H11", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Riverside Inn", "category": "Hotel", "amount": 520, "receipt": false, "memo": "", "approval_code": null}
```

**Expected FLAG** — Need the receipt, city and exact nights in one contact. The answer places the hotel in Tier 2.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"receipt": true, "city": "Columbus", "nights": 2}
```

Expected after a complete reply: **reject**.

### H11 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 520.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: Receipts are required for any expense over $25.00; Hotel limits depend on the city ($350/night in Tier-1 cities, $200/night elsewhere); Please confirm the exact positive whole number of nights on this charge.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 520.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt: No memo or employee answer provided; merchant name 'Riverside Inn' does not specify a city or any other details. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ? | `RECEIPT_REQUIRED` | gap | $520.00 > $25.00 and no receipt |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ? | `HOTEL_CITY_KNOWN` | gap | hotel city could not be determined |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Hotel:** city=None tier=None nights=None via None
**Fact sources:** attendee=code
**LLM:** deepseek/deepseek-v4-flash · prompt hotel_v1.txt
**LLM reasoning:** No memo or employee answer provided; merchant name 'Riverside Inn' does not specify a city or any other details.

**Question to employee:**

To finish reviewing expense H11 ($520.00 hotel at Riverside Inn on 2026-06-17), we need the following (please answer all in one reply):
1. Receipts are required for any expense over $25.00. Please attach it.
2. Which city was the hotel in?
3. Exactly how many nights does this charge cover?

**Fields offered** receipt, city, nights, employee_note

**Employee actually returned** {"receipt": true, "city": "Columbus", "nights": 2}

### H11 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 520.00 USD

**DECISION: REJECT** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Rejected: HOTEL_CAP_TIER2 ($520.00 total exceeds 2 nights x $200.00 (Columbus, Tier 2))

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 520.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt: The memo and employee answer are empty, and the merchant name 'Riverside Inn' does not specify a city, attendees, or duration. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $520.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | Columbus -> Tier 2 via employee_answer |
| ✗ | `HOTEL_CAP_TIER2` | fail | $520.00 total exceeds 2 nights x $200.00 (Columbus, Tier 2) |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Hotel:** city=Columbus tier=2 nights=2 via employee_answer
**Fact sources:** attendee=code · city=employee_answer · nights=employee_answer
**LLM:** deepseek/deepseek-v4-flash · prompt hotel_v1.txt
**LLM reasoning:** The memo and employee answer are empty, and the merchant name 'Riverside Inn' does not specify a city, attendees, or duration.

---

## H13 · Uneven nightly charges

Input

```json
{"id": "H13", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Columbus Inn", "category": "Hotel", "amount": 400, "receipt": true, "memo": "2 nights. First $150, second $250.", "approval_code": null}
```

**Expected APPROVE** — Presentation assumption A01: average $200 equals the cap. Confirm the averaging rule with Priya.

**QA** Expected approve, got flag.

Complete employee answer available in this scenario

```json
{"city": "Columbus"}
```

Expected after a complete reply: **approve**.

### H13 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 400.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: Hotel limits depend on the city ($350/night in Tier-1 cities, $200/night elsewhere).

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 400.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt: Merchant name 'Columbus Inn' suggests the city is Columbus, but the location is not explicit in the memo. Memo states '2 nights'. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $400.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ? | `HOTEL_CITY_KNOWN` | gap | hotel city could not be determined |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=None tier=None nights=2 via None
**Fact sources:** attendee=memo_llm · nights=memo_keyword
**LLM:** deepseek/deepseek-v4-flash · prompt hotel_v1.txt
**LLM reasoning:** Merchant name 'Columbus Inn' suggests the city is Columbus, but the location is not explicit in the memo. Memo states '2 nights'.

**Question to employee:**

To finish reviewing expense H13 ($400.00 hotel at Columbus Inn on 2026-06-17), we need one thing: Which city was the hotel in?

**Fields offered** city, employee_note

**Employee actually returned** {"city": "Columbus"}

### H13 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 400.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 400.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt: The merchant name 'Columbus Inn' suggests a city but does not explicitly confirm the hotel's location, so city confidence is medium. The memo states '2 nights'. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $400.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | Columbus -> Tier 2 via employee_answer |
| ✓ | `HOTEL_CAP_TIER2` | pass | $200.00/night x 2 <= $200.00/night (Columbus) |

**Client check:** unknown (source: memo_llm) — UNCLEAR/low name=None -> not trusted
**Hotel:** city=Columbus tier=2 nights=2 via employee_answer
**Fact sources:** attendee=memo_llm · city=employee_answer · nights=memo_keyword
**LLM:** deepseek/deepseek-v4-flash · prompt hotel_v1.txt
**LLM reasoning:** The merchant name 'Columbus Inn' suggests a city but does not explicitly confirm the hotel's location, so city confidence is medium. The memo states '2 nights'.

---

## H16 · Unclear relationship / Drinks with internal clients / reject

Input

```json
{"id": "H16", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Dinner", "amount": 88, "receipt": true, "memo": "Drinks with internal clients", "approval_code": null}
```

**Expected FLAG** — Internal client can describe colleagues. Even a confident model label cannot resolve this relationship.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"attendee_type": "Internal only (our employees)", "alcohol_declared": true}
```

Expected after a complete reply: **reject**.

### H16 · Alex Rivera · 2026-06-17 (Wed) · Dinner · 88.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: The wording could mean coworkers or an external customer. If alcohol was included, confirm who attended; The memo says drinks. Did this expense include alcohol?.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 88.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt: "internal clients" is ambiguous per instructions and no later answer resolves who attended; "Drinks" indicates alcohol. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $88.00 > $25.00 and receipt attached |
| ? | `ATTESTATION_CONFLICT_ALCOHOL` | gap | The memo says drinks |
| ? | `MEAL_CAP_DINNER` | gap | $88.00 > $60.00, client not confirmed |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |
| ? | `ATTESTATION_CONFLICT_CLIENT` | gap | The wording could mean coworkers or an external customer |

**Client check:** unknown (source: memo_llm) — The wording could mean coworkers or an external customer
**Alcohol:** mentioned (via memo_llm)
**Fact sources:** attendee=memo_llm · alcohol=memo_llm
**LLM:** deepseek/deepseek-v4-flash · prompt meals_v1.txt
**LLM reasoning:** "internal clients" is ambiguous per instructions and no later answer resolves who attended; "Drinks" indicates alcohol.

**Question to employee:**

To finish reviewing expense H16 ($88.00 dinner at Market Street on 2026-06-17), we need the following (please answer all in one reply):
1. Who attended: coworkers only, an external customer, or a vendor/partner? If a customer, please name the company. (The wording could mean coworkers or an external customer. If alcohol was included, confirm who attended.)
2. The memo says drinks. Did this expense include alcohol?

**Fields offered** attendee_type, client_name, alcohol_declared, employee_note

**Employee actually returned** {"attendee_type": "Internal only (our employees)", "alcohol_declared": true}

### H16 · Alex Rivera · 2026-06-17 (Wed) · Dinner · 88.00 USD

**DECISION: REJECT** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Rejected: MEAL_CAP_DINNER ($88.00 > $60.00; employee stated internal (not a client)); ALCOHOL_INTERNAL (alcohol mentioned; employee stated internal (not a client))

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 88.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt: The memo says 'internal clients' which is ambiguous per instructions; treat as UNCLEAR. 'Drinks' indicates alcohol. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $88.00 > $25.00 and receipt attached |
| ✗ | `MEAL_CAP_DINNER` | fail | $88.00 > $60.00; employee stated internal (not a client) |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |
| ✗ | `ALCOHOL_INTERNAL` | fail | alcohol mentioned; employee stated internal (not a client) |

**Client check:** internal (source: employee_answer) — employee stated internal (not a client)
**Alcohol:** mentioned (via employee_answer)
**Fact sources:** attendee=employee_answer · alcohol=employee_answer
**LLM:** deepseek/deepseek-v4-flash · prompt meals_v1.txt
**LLM reasoning:** The memo says 'internal clients' which is ambiguous per instructions; treat as UNCLEAR. 'Drinks' indicates alcohol.

---

## H17 · Unclear relationship / Drinks with internal clients / approve

Input

```json
{"id": "H17", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Dinner", "amount": 88, "receipt": true, "memo": "Drinks with internal clients", "approval_code": null}
```

**Expected FLAG** — Internal client can describe colleagues. Even a confident model label cannot resolve this relationship.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"attendee_type": "Client", "client_name": "Juniper Labs", "alcohol_declared": true}
```

Expected after a complete reply: **approve**.

### H17 · Alex Rivera · 2026-06-17 (Wed) · Dinner · 88.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: The wording could mean coworkers or an external customer. If alcohol was included, confirm who attended; The memo says drinks. Did this expense include alcohol?.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 88.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt: The memo says 'internal clients' which is contradictory and unclear; it could mean internal employees or external clients. No specific client name is given, so attendee_type is UNCLEAR with low confidence. 'Drinks' indicates alcohol. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $88.00 > $25.00 and receipt attached |
| ? | `ATTESTATION_CONFLICT_ALCOHOL` | gap | The memo says drinks |
| ? | `MEAL_CAP_DINNER` | gap | $88.00 > $60.00, client not confirmed |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |
| ? | `ATTESTATION_CONFLICT_CLIENT` | gap | The wording could mean coworkers or an external customer |

**Client check:** unknown (source: memo_llm) — The wording could mean coworkers or an external customer
**Fact sources:** attendee=memo_llm
**LLM:** deepseek/deepseek-v4-flash · prompt meals_v1.txt
**LLM reasoning:** The memo says 'internal clients' which is contradictory and unclear; it could mean internal employees or external clients. No specific client name is given, so attendee_type is UNCLEAR with low confidence. 'Drinks' indicates alcohol.

**Question to employee:**

To finish reviewing expense H17 ($88.00 dinner at Market Street on 2026-06-17), we need the following (please answer all in one reply):
1. Who attended: coworkers only, an external customer, or a vendor/partner? If a customer, please name the company. (The wording could mean coworkers or an external customer. If alcohol was included, confirm who attended.)
2. The memo says drinks. Did this expense include alcohol?

**Fields offered** attendee_type, client_name, alcohol_declared, employee_note

**Employee actually returned** {"attendee_type": "Client", "client_name": "Juniper Labs", "alcohol_declared": true}

### H17 · Alex Rivera · 2026-06-17 (Wed) · Dinner · 88.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

**Tags:** approved_on_employee_attestation

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 88.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt: The memo says 'internal clients' which is ambiguous; it could mean internal employees or external clients, so attendee type is unclear. 'Drinks' indicates alcohol. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $88.00 > $25.00 and receipt attached |
| ✓ | `ALCOHOL_INTERNAL` | pass | alcohol mentioned, client confirmed (Juniper Labs) |
| ✓ | `MEAL_CAP_DINNER` | pass | $88.00 > $60.00 but client confirmed (Juniper Labs) -> cap waived |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** client (source: employee_answer) — employee stated client 'Juniper Labs'
**Alcohol:** mentioned (via employee_answer)
**Fact sources:** attendee=employee_answer · alcohol=employee_answer
**LLM:** deepseek/deepseek-v4-flash · prompt meals_v1.txt
**LLM reasoning:** The memo says 'internal clients' which is ambiguous; it could mean internal employees or external clients, so attendee type is unclear. 'Drinks' indicates alcohol.

---

## H20 · Literal language / Soft drinks with our team

Input

```json
{"id": "H20", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Lunch", "amount": 18, "receipt": true, "memo": "Soft drinks with our team", "approval_code": null}
```

**Expected APPROVE** — The wording explicitly describes a nonalcoholic purchase and the internal meal is within its cap.

**QA** Matched the scripted checks.

### H20 · Alex Rivera · 2026-06-17 (Wed) · Lunch · 18.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Lunch |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt: The memo says 'our team', which clearly indicates only internal employees attended, so attendee_type is INTERNAL with high confidence. No alcohol is mentioned; 'Soft drinks' explicitly indicates no alcohol. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `MEAL_CAP_LUNCH` | pass | $18.00 <= $30.00 |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** internal (source: memo_llm) — INTERNAL/high (evidence: 'our team')
**Fact sources:** attendee=memo_llm
**LLM:** deepseek/deepseek-v4-flash · prompt meals_v1.txt
**LLM reasoning:** The memo says 'our team', which clearly indicates only internal employees attended, so attendee_type is INTERNAL with high confidence. No alcohol is mentioned; 'Soft drinks' explicitly indicates no alcohol.

---

## H22 · Literal language / Non-alcoholic beer with our team

Input

```json
{"id": "H22", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Lunch", "amount": 18, "receipt": true, "memo": "Non-alcoholic beer with our team", "approval_code": null}
```

**Expected APPROVE** — The wording explicitly describes a nonalcoholic purchase and the internal meal is within its cap.

**QA** Matched the scripted checks.

### H22 · Alex Rivera · 2026-06-17 (Wed) · Lunch · 18.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Lunch |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt: The memo explicitly says 'our team', indicating internal attendees only. Non-alcoholic beer is not alcohol, so alcohol_mentioned is false. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `MEAL_CAP_LUNCH` | pass | $18.00 <= $30.00 |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** internal (source: memo_llm) — INTERNAL/high (evidence: 'our team')
**Fact sources:** attendee=memo_llm
**LLM:** deepseek/deepseek-v4-flash · prompt meals_v1.txt
**LLM reasoning:** The memo explicitly says 'our team', indicating internal attendees only. Non-alcoholic beer is not alcohol, so alcohol_mentioned is false.

---

## H23 · Generic drinks with coworkers

Input

```json
{"id": "H23", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Lunch", "amount": 18, "receipt": true, "memo": "Drinks with our team", "approval_code": null}
```

**Expected FLAG** — Beverages could be alcoholic or nonalcoholic. Ask only about alcohol because attendees are known.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"alcohol_declared": false}
```

Expected after a complete reply: **approve**.

### H23 · Alex Rivera · 2026-06-17 (Wed) · Lunch · 18.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: The memo says drinks. Did this expense include alcohol?.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Lunch |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt: The memo states 'Drinks with our team', clearly indicating only internal employees attended. 'Drinks' is generic and does not establish alcohol per the rules. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| ? | `ATTESTATION_CONFLICT_ALCOHOL` | gap | The memo says drinks |
| ✓ | `MEAL_CAP_LUNCH` | pass | $18.00 <= $30.00 |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** internal (source: memo_llm) — INTERNAL/high (evidence: '"our team"')
**Fact sources:** attendee=memo_llm
**LLM:** deepseek/deepseek-v4-flash · prompt meals_v1.txt
**LLM reasoning:** The memo states 'Drinks with our team', clearly indicating only internal employees attended. 'Drinks' is generic and does not establish alcohol per the rules.

**Question to employee:**

To finish reviewing expense H23 ($18.00 lunch at Market Street on 2026-06-17), we need one thing: The memo says drinks. Did this expense include alcohol?

**Fields offered** alcohol_declared, employee_note

**Employee actually returned** {"alcohol_declared": false}

### H23 · Alex Rivera · 2026-06-17 (Wed) · Lunch · 18.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Lunch |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt: The memo explicitly says 'our team', indicating internal employees attended. 'Drinks' is generic and does not by itself establish alcohol. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `MEAL_CAP_LUNCH` | pass | $18.00 <= $30.00 |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** internal (source: memo_llm) — INTERNAL/high (evidence: 'Drinks with our team')
**Fact sources:** attendee=memo_llm · alcohol=employee_answer
**LLM:** deepseek/deepseek-v4-flash · prompt meals_v1.txt
**LLM reasoning:** The memo explicitly says 'our team', indicating internal employees attended. 'Drinks' is generic and does not by itself establish alcohol.

---

## H24 · Soft drinks plus real wine

Input

```json
{"id": "H24", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Lunch", "amount": 18, "receipt": true, "memo": "Soft drinks and wine with our team", "approval_code": null}
```

**Expected REJECT** — The soft drinks do not cancel the explicit wine.

**QA** Matched the scripted checks.

### H24 · Alex Rivera · 2026-06-17 (Wed) · Lunch · 18.00 USD

**DECISION: REJECT** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Rejected: ALCOHOL_INTERNAL (alcohol mentioned; INTERNAL/high (evidence: 'our team'))

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 18.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Lunch |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt: The memo says 'our team', indicating only internal employees attended, so attendee_type is INTERNAL with high confidence. Wine is mentioned, so alcohol_mentioned is true. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| – | `RECEIPT_REQUIRED` | n/a | $18.00 <= $25.00 |
| ✓ | `MEAL_CAP_LUNCH` | pass | $18.00 <= $30.00 |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |
| ✗ | `ALCOHOL_INTERNAL` | fail | alcohol mentioned; INTERNAL/high (evidence: 'our team') |

**Client check:** internal (source: memo_llm) — INTERNAL/high (evidence: 'our team')
**Alcohol:** mentioned (via memo_keyword)
**Fact sources:** attendee=memo_llm · alcohol=memo_keyword
**LLM:** deepseek/deepseek-v4-flash · prompt meals_v1.txt
**LLM reasoning:** The memo says 'our team', indicating only internal employees attended, so attendee_type is INTERNAL with high confidence. Wine is mentioned, so alcohol_mentioned is true.

---

## H25 · Uncategorized charge becomes Hotel

Input

```json
{"id": "H25", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "", "amount": 480, "receipt": false, "memo": "", "approval_code": null}
```

**Expected FLAG** — Ask for the category, receipt and the applicable conditional details in one message.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"category": "Hotel", "city": "Columbus", "nights": 3, "receipt": true}
```

Expected after a complete reply: **approve**.

### H25 · Alex Rivera · 2026-06-17 (Wed) · no category · 480.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: category is missing or not recognised; Receipts are required for any expense over $25.00.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 480.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ? | `CATEGORY_PRESENT` | gap | category is blank |
| ✓ | `LLM_EXTRACTION` | pass | uncategorized_v1.txt: No memo or employee answer provided, and merchant name 'Market Street' is too generic to determine category or attendees. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ? | `RECEIPT_REQUIRED` | gap | $480.00 > $25.00 and no receipt |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code
**LLM:** deepseek/deepseek-v4-flash · prompt uncategorized_v1.txt
**LLM reasoning:** No memo or employee answer provided, and merchant name 'Market Street' is too generic to determine category or attendees.

**Question to employee:**

To finish reviewing expense H25 ($480.00 expense at Market Street on 2026-06-17), we need the following (please answer all in one reply):
1. What category is this expense (e.g. Lunch, Dinner, Office, Hotel, Software)? If it was a meal or entertainment, tell us whether it was internal or with a client, and name the client company.
2. If Software, include the approval code.
3. If Hotel, include the city of the stay.
4. If Hotel, include the exact billed nights if the total exceeds the city's nightly cap.
5. Receipts are required for any expense over $25.00. Please attach it.

**Fields offered** category, attendee_type, client_name, approval_code, city, nights, receipt, employee_note

**Employee actually returned** {"category": "Hotel", "city": "Columbus", "nights": 3, "receipt": true}

### H25 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 480.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 480.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt: No memo or employee answer; merchant 'Market Street' provides no city or night count. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $480.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | Columbus -> Tier 2 via employee_answer |
| ✓ | `HOTEL_CAP_TIER2` | pass | $160.00/night x 3 <= $200.00/night (Columbus) |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Hotel:** city=Columbus tier=2 nights=3 via employee_answer
**Fact sources:** attendee=code · city=employee_answer · nights=employee_answer
**LLM:** deepseek/deepseek-v4-flash · prompt hotel_v1.txt
**LLM reasoning:** No memo or employee answer; merchant 'Market Street' provides no city or night count.

---

## H26 · Uncategorized charge becomes Software

Input

```json
{"id": "H26", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "", "amount": 480, "receipt": false, "memo": "", "approval_code": null}
```

**Expected FLAG** — Ask for the category, receipt and the applicable conditional details in one message.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"category": "Software", "approval_code": "SW-19", "receipt": true}
```

Expected after a complete reply: **approve**.

### H26 · Alex Rivera · 2026-06-17 (Wed) · no category · 480.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: category is missing or not recognised; Receipts are required for any expense over $25.00.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 480.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ? | `CATEGORY_PRESENT` | gap | category is blank |
| ✓ | `LLM_EXTRACTION` | pass | uncategorized_v1.txt: No memo or employee answer is provided, so attendee context and any alcohol mention cannot be determined. The merchant name 'Market Street' alone is insufficient to suggest a confident expense category. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ? | `RECEIPT_REQUIRED` | gap | $480.00 > $25.00 and no receipt |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code
**LLM:** deepseek/deepseek-v4-flash · prompt uncategorized_v1.txt
**LLM reasoning:** No memo or employee answer is provided, so attendee context and any alcohol mention cannot be determined. The merchant name 'Market Street' alone is insufficient to suggest a confident expense category.

**Question to employee:**

To finish reviewing expense H26 ($480.00 expense at Market Street on 2026-06-17), we need the following (please answer all in one reply):
1. What category is this expense (e.g. Lunch, Dinner, Office, Hotel, Software)? If it was a meal or entertainment, tell us whether it was internal or with a client, and name the client company.
2. If Software, include the approval code.
3. If Hotel, include the city of the stay.
4. If Hotel, include the exact billed nights if the total exceeds the city's nightly cap.
5. Receipts are required for any expense over $25.00. Please attach it.

**Fields offered** category, attendee_type, client_name, approval_code, city, nights, receipt, employee_note

**Employee actually returned** {"category": "Software", "approval_code": "SW-19", "receipt": true}

### H26 · Alex Rivera · 2026-06-17 (Wed) · Software · 480.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 480.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Software |
| ✓ | `RECEIPT_REQUIRED` | pass | $480.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `SOFTWARE_APPROVAL_CODE` | pass | code 'SW-19' |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Fact sources:** attendee=code

---

## H35 · Hotel amount and city both missing

Input

```json
{"id": "H35", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Inn", "category": "Hotel", "amount": "unknown", "receipt": false, "memo": "", "approval_code": null}
```

**Expected FLAG** — The corrected amount can exceed either nightly cap. Collect all conditional facts together.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"amount_corrected": 520, "city": "Columbus", "nights": 2, "receipt": true}
```

Expected after a complete reply: **reject**.

### H35 · Alex Rivera · 2026-06-17 (Wed) · Hotel · amount ?

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: amount could not be read: 'unknown'; If the corrected USD amount is above $25, attach the receipt; Hotel limits depend on the city ($350/night in Tier-1 cities, $200/night elsewhere); Please confirm the exact positive whole number of nights on this charge.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ? | `AMOUNT_VALID` | gap | amount could not be read: 'unknown' |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt: No memo or employee answer provided; merchant 'Inn' gives no location or attendee details. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ? | `RECEIPT_REQUIRED` | gap | USD amount unknown and no receipt |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ? | `HOTEL_CITY_KNOWN` | gap | hotel city could not be determined |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Hotel:** city=None tier=None nights=None via None
**Fact sources:** attendee=code
**LLM:** deepseek/deepseek-v4-flash · prompt hotel_v1.txt
**LLM reasoning:** No memo or employee answer provided; merchant 'Inn' gives no location or attendee details.

**Question to employee:**

To finish reviewing expense H35 (hotel at Inn on 2026-06-17), we need the following (please answer all in one reply):
1. Please correct the amount (amount could not be read: 'unknown').
2. If the corrected USD amount is above $25, attach the receipt.
3. Which city was the hotel in?
4. Exactly how many nights does this charge cover?

**Fields offered** amount_corrected, receipt, city, nights, employee_note

**Employee actually returned** {"amount_corrected": 520, "city": "Columbus", "nights": 2, "receipt": true}

### H35 · Alex Rivera · 2026-06-17 (Wed) · Hotel · 520.00 USD

**DECISION: REJECT** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Rejected: HOTEL_CAP_TIER2 ($520.00 total exceeds 2 nights x $200.00 (Columbus, Tier 2))

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 520.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Hotel |
| ✓ | `LLM_EXTRACTION` | pass | hotel_v1.txt: The record has no memo or employee answer, and the merchant is only 'Inn', so no attendee, city, nights, or client information is available. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $520.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `HOTEL_CITY_KNOWN` | pass | Columbus -> Tier 2 via employee_answer |
| ✗ | `HOTEL_CAP_TIER2` | fail | $520.00 total exceeds 2 nights x $200.00 (Columbus, Tier 2) |

**Client check:** internal (source: code) — memo blank -> NONE -> treated as internal
**Hotel:** city=Columbus tier=2 nights=2 via employee_answer
**Fact sources:** attendee=code · city=employee_answer · nights=employee_answer
**LLM:** deepseek/deepseek-v4-flash · prompt hotel_v1.txt
**LLM reasoning:** The record has no memo or employee answer, and the merchant is only 'Inn', so no attendee, city, nights, or client information is available.

---

## H57 · Mixed attendance / 1

Input

```json
{"id": "H57", "employee": "Alex Rivera", "date": "2026-06-20", "merchant": "Market Street", "category": "Dinner", "amount": 120, "receipt": true, "memo": "Internal team and end client Juniper Labs attended dinner; wine included.", "approval_code": null}
```

**Expected APPROVE** — The named high-confidence external customer is present alongside employees. Client exceptions cover the meal cap, weekend and alcohol.

**QA** Matched the scripted checks.

### H57 · Alex Rivera · 2026-06-20 (Sat) · Dinner · 120.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 120.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-20 (Saturday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt: Memo explicitly states 'end client Juniper Labs' and mentions wine, so client is clear and alcohol is present. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $120.00 > $25.00 and receipt attached |
| ✓ | `ALCOHOL_INTERNAL` | pass | alcohol mentioned, client confirmed (Juniper Labs) |
| ✓ | `MEAL_CAP_DINNER` | pass | $120.00 > $60.00 but client confirmed (Juniper Labs) -> cap waived |
| ✓ | `WEEKEND_MEAL_INTERNAL` | pass | Sat, client confirmed (Juniper Labs) |

**Client check:** client (source: memo_llm) — CLIENT/high 'Juniper Labs' (evidence: 'Internal team and end client Juniper Labs attended dinner')
**Alcohol:** mentioned (via memo_keyword)
**Fact sources:** attendee=memo_llm · alcohol=memo_keyword
**LLM:** deepseek/deepseek-v4-flash · prompt meals_v1.txt
**LLM reasoning:** Memo explicitly states 'end client Juniper Labs' and mentions wine, so client is clear and alcohol is present.

---

## H58 · Mixed attendance / 2

Input

```json
{"id": "H58", "employee": "Alex Rivera", "date": "2026-06-20", "merchant": "Market Street", "category": "Dinner", "amount": 120, "receipt": true, "memo": "Internal team and official client Juniper Labs attended dinner; wine included.", "approval_code": null}
```

**Expected APPROVE** — The named high-confidence external customer is present alongside employees. Client exceptions cover the meal cap, weekend and alcohol.

**QA** Matched the scripted checks.

### H58 · Alex Rivera · 2026-06-20 (Sat) · Dinner · 120.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 120.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-20 (Saturday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt: Memo explicitly states 'official client Juniper Labs' and mentions wine, so client is identified and alcohol is present. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $120.00 > $25.00 and receipt attached |
| ✓ | `ALCOHOL_INTERNAL` | pass | alcohol mentioned, client confirmed (Juniper Labs) |
| ✓ | `MEAL_CAP_DINNER` | pass | $120.00 > $60.00 but client confirmed (Juniper Labs) -> cap waived |
| ✓ | `WEEKEND_MEAL_INTERNAL` | pass | Sat, client confirmed (Juniper Labs) |

**Client check:** client (source: memo_llm) — CLIENT/high 'Juniper Labs' (evidence: 'official client Juniper Labs')
**Alcohol:** mentioned (via memo_keyword)
**Fact sources:** attendee=memo_llm · alcohol=memo_keyword
**LLM:** deepseek/deepseek-v4-flash · prompt meals_v1.txt
**LLM reasoning:** Memo explicitly states 'official client Juniper Labs' and mentions wine, so client is identified and alcohol is present.

---

## H59 · Mixed attendance / 3

Input

```json
{"id": "H59", "employee": "Alex Rivera", "date": "2026-06-17", "merchant": "Market Street", "category": "Dinner", "amount": 120, "receipt": true, "memo": "Our internal team and external customer Juniper Labs shared dinner and beer.", "approval_code": null}
```

**Expected APPROVE** — The named high-confidence external customer is present alongside employees. Client exceptions cover the meal cap, weekend and alcohol.

**QA** Matched the scripted checks.

### H59 · Alex Rivera · 2026-06-17 (Wed) · Dinner · 120.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 120.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-17 (Wednesday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt: The memo explicitly states 'external customer Juniper Labs', clearly identifying a client. Beer is mentioned, so alcohol is present. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $120.00 > $25.00 and receipt attached |
| ✓ | `ALCOHOL_INTERNAL` | pass | alcohol mentioned, client confirmed (Juniper Labs) |
| ✓ | `MEAL_CAP_DINNER` | pass | $120.00 > $60.00 but client confirmed (Juniper Labs) -> cap waived |
| – | `WEEKEND_MEAL_INTERNAL` | n/a | Wed |

**Client check:** client (source: memo_llm) — CLIENT/high 'Juniper Labs' (evidence: 'external customer Juniper Labs')
**Alcohol:** mentioned (via memo_keyword)
**Fact sources:** attendee=memo_llm · alcohol=memo_keyword
**LLM:** deepseek/deepseek-v4-flash · prompt meals_v1.txt
**LLM reasoning:** The memo explicitly states 'external customer Juniper Labs', clearly identifying a client. Beer is mentioned, so alcohol is present.

---

## H60 · Mixed attendance / 4

Input

```json
{"id": "H60", "employee": "Alex Rivera", "date": "2026-06-20", "merchant": "Market Street", "category": "Dinner", "amount": 120, "receipt": true, "memo": "Our internal team and client Juniper Labs shared Saturday lunch.", "approval_code": null}
```

**Expected APPROVE** — The named high-confidence external customer is present alongside employees. Client exceptions cover the meal cap, weekend and alcohol.

**QA** Matched the scripted checks.

### H60 · Alex Rivera · 2026-06-20 (Sat) · Dinner · 120.00 USD

**DECISION: APPROVE** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 120.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-20 (Saturday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt: The memo explicitly states 'client Juniper Labs', clearly identifying an external client. No alcohol is mentioned. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $120.00 > $25.00 and receipt attached |
| – | `ALCOHOL_INTERNAL` | n/a | no alcohol mentioned |
| ✓ | `MEAL_CAP_DINNER` | pass | $120.00 > $60.00 but client confirmed (Juniper Labs) -> cap waived |
| ✓ | `WEEKEND_MEAL_INTERNAL` | pass | Sat, client confirmed (Juniper Labs) |

**Client check:** client (source: memo_llm) — CLIENT/high 'Juniper Labs' (evidence: 'client Juniper Labs')
**Fact sources:** attendee=memo_llm
**LLM:** deepseek/deepseek-v4-flash · prompt meals_v1.txt
**LLM reasoning:** The memo explicitly states 'client Juniper Labs', clearly identifying an external client. No alcohol is mentioned.

---

## H61 · Mixed attendance / 5

Input

```json
{"id": "H61", "employee": "Alex Rivera", "date": "2026-06-20", "merchant": "Market Street", "category": "Dinner", "amount": 120, "receipt": true, "memo": "Internal team dinner with wine, no external guests.", "approval_code": null}
```

**Expected REJECT** — Only employees or a vendor are confirmed. No client exception applies.

**QA** Matched the scripted checks.

### H61 · Alex Rivera · 2026-06-20 (Sat) · Dinner · 120.00 USD

**DECISION: REJECT** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Rejected: MEAL_CAP_DINNER ($120.00 > $60.00; INTERNAL/high (evidence: 'Internal team dinner with wine, no external guests.')); WEEKEND_MEAL_INTERNAL (meal on Sat; INTERNAL/high (evidence: 'Internal team dinner with wine, no external guests.')); ALCOHOL_INTERNAL (alcohol mentioned; INTERNAL/high (evidence: 'Internal team dinner with wine, no external guests.'))

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 120.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-20 (Saturday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt: The memo explicitly states 'Internal team dinner' and 'no external guests', indicating only employees attended. Wine is mentioned, so alcohol is present. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $120.00 > $25.00 and receipt attached |
| ✗ | `MEAL_CAP_DINNER` | fail | $120.00 > $60.00; INTERNAL/high (evidence: 'Internal team dinner with wine, no external guests.') |
| ✗ | `WEEKEND_MEAL_INTERNAL` | fail | meal on Sat; INTERNAL/high (evidence: 'Internal team dinner with wine, no external guests.') |
| ✗ | `ALCOHOL_INTERNAL` | fail | alcohol mentioned; INTERNAL/high (evidence: 'Internal team dinner with wine, no external guests.') |

**Client check:** internal (source: memo_llm) — INTERNAL/high (evidence: 'Internal team dinner with wine, no external guests.')
**Alcohol:** mentioned (via memo_keyword)
**Fact sources:** attendee=memo_llm · alcohol=memo_keyword
**LLM:** deepseek/deepseek-v4-flash · prompt meals_v1.txt
**LLM reasoning:** The memo explicitly states 'Internal team dinner' and 'no external guests', indicating only employees attended. Wine is mentioned, so alcohol is present.

---

## H62 · Mixed attendance / 6

Input

```json
{"id": "H62", "employee": "Alex Rivera", "date": "2026-06-20", "merchant": "Market Street", "category": "Dinner", "amount": 120, "receipt": true, "memo": "Internal team dinner with a client; wine included.", "approval_code": null}
```

**Expected FLAG** — The client is unnamed. Ask for the customer company.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"attendee_type": "Client", "client_name": "Juniper Labs"}
```

Expected after a complete reply: **approve**.

### H62 · Alex Rivera · 2026-06-20 (Sat) · Dinner · 120.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: Alcohol is reimbursed only when a client attended.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 120.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-20 (Saturday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt: The memo mentions 'a client' but does not name the client, so attendee_confidence is low. Alcohol is mentioned via 'wine included'. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $120.00 > $25.00 and receipt attached |
| ? | `ALCOHOL_INTERNAL` | gap | alcohol mentioned, client not confirmed |
| ? | `MEAL_CAP_DINNER` | gap | $120.00 > $60.00, client not confirmed |
| ? | `WEEKEND_MEAL_INTERNAL` | gap | Sat, client not confirmed |

**Client check:** unknown (source: memo_llm) — CLIENT/low name=None -> not trusted
**Alcohol:** mentioned (via memo_keyword)
**Fact sources:** attendee=memo_llm · alcohol=memo_keyword
**LLM:** deepseek/deepseek-v4-flash · prompt meals_v1.txt
**LLM reasoning:** The memo mentions 'a client' but does not name the client, so attendee_confidence is low. Alcohol is mentioned via 'wine included'.

**Question to employee:**

To finish reviewing expense H62 ($120.00 dinner at Market Street on 2026-06-20), we need one thing: Who attended: coworkers only, an external customer, or a vendor/partner? If a customer, please name the company. (Alcohol is reimbursed only when a client attended.)

**Fields offered** attendee_type, client_name, employee_note

**Employee actually returned** {"attendee_type": "Client", "client_name": "Juniper Labs"}

### H62 · Alex Rivera · 2026-06-20 (Sat) · Dinner · 120.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

**Tags:** approved_on_employee_attestation

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 120.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-20 (Saturday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt: The memo mentions a client but does not name them, so client attendance is low confidence. Wine is explicitly mentioned, so alcohol_mentioned is true. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $120.00 > $25.00 and receipt attached |
| ✓ | `ALCOHOL_INTERNAL` | pass | alcohol mentioned, client confirmed (Juniper Labs) |
| ✓ | `MEAL_CAP_DINNER` | pass | $120.00 > $60.00 but client confirmed (Juniper Labs) -> cap waived |
| ✓ | `WEEKEND_MEAL_INTERNAL` | pass | Sat, client confirmed (Juniper Labs) |

**Client check:** client (source: employee_answer) — employee stated client 'Juniper Labs'
**Alcohol:** mentioned (via memo_keyword)
**Fact sources:** attendee=employee_answer · alcohol=memo_keyword
**LLM:** deepseek/deepseek-v4-flash · prompt meals_v1.txt
**LLM reasoning:** The memo mentions a client but does not name them, so client attendance is low confidence. Wine is explicitly mentioned, so alcohol_mentioned is true.

---

## H63 · Mixed attendance / 7

Input

```json
{"id": "H63", "employee": "Alex Rivera", "date": "2026-06-20", "merchant": "Market Street", "category": "Dinner", "amount": 120, "receipt": true, "memo": "Internal team dinner with vendor Juniper Labs; wine included.", "approval_code": null}
```

**Expected REJECT** — Only employees or a vendor are confirmed. No client exception applies.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"attendee_type": "Vendor / partner / other"}
```

Expected after a complete reply: **reject**.

### H63 · Alex Rivera · 2026-06-20 (Sat) · Dinner · 120.00 USD

**DECISION: REJECT** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Rejected: MEAL_CAP_DINNER ($120.00 > $60.00; VENDOR/high (evidence: 'vendor Juniper Labs')); WEEKEND_MEAL_INTERNAL (meal on Sat; VENDOR/high (evidence: 'vendor Juniper Labs')); ALCOHOL_INTERNAL (alcohol mentioned; VENDOR/high (evidence: 'vendor Juniper Labs'))

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 120.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-20 (Saturday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt: The memo explicitly states 'vendor Juniper Labs', indicating a vendor attended with the internal team. 'wine included' confirms alcohol. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $120.00 > $25.00 and receipt attached |
| ✗ | `MEAL_CAP_DINNER` | fail | $120.00 > $60.00; VENDOR/high (evidence: 'vendor Juniper Labs') |
| ✗ | `WEEKEND_MEAL_INTERNAL` | fail | meal on Sat; VENDOR/high (evidence: 'vendor Juniper Labs') |
| ✗ | `ALCOHOL_INTERNAL` | fail | alcohol mentioned; VENDOR/high (evidence: 'vendor Juniper Labs') |

**Client check:** vendor (source: memo_llm) — VENDOR/high (evidence: 'vendor Juniper Labs')
**Alcohol:** mentioned (via memo_keyword)
**Fact sources:** attendee=memo_llm · alcohol=memo_keyword
**LLM:** deepseek/deepseek-v4-flash · prompt meals_v1.txt
**LLM reasoning:** The memo explicitly states 'vendor Juniper Labs', indicating a vendor attended with the internal team. 'wine included' confirms alcohol.

---

## H64 · Mixed attendance / 8

Input

```json
{"id": "H64", "employee": "Alex Rivera", "date": "2026-06-20", "merchant": "Market Street", "category": "Dinner", "amount": 120, "receipt": false, "memo": "Internal team and end client Juniper Labs attended dinner; wine included.", "approval_code": null}
```

**Expected FLAG** — A named client cannot waive the receipt requirement.

**QA** Matched the scripted checks.

Complete employee answer available in this scenario

```json
{"receipt": true}
```

Expected after a complete reply: **approve**.

### H64 · Alex Rivera · 2026-06-20 (Sat) · Dinner · 120.00 USD

**DECISION: FLAG** (v1, rulebook v0.3, source batch, POST not_sent)

**Reason:** Needs information: Receipts are required for any expense over $25.00.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 120.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-20 (Saturday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt: The memo explicitly states 'end client Juniper Labs', clearly identifying an external client. Wine is mentioned, so alcohol is present. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ? | `RECEIPT_REQUIRED` | gap | $120.00 > $25.00 and no receipt |
| ✓ | `ALCOHOL_INTERNAL` | pass | alcohol mentioned, client confirmed (Juniper Labs) |
| ✓ | `MEAL_CAP_DINNER` | pass | $120.00 > $60.00 but client confirmed (Juniper Labs) -> cap waived |
| ✓ | `WEEKEND_MEAL_INTERNAL` | pass | Sat, client confirmed (Juniper Labs) |

**Client check:** client (source: memo_llm) — CLIENT/high 'Juniper Labs' (evidence: 'end client Juniper Labs')
**Alcohol:** mentioned (via memo_keyword)
**Fact sources:** attendee=memo_llm · alcohol=memo_keyword
**LLM:** deepseek/deepseek-v4-flash · prompt meals_v1.txt
**LLM reasoning:** The memo explicitly states 'end client Juniper Labs', clearly identifying an external client. Wine is mentioned, so alcohol is present.

**Question to employee:**

To finish reviewing expense H64 ($120.00 dinner at Market Street on 2026-06-20), we need one thing: Receipts are required for any expense over $25.00. Please attach it.

**Fields offered** receipt, employee_note

**Employee actually returned** {"receipt": true}

### H64 · Alex Rivera · 2026-06-20 (Sat) · Dinner · 120.00 USD

**DECISION: APPROVE** (v2, rulebook v0.3, source batch, POST not_sent)

**Reason:** Approved: every applicable rule passed.

| | Rule | Result | Detail |
|---|---|---|---|
| ✓ | `SECURITY_PROMPT_INJECTION` | pass | phrase screen: no hits |
| ✓ | `AMOUNT_VALID` | pass | 120.0 USD |
| ✓ | `DATE_VALID` | pass | 2026-06-20 (Saturday) |
| ✓ | `CATEGORY_PRESENT` | pass | Dinner |
| ✓ | `LLM_EXTRACTION` | pass | meals_v1.txt: The memo explicitly states 'end client Juniper Labs', clearly identifying an external client. Wine is mentioned, so alcohol is present. |
| ✓ | `SECURITY_PROMPT_INJECTION_LLM` | pass |  |
| ✓ | `RECEIPT_REQUIRED` | pass | $120.00 > $25.00 and receipt attached |
| ✓ | `ALCOHOL_INTERNAL` | pass | alcohol mentioned, client confirmed (Juniper Labs) |
| ✓ | `MEAL_CAP_DINNER` | pass | $120.00 > $60.00 but client confirmed (Juniper Labs) -> cap waived |
| ✓ | `WEEKEND_MEAL_INTERNAL` | pass | Sat, client confirmed (Juniper Labs) |

**Client check:** client (source: memo_llm) — CLIENT/high 'Juniper Labs' (evidence: 'end client Juniper Labs')
**Alcohol:** mentioned (via memo_keyword)
**Fact sources:** attendee=memo_llm · alcohol=memo_keyword
**LLM:** deepseek/deepseek-v4-flash · prompt meals_v1.txt
**LLM reasoning:** The memo explicitly states 'end client Juniper Labs', clearly identifying an external client. Wine is mentioned, so alcohol is present.
