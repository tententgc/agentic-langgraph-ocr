from __future__ import annotations
from typing import Any, Dict, List, TypedDict
from pydantic import BaseModel
from .invoice import Invoice

class Artifact(BaseModel):
    kind: str
    data: Any

class PipelineState(TypedDict, total=False):
    input_path: str
    input_bytes: bytes
    mime_type: str

    # Multi-page
    pages: List[bytes]
    page_index: int

    # Results
    preprocessed_path: str
    ocr_text: str
    ocr_blocks: List[Dict]
    ocr_confidence: float
    invoice: Invoice
    filled_layout: Dict[str, Any]
    summary_md: str
    exports: Dict[str, str]

    # Diagnostics
    warnings: List[str]
    errors: List[str]
    audit_log: List[str]
    needs_re_ocr: bool
    re_ocr_attempts: int
    max_re_ocr_attempts: int
