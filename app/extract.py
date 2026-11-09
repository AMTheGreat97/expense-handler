"""Category-specific LLM fact extraction (stage S3) + the trust rule.

The LLM returns raw labels. This module:
  1. picks the category-specific prompt,
  2. wraps untrusted text in tags,
  3. VERIFIES evidence quotes really appear in the text (else downgrades),
  4. never lets a non-'high' label count as a known fact (done in engine).
"""

import re

from . import config
from .llm import LLMError

_PROMPTS = {}


def _load(name):
    if name not in _PROMPTS:
        _PROMPTS[name] = (config.PROMPT_DIR / name).read_text(encoding="utf-8")
    return _PROMPTS[name]


def prompt_for(category):
    if category in config.MEAL_CATEGORIES or category == "Entertainment":
        return "meals_v1.txt"
    if category == "Hotel":
        return "hotel_v1.txt"
    if category is None:
        return "uncategorized_v1.txt"
    return "general_v1.txt"


def build_prompts(category, raw_category, merchant, memo, employee_note):
    section_file = prompt_for(category)
    system = _load("system_v1.txt").replace("{category_instructions}", _load(section_file))

    def tag(name, value):
        value = (value or "").replace("<", "‹").replace(">", "›")   # cannot close our tags
        return f"<{name}>{value}</{name}>"

    user = "\n".join([
        "Expense record (untrusted employee text inside tags):",
        tag("category", raw_category),
        tag("merchant", merchant),
        tag("memo", memo),
        tag("employee_answer", employee_note),
        "Return the JSON object now.",
    ])
    return system, user, section_file


def _norm(s):
    return " ".join(re.sub(r"[^\w\s&.-]", " ", (s or "").lower()).split())


def _quoted(evidence, haystack):
    return bool(evidence) and _norm(evidence) in _norm(haystack)


def run(llm, category, raw_category, merchant, memo, employee_note):
    """Return dict(facts=..., verification=[...], call=..., prompt_file=..., error=None|str)."""
    system, user, section_file = build_prompts(category, raw_category, merchant, memo, employee_note)
    try:
        facts, call = llm.extract(system, user)
    except LLMError as e:
        return {"facts": None, "verification": [], "call": None, "prompt_file": section_file, "error": str(e)}

    facts = dict(facts)
    notes = []
    attendee_text = f"{memo or ''} {employee_note or ''}"
    all_text = f"{raw_category or ''} {merchant or ''} {memo or ''} {employee_note or ''}"

    if facts["attendee_confidence"] == "high" and not _quoted(facts.get("attendee_evidence"), attendee_text):
        facts["attendee_confidence"] = "medium"
        notes.append("attendee evidence not found in memo -> downgraded to medium")
    if facts["attendee_type"] == "CLIENT" and facts.get("client_name") \
            and _norm(facts["client_name"]) not in _norm(attendee_text):
        facts["attendee_confidence"] = "low"
        notes.append("client_name not present in memo/answer -> downgraded to low")
    if facts["city_confidence"] == "high" and facts.get("city") \
            and _norm(facts["city"]) not in _norm(f"{merchant or ''} {memo or ''} {employee_note or ''}"):
        facts["city_confidence"] = "medium"
        notes.append("city not literally present in merchant/memo -> downgraded to medium")

    facts["_injection_verified"] = bool(facts["injection_detected"]) and _quoted(facts.get("injection_evidence"), all_text)
    if facts["injection_detected"] and not facts["_injection_verified"]:
        notes.append("LLM claimed injection but its quote is not in the text -> needs human review")

    return {"facts": facts, "verification": notes, "call": call, "prompt_file": section_file, "error": None}
