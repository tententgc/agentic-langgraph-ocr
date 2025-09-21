import re
from typing import Optional

CURRENCY_HINTS = {
    "฿": "THB", "THB": "THB", "บาท": "THB",
    "$": "USD", "USD": "USD",
}

AMOUNT_RE = re.compile(r"([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?|[0-9]+(?:\.[0-9]{2})?)")

def detect_currency(text: str) -> Optional[str]:
    for k, v in CURRENCY_HINTS.items():
        if k in text:
            return v
    return None

def to_float(s: str) -> float:
    return float(s.replace(",", "").strip())
