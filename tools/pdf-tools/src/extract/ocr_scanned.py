"""OCR scanned PDFs using Tesseract + Pillow."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))

import pytesseract
from PIL import Image
import subprocess

cache_dir = os.path.join(os.path.dirname(__file__), "cache")

def pdf_to_images(pdf_path, max_pages=3):
    """Convert PDF pages to images using pdftoppm (poppler) or fallback."""
    import tempfile
    tmpdir = tempfile.mkdtemp()
    
    # Try pdftoppm first (poppler)
    try:
        cmd = ['pdftoppm', '-png', '-r', '200', '-l', str(max_pages), pdf_path, os.path.join(tmpdir, 'page')]
        subprocess.run(cmd, capture_output=True, timeout=30)
        images = sorted([os.path.join(tmpdir, f) for f in os.listdir(tmpdir) if f.endswith('.png')])
        return images
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Try pymupdf (fitz)
    try:
        import fitz
        doc = fitz.open(pdf_path)
        images = []
        for i in range(min(max_pages, len(doc))):
            page = doc[i]
            pix = page.get_pixmap(dpi=200)
            img_path = os.path.join(tmpdir, f'page_{i:03d}.png')
            pix.save(img_path)
            images.append(img_path)
        doc.close()
        return images
    except ImportError:
        pass
    
    return []

def ocr_image(img_path):
    """OCR a single image."""
    try:
        img = Image.open(img_path)
        text = pytesseract.image_to_string(img, lang='eng')
        return text.strip()
    except Exception as e:
        return ""

def ocr_pdf(pdf_path, max_pages=3):
    """OCR a PDF file."""
    images = pdf_to_images(pdf_path, max_pages)
    texts = []
    for img in images:
        text = ocr_image(img)
        if text:
            texts.append(text)
        os.remove(img)
    
    # Cleanup temp dir
    try:
        os.rmdir(os.path.dirname(images[0])) if images else None
    except:
        pass
    
    return '\n\n'.join(texts)

if __name__ == "__main__":
    # Load data
    with open(os.path.join(cache_dir, "pdf_extractions.json"), encoding="utf-8") as f:
        extractions = json.load(f)
    
    with open(os.path.join(cache_dir, "summaries.json"), encoding="utf-8") as f:
        summaries = json.load(f)
    
    # Find scanned PDFs
    scanned = [(p, d) for p, d in extractions.items() if p not in summaries and not d.get("text")]
    print(f"Scanned PDFs: {len(scanned)}")
    
    # Test with first one
    if scanned:
        path, data = scanned[0]
        print(f"Testing OCR on: {path[:60]}")
        
        # Find actual file
        pdf_path = None
        for prefix in [r"C:\Users\Admin\My Drive\LifeWorkspace", r"C:\Users\Admin\Desktop"]:
            candidate = os.path.join(prefix, path)
            if os.path.exists(candidate):
                pdf_path = candidate
                break
        
        if pdf_path:
            text = ocr_pdf(pdf_path)
            print(f"OCR result: {len(text)} chars")
            print(f"Preview: {text[:200]}")
        else:
            print(f"File not found: {path}")
