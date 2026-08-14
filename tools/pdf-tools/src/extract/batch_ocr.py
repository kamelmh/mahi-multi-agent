"""Batch OCR all scanned PDFs and summarize."""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))

import pytesseract
from PIL import Image
import fitz
import tempfile
from summarizer import summarize_text

cache_dir = os.path.join(os.path.dirname(__file__), "cache")

def ocr_pdf(pdf_path, max_pages=3):
    """OCR a PDF using pymupdf + tesseract."""
    try:
        doc = fitz.open(pdf_path)
        texts = []
        for i in range(min(max_pages, len(doc))):
            page = doc[i]
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img, lang='eng')
            if text.strip():
                texts.append(text.strip())
        doc.close()
        return '\n\n'.join(texts)
    except Exception as e:
        return ""

# Load data
with open(os.path.join(cache_dir, "pdf_extractions.json"), encoding="utf-8") as f:
    extractions = json.load(f)

with open(os.path.join(cache_dir, "summaries.json"), encoding="utf-8") as f:
    summaries = json.load(f)

# Find scanned PDFs
scanned = [(p, d) for p, d in extractions.items() if p not in summaries and not d.get("text")]
print(f"Scanned PDFs to OCR: {len(scanned)}")

# Find LifeWorkspace root
lw_root = r"C:\Users\Admin\My Drive\LifeWorkspace"

processed = 0
failed = 0

for i in range(min(10, len(scanned))):
    path, data = scanned[i]
    full_path = os.path.join(lw_root, path)
    short = os.path.basename(path)[:50]
    
    print(f"[{i+1}/10] {short}...", end=' ', flush=True)
    
    if not os.path.exists(full_path):
        print("NOT FOUND")
        failed += 1
        continue
    
    text = ocr_pdf(full_path)
    if not text:
        print("EMPTY OCR")
        failed += 1
        continue
    
    # Summarize the OCR text
    result = summarize_text(text[:2000], context=path)
    if result.get("success"):
        summaries[path] = {**result, "summarized_at": "2026-07-14", "ocr": True}
        print("OK")
        processed += 1
    else:
        err = result.get("error", "unknown")[:60]
        print(f"FAIL: {err}")
        failed += 1
        if "429" in err:
            print("Rate limited, stopping.")
            break
    
    time.sleep(20)

# Save
with open(os.path.join(cache_dir, "summaries.json"), "w", encoding="utf-8") as f:
    json.dump(summaries, f, indent=2, ensure_ascii=False)

print(f"\nBatch: {processed} OK, {failed} fail")
print(f"Total: {len(summaries)}/786")
print(f"Remaining: {len(extractions) - len(summaries)}")
