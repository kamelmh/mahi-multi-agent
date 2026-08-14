"""Background OCR+Summarize processor with exponential backoff.
Run: python bg_processor.py [batch_size] [delay_seconds]
"""
import json, os, sys, time, datetime
sys.path.insert(0, os.path.dirname(__file__))

import pytesseract
from PIL import Image
import fitz
from summarizer import summarize_text

cache_dir = os.path.join(os.path.dirname(__file__), "cache")
log_file = os.path.join(os.path.dirname(__file__), "processor.log")

def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def ocr_pdf(pdf_path, max_pages=3):
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

def load_state():
    with open(os.path.join(cache_dir, "pdf_extractions.json"), encoding="utf-8") as f:
        extractions = json.load(f)
    with open(os.path.join(cache_dir, "summaries.json"), encoding="utf-8") as f:
        summaries = json.load(f)
    return extractions, summaries

def save_state(summaries):
    with open(os.path.join(cache_dir, "summaries.json"), "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)

def run(batch_size=5, delay=20):
    lw_root = r"C:\Users\Admin\My Drive\LifeWorkspace"
    
    extractions, summaries = load_state()
    remaining = [(p, d) for p, d in extractions.items() if p not in summaries]
    log(f"Starting: {len(remaining)} remaining, batch_size={batch_size}")
    
    processed = 0
    failed = 0
    consecutive_fails = 0
    
    for i in range(min(batch_size, len(remaining))):
        path, data = remaining[i]
        short = os.path.basename(path)[:40]
        
        if data.get("text"):
            # Has text - just summarize
            log(f"[{i+1}] TEXT: {short}...")
            result = summarize_text(data["text"][:2000], context=path)
        else:
            # Scanned - OCR then summarize
            full_path = os.path.join(lw_root, path)
            if not os.path.exists(full_path):
                log(f"[{i+1}] NOT FOUND: {short}")
                failed += 1
                continue
            
            log(f"[{i+1}] OCR: {short}...")
            text = ocr_pdf(full_path)
            if not text:
                log(f"  EMPTY OCR")
                failed += 1
                continue
            result = summarize_text(text[:2000], context=path)
        
        if result.get("success"):
            summaries[path] = {**result, "summarized_at": "2026-07-14"}
            log(f"  OK")
            processed += 1
            consecutive_fails = 0
            save_state(summaries)
        else:
            err = result.get("error", "unknown")[:60]
            log(f"  FAIL: {err}")
            failed += 1
            consecutive_fails += 1
            if "429" in err:
                wait = delay * (2 ** min(consecutive_fails, 4))
                log(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
                if consecutive_fails >= 3:
                    log("Too many consecutive failures, stopping.")
                    break
        
        time.sleep(delay)
    
    _, summaries_final = load_state()
    log(f"Batch done: {processed} OK, {failed} fail | Total: {len(summaries_final)}/786 | Remaining: {len(extractions) - len(summaries_final)}")

if __name__ == "__main__":
    batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    delay = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    run(batch_size, delay)
