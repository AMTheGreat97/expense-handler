"""Tier-1 city table and matching [RULEBOOK §3 Hotel].

Only the 8 main cities count. Accepted spellings are the city name and its
common short forms. Neighborhoods and nearby cities do NOT count.
"""

import re

# canonical -> (case-insensitive spellings, case-SENSITIVE short forms)
TIER1 = {
    "New York":      (["new york city", "new york", "nyc"], []),
    "Los Angeles":   (["los angeles"], ["LA", "L.A."]),
    "San Francisco": (["san francisco", "san fran"], ["SF"]),
    "Washington DC": (["washington dc", "washington d.c.", "washington, dc", "washington, d.c."], ["DC", "D.C."]),
    "Seattle":       (["seattle"], []),
    "Chicago":       (["chicago"], []),
    "Boston":        (["boston"], []),
    "London":        (["london"], []),
}

# Strings that contain a Tier-1 name but are NOT in that city. If one of these
# matches we refuse the table match and fall back to the LLM / a question.
TRAPS = [r"new\s+york[\s-]+new\s+york", r"new\s+london", r"london,?\s+ontario", r"east\s+boston"]


def _norm(s):
    return " ".join((s or "").lower().split())


def table_match(text):
    """Return (canonical_city | None, note)."""
    if not text:
        return None, "no text"
    low = _norm(text)
    for trap in TRAPS:
        if re.search(trap, low):
            return None, f"ambiguous name ({trap})"
    found = set()
    for city, (spellings, short) in TIER1.items():
        for sp in spellings:
            if re.search(r"(?<![a-z])" + re.escape(sp) + r"(?![a-z])", low):
                found.add(city)
        for sf in short:
            if re.search(r"(?<![A-Za-z.])" + re.escape(sf) + r"(?![A-Za-z])", text):
                found.add(city)
    if len(found) == 1:
        return found.pop(), "table match"
    if len(found) > 1:
        return None, f"several cities matched: {sorted(found)}"
    return None, "no tier-1 match"


def canonical_tier1(city_name):
    """Map an extracted city name to a Tier-1 canonical name, or None."""
    if not city_name:
        return None
    c, _ = table_match(city_name)
    if c:
        return c
    low = _norm(city_name)
    if low in {"washington, district of columbia", "district of columbia"}:
        return "Washington DC"
    return None
