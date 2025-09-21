from __future__ import annotations
import os, tempfile
from typing import Dict, Optional

# pip install typhoon-ocr
from typhoon_ocr import ocr_document

class TyphoonOCRClient:
    """
    Wrapper around the official typhoon-ocr package.
    Env:
      - TYPHOON_OCR_API_KEY (or OPENAI_API_KEY)
    """

    def __init__(self, task_type: str = "default"):
        # "default" returns markdown-ish text; "structure" returns structural output (if supported)
        self.task_type = task_type

    def ocr_file(self, file_bytes: bytes, filename: str = "document", params: Optional[Dict] = None) -> Dict:
        # typhoon_ocr.ocr_document currently accepts a *path*, so write a temp file:
        suffix = ".pdf" if filename.lower().endswith(".pdf") else ".png"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            markdown = ocr_document(
                pdf_or_image_path=tmp_path,
                task_type=(params or {}).get("task_type", self.task_type),
                page_num=(params or {}).get("page_num", 1),
            )
        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

        return {
            "text": markdown or "",
            "pages": [markdown or ""],  # simple single-page mapping; extend if you loop pages
            "messages": [],
            "raw": {"markdown": markdown},
        }
