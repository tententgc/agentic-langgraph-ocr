# quick_test_opentyphoon.py
import os, json
from dotenv import load_dotenv
from src.clients.typhoon_client import TyphoonOCRClient

load_dotenv()
path = os.getenv("SAMPLE_INVOICE", "./sample_invoice.jpg")
with open(path, "rb") as f:
    fb = f.read()

client = TyphoonOCRClient()
res = client.ocr_file(fb, filename=os.path.basename(path), params={"model": "typhoon-ocr-preview"})
print("TEXT:\n", res["text"][:1000])
print("\nRAW keys:", list(res["raw"].keys()))
