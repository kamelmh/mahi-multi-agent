"""Resilient batch processor - handles rate limits with exponential backoff."""
import json, os, time, sys
sys.path.insert(0, os.path.dirname(__file__))
from summarizer import summarize_text

cache_dir = os.path.join(os.path.dirname(__file__), "cache")
summaries_path = os.path.join(cache_dir, "summaries.json")

def load():
    with open(os.path.join(cache_dir, "pdf_extractions.json"), encoding="utf-8") as f:
        extractions = json.load(f)
    with open(summaries_path, encoding="utf-8") as f:
        summaries = json.load(f)
    remaining = [(p, d) for p, d in extractions.items() if p not in summaries and d.get("text")]
    return extractions, summaries, remaining

def save(summaries):
    with open(summaries_path, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)

def run_batch(target=50, delay=20, max_retries=3):
    extractions, summaries, remaining = load()
    total = len(remaining)
    print(f"Starting batch: {total} remaining, target {target}")
    
    processed = 0
    failed = 0
    consecutive_fails = 0
    
    for i in range(min(target, total)):
        path, data = remaining[i]
        short = os.path.basename(path)[:50]
        
        retries = 0
        while retries < max_retries:
            print(f'[{i+1}/{min(target, total)}] {short}...', end=' ', flush=True)
            result = summarize_text(data['text'][:2000], context=path)
            
            if result.get('success'):
                summaries[path] = {**result, 'summarized_at': '2026-07-14'}
                print('OK')
                processed += 1
                consecutive_fails = 0
                save(summaries)
                break
            else:
                err = result.get('error', 'unknown')[:80]
                if '429' in err:
                    wait = delay * (2 ** retries)
                    print(f'RATE LIMIT (wait {wait}s)')
                    time.sleep(wait)
                    retries += 1
                    consecutive_fails += 1
                else:
                    print(f'FAIL: {err}')
                    failed += 1
                    consecutive_fails += 1
                    break
        
        if consecutive_fails >= 5:
            print("Too many consecutive failures, stopping.")
            break
        
        time.sleep(delay)
    
    save(summaries)
    _, _, new_remaining = load()
    print(f"\nBatch complete: {processed} OK, {failed} fail")
    print(f"Total: {len(summaries)}/786 | Remaining: {len(new_remaining)}")

if __name__ == "__main__":
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    delay = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    run_batch(target=target, delay=delay)
