"""POST decisions to Finance's endpoint (the mock server in this exercise)."""

import json
import time
import urllib.error
import urllib.request

from . import config


class HttpPublisher:
    def __init__(self, endpoint=None, retries=3, timeout=5):
        self.endpoint = endpoint or config.DECISIONS_ENDPOINT
        self.retries = retries
        self.timeout = timeout

    def post(self, payload):
        """Return (status, detail). status: sent | failed."""
        body = json.dumps(payload).encode()
        last = ""
        for attempt in range(self.retries):
            req = urllib.request.Request(self.endpoint, data=body, headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    if resp.status == 200:
                        return "sent", f"HTTP 200 from {self.endpoint}"
                    last = f"HTTP {resp.status}"
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                last = f"{type(e).__name__}: {e}"
            time.sleep(0.5 * (2 ** attempt))
        return "failed", last


class NullPublisher:
    """For eval / preview: records what WOULD be posted."""

    def __init__(self):
        self.sent = []

    def post(self, payload):
        self.sent.append(json.loads(json.dumps(payload)))
        return "not_sent", "dry run"
