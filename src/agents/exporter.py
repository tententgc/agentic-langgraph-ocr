import json
from typing import Dict
from ..schema.invoice import Invoice
import os

class ExporterAgent:
    def __init__(self, outdir: str = "./outputs"):
        self.outdir = outdir

    def run(self, state: Dict) -> Dict:
        os.makedirs(self.outdir, exist_ok=True)
        audit = state.setdefault("audit_log", [])
        inv: Invoice = state.get("invoice")
        md = state.get("summary_md", "")
        exports = {}
        if inv:
            jpath = os.path.join(self.outdir, "invoice.json")
            with open(jpath, "w", encoding="utf-8") as f:
                json.dump(inv.model_dump(), f, ensure_ascii=False, indent=2)
            exports["json"] = jpath
        if md:
            mpath = os.path.join(self.outdir, "summary.md")
            with open(mpath, "w", encoding="utf-8") as f:
                f.write(md)
            exports["md"] = mpath
        state["exports"] = exports
        audit.append(f"exporter: {list(exports.keys())}")
        return state
