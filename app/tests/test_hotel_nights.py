"""Hotel nights must be stated unambiguously; otherwise we ask (fail closed)."""

import unittest

from app import normalize
from app.engine import decide
from app.fx import StubFX
from app.llm import StubLLM


def hotel(amount, memo, llm=None):
    e = {"id": "H-1", "employee": "T", "date": "2026-06-17", "category": "Hotel", "merchant": "Hilton London",
         "amount": amount, "memo": memo, "receipt": True}
    return decide(e, llm or StubLLM({}), StubFX())[0]


class ParseNights(unittest.TestCase):
    def test_exact_statements(self):
        for text, n in (("2 nights", 2), ("two nights", 2), ("1 night", 1), ("3-night stay", 3),
                        ("Twelve nights in London", 12)):
            self.assertEqual(normalize.parse_nights(text)[:2], (n, "found"), text)

    def test_ambiguous_statements(self):
        for text in ("2-3 nights", "2 to 3 nights", "2 or 3 nights", "two or three nights", "2/3 nights",
                     "a couple of nights", "few nights", "several nights", "about 3 nights", "~2 nights",
                     "approx 2 nights", "1 night then 2 nights extension"):
            n, status, _ = normalize.parse_nights(text)
            self.assertEqual((n, status), (None, "ambiguous"), text)

    def test_no_statement(self):
        self.assertEqual(normalize.parse_nights("London conference stay")[:2], (None, "none"))


class HotelNightsDecisions(unittest.TestCase):
    def test_range_flags(self):
        p = hotel(400, "2-3 nights")
        self.assertEqual(p["decision"], "flag")
        self.assertIn("nights", p["missing_fields"])

    def test_couple_of_nights_flags(self):
        self.assertEqual(hotel(400, "stayed a couple of nights")["decision"], "flag")

    def test_two_nights_word_approves(self):
        p = hotel(400, "two nights")
        self.assertEqual(p["decision"], "approve")
        self.assertEqual(p["facts"]["sources"]["nights"], "memo_keyword")

    def test_two_nights_digit_approves(self):
        self.assertEqual(hotel(400, "2 nights")["decision"], "approve")

    def test_two_different_numbers_flags(self):
        self.assertEqual(hotel(400, "1 night then 2 nights extension")["decision"], "flag")

    def test_llm_guess_without_quote_flags(self):
        p = hotel(400, "London offsite", llm=StubLLM({"London offsite": {"nights": 3}}))
        self.assertEqual(p["decision"], "flag")
        self.assertIn("nights", p["missing_fields"])

    def test_llm_disagreeing_with_memo_flags(self):
        p = hotel(400, "2 nights", llm=StubLLM({"2 nights": {"nights": 3}}))
        self.assertEqual(p["decision"], "flag")

    def test_under_one_night_cap_needs_no_nights(self):
        self.assertEqual(hotel(300, "London conference stay")["decision"], "approve")


if __name__ == "__main__":
    unittest.main()
