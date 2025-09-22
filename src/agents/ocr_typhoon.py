# src/agents/ocr_typhoon.py
from __future__ import annotations

from typing import Dict, Optional
from ..clients.typhoon_client import TyphoonOCRClient


class OCRTyphoonAgent:
    def __init__(self, params: Optional[Dict] = None):
        """
        params: overrides for Typhoon API (model, task_type, etc.)
        """
        self.client = TyphoonOCRClient()
        self.params = params or {}

    def run(self, state: Dict) -> Dict:
        print("ocr_typhoon")
        audit = state.setdefault("audit_log", [])

        image_bytes = state.get("input_bytes")
        if not image_bytes:
            state.setdefault("errors", []).append("OCR: missing image bytes")
            return state

        # Filename for the multipart form; purely cosmetic.
        fname = state.get("input_path", "document").split("/")[-1] or "document"

        try:
            result = self.client.ocr_file(image_bytes, filename=fname, params=self.params)
        except Exception as e:
            state.setdefault("errors", []).append(f"OCR request failed: {e}")
            return state

        # Populate state
        state["ocr_text"] = result.get("text", "")
        # Typhoon’s response doesn’t include bbox blocks by default in this route.
        # If your org has a variant that returns layout, place it into ocr_blocks:
        state["ocr_blocks"] = []  # keep contract for downstream agents
        # Save raw messages for debugging/integration
        state["typhoon_raw"] = result.get("raw")
        state["typhoon_messages"] = result.get("messages", [])

        if not state["ocr_text"]:
            state.setdefault("warnings", []).append("OCR returned empty text")

        audit.append("ocr: typhoon (multipart)")
        print(state["ocr_text"])
        print(audit)
        return state
