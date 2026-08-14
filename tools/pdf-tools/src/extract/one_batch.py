"""Process one PDF at a time, save immediately."""
import sys, time, json, os
sys.path.insert(0, os.path.dirname(__file__))

from summarizer import summarize_text

cache_dir = os.path.join(os.path.dirname(__file__), "cache")

with open(os.path.join(cache_dir, "pdf_extractions.json"), encoding="utf-8") as f:
    extractions = json.load(f)

with open(os.path.join(cache_dir, "summaries.json"), encoding="utf-8") as f:
    summaries = json.load(f)

remaining = [(p, d) for p, d in extractions.items() if p not in summaries and d.get("text")]
print(f"Remaining: {len(remaining)}")

if remaining:
    path, data = remaining[0]
    print(f"Processing: {path[:60]}")
    result = summarize_text(data["text"][:2000], context=path)
    if result.get("success"):
        summaries[path] = {**result, "summarized_at": "now"}
        print("OK")
    else:
        print(f"Failed: {result.get('error', 'unknown')[:80]}")
    
    with open(os.path.join(cache_dir, "summaries.json"), "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)
    print(f"Total: {len(summaries)}")
