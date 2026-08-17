"""Playwright walkthrough of the Dashboard Hub (http://127.0.0.1:8000)."""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

SHOTS = Path(r"C:\Users\Admin\projects\active\agents\mahi-multi-agent\ui\gadget\screenshots")
SHOTS.mkdir(exist_ok=True)

async def shot(page, name):
    await page.screenshot(path=str(SHOTS / f"hub_{name}.png"), full_page=False)
    print(f"  [shot] {name}")

async def main():
    report = {"tabs": {}, "hub": {}, "issues": []}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 900})
        await page.goto("http://127.0.0.1:8000", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)
        await shot(page, "00_overview")

        # Count nav tabs
        nav_btns = await page.query_selector_all(".nav-btn")
        print(f"Nav tabs: {len(nav_btns)}")
        report["tabs"]["count"] = len(nav_btns)

        # === Dashboard Hub tab ===
        try:
            await page.click("button:has-text('Dashboard Hub')")
        except Exception as e:
            report["issues"].append(f"hub tab click: {e}")
        await page.wait_for_timeout(2500)
        await shot(page, "01_hub")

        # App cards
        cards = await page.query_selector_all(".app-card, [class*=app-card]")
        print(f"App cards: {len(cards)}")
        report["hub"]["app_cards"] = len(cards)

        for card in cards:
            try:
                name_el = await card.query_selector(".app-name, h3")
                status_el = await card.query_selector(".status-badge, [class*=status]")
                name = await name_el.inner_text() if name_el else "?"
                status = await status_el.inner_text() if status_el else "?"
                print(f"  {name:<22} -> {status}")
            except Exception:
                pass

        # Click Launch on first stopped app
        launch_btns = await page.query_selector_all("button:has-text('Launch')")
        print(f"Launch buttons: {len(launch_btns)}")
        report["hub"]["launch_buttons"] = len(launch_btns)
        if launch_btns:
            await launch_btns[0].click()
            await page.wait_for_timeout(1500)
            await shot(page, "02_hub_after_launch")
            await page.reload(wait_until="networkidle")
            await page.wait_for_timeout(2000)
            await page.click("button:has-text('Dashboard Hub')")
            await page.wait_for_timeout(1500)
            await shot(page, "03_hub_reloaded")

        # Check status of each app via API
        import urllib.request
        data = json.loads(urllib.request.urlopen("http://127.0.0.1:8000/api/apps", timeout=20).read())
        report["hub"]["api_apps"] = [
            {"id": a["id"], "status": a["status"], "running": a["running"]}
            for a in data.get("apps", [])
        ]
        print("API status:")
        for a in report["hub"]["api_apps"]:
            print(f"  {a['id']:<18} {a['status']}")

        # Walk a few other key tabs
        for tab in ["Agents", "Agent Control", "Projects", "Skills"]:
            try:
                await page.click(f"button:has-text('{tab}')")
                await page.wait_for_timeout(1200)
                await shot(page, f"04_{tab.lower().replace(' ', '_')}")
                print(f"  visited tab: {tab}")
            except Exception as e:
                report["issues"].append(f"tab {tab}: {e}")

        await browser.close()

    SHOTS.mkdir(exist_ok=True)
    (SHOTS / "hub_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nReport: {SHOTS / 'hub_report.json'}")
    print(f"Issues: {len(report['issues'])}")

asyncio.run(main())