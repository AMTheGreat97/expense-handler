"""Deterministic prompt-injection screen (stage S0a).

Runs on every free-text field BEFORE anything reaches the LLM. The LLM runs a
second, paraphrase-tolerant check later (stage S3). Either one => REJECT
[RULEBOOK G-0.1].
"""

import re

# Phrases that try to direct the reviewer / system. Kept deliberately specific
# so ordinary memos ("lunch w/ Acme") never match.
INJECTION_PATTERNS = [
    r"note\s+to\s+(the\s+)?(reviewer|approver|finance|ai|system|bot)",
    r"\bauto[\s-]?approve",
    r"\bplease\s+approve\b",
    r"\bapprove\s+(this|it|immediately|automatically)\b",
    r"\bignore\s+(the\s+|all\s+|any\s+|previous\s+|prior\s+)*(limit|limits|rule|rules|policy|policies|instructions|cap)\b",
    r"\bdisregard\s+(the\s+|all\s+|any\s+|previous\s+)*(limit|rule|rules|policy|instructions)",
    r"\b(override|bypass)\s+(the\s+)?(limit|rule|rules|policy|cap|check)",
    r"\bsystem\s*(prompt|message)?\s*:",
    r"\byou\s+are\s+(an?\s+)?(ai|assistant|language model|llm)\b",
    r"\bas\s+an\s+ai\b",
    r"\bmark\s+(this\s+)?as\s+approved\b",
]
_COMPILED = [re.compile(p, re.I) for p in INJECTION_PATTERNS]


def screen(fields: dict):
    """fields: {field_name: text}. Returns list of {"field", "pattern", "quote"}."""
    hits = []
    for name, text in fields.items():
        if not isinstance(text, str) or not text:
            continue
        for pat in _COMPILED:
            m = pat.search(text)
            if m:
                hits.append({"field": name, "pattern": pat.pattern, "quote": m.group(0)})
    return hits
