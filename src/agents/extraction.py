import re
from typing import Dict, List
from ..schema.invoice import Invoice, LineItem
from ..utils.currency import detect_currency, to_float, AMOUNT_RE
from ..utils.thai_text import normalize_whitespace

INV_NO_RE = re.compile(r"(Invoice\s*No\.?|เลขที่ใบแจ้งหนี้|เลขที่)\s*[:#]?\s*([\w\-\/]+)", re.IGNORECASE)
DATE_RE = re.compile(r"(วันที่|Date)\s*[:#]?\s*([0-9]{1,2}[\-/][0-9]{1,2}[\-/][0-9]{2,4})")
QTY_HEADER_RE = re.compile(r"(Qty|จำนวน)", re.I)
PRICE_HEADER_RE = re.compile(r"(Price|Unit Price|ราคา/หน่วย)", re.I)

class ExtractionAgent:
    def run(self, state: Dict) -> Dict:
        audit = state.setdefault("audit_log", [])
        text = normalize_whitespace(state.get("ocr_text", ""))
        invoice = Invoice()

        invoice.currency = detect_currency(text) or invoice.currency

        if m := INV_NO_RE.search(text):
            invoice.invoice_number = m.group(2)
        if m := DATE_RE.search(text):
            invoice.invoice_date = m.group(2)

        blocks = state.get("ocr_blocks", [])
        items: List[LineItem] = []

        header_idx = None
        for i, b in enumerate(blocks):
            bt = normalize_whitespace(b.get("text", ""))
            if QTY_HEADER_RE.search(bt) and PRICE_HEADER_RE.search(bt):
                header_idx = i
                break
        if header_idx is not None:
            for b in blocks[header_idx + 1:]:
                bt = normalize_whitespace(b.get("text", ""))
                if re.search(r"(รวม|Subtotal|Total|VAT)", bt, re.I):
                    break
                nums = AMOUNT_RE.findall(bt)
                if len(nums) >= 1:
                    try:
                        unit_price = to_float(nums[-1])
                        qty = 1.0
                        if len(nums) >= 2:
                            qty = to_float(nums[-2])
                        mfirst = AMOUNT_RE.search(bt)
                        desc = bt[:mfirst.start()].strip() if mfirst else bt
                        if desc:
                            items.append(LineItem(description=desc, quantity=qty, unit_price=unit_price))
                    except Exception:
                        pass
        if not items:
            for b in blocks:
                bt = normalize_whitespace(b.get("text", ""))
                if " x " in bt:
                    try:
                        left, price_s = bt.rsplit(" x ", 1)
                        parts = left.rsplit(" ", 1)
                        if len(parts) == 2 and AMOUNT_RE.fullmatch(parts[1]):
                            qty = to_float(parts[1])
                            desc = parts[0]
                            unit_price = to_float(AMOUNT_RE.search(price_s).group(1))
                            items.append(LineItem(description=desc, quantity=qty, unit_price=unit_price))
                    except Exception:
                        pass
                elif m := AMOUNT_RE.search(bt):
                    desc = bt[: m.start()].strip()
                    try:
                        unit_price = to_float(m.group(1))
                        if desc:
                            items.append(LineItem(description=desc, quantity=1.0, unit_price=unit_price))
                    except Exception:
                        pass

        if items:
            invoice.line_items = items

        state["invoice"] = invoice
        audit.append("extraction: fields+items (tabular)")
        return state
