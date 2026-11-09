"""Currency conversion [RULEBOOK G-3.x].

Historical rate on the expense date (Frankfurter / ECB data, no API key),
falling back to the latest rate. Any failure => None, and the engine asks the
employee for the USD amount instead of guessing.
"""

import json
import urllib.request

from . import config


class FrankfurterFX:
    name = "frankfurter"

    def __init__(self, base_url=None, timeout=10):
        self.base_url = (base_url or config.FX_URL).rstrip("/")
        self.timeout = timeout

    def _get(self, path):
        with urllib.request.urlopen(f"{self.base_url}/{path}", timeout=self.timeout) as r:
            return json.loads(r.read())

    def to_usd(self, amount, currency, on_date):
        """Return dict(rate, rate_date, source, amount_usd) or dict(error=...)."""
        if currency == "USD":
            return {"rate": 1.0, "rate_date": None, "source": "none (USD)", "amount_usd": amount}
        tried = []
        for path in (f"{on_date.isoformat()}?from={currency}&to=USD" if on_date else None,
                     f"latest?from={currency}&to=USD"):
            if not path:
                continue
            try:
                data = self._get(path)
                rate = float(data["rates"]["USD"])
                return {"rate": rate, "rate_date": data.get("date"), "source": f"{self.base_url}/{path}",
                        "amount_usd": round(amount * rate, 2)}
            except Exception as e:  # network, unknown currency, bad payload
                tried.append(f"{path}: {type(e).__name__}: {e}")
        return {"error": "; ".join(tried)}


class StubFX:
    name = "stub"

    def __init__(self, rates=None, fail=False):
        self.rates = rates or {"EUR": 1.08, "GBP": 1.27}
        self.fail = fail

    def to_usd(self, amount, currency, on_date):
        if currency == "USD":
            return {"rate": 1.0, "rate_date": None, "source": "none (USD)", "amount_usd": amount}
        if self.fail or currency not in self.rates:
            return {"error": f"stub has no rate for {currency}"}
        r = self.rates[currency]
        return {"rate": r, "rate_date": on_date.isoformat() if on_date else None,
                "source": "stub", "amount_usd": round(amount * r, 2)}
