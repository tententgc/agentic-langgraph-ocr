import os
from dotenv import load_dotenv
from src.graph.builder import build_graph
from src.utils.image_io import read_image

def main():
    load_dotenv()
    app = build_graph()

    sample_path = os.environ.get("SAMPLE_INVOICE", "sample_invoice.jpg")
    state = {
        "input_path": sample_path,
        "input_bytes": None if sample_path.lower().endswith(".pdf") else (read_image(sample_path) if os.path.exists(sample_path) else None),
        "mime_type": "image/jpeg",
        "warnings": [],
        "errors": [],
        "audit_log": [],
    }

    out = app.invoke(state)
    print("\\n=== RESULT ===")
    print("Exports:", out.get("exports"))
    print("Warnings:", out.get("warnings"))
    print("Errors:", out.get("errors"))
    print("Audit:", out.get("audit_log"))

if __name__ == "__main__":
    main()
