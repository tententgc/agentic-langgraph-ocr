from typing import Dict, Any
from ..schema.invoice import Invoice

class LayoutFillerAgent:
    def run(self, state: Dict) -> Dict:
        print("layout_fillter")
        audit = state.setdefault("audit_log", [])
        inv: Invoice = state.get("invoice")
        blocks = state.get("ocr_blocks", [])
        layout: Dict[str, Any] = {"fields": {}, "items": []}
        if inv:
            layout["fields"].update({
                "invoice_number": {"value": inv.invoice_number, "bbox": self._find_bbox(blocks, [inv.invoice_number])},
                "invoice_date": {"value": inv.invoice_date, "bbox": self._find_bbox(blocks, [inv.invoice_date])},
                "currency": {"value": inv.currency, "bbox": None},
            })
            for it in inv.line_items:
                layout["items"].append({
                    "description": it.description,
                    "quantity": it.quantity,
                    "unit_price": it.unit_price,
                    "discount": it.discount,
                    "tax_rate": it.tax_rate,
                    "bbox": self._find_bbox(blocks, [it.description])
                })
        state["filled_layout"] = layout
        audit.append("layout_filler: map built")
        return state

    def _find_bbox(self, blocks, needles):
        if not needles:
            return None
        targets = set([n for n in needles if n])
        for b in blocks:
            t = b.get("text", "")
            if any(n in t for n in targets):
                return b.get("bbox")
        return None
