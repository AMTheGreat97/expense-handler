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

# ---- Portal form requirements ---------------------------------------------
# Batch (legacy) data only has a memo, so the LLM extracts facts and the engine
# asks. The portal instead collects every decision-critical fact as a field.
# This one map drives BOTH what the portal shows and what it requires before
# Submit, so the form and the rules cannot drift apart.
#   field       portal input name
#   engine_key  expense key the engine reads (tests check the engine reads it)
#   categories  None = every category, else the categories that show it
#   required    always | if_shown | if_over_receipt_threshold | optional
#   show_if     (other_field, value) ; value "!X" means "anything but X"
_MEAL_LIKE = ["Breakfast", "Lunch", "Dinner", "Entertainment"]
FORM_REQUIREMENTS = [
    {"field": "employee", "label": "Employee", "engine_key": "employee", "required": "always"},
    {"field": "date", "label": "Date", "engine_key": "date", "required": "always"},
    {"field": "category", "label": "Category", "engine_key": "category", "required": "always"},
    {"field": "merchant", "label": "Merchant", "engine_key": "merchant", "required": "always"},
    {"field": "amount", "label": "Amount", "engine_key": "amount", "required": "always"},
    {"field": "currency", "label": "Currency", "engine_key": "amount", "required": "always"},
    {"field": "amount_usd", "label": "USD amount on your card statement", "engine_key": "amount_usd",
     "required": "optional", "show_if": ("currency", "!USD")},
    {"field": "memo", "label": "Memo (brief description)", "engine_key": "memo", "required": "always"},
    {"field": "receipt", "label": "Receipt attached (required over $25)", "engine_key": "receipt",
     "required": "if_over_receipt_threshold"},
    {"field": "client_business", "label": "Client business (a client attended)", "engine_key": "attendee_type",
     "categories": _MEAL_LIKE, "required": "optional",
     "warn_unchecked": {"Entertainment": "Entertainment is only reimbursed for client business."}},
    {"field": "client_name", "label": "Client company name", "engine_key": "client_name",
     "categories": _MEAL_LIKE, "required": "if_shown", "show_if": ("client_business", True)},
    {"field": "alcohol_declared", "label": "Includes alcohol", "engine_key": "alcohol_declared",
     "categories": _MEAL_LIKE, "required": "optional"},
    {"field": "city", "label": "Hotel city", "engine_key": "city", "categories": ["Hotel"], "required": "always"},
    {"field": "city_other", "label": "City name", "engine_key": "city", "categories": ["Hotel"],
     "required": "if_shown", "show_if": ("city", "Other")},
    # Nights are never typed: the portal derives them from the stay dates (check-out minus check-in).
    {"field": "check_in", "label": "Check-in date", "engine_key": "nights",
     "categories": ["Hotel"], "required": "always"},
    {"field": "check_out", "label": "Check-out date", "engine_key": "nights",
     "categories": ["Hotel"], "required": "always"},
    {"field": "approval_code", "label": "Software approval code", "engine_key": "approval_code",
     "categories": ["Software"], "required": "always"},
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
