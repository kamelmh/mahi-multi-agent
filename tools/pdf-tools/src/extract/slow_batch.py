"""Ultra-slow batch - 5 second delay between each API call."""
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
        result = summarize_text(data["text"][:2000], context=path)
        if result.get("success"):
            summaries[path] = {**result, "summarized_at": "now"}
            processed += 1
            print(f"OK {processed}/{len(remaining)}: {os.path.basename(path)[:40]}")
        else:
            err = str(result.get("error", ""))
            if "429" in err or "rate" in err.lower():
                print("Rate limited, waiting 60s...")
                time.sleep(60)
                continue
            print(f"Skip: {err[:40]}")
        time.sleep(5)
    except Exception as e:
        print(f"Error: {str(e)[:40]}")
        time.sleep(10)

with open(os.path.join(cache_dir, "summaries.json"), "w", encoding="utf-8") as f:
    json.dump(summaries, f, indent=2, ensure_ascii=False)

print(f"Done. New: {processed}, Total: {len(summaries)}")
