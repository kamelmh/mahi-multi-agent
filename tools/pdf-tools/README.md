# lifeworkspace-pdf-tools

PDF processing toolkit for LifeWorkspace — signing, extraction, OCR, and conversion.

## Features

### Sign (`src/sign/`)
- `sign_pdf.py` — Sign PDFs with image signatures
- `batch_sign.py` — Batch sign multiple PDFs
- `create_signature.py` — Generate signature images
- `create_short_signature.py` — Short signature variant

### Extract (`src/extract/`)
- `pdf_extractor.py` — Extract images from PDFs
- `image_analyzer.py` — Analyze extracted images
- `ocr_scanned.py` — OCR for scanned documents
- `batch_ocr.py` — Batch OCR processing
- `pipeline.py` — Full extraction pipeline
- `summarizer.py` — Summarize extracted content

### Convert (`src/convert/`)
- `create_cv.py` — CV creation from templates
- `create_motivation_letter.py` — Letter generation
- `pdf_to_bw.py` — Convert PDF to black & white

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Sign a PDF
python src/sign/sign_pdf.py input.pdf --signature assets/signatures/formal.png --output signed.pdf

# Extract images
python src/extract/pdf_extractor.py document.pdf --output ./images/

# OCR scanned PDF
python src/extract/ocr_scanned.py scanned.pdf --lang eng

# Convert to B&W
python src/convert/pdf_to_bw.py color.pdf --output bw.pdf
```

## Assets

- `assets/signatures/` — Pre-generated signature images (formal, artistic, short)
- `assets/stamps/` — Stamp images

## Requirements

See `requirements.txt` for dependencies.
