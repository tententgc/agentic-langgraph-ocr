from typing import Dict
from ..schema.invoice import Invoice

class CalculatorAgent:
    def __init__(self, default_tax_rate: float | None = None):
        self.default_tax_rate = default_tax_rate

    def run(self, state: Dict) -> Dict:
        audit = state.setdefault("audit_log", [])
        inv: Invoice = state.get("invoice")
        if not inv:
            state.setdefault("errors", []).append("calculator: missing invoice")
            return state
        if self.default_tax_rate is not None:
            for it in inv.line_items:
                if it.tax_rate == 0.0:
                    it.tax_rate = self.default_tax_rate
        inv.subtotal = sum(it.subtotal for it in inv.line_items)
        inv.tax_total = sum(it.tax_amount for it in inv.line_items)
        inv.total = inv.subtotal + inv.tax_total
        state["invoice"] = inv
        audit.append("calculator: totals computed")
        return state
