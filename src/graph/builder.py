from __future__ import annotations
from typing import Dict
from langgraph.graph import StateGraph
from ..schema.state import PipelineState
from ..agents.pdf_pager import PDFPagerAgent
from ..agents.preprocessing import PreprocessingAgent
from ..agents.ocr_typhoon import OCRTyphoonAgent
from ..agents.quality_gate import QualityGateAgent
from ..agents.extraction import ExtractionAgent
from ..agents.validator import ValidatorAgent
from ..agents.calculator import CalculatorAgent
from ..agents.layout_filler import LayoutFillerAgent
from ..agents.summarizer import SummarizerAgent
from ..agents.fx_converter import FXConverterAgent
from ..agents.exporter import ExporterAgent

def node_pdf(state: Dict) -> Dict: return PDFPagerAgent().run(state)
def node_preprocess(state: Dict) -> Dict: return PreprocessingAgent().run(state)
def node_ocr(state: Dict) -> Dict:
    return OCRTyphoonAgent(params={
        "model": "typhoon-ocr-preview",   # or your preferred model
        "task_type": "default",
        "max_tokens": 16000,
        "temperature": 0.1,
        "top_p": 0.6,
        "repetition_penalty": 1.2,
    }).run(state)
def node_quality(state: Dict) -> Dict: return QualityGateAgent().run(state)
def node_extract(state: Dict) -> Dict: return ExtractionAgent().run(state)
def node_validate(state: Dict) -> Dict: return ValidatorAgent().run(state)
def node_calculate(state: Dict) -> Dict: return CalculatorAgent(default_tax_rate=7.0).run(state)
def node_layout(state: Dict) -> Dict: return LayoutFillerAgent().run(state)
def node_fx(state: Dict) -> Dict: return FXConverterAgent(base="THB").run(state)
def node_summarize(state: Dict) -> Dict: return SummarizerAgent().run(state)
def node_export(state: Dict) -> Dict: return ExporterAgent().run(state)

def build_graph():
    g = StateGraph(PipelineState)
    g.add_node("pdf", node_pdf)
    g.add_node("preprocess", node_preprocess)
    g.add_node("ocr", node_ocr)
    g.add_node("quality", node_quality)
    g.add_node("extract", node_extract)
    g.add_node("validate", node_validate)
    g.add_node("calculate", node_calculate)
    g.add_node("layout", node_layout)
    g.add_node("fx", node_fx)
    g.add_node("summarize", node_summarize)
    g.add_node("export", node_export)

    g.set_entry_point("pdf")

    g.add_edge("pdf", "preprocess")
    g.add_edge("preprocess", "ocr")
    g.add_edge("ocr", "quality")

    def route_after_quality(state: Dict):
        attempts = state.get("re_ocr_attempts", 0)
        if state.get("needs_re_ocr"):
            max_attempts = state.get("max_re_ocr_attempts", 2)
            if attempts >= max_attempts:
                state["needs_re_ocr"] = False
                state.setdefault("warnings", []).append(
                    "quality_gate: retry limit reached; proceeding with low confidence OCR"
                )
                return "extract"
            state["re_ocr_attempts"] = attempts + 1
            return "preprocess"
        state["re_ocr_attempts"] = 0
        return "extract"

    g.add_conditional_edges("quality", route_after_quality, {
        "preprocess": "preprocess",
        "extract": "extract",
    })

    g.add_edge("extract", "validate")
    g.add_edge("validate", "calculate")
    g.add_edge("calculate", "layout")
    g.add_edge("layout", "fx")
    g.add_edge("fx", "summarize")
    g.add_edge("summarize", "export")

    g.set_finish_point("export")
    return g.compile()
