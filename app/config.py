"""Configuration: paths, env loading, and policy constants.

Every policy number lives here (or in rules.py next to the rule that uses it),
so a reviewer can see the whole policy surface in one place.
"""

import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent                      # the candidate folder
DATA_DIR = ROOT_DIR / "data"
LOG_DIR = ROOT_DIR / "logs"
PROMPT_DIR = APP_DIR / "prompts"

RULEBOOK_VERSION = "v0.3"


def load_dotenv(path: Path = ROOT_DIR / ".env") -> None:
    """Minimal .env loader (stdlib only). Existing env vars win."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_URL = os.environ.get("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-v4-flash")
LLM_TIMEOUT_S = float(os.environ.get("LLM_TIMEOUT_S", "45"))

DECISIONS_ENDPOINT = os.environ.get("DECISIONS_ENDPOINT", "http://localhost:8000/decisions")
FX_URL = os.environ.get("FX_URL", "https://api.frankfurter.app")

# ---- Policy constants (RULEBOOK v0.3) -------------------------------------
RECEIPT_THRESHOLD_USD = 25.00            # strictly above needs a receipt

MEAL_CAPS_USD = {"Breakfast": 20.00, "Lunch": 30.00, "Dinner": 60.00}
MEAL_CATEGORIES = set(MEAL_CAPS_USD)

HOTEL_CAP_TIER1_USD = 350.00
HOTEL_CAP_TIER2_USD = 200.00

ALLOWED_CATEGORIES = [
    "Breakfast", "Lunch", "Dinner", "Entertainment", "Hotel",
    "Software", "Office", "Ground Transport", "Airfare",
]

CATEGORY_SYNONYMS = {
    "breakfast": "Breakfast", "lunch": "Lunch", "dinner": "Dinner",
    "entertainment": "Entertainment",
    "hotel": "Hotel", "lodging": "Hotel",
    "software": "Software", "saas": "Software",
    "office": "Office", "office supplies": "Office",
    "uber": "Ground Transport", "lyft": "Ground Transport", "taxi": "Ground Transport",
    "cab": "Ground Transport", "ground transport": "Ground Transport", "rideshare": "Ground Transport",
    "airfare": "Airfare", "flight": "Airfare", "air": "Airfare",
}
