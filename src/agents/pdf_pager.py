from typing import Dict
import io
try:
    from pdf2image import convert_from_path
except Exception:
    convert_from_path = None

class PDFPagerAgent:
    def __init__(self, dpi: int = 200):
        self.dpi = dpi

    def run(self, state: Dict) -> Dict:
        audit = state.setdefault("audit_log", [])
        path = state.get("input_path")
        if not path or not path.lower().endswith(".pdf"):
            return state
        if convert_from_path is None:
            state.setdefault("warnings", []).append("pdf2image not installed; skipping PDF paging")
            return state
        images = convert_from_path(path, dpi=self.dpi)
        state["pages"] = []
        for im in images:
            buf = io.BytesIO()
            im.save(buf, format="PNG")
            state["pages"].append(buf.getvalue())
        state["page_index"] = 0
        audit.append(f"pdf_pager: {len(state['pages'])} page(s)")
        return state
