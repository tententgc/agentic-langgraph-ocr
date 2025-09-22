from typing import Dict

class QualityGateAgent:
    def __init__(self, min_conf: float = 0.55, min_chars: int = 120):
        self.min_conf = min_conf
        self.min_chars = min_chars

    def run(self, state: Dict) -> Dict:
        print('quality_gate')
        audit = state.setdefault("audit_log", [])
        conf = state.get("ocr_confidence", 0.0)
        text = state.get("ocr_text", "")
        if conf < self.min_conf or len(text) < self.min_chars:
            state["needs_re_ocr"] = True
            state.setdefault("warnings", []).append(
                f"quality_gate: low OCR quality (conf={conf:.2f}, chars={len(text)})"
            )
        else:
            state["needs_re_ocr"] = False
        audit.append("quality_gate: evaluated")
        return state
