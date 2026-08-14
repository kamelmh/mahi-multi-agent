"""Knowledge Extractor Pipeline - Processes PDFs and images into MD files.

Usage:
    python pipeline.py --scan           # Scan and inventory all files
    python pipeline.py --extract-pdf    # Extract text from PDFs
    python pipeline.py --extract-img    # Analyze images
    python pipeline.py --summarize      # Summarize extracted content
    python pipeline.py --all            # Run full pipeline
"""

import os
import sys
import json
import argparse
from datetime import datetime

from pdf_extractor import extract_text, extract_metadata
from image_analyzer import analyze_image
from summarizer import summarize_text, analyze_image_context

LW_ROOT = r"C:\Users\Admin\My Drive\LifeWorkspace"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")


def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)


def scan_files():
    """Scan and inventory all PDFs and images."""
    print("=== SCANNING FILES ===")
    inventory = {"pdfs": [], "images": [], "scan_time": datetime.now().isoformat()}

    for root, _, files in os.walk(LW_ROOT):
        for file in files:
            path = os.path.join(root, file)
            rel_path = path.replace(LW_ROOT + "\\", "")
            ext = os.path.splitext(file)[1].lower()

            try:
                file_size = os.path.getsize(path)
            except (OSError, FileNotFoundError):
                continue

            if ext == ".pdf":
                meta = extract_metadata(path)
                inventory["pdfs"].append({
                    "path": rel_path,
                    "size": file_size,
                    "pages": meta.get("pages", 0),
                    "title": meta.get("title", ""),
                })
            elif ext in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"):
                inventory["images"].append({
                    "path": rel_path,
                    "size": file_size,
                })

    # Save inventory
    inv_path = os.path.join(OUTPUT_DIR, "file_inventory.json")
    with open(inv_path, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)

    print(f"Found {len(inventory['pdfs'])} PDFs, {len(inventory['images'])} images")
    print(f"Inventory saved to {inv_path}")
    return inventory


def extract_pdfs(inventory=None, limit=50):
    """Extract text from PDFs."""
    print(f"\n=== EXTRACTING PDFs (limit: {limit}) ===")

    if not inventory:
        inv_path = os.path.join(OUTPUT_DIR, "file_inventory.json")
        if os.path.exists(inv_path):
            with open(inv_path) as f:
                inventory = json.load(f)
        else:
            inventory = scan_files()

    cache_path = os.path.join(CACHE_DIR, "pdf_extractions.json")
    cache = {}
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            cache = json.load(f)

    extracted = 0
    for pdf_info in inventory["pdfs"][:limit]:
        rel_path = pdf_info["path"]
        if rel_path in cache:
            continue

        full_path = os.path.join(LW_ROOT, rel_path)
        if not os.path.exists(full_path):
            continue
        print(f"  Extracting: {rel_path[:60]}...")
        try:
            result = extract_text(full_path, max_pages=5)
        except Exception as e:
            print(f"    Error: {e}")
            continue
        cache[rel_path] = {
            "text": result.get("text", ""),
            "pages": result.get("total_pages", 0),
            "metadata": result.get("metadata", {}),
            "extracted_at": datetime.now().isoformat(),
        }
        extracted += 1

        # Save periodically
        if extracted % 10 == 0:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

    print(f"Extracted {extracted} new PDFs (total cached: {len(cache)})")
    return cache


def analyze_images(inventory=None, limit=50):
    """Analyze images."""
    print(f"\n=== ANALYZING IMAGES (limit: {limit}) ===")

    if not inventory:
        inv_path = os.path.join(OUTPUT_DIR, "file_inventory.json")
        if os.path.exists(inv_path):
            with open(inv_path) as f:
                inventory = json.load(f)
        else:
            inventory = scan_files()

    cache_path = os.path.join(CACHE_DIR, "image_analysis.json")
    cache = {}
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            cache = json.load(f)

    analyzed = 0
    for img_info in inventory["images"][:limit]:
        rel_path = img_info["path"]
        if rel_path in cache:
            continue

        full_path = os.path.join(LW_ROOT, rel_path)
        if not os.path.exists(full_path):
            continue

        print(f"  Analyzing: {rel_path}")
        result = analyze_image(full_path)
        filename = os.path.basename(rel_path)
        context = analyze_image_context(filename, result.get("width", 0), result.get("category", ""))
        cache[rel_path] = {
            **result,
            "context": context,
            "analyzed_at": datetime.now().isoformat(),
        }
        analyzed += 1

        if analyzed % 20 == 0:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

    print(f"Analyzed {analyzed} new images (total cached: {len(cache)})")
    return cache


def summarize_all(pdf_cache=None, image_cache=None, limit=30):
    """Summarize extracted content using Groq API."""
    print(f"\n=== SUMMARIZING (limit: {limit}) ===")

    if not pdf_cache:
        cache_path = os.path.join(CACHE_DIR, "pdf_extractions.json")
        if os.path.exists(cache_path):
            with open(cache_path) as f:
                pdf_cache = json.load(f)
        else:
            pdf_cache = extract_pdfs()

    summaries_path = os.path.join(OUTPUT_DIR, "summaries.json")
    summaries = {}
    if os.path.exists(summaries_path):
        with open(summaries_path) as f:
            summaries = json.load(f)

    summarized = 0
    for path, data in list(pdf_cache.items())[:limit]:
        if path in summaries:
            continue
        if not data.get("text"):
            continue

        print(f"  Summarizing: {path}")
        result = summarize_text(data["text"], context=path)
        if result.get("success"):
            summaries[path] = {
                **result,
                "summarized_at": datetime.now().isoformat(),
            }
            summarized += 1

        if summarized % 5 == 0:
            with open(summaries_path, "w", encoding="utf-8") as f:
                json.dump(summaries, f, indent=2, ensure_ascii=False)

    with open(summaries_path, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)

    print(f"Summarized {summarized} PDFs (total: {len(summaries)})")
    return summaries


def generate_md(summaries, image_cache):
    """Generate MD files from summaries and image analysis."""
    print("\n=== GENERATING MD FILES ===")

    # Group by category
    categories = {}
    for path, summary in summaries.items():
        cat = summary.get("category", "other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({"path": path, **summary})

    # Create category MD files
    for cat, items in categories.items():
        cat_name = cat.replace(" ", "_").lower()
        md_path = os.path.join(OUTPUT_DIR, f"{cat_name}.md")

        lines = [f"# {cat.title()} Documents\n"]
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        lines.append(f"Total: {len(items)} documents\n\n")

        for item in items:
            lines.append(f"## {item.get('title', os.path.basename(item['path']))}\n")
            lines.append(f"**File:** `{item['path']}`\n")
            lines.append(f"**Summary:** {item.get('summary', 'N/A')}\n")
            topics = item.get("key_topics", [])
            if topics:
                lines.append(f"**Topics:** {', '.join(topics)}\n")
            actions = item.get("actionable_info", [])
            if actions:
                lines.append("**Actionable Info:**")
                for a in actions:
                    lines.append(f"- {a}")
            lines.append("")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"  Created: {cat_name}.md ({len(items)} items)")

    # Create image summary
    if image_cache:
        img_md = os.path.join(OUTPUT_DIR, "images_summary.md")
        lines = ["# Image Analysis\n"]
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        lines.append(f"Total: {len(image_cache)} images\n\n")

        # Group by category
        img_cats = {}
        for path, data in image_cache.items():
            cat = data.get("category", "unknown")
            if cat not in img_cats:
                img_cats[cat] = []
            img_cats[cat].append({"path": path, **data})

        for cat, items in img_cats.items():
            lines.append(f"## {cat.title()} ({len(items)})\n")
            for item in items[:5]:
                lines.append(f"- `{item['path']}` ({item.get('width', '?')}x{item.get('height', '?')})")
            if len(items) > 5:
                lines.append(f"- ... and {len(items)-5} more")
            lines.append("")

        with open(img_md, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"  Created: images_summary.md")

    print(f"\nAll MD files saved to: {OUTPUT_DIR}")


def main():
    parser = argparse.ArgumentParser(description="Knowledge Extractor Pipeline")
    parser.add_argument("--scan", action="store_true", help="Scan and inventory files")
    parser.add_argument("--extract-pdf", action="store_true", help="Extract PDF text")
    parser.add_argument("--extract-img", action="store_true", help="Analyze images")
    parser.add_argument("--summarize", action="store_true", help="Summarize content")
    parser.add_argument("--generate", action="store_true", help="Generate MD files")
    parser.add_argument("--all", action="store_true", help="Run full pipeline")
    parser.add_argument("--limit", type=int, default=30, help="Max items to process")
    args = parser.parse_args()

    ensure_dirs()

    if args.all or args.scan:
        inventory = scan_files()
    else:
        inventory = None

    pdf_cache = None
    if args.all or args.extract_pdf:
        pdf_cache = extract_pdfs(inventory, limit=args.limit)

    image_cache = None
    if args.all or args.extract_img:
        image_cache = analyze_images(inventory, limit=args.limit)

    summaries = None
    if args.all or args.summarize:
        summaries = summarize_all(pdf_cache, image_cache, limit=args.limit)

    if args.all or args.generate:
        generate_md(summaries or {}, image_cache or {})

    print("\n=== DONE ===")


if __name__ == "__main__":
    main()
