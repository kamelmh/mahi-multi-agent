"""Quick batch - summarize remaining PDFs one at a time with delays."""
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

processed = 0
for path, data in remaining:
    try:
        result = summarize_text(data["text"][:3000], context=path)
        if result.get("success"):
            summaries[path] = {**result, "summarized_at": "now"}
            processed += 1
            print(f"  OK {processed}: {path[:60]}")
            time.sleep(2)
        else:
            err = str(result.get("error", ""))
            print(f"  FAIL: {err[:80]}")
            if "rate" in err.lower() or "429" in err:
                print("  Rate limited, waiting 30s...")
                time.sleep(30)
            else:
                time.sleep(3)
    except Exception as e:
        print(f"  ERROR: {str(e)[:80]}")
        time.sleep(5)

with open(os.path.join(cache_dir, "summaries.json"), "w", encoding="utf-8") as f:
    json.dump(summaries, f, indent=2, ensure_ascii=False)

print(f"\nDone. Processed: {processed}, Total: {len(summaries)}")
