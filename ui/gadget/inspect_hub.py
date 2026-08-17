"""Full Playwright inspection of the Dashboard Hub gadget.

Covers: all nav tabs, Dashboard Hub (cards/launch/stop/log/iframe), search,
keyboard shortcuts, quick capture, responsive views, console errors.
"""
import asyncio
import json
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "http://127.0.0.1:8000"
SHOTS = Path(r"C:\Users\Admin\projects\active\agents\mahi-multi-agent\ui\gadget\screenshots\inspect")
SHOTS.mkdir(parents=True, exist_ok=True)

CONSOLE_ERRORS = []
PAGE_ERRORS = []


async def shot(page, name):
    await page.screenshot(path=str(SHOTS / f"{name}.png"), full_page=False)
    print(f"  [shot] {name}")


async def click_tab(page, label):
    try:
        await page.click(f"button:has-text('{label}')")
        await page.wait_for_timeout(900)
        return True
    except Exception as e:
        print(f"  [!!] tab '{label}' failed: {e}")
        return False


async def inspect_tab(page, label, selectors, report, key):
    """Click tab, count selectors, screenshot."""
    if not await click_tab(page, label):
        report[key] = {"visited": False}
        return
    counts = {}
    for name, sel in selectors.items():
        try:
            els = await page.query_selector_all(sel)
            counts[name] = len(els)
        except Exception:
            counts[name] = -1
    print(f"  {label}: {counts}")
    report[key] = {"visited": True, **counts}
    await shot(page, f"tab_{label.lower().replace(' ', '_')}")


async def main():
    report = {"apps": {}, "hub": {}, "interactive": {}, "responsive": {}, "errors": {"console": [], "page": []}}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1600, "height": 900})
        page = await context.new_page()

        page.on("console", lambda msg: CONSOLE_ERRORS.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: PAGE_ERRORS.append(str(exc)))

        await page.goto(BASE, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        # ---- Overview ----
        stats = await page.query_selector_all(".stat")
        print(f"Overview stats: {len(stats)}")
        for s in stats:
            try:
                lbl = await s.query_selector(".stat-label")
                val = await s.query_selector(".stat-value")
                print(f"    {(await lbl.inner_text() if lbl else '?')}: {(await val.inner_text() if val else '?')}")
            except Exception:
                pass
        report["apps"]["overview_stats"] = len(stats)
        await shot(page, "00_overview")

        # ---- All tabs inventory ----
        nav_btns = await page.query_selector_all(".nav-btn")
        labels = []
        for b in nav_btns:
            labels.append((await b.inner_text()).strip())
        print(f"\nNav tabs ({len(labels)}): {', '.join(labels)}")
        report["apps"]["tabs"] = labels

        # ---- Dashboard Hub deep dive ----
        await click_tab(page, "Dashboard Hub")
        await page.wait_for_timeout(2000)
        await shot(page, "01_hub")

        cards = await page.query_selector_all(".hub-app-card")
        print(f"\nHub app cards: {len(cards)}")
        report["hub"]["card_count"] = len(cards)

        for c in cards:
            try:
                name = await c.query_selector(".hub-app-name")
                status = await c.query_selector(".hub-app-status")
                desc = await c.query_selector(".hub-app-desc")
                btns = await c.query_selector_all(".hub-app-actions .hub-btn")
                texts = [(await b.inner_text()).strip() for b in btns]
                print(f"  {(await name.inner_text() if name else '?'):<22} {(await status.inner_text() if status else '?'):<9} :: {', '.join(texts)}")
            except Exception as e:
                print(f"  card error: {e}")

        # status colors
        colors = await page.evaluate("""() => {
            const out = {};
            document.querySelectorAll('.hub-app-status').forEach(s => {
                const cls = s.className.split(' ').pop();
                out[cls] = getComputedStyle(s).backgroundColor;
            });
            return out;
        }""")
        print(f"Status badge colors: {colors}")
        report["hub"]["badge_colors"] = colors

        # --- Log view (stopped app) ---
        try:
            log_btn = await page.query_selector(".hub-app-card .hub-btn:has-text('Log')")
            if log_btn:
                await log_btn.click()
                await page.wait_for_timeout(800)
                await shot(page, "02_hub_log")
                modal_visible = await page.evaluate("() => !!document.querySelector('.hub-modal, [class*=modal]') && getComputedStyle(document.querySelector('.hub-modal, [class*=modal]')).display !== 'none'")
                print(f"Log modal visible: {modal_visible}")
                report["hub"]["log_modal"] = modal_visible
                # close modal (Escape)
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(400)
        except Exception as e:
            print(f"log view: {e}")

        # --- iframe embed (running app: teaching) ---
        try:
            teach_card = await page.query_selector(".hub-app-card:has-text('Teaching Platform')")
            if teach_card:
                await teach_card.click()
                await page.wait_for_timeout(2500)
                iframe = await page.query_selector("#hub-iframe")
                vis = await page.evaluate("() => { const f = document.getElementById('hub-iframe'); return f && getComputedStyle(f).display !== 'none'; }")
                print(f"iframe embedded: {vis}")
                report["hub"]["iframe_embed"] = vis
                await shot(page, "03_hub_iframe")
                close_btn = await page.query_selector("#hub-iframe-close, button:has-text('Close')")
                if close_btn:
                    await close_btn.click()
                    await page.wait_for_timeout(500)
                    print("iframe closed")
        except Exception as e:
            print(f"iframe: {e}")

        # --- Stop + relaunch test (teaching) ---
        try:
            stop_btn = await page.query_selector(".hub-app-card:has-text('Teaching Platform') button:has-text('Stop')")
            if stop_btn:
                await stop_btn.click()
                await page.wait_for_timeout(2000)
                st = await page.evaluate("""() => {
                    const cards = [...document.querySelectorAll('.hub-app-card')];
                    const c = cards.find(x => x.innerText.includes('Teaching Platform'));
                    return c ? c.querySelector('.hub-app-status').innerText : '?';
                }""")
                print(f"After Stop -> Teaching status: {st}")
                report["hub"]["stop_test"] = st
                await shot(page, "04_hub_after_stop")
                # relaunch
                await page.click(".hub-app-card:has-text('Teaching Platform') button:has-text('Launch')")
                await page.wait_for_timeout(6000)
                await page.click("button:has-text('Dashboard Hub')")
                await page.wait_for_timeout(2500)
                st2 = await page.evaluate("""() => {
                    const cards = [...document.querySelectorAll('.hub-app-card')];
                    const c = cards.find(x => x.innerText.includes('Teaching Platform'));
                    return c ? c.querySelector('.hub-app-status').innerText : '?';
                }""")
                print(f"After Relaunch -> Teaching status: {st2}")
                report["hub"]["relaunch_test"] = st2
                await shot(page, "05_hub_after_relaunch")
        except Exception as e:
            print(f"stop/relaunch: {e}")

        # ---- Other tabs ----
        tabs_to_visit = [
            ("Overview", {".stat": ".stat"}),
            ("Graph", {"canvas": "#graph-canvas", "count": "#graph-count"}),
            ("Journal", {".journal-entry": ".journal-entry"}),
            ("Notes", {"#notes-list .recent-item": "#notes-list .recent-item"}),
            ("Tags", {".tag-pill": ".tag-pill"}),
            ("Inbox", {".inbox-item": ".inbox-item"}),
            ("Bookmarks", {"#bookmarks-list .recent-item": "#bookmarks-list .recent-item"}),
            ("Recent", {"#recent-list .recent-item": "#recent-list .recent-item"}),
            ("History", {".version-item": ".version-item"}),
            ("Templates", {".template-card": ".template-card"}),
            ("Training", {"#training-list .project-card": "#training-list .project-card"}),
            ("Agents", {"#agents-grid-full .project-card": "#agents-grid-full .project-card"}),
            ("Agent Control", {".agent-control-card": ".agent-control-card", ".squad-group": ".squad-group"}),
            ("Autopilots", {".autopilot-card": ".autopilot-card", ".toggle-switch input": ".toggle-switch input"}),
            ("Goals", {".goal-card": ".goal-card", ".goal-task": ".goal-task"}),
            ("Skills", {"#skills-grid .project-card": "#skills-grid .project-card"}),
            ("Projects", {".project-card": "#projects-grid .project-card"}),
            ("Academix", {"iframe": "iframe"}),
        ]
        print("\n--- Tab inventory ---")
        for label, sels in tabs_to_visit:
            key = label.lower().replace(" ", "_")
            await inspect_tab(page, label, sels, report["apps"], key)

        # ---- Interactive: search ----
        print("\n--- Search ---")
        await click_tab(page, "Overview")
        search = page.locator("#search")
        await search.fill("CCA-F")
        await page.wait_for_timeout(600)
        dimmed = await page.evaluate("""() => {
            const items = document.querySelectorAll('.project-card, .recent-item, .inbox-item, .tag-pill, .template-card');
            let n = 0;
            items.forEach(i => { if (i.style.opacity === '0.3') n++; });
            return n;
        }""")
        print(f"Search 'CCA-F' dimmed items: {dimmed}")
        report["interactive"]["search_dimmed"] = dimmed
        await shot(page, "06_search")
        await search.fill("")
        await page.keyboard.press("Escape")

        # ---- Interactive: quick capture ----
        try:
            cap = page.locator("#capture-input")
            await cap.fill("Inspection test capture")
            await page.click("button:has-text('Save')")
            await page.wait_for_timeout(600)
            print("Quick capture: executed")
            report["interactive"]["quick_capture"] = True
        except Exception as e:
            print(f"quick capture: {e}")

        # ---- Interactive: keyboard shortcuts ----
        print("\n--- Keyboard shortcuts ---")
        for k, tab_id, name in [("Control+i", "inbox", "Ctrl+I"), ("Control+j", "journal", "Ctrl+J")]:
            await page.keyboard.press(k)
            await page.wait_for_timeout(500)
            visible = await page.evaluate(f"() => !document.getElementById('{tab_id}').classList.contains('hidden')")
            print(f"{name} -> {tab_id} visible: {visible}")
            report["interactive"][f"shortcut_{tab_id}"] = visible

        # ---- Responsive ----
        print("\n--- Responsive ---")
        for w, h, name in [(375, 812, "mobile"), (768, 1024, "tablet")]:
            await page.set_viewport_size({"width": w, "height": h})
            await page.wait_for_timeout(700)
            await click_tab(page, "Overview")
            nav_vis = await page.evaluate("() => { const n = document.getElementById('main-nav'); return getComputedStyle(n).display !== 'none'; }")
            print(f"{name} ({w}x{h}): nav visible={nav_vis}")
            report["responsive"][name] = {"nav_visible": nav_vis}
            await shot(page, f"07_{name}")
        await page.set_viewport_size({"width": 1600, "height": 900})

        # ---- API parity ----
        try:
            data = json.loads(urllib.request.urlopen(f"{BASE}/api/apps", timeout=20).read())
            report["hub"]["api"] = [(a["id"], a["status"]) for a in data.get("apps", [])]
            print("\nAPI:", report["hub"]["api"])
        except Exception as e:
            print("api probe:", e)

        report["errors"]["console"] = CONSOLE_ERRORS
        report["errors"]["page"] = PAGE_ERRORS
        await browser.close()

    (SHOTS / "inspection_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n=== DONE ===")
    print(f"Console errors: {len(CONSOLE_ERRORS)}")
    for e in CONSOLE_ERRORS[:5]:
        print("   ", e[:150])
    print(f"Page errors: {len(PAGE_ERRORS)}")
    for e in PAGE_ERRORS[:5]:
        print("   ", e[:150])
    print(f"Report: {SHOTS / 'inspection_report.json'}")


if __name__ == "__main__":
    from playwright.async_api import async_playwright
    asyncio.run(main())