"""Batch Processor - Runs extraction pipeline on all LifeWorkspace files.

Processes in batches to avoid API rate limits.
Saves progress to resume if interrupted.
"""

import os
import sys
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from pdf_extractor import extract_text
from image_analyzer import analyze_image
from summarizer import summarize_text

LW_ROOT = r"C:\Users\Admin\My Drive\LifeWorkspace"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")


def load_cache(filename):
    path = os.path.join(CACHE_DIR, filename)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(filename, data):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def batch_extract_pdfs(batch_size=20, delay=1):
    """Extract text from PDFs in batches."""
    # Also check output directory
    inv_path = os.path.join(OUTPUT_DIR, "file_inventory.json")
    if os.path.exists(inv_path):
        with open(inv_path, encoding="utf-8") as f:
            inventory = json.load(f)
    else:
        inventory = {}
    pdfs = inventory.get("pdfs", [])
    cache = load_cache("pdf_extractions.json")

    print(f"Total PDFs: {len(pdfs)}, Already cached: {len(cache)}")
    processed = 0

    for i, pdf_info in enumerate(pdfs):
        rel_path = pdf_info["path"]
        if rel_path in cache:
            continue

        full_path = os.path.join(LW_ROOT, rel_path)
        if not os.path.exists(full_path):
            continue

        try:
            result = extract_text(full_path, max_pages=5)
            cache[rel_path] = {
                "text": result.get("text", "")[:5000],  # Limit text size
                "pages": result.get("total_pages", 0),
                "metadata": result.get("metadata", {}),
                "extracted_at": datetime.now().isoformat(),
            }
            processed += 1

            if processed % batch_size == 0:
                save_cache("pdf_extractions.json", cache)
                print(f"  Processed {processed} PDFs (total cached: {len(cache)})")
                time.sleep(delay)

        except Exception as e:
            print(f"  Error: {rel_path[:50]}... - {e}")
            continue

    save_cache("pdf_extractions.json", cache)
    print(f"Batch complete: {processed} new PDFs extracted")
    return cache


def batch_summarize(batch_size=10, delay=2):
    """Summarize extracted PDF content."""
    cache = load_cache("pdf_extractions.json")
    summaries = load_cache("summaries.json")

    print(f"Total extracted: {len(cache)}, Already summarized: {len(summaries)}")
    processed = 0

    for path, data in cache.items():
        if path in summaries or not data.get("text"):
            continue

        try:
            result = summarize_text(data["text"], context=path)
            if result.get("success"):
                summaries[path] = {
                    **result,
                    "summarized_at": datetime.now().isoformat(),
                }
                processed += 1

                if processed % batch_size == 0:
                    save_cache("summaries.json", summaries)
                    print(f"  Summarized {processed} (total: {len(summaries)})")
                    time.sleep(delay)

        except Exception as e:
            print(f"  Error summarizing: {path[:50]}... - {e}")
            continue

    save_cache("summaries.json", summaries)
    print(f"Batch complete: {processed} new summaries")
    return summaries


def batch_analyze_images(batch_size=20, delay=1):
    """Analyze images in batches."""
    inv_path = os.path.join(OUTPUT_DIR, "file_inventory.json")
    if os.path.exists(inv_path):
        with open(inv_path, encoding="utf-8") as f:
            inventory = json.load(f)
    else:
        inventory = {}
    images = inventory.get("images", [])
    cache = load_cache("image_analysis.json")

    print(f"Total images: {len(images)}, Already cached: {len(cache)}")
    processed = 0

    for img_info in images:
        rel_path = img_info["path"]
        if rel_path in cache:
            continue

        full_path = os.path.join(LW_ROOT, rel_path)
        if not os.path.exists(full_path):
            continue

        try:
            result = analyze_image(full_path)
            cache[rel_path] = {
                **result,
                "analyzed_at": datetime.now().isoformat(),
            }
            processed += 1

            if processed % batch_size == 0:
                save_cache("image_analysis.json", cache)
                print(f"  Analyzed {processed} images (total: {len(cache)})")
                time.sleep(delay)

        except Exception as e:
            continue

    save_cache("image_analysis.json", cache)
    print(f"Batch complete: {processed} new images analyzed")
    return cache


def generate_all_md():
    """Generate comprehensive MD files from all cached data."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    summaries = load_cache("summaries.json")
    image_cache = load_cache("image_analysis.json")

    # Generate PDF summaries MD
    if summaries:
        categories = {}
        for path, summary in summaries.items():
            cat = summary.get("category", "other")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append({"path": path, **summary})

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

    # Generate image summary MD
    if image_cache:
        img_md = os.path.join(OUTPUT_DIR, "images_summary.md")
        lines = ["# Image Analysis\n"]
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        lines.append(f"Total: {len(image_cache)} images\n\n")

        img_cats = {}
        for path, data in image_cache.items():
            cat = data.get("category", "unknown")
            if cat not in img_cats:
                img_cats[cat] = []
            img_cats[cat].append({"path": path, **data})

        for cat, items in img_cats.items():
            lines.append(f"## {cat.title()} ({len(items)})\n")
            for item in items[:10]:
                lines.append(f"- `{item['path']}` ({item.get('width', '?')}x{item.get('height', '?')})")
            if len(items) > 10:
                lines.append(f"- ... and {len(items)-10} more")
            lines.append("")

        with open(img_md, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    # Generate master index
    index_path = os.path.join(OUTPUT_DIR, "00-INDEX.md")
    lines = ["# Knowledge Base Index\n"]
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    lines.append(f"PDFs summarized: {len(summaries)}\n")
    lines.append(f"Images analyzed: {len(image_cache)}\n\n")

    lines.append("## Categories\n")
    for cat in sorted(set(s.get("category", "other") for s in summaries.values())):
        count = sum(1 for s in summaries.values() if s.get("category") == cat)
        lines.append(f"- **{cat.title()}:** {count} documents")

    lines.append("\n## Files\n")
    for f in sorted(os.listdir(OUTPUT_DIR)):
        if f.endswith(".md"):
            lines.append(f"- [[{f[:-3]}]]")

    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Generated MD files in: {OUTPUT_DIR}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract", action="store_true")
    parser.add_argument("--summarize", action="store_true")
    parser.add_argument("--images", action="store_true")
    parser.add_argument("--md", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--batch", type=int, default=20)
    args = parser.parse_args()

    if args.all or args.extract:
        batch_extract_pdfs(batch_size=args.batch)
    if args.all or args.summarize:
        batch_summarize(batch_size=args.batch)
    if args.all or args.images:
        batch_analyze_images(batch_size=args.batch)
    if args.all or args.md:
        generate_all_md()
