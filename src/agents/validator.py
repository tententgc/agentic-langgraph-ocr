from typing import Dict
from ..schema.invoice import Invoice

class ValidatorAgent:
    def run(self, state: Dict) -> Dict:
        audit = state.setdefault("audit_log", [])
        inv: Invoice = state.get("invoice")
        if not inv:
            state.setdefault("errors", []).append("validator: missing invoice")
            return state
        if not inv.line_items:
            state.setdefault("warnings", []).append("No line items detected; check OCR quality")
        if not inv.invoice_number:
            state.setdefault("warnings", []).append("Missing invoice number")
        audit.append("validator: basic checks")
        return state
