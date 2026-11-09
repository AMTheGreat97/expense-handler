"""Portal form (structured facts) vs batch (memo only). Stub LLM, no network."""

import re
import unittest
from datetime import date, timedelta
from pathlib import Path

from app import config, form
from app.engine import decide
from app.fx import StubFX
from app.llm import StubLLM
from app.pipeline import Pipeline
from app.publisher import NullPublisher
from app.store import Store

ACME = {"attendee_type": "CLIENT", "client_name": "Acme Corp", "attendee_confidence": "high",
        "attendee_evidence": "w/ Acme Corp"}
TEAM = {"attendee_type": "INTERNAL", "attendee_confidence": "high", "attendee_evidence": "team dinner"}
BEERS = {"attendee_type": "INTERNAL", "attendee_confidence": "high", "attendee_evidence": "team",
         "alcohol_mentioned": True}


def stay(n, check_in="2026-06-14"):
    """Hotel stay of n nights as the two portal date fields."""
    d = date.fromisoformat(check_in)
    return {"check_in": check_in, "check_out": (d + timedelta(days=n)).isoformat()}


def values(**kw):
    v = {"employee": "Test", "date": "2026-06-17", "category": "Dinner", "merchant": "Bistro",
         "amount": 50, "currency": "USD", "amount_usd": None, "memo": "team dinner", "receipt": True,
         "client_business": False, "client_name": "", "alcohol_declared": False,
         "city": None, "city_other": "", "check_in": None, "check_out": None, "approval_code": ""}
    v.update(kw)
    return v


def run_form(llm=None, **kw):
    e = form.form_expense(values(**kw))
    e["id"] = "P-1"
    return decide(e, llm or StubLLM({"w/ Acme Corp": ACME, "team dinner": TEAM}), StubFX())[0]


def rule(p, rid):
    return next((r for r in p["rules_fired"] if r["rule"] == rid), None)


class FormRequirementsMap(unittest.TestCase):
    def test_every_requirement_is_read_by_the_engine(self):
        src = Path(config.APP_DIR / "engine.py").read_text(encoding="utf-8")
        for r in config.FORM_REQUIREMENTS:
            key = r["engine_key"]
            self.assertRegex(src, rf'exp(?:\.get\(|\[)"{re.escape(key)}"',
                             f"{r['field']} -> {key!r} is not read by engine.py")

    def test_every_requirement_reaches_the_expense(self):
        full = values(category="Hotel", currency="EUR", amount_usd=55, city="Other", city_other="Des Moines",
                      **stay(2))
        keys = set(form.form_expense(full)) | set(form.form_expense(values(client_business=True, client_name="X")))
        keys |= set(form.form_expense(values(category="Software", approval_code="SW-1")))
        for r in config.FORM_REQUIREMENTS:
            self.assertIn(r["engine_key"], keys, r["field"])


class RequiredFields(unittest.TestCase):
    def test_complete_form_has_nothing_missing(self):
        self.assertEqual(form.missing_required(values(), amount_usd=50), [])

    def test_missing_required_field_blocks_submit(self):
        self.assertIn("Memo (brief description)", form.missing_required(values(memo=""), amount_usd=50))
        self.assertIn("Receipt attached (required over $25)",
                      form.missing_required(values(receipt=False), amount_usd=50))
        self.assertEqual(form.missing_required(values(receipt=False, amount=20), amount_usd=20), [])

    def test_client_name_required_only_when_box_checked(self):
        self.assertIn("Client company name", form.missing_required(values(client_business=True), amount_usd=50))
        self.assertEqual(form.missing_required(values(client_business=True, client_name="Acme"), amount_usd=50), [])

    def test_hotel_needs_city_and_nights(self):
        m = form.missing_required(values(category="Hotel"), amount_usd=300)
        self.assertIn("Hotel city", m)
        self.assertIn("Check-in date", m)
        self.assertIn("Check-out date", m)
        m = form.missing_required(values(category="Hotel", city="Other", **stay(2)), amount_usd=300)
        self.assertEqual(m, ["City name"])

    def test_software_needs_approval_code(self):
        self.assertIn("Software approval code", form.missing_required(values(category="Software"), amount_usd=50))

    def test_pipeline_blocks_nothing_but_portal_submit_does(self):
        """Hotel without nights: blocked in the portal, but batch still asks the nights question."""
        self.assertIn("Check-in date",
                      form.missing_required(values(category="Hotel", city="Other", city_other="Des Moines"),
                                            amount_usd=400))
        batch = {"id": "B-1", "employee": "T", "date": "2026-06-17", "category": "Hotel",
                 "merchant": "Marriott Des Moines", "amount": 400, "memo": "", "receipt": True}
        llm = StubLLM({"Des Moines": {"city": "Des Moines", "city_confidence": "high"}})
        p = decide(batch, llm, StubFX())[0]
        self.assertEqual(p["decision"], "flag")
        self.assertIn("nights", p["missing_fields"])

    def test_invalid_date_blocks_submit(self):
        self.assertIn("Date (use YYYY-MM-DD)", form.missing_required(values(date="17th June"), amount_usd=50))

    def test_fx_failure_makes_card_usd_amount_required(self):
        v = values(currency="EUR")
        self.assertEqual(form.missing_required(v, amount_usd=55), [])
        m = form.missing_required(v, amount_usd=None, engine_gaps=["amount_usd"])
        self.assertTrue(any(x.startswith("USD amount on your card statement") for x in m))
        self.assertEqual(form.missing_required(values(currency="EUR", amount_usd=55), amount_usd=55,
                                               engine_gaps=["amount_usd"]), [])

    def test_complete_portal_form_never_flags_for_a_missing_fact(self):
        """Audit: a fully filled form leaves the engine nothing to ask (only conflicts / LLM outage remain)."""
        cases = [values(amount=88, client_business=True, client_name="Acme Corp", memo="dinner w/ Acme Corp"),
                 values(amount=88), values(category="Entertainment", amount=60, memo="team dinner"),
                 values(category="Hotel", amount=500, city="Other", city_other="Des Moines", **stay(3), memo="stay"),
                 values(category="Hotel", amount=700, city="Boston", **stay(2), memo="stay"),
                 values(category="Software", amount=16, approval_code="SW-42", memo="Notion seat", receipt=False),
                 values(category="Office", amount=84, memo="monitor stand"),
                 values(date="2026-06-20", amount=25, memo="team dinner")]
        for v in cases:
            self.assertEqual(form.missing_required(v, amount_usd=float(v["amount"])), [], v)
            p = run_form(**{k: v[k] for k in v})
            self.assertNotEqual(p["decision"], "flag", (v, p["missing_fields"]))

    def test_entertainment_without_client_box_warns(self):
        self.assertTrue(form.warnings(values(category="Entertainment")))
        self.assertFalse(form.warnings(values(category="Entertainment", client_business=True)))


class FormMapping(unittest.TestCase):
    def test_currency_dropdown(self):
        self.assertEqual(form.build_amount(65, "EUR"), "65 EUR")
        self.assertEqual(form.build_amount(65, "USD"), 65.0)

    def test_unchecked_client_box_over_cap_dinner_rejects(self):
        self.assertEqual(run_form(amount=88)["decision"], "reject")

    def test_checked_box_with_name_approves_with_attestation_tag(self):
        p = run_form(amount=88, client_business=True, client_name="Acme Corp", memo="dinner w/ Acme Corp")
        self.assertEqual(p["decision"], "approve")
        self.assertIn("approved_on_employee_attestation", p["tags"])
        self.assertEqual(p["facts"]["sources"]["attendee"], "form")

    def test_checked_box_without_name_flags_for_client_name(self):
        p = run_form(amount=88, client_business=True, client_name="")
        self.assertEqual(p["decision"], "flag")
        self.assertIn("attendee", p["missing_fields"])

    def test_alcohol_checkbox_on_internal_dinner_rejects(self):
        p = run_form(amount=50, alcohol_declared=True)
        self.assertEqual(p["decision"], "reject")
        self.assertEqual(rule(p, "ALCOHOL_INTERNAL")["result"], "fail")
        self.assertEqual(p["facts"]["sources"]["alcohol"], "form")

    def test_unchecked_box_but_memo_names_client_flags_conflict(self):
        p = run_form(amount=88, memo="dinner w/ Acme Corp")
        self.assertEqual(p["decision"], "flag")
        self.assertEqual(rule(p, "ATTESTATION_CONFLICT_CLIENT")["result"], "gap")
        self.assertIn("Client business", p["question"]["text"])

    def test_client_conflict_that_does_not_change_outcome_is_not_asked(self):
        p = run_form(amount=40, memo="dinner w/ Acme Corp")       # under the $60 cap either way
        self.assertEqual(p["decision"], "approve")
        self.assertEqual(rule(p, "ATTESTATION_CONFLICT_CLIENT")["result"], "pass")

    def test_no_alcohol_box_but_memo_mentions_beer_flags_conflict(self):
        p = run_form(amount=50, memo="team dinner, 2 beers", llm=StubLLM({"team dinner": BEERS}))
        self.assertEqual(p["decision"], "flag")
        self.assertEqual(rule(p, "ATTESTATION_CONFLICT_ALCOHOL")["result"], "gap")
        self.assertIn("alcohol", p["missing_fields"])

    def test_hotel_other_city_is_tier2(self):
        p = run_form(category="Hotel", amount=240, city="Other", city_other="Des Moines", **stay(1))
        self.assertEqual(p["decision"], "reject")
        self.assertIsNotNone(rule(p, "HOTEL_CAP_TIER2"))
        self.assertEqual(p["facts"]["sources"]["city"], "form")

    def test_hotel_per_night_math(self):
        p = run_form(category="Hotel", amount=300, city="Other", city_other="Des Moines", **stay(2), memo="stay")
        self.assertEqual(p["decision"], "approve")
        self.assertIn("$150.00/night", form.hotel_rule_detail(p))

    def test_hotel_400_tier2_no_nights_asks_nights(self):
        p = run_form(category="Hotel", amount=400, city="Other", city_other="Des Moines", memo="stay")
        self.assertEqual(p["decision"], "flag")
        self.assertIn("nights", p["missing_fields"])

    def test_hotel_nights_from_memo(self):
        p = run_form(category="Hotel", amount=400, city="Other", city_other="Des Moines", memo="2 nights")
        self.assertEqual(p["decision"], "approve")
        self.assertEqual(p["facts"]["sources"]["nights"], "memo_keyword")


class AnswerAfterConflict(unittest.TestCase):
    def test_answering_the_conflict_question_resolves_it(self):
        pipe = Pipeline(llm=StubLLM({"w/ Acme Corp": ACME}), fx=StubFX(), publisher=NullPublisher(), store=Store(), write_logs=False)
        e = form.form_expense(values(amount=88, memo="dinner w/ Acme Corp"))
        e["id"] = "P-9"
        self.assertEqual(pipe.process(e, "portal")["decision"], "flag")
        p2 = pipe.answer("P-9", {"attendee_type": "Client", "client_name": "Acme Corp"})
        self.assertEqual(p2["decision"], "approve")
        self.assertEqual(p2["facts"]["sources"]["attendee"], "employee_answer")


class StayDates(unittest.TestCase):
    """Hotel nights come from check-in/check-out, never a typed number."""

    def test_nights_are_derived_from_the_dates(self):
        self.assertEqual(form.stay_nights("2026-06-14", "2026-06-17"), (3, None))
        e = form.form_expense(values(category="Hotel", city="Boston", **stay(3)))
        self.assertEqual((e["nights"], e["check_in"], e["check_out"]), (3, "2026-06-14", "2026-06-17"))

    def test_check_out_must_be_after_check_in(self):
        for ci, co in (("2026-06-14", "2026-06-14"), ("2026-06-14", "2026-06-12")):
            m = form.missing_required(values(category="Hotel", city="Boston", check_in=ci, check_out=co),
                                      amount_usd=300)
            self.assertIn("Check-out date (check-out must be after check-in)", m)
            self.assertNotIn("nights", form.form_expense(values(category="Hotel", check_in=ci, check_out=co)))

    def test_date_picker_values_are_accepted(self):
        self.assertEqual(form.to_iso_date("2026-06-14 00:00:00"), "2026-06-14")
        self.assertEqual(form.to_iso_date(date(2026, 6, 14)), "2026-06-14")
        self.assertEqual(form.stay_nights("2026-06-14 00:00:00", "2026-06-16 00:00:00"), (2, None))

    def test_engine_uses_derived_nights_for_the_per_night_cap(self):
        p = run_form(category="Hotel", amount=600, city="Boston", **stay(2), memo="stay")
        self.assertEqual(p["decision"], "approve")
        self.assertEqual(p["facts"]["sources"]["nights"], "form")
        p = run_form(category="Hotel", amount=600, city="Other", city_other="Des Moines", **stay(2), memo="stay")
        self.assertEqual(p["decision"], "reject")

    def test_payment_before_check_in_only_warns(self):
        v = values(category="Hotel", city="Boston", date="2026-06-01", **stay(2))
        self.assertTrue(any("before check-in" in w for w in form.warnings(v)))
        self.assertEqual(form.missing_required(v, amount_usd=300), [])


class FormValidation(unittest.TestCase):
    def test_future_date_says_future_not_format(self):
        m = form.missing_required(values(date="2099-01-01"), amount_usd=50)
        self.assertIn("Date (can't be in the future)", m)

    def test_zero_amount_and_negative_card_amount_block(self):
        self.assertIn("Amount (must be more than 0)", form.missing_required(values(amount=0), amount_usd=None))
        m = form.missing_required(values(currency="EUR", amount_usd=-5), amount_usd=55)
        self.assertTrue(any("must be more than 0" in x for x in m))

    def test_values_in_hidden_fields_are_dropped(self):
        """Switching Software -> Office must not carry the old approval code (or hotel dates) along."""
        e = form.form_expense(values(category="Office", approval_code="SW-1", city="Boston", **stay(2)))
        self.assertIsNone(e["approval_code"])
        self.assertNotIn("nights", e)
        self.assertNotIn("city", e)

    def test_gap_labels_are_plain_words(self):
        self.assertEqual(form.gap_labels(["nights", "amount_usd"]),
                         ["the hotel stay dates", "the USD amount on your card statement"])


class AnswerForm(unittest.TestCase):
    Q_NIGHTS = [{"name": "nights", "type": "number"}, {"name": "employee_note", "optional": True}]
    Q_CLIENT = [{"name": "attendee_type"}, {"name": "client_name", "label": "Client company name"},
                {"name": "employee_note", "optional": True}]

    def test_empty_answer_is_blocked(self):
        _, problems = form.clean_answers(self.Q_NIGHTS, {})
        self.assertEqual(problems, ["the check-in and check-out dates"])

    def test_nights_answer_from_dates(self):
        a, problems = form.clean_answers(self.Q_NIGHTS, stay(3))
        self.assertEqual(problems, [])
        self.assertEqual(a["nights"], 3)

    def test_bad_stay_dates_are_blocked(self):
        _, problems = form.clean_answers(self.Q_NIGHTS, {"check_in": "2026-06-14", "check_out": "2026-06-14"})
        self.assertEqual(problems, ["the stay dates (check-out must be after check-in)"])

    def test_client_answer_needs_company(self):
        _, problems = form.clean_answers(self.Q_CLIENT, {"attendee_type": "Client"})
        self.assertIn("the client company name", problems)
        a, problems = form.clean_answers(self.Q_CLIENT, {"attendee_type": "Client", "client_name": "Acme"})
        self.assertEqual(problems, [])
        a, problems = form.clean_answers(self.Q_CLIENT, {"attendee_type": "Internal only (our employees)"})
        self.assertEqual(problems, [])

    def test_other_city_needs_a_name(self):
        q = [{"name": "city"}]
        self.assertTrue(form.clean_answers(q, {"city": "Other (type it)"})[1])
        self.assertEqual(form.clean_answers(q, {"city": "Other (type it)", "city_other": "Des Moines"})[0],
                         {"city": "Des Moines"})

    def test_answered_nights_reach_the_engine(self):
        pipe = Pipeline(llm=StubLLM({}), fx=StubFX(), publisher=NullPublisher(), store=Store(), write_logs=False)
        batch = {"id": "B-7", "employee": "T", "date": "2026-06-17", "category": "Hotel", "city": "Des Moines",
                 "merchant": "Marriott", "amount": 400, "memo": "stay", "receipt": True}
        p = pipe.process(batch, "batch")
        self.assertIn("nights", p["missing_fields"])
        a, problems = form.clean_answers(p["question"]["fields"], stay(2))
        self.assertEqual(problems, [])
        self.assertEqual(pipe.answer("B-7", a)["decision"], "approve")


if __name__ == "__main__":
    unittest.main()
