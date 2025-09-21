# src/agents/summarizer.py
from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from ..clients.llm_client import LLMClient
from ..schema.invoice import Invoice


class SummarizerAgent:
    """
    Generate a concise Markdown summary (Thai + English by default) for the invoice
    currently stored in the pipeline state.

    Expects in `state`:
      - invoice: Invoice
      - filled_layout: Optional[dict]  (for downstream UI highlighting; optional)

    Produces in `state`:
      - summary_md: str
    """

    def __init__(
        self,
        llm: Optional[LLMClient] = None,
        bilingual: bool = True,
        max_words: int = 120,
    ) -> None:
        self.llm = llm or LLMClient()
        self.bilingual = bilingual
        self.max_words = max_words

    # --------------- Public API ---------------

    def run(self, state: Dict) -> Dict:
        audit = state.setdefault("audit_log", [])
        inv: Optional[Invoice] = state.get("invoice")
        layout = state.get("filled_layout", {})

        if not inv:
            state.setdefault("errors", []).append("summarizer: missing invoice")
            return state

        prompt = self._build_prompt(inv, layout)
        try:
            md = self.llm.summarize(prompt)
        except Exception as e:
            # Fallback: create a local summary if LLM fails
            md = self._fallback_summary(inv)
            state.setdefault("warnings", []).append(
                f"summarizer: LLM client failed, used fallback ({e})"
            )

        state["summary_md"] = md
        audit.append("summarizer: md summary")
        return state

    # --------------- Helpers ---------------

    def _build_prompt(self, inv: Invoice, layout: Dict) -> str:
        """
        Create an instruction-following prompt for a concise, structured summary.
        """
        items_preview: List[Tuple[str, float, float, float]] = [
            (it.description, it.quantity, it.unit_price, it.tax_rate)
            for it in inv.line_items
        ]

        bilingual_block = (
            "• Output **both** Thai and English sections.\n"
            if self.bilingual
            else "• Output **Thai only**.\n"
        )

        return f"""
You are a precise financial assistant. Create a **concise** Markdown summary for an invoice.
Follow these rules:
{bilingual_block}• Keep each section under **{self.max_words} words**.
• If any value is missing, write **ไม่ระบุ / N/A**.
• Use bullet points and short, clear lines.
• Do not invent values.

INVOICE DATA (structured):
- Invoice No: {inv.invoice_number or "N/A"}
- Date: {inv.invoice_date or "N/A"}
- Due Date: {inv.due_date or "N/A"}
- Currency: {inv.currency or "N/A"}
- Items: {items_preview}
- Subtotal: {inv.subtotal:.2f}
- Tax: {inv.tax_total:.2f}
- Total: {inv.total:.2f}
- Notes: {inv.notes or "N/A"}

OPTIONAL LAYOUT HINTS (for UI highlighting; do not repeat verbatim): {layout}

Format exactly like this:

## สรุปใบแจ้งหนี้ (TH)
- เลขที่: ...
- วันที่: ...
- สกุลเงิน: ...
- รายการหลัก: ...
- ยอดก่อนภาษี: ...
- ภาษี: ...
- ทั้งหมด: ...
- หมายเหตุ: ...

## Invoice Summary (EN)
- Invoice No: ...
- Date: ...
- Currency: ...
- Key Items: ...
- Subtotal: ...
- Tax: ...
- Total: ...
- Notes: ...
""".strip()

    def _fallback_summary(self, inv: Invoice) -> str:
        """
        Offline fallback if LLM is unavailable.
        """
        def fmt(n: Optional[float]) -> str:
            try:
                return f"{float(n):.2f}"
            except Exception:
                return "N/A"

        items_lines = []
        for it in inv.line_items[:5]:  # cap preview
            items_lines.append(
                f"- {it.description} (qty: {it.quantity}, unit: {fmt(it.unit_price)}, tax%: {fmt(it.tax_rate)})"
            )
        items_str = "\n".join(items_lines) if items_lines else "- ไม่ระบุ / N/A"

        return f"""## สรุปใบแจ้งหนี้ (TH)
- เลขที่: {inv.invoice_number or "ไม่ระบุ / N/A"}
- วันที่: {inv.invoice_date or "ไม่ระบุ / N/A"}
- สกุลเงิน: {inv.currency or "ไม่ระบุ / N/A"}
- รายการหลัก:
{items_str}
- ยอดก่อนภาษี: {fmt(inv.subtotal)}
- ภาษี: {fmt(inv.tax_total)}
- ทั้งหมด: {fmt(inv.total)}
- หมายเหตุ: {inv.notes or "ไม่ระบุ / N/A"}

## Invoice Summary (EN)
- Invoice No: {inv.invoice_number or "N/A"}
- Date: {inv.invoice_date or "N/A"}
- Currency: {inv.currency or "N/A"}
- Key Items:
{items_str}
- Subtotal: {fmt(inv.subtotal)}
- Tax: {fmt(inv.tax_total)}
- Total: {fmt(inv.total)}
- Notes: {inv.notes or "N/A"}
""".strip()
