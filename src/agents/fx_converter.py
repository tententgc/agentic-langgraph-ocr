from typing import Dict

class FXConverterAgent:
    def __init__(self, base: str = "THB", rates: Dict[str, float] | None = None):
        self.base = base
        self.rates = rates or {"USD": 36.5, "THB": 1.0, "EUR": 39.0}

    def run(self, state: Dict) -> Dict:
        print("fx_convertor")
        audit = state.setdefault("audit_log", [])
        inv = state.get("invoice")
        if not inv:
            return state
        cur = (inv.currency or "THB").upper()
        if cur != self.base and cur in self.rates:
            fx = self.rates[cur]
            inv.subtotal *= fx
            inv.tax_total *= fx
            inv.total *= fx
            inv.currency = self.base
            audit.append(f"fx: converted from {cur}→{self.base} @{fx}")
        else:
            audit.append("fx: no conversion")
        state["invoice"] = inv
        return state
