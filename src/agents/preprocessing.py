from typing import Dict
from ..utils import image_io

class PreprocessingAgent:
    def run(self, state: Dict) -> Dict:
        print("preprcessing")
        audit = state.setdefault("audit_log", [])
        if state.get("pages"):
            idx = state.get("page_index", 0)
            image_bytes = state["pages"][idx]
        else:
            image_bytes = state.get("input_bytes")
            if not image_bytes and state.get("input_path"):
                image_bytes = image_io.read_image(state["input_path"])
                state["input_bytes"] = image_bytes
        if not image_bytes:
            state.setdefault("errors", []).append("No input image")
            return state
        processed = image_io.deskew_grayscale(image_bytes)
        state["input_bytes"] = processed
        audit.append("preprocessing: deskew+denoise+adaptive")
        return state
