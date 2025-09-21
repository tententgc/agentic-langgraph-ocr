import re

TH_DATE_HINTS = ["พ.ศ.", "ใบเสร็จ", "เลขที่", "วันที่"]

def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
