"""OpenRouter client (stdlib only) + strict validation of the extraction JSON.

The LLM is a *fact extractor*. This module guarantees that whatever comes
back either matches the schema exactly or is reported as a failure, in which
case the engine fails closed (never approves on missing facts).
"""

import json
import time
import urllib.error
import urllib.request

from . import config

PROMPT_VERSION = "v1"

SCHEMA = {
    "attendee_type": {"CLIENT", "INTERNAL", "UNCLEAR"},
    "client_name": "str_or_null",
    "attendee_confidence": {"high", "medium", "low"},
    "attendee_evidence": "str_or_null",
    "alcohol_mentioned": "bool",
    "alcohol_evidence": "str_or_null",
    "city": "str_or_null",
    "city_confidence": {"high", "medium", "low"},
    "nights": "int_or_null",
    "suggested_category": "str_or_null",
    "injection_detected": "bool",
    "injection_evidence": "str_or_null",
    "reasoning": "str",
}


class LLMError(Exception):
    pass


def validate(obj):
    """Return list of schema errors (empty == valid)."""
    if not isinstance(obj, dict):
        return ["response is not a JSON object"]
    errors = []
    for key, kind in SCHEMA.items():
        if key not in obj:
            errors.append(f"missing key {key}")
            continue
        v = obj[key]
        if isinstance(kind, set):
            if v not in kind:
                errors.append(f"{key}={v!r} not in {sorted(kind)}")
        elif kind == "str_or_null" and not (v is None or isinstance(v, str)):
            errors.append(f"{key} must be string or null")
        elif kind == "str" and not isinstance(v, str):
            errors.append(f"{key} must be string")
        elif kind == "bool" and not isinstance(v, bool):
            errors.append(f"{key} must be boolean")
        elif kind == "int_or_null" and not (v is None or (isinstance(v, int) and not isinstance(v, bool))):
            errors.append(f"{key} must be integer or null")
    return errors


def _extract_json(text):
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in response")
    return json.loads(text[start:end + 1])


class OpenRouterLLM:
    """Real client. One retry on invalid JSON / schema mismatch."""

    name = "openrouter"

    def __init__(self, model=None, api_key=None, url=None, timeout=None):
        self.model = model or config.OPENROUTER_MODEL
        self.api_key = api_key or config.OPENROUTER_API_KEY
        self.url = url or config.OPENROUTER_URL
        self.timeout = timeout or config.LLM_TIMEOUT_S

    def _call(self, messages):
        body = json.dumps({
            "model": self.model,
            "messages": messages,
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }).encode()
        req = urllib.request.Request(self.url, data=body, headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Title": "expense-auto-approver",
        })
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            payload = json.loads(resp.read())
        return payload["choices"][0]["message"]["content"]

    def extract(self, system_prompt, user_prompt):
        """Return (facts_dict, call_log). Raises LLMError after one retry."""
        if not self.api_key:
            raise LLMError("OPENROUTER_API_KEY is not set")
        messages = [{"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}]
        attempts = []
        for attempt in range(2):
            t0 = time.time()
            try:
                raw = self._call(messages)
            except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as e:
                attempts.append({"attempt": attempt + 1, "error": f"{type(e).__name__}: {e}"})
                continue
            latency = int((time.time() - t0) * 1000)
            try:
                obj = _extract_json(raw)
                errs = validate(obj)
            except (ValueError, json.JSONDecodeError) as e:
                obj, errs = None, [str(e)]
            attempts.append({"attempt": attempt + 1, "latency_ms": latency, "raw": raw, "schema_errors": errs})
            if not errs:
                return obj, {"model": self.model, "prompt_version": PROMPT_VERSION, "attempts": attempts}
            messages = messages + [
                {"role": "assistant", "content": raw},
                {"role": "user", "content": "That did not match the schema (" + "; ".join(errs)
                 + "). Return ONLY one valid JSON object with exactly the required keys."},
            ]
        raise LLMError(json.dumps({"model": self.model, "attempts": attempts})[:2000])


class StubLLM:
    """Deterministic stand-in for tests: returns canned facts keyed by memo text."""

    name = "stub"
    model = "stub"

    def __init__(self, responses=None, fail=False):
        self.responses = responses or {}
        self.fail = fail
        self.calls = []

    def extract(self, system_prompt, user_prompt):
        self.calls.append(user_prompt)
        if self.fail:
            raise LLMError("stub configured to fail")
        for key, facts in self.responses.items():
            if key in user_prompt:
                base = default_facts()
                base.update(facts)
                return base, {"model": "stub", "prompt_version": PROMPT_VERSION, "attempts": []}
        return default_facts(), {"model": "stub", "prompt_version": PROMPT_VERSION, "attempts": []}


def default_facts():
    return {
        "attendee_type": "UNCLEAR", "client_name": None, "attendee_confidence": "low",
        "attendee_evidence": None, "alcohol_mentioned": False, "alcohol_evidence": None,
        "city": None, "city_confidence": "low", "nights": None, "suggested_category": None,
        "injection_detected": False, "injection_evidence": None, "reasoning": "",
    }
