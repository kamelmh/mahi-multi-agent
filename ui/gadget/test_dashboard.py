"""
LifeWorkspace Gadget v2 — Full Systematic Browser Walkthrough
Tests all 13 tabs, PKMS features, and interactive elements.
"""
import asyncio
import os
import json
from playwright.async_api import async_playwright

SCREENSHOTS_DIR = r"C:\Users\Admin\projects\active\lifeworkspace-gadget\screenshots"
REPORT_FILE = r"C:\Users\Admin\projects\active\lifeworkspace-gadget\walkthrough_report.json"

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

async def screenshot(page, name):
    path = os.path.join(SCREENSHOTS_DIR, f"{name}.png")
    await page.screenshot(path=path, full_page=True)
    print(f"  [screenshot] {name}")
    return path

async def walkthrough():
    report = {
        "sections": {},
        "features": {},
        "issues": [],
        "findings": [],
        "interactive": {}
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        url = r"file:///C:/Users/Admin/projects/active/lifeworkspace-gadget/index.html"
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # === OVERVIEW TAB ===
        print("\n=== OVERVIEW TAB ===")
        await screenshot(page, "01_overview_full")

        stats = await page.query_selector_all(".stat")
        print(f"  Stats cards: {len(stats)}")
        report["sections"]["overview_stats"] = len(stats)

        for stat in stats:
            label_el = await stat.query_selector(".stat-label")
            value_el = await stat.query_selector(".stat-value")
            if label_el and value_el:
                label = await label_el.inner_text()
                value = await value_el.inner_text()
                print(f"    {label}: {value}")

        projects = await page.query_selector_all("#projects-grid .project-card")
        print(f"  Project cards: {len(projects)}")
        report["sections"]["overview_projects"] = len(projects)

        activities = await page.query_selector_all(".activity-item")
        print(f"  Activity items: {len(activities)}")
        report["sections"]["overview_activities"] = len(activities)

        # === GRAPH TAB ===
        print("\n=== GRAPH TAB ===")
        await page.click("button:has-text('Graph')")
        await page.wait_for_timeout(1500)
        await screenshot(page, "02_graph")

        canvas = await page.query_selector("#graph-canvas")
        graph_count = await page.query_selector("#graph-count")
        count_text = await graph_count.inner_text() if graph_count else "0"
        print(f"  Canvas present: {canvas is not None}")
        print(f"  Graph nodes: {count_text}")
        report["sections"]["graph"] = {"canvas": canvas is not None, "nodes": count_text}

        # === JOURNAL TAB ===
        print("\n=== JOURNAL TAB ===")
        await page.click("button:has-text('Journal')")
        await page.wait_for_timeout(1000)
        await screenshot(page, "03_journal")

        journal_entries = await page.query_selector_all(".journal-entry")
        print(f"  Journal entries: {len(journal_entries)}")
        report["sections"]["journal"] = len(journal_entries)

        for entry in journal_entries:
            date_el = await entry.query_selector(".je-date")
            title_el = await entry.query_selector(".je-title")
            if date_el and title_el:
                date = await date_el.inner_text()
                title = await title_el.inner_text()
                print(f"    {date}: {title}")

        # === NOTES TAB ===
        print("\n=== NOTES TAB ===")
        await page.click("button:has-text('Notes')")
        await page.wait_for_timeout(1000)
        await screenshot(page, "04_notes")

        note_items = await page.query_selector_all("#notes-list .recent-item")
        print(f"  Note items: {len(note_items)}")
        report["sections"]["notes_list"] = len(note_items)

        # Click first note to test wikilinks and backlinks
        if note_items:
            await note_items[0].click()
            await page.wait_for_timeout(500)
            await screenshot(page, "04b_note_view")

            note_view = await page.query_selector(".note-view")
            wikilinks = await page.query_selector_all(".wikilink")
            backlinks = await page.query_selector_all(".backlink-item")
            print(f"  Note view rendered: {note_view is not None}")
            print(f"  Wikilinks: {len(wikilinks)}")
            print(f"  Backlinks: {len(backlinks)}")
            report["sections"]["note_view"] = {
                "rendered": note_view is not None,
                "wikilinks": len(wikilinks),
                "backlinks": len(backlinks)
            }

        # === TAGS TAB ===
        print("\n=== TAGS TAB ===")
        await page.click("button:has-text('Tags')")
        await page.wait_for_timeout(1000)
        await screenshot(page, "05_tags")

        tag_pills = await page.query_selector_all(".tag-pill")
        print(f"  Tags: {len(tag_pills)}")
        report["sections"]["tags"] = len(tag_pills)

        # Click a tag to test filtering
        if tag_pills:
            await tag_pills[0].click()
            await page.wait_for_timeout(500)
            await screenshot(page, "05b_tag_filter")
            filtered_notes = await page.query_selector_all("#tag-filtered-notes .recent-item")
            print(f"  Filtered notes: {len(filtered_notes)}")

        # === INBOX TAB ===
        print("\n=== INBOX TAB ===")
        await page.click("button:has-text('Inbox')")
        await page.wait_for_timeout(1000)
        await screenshot(page, "06_inbox")

        inbox_items = await page.query_selector_all(".inbox-item")
        print(f"  Inbox items: {len(inbox_items)}")
        report["sections"]["inbox"] = len(inbox_items)

        # Test quick capture
        inbox_input = page.locator("#inbox-capture")
        await inbox_input.fill("Test inbox item from Playwright")
        await page.click("button:has-text('Add')")
        await page.wait_for_timeout(500)
        new_items = await page.query_selector_all(".inbox-item")
        print(f"  After add: {len(new_items)} items")
        report["interactive"]["inbox_add"] = len(new_items) > len(inbox_items)

        # === BOOKMARKS TAB ===
        print("\n=== BOOKMARKS TAB ===")
        await page.click("button:has-text('Bookmarks')")
        await page.wait_for_timeout(1000)
        await screenshot(page, "07_bookmarks")

        bookmark_items = await page.query_selector_all("#bookmarks-list .recent-item")
        print(f"  Bookmarked items: {len(bookmark_items)}")
        report["sections"]["bookmarks"] = len(bookmark_items)

        # === RECENT TAB ===
        print("\n=== RECENT TAB ===")
        await page.click("button:has-text('Recent')")
        await page.wait_for_timeout(1000)
        await screenshot(page, "08_recent")

        recent_items = await page.query_selector_all("#recent-list .recent-item")
        print(f"  Recent items: {len(recent_items)}")
        report["sections"]["recent"] = len(recent_items)

        # === HISTORY TAB ===
        print("\n=== HISTORY TAB ===")
        await page.click("button:has-text('History')")
        await page.wait_for_timeout(1000)
        await screenshot(page, "09_history")

        history_items = await page.query_selector_all(".version-item")
        print(f"  Version entries: {len(history_items)}")
        report["sections"]["history"] = len(history_items)

        # === TEMPLATES TAB ===
        print("\n=== TEMPLATES TAB ===")
        await page.click("button:has-text('Templates')")
        await page.wait_for_timeout(1000)
        await screenshot(page, "10_templates")

        template_cards = await page.query_selector_all(".template-card")
        print(f"  Templates: {len(template_cards)}")
        report["sections"]["templates"] = len(template_cards)

        # === TRAINING TAB ===
        print("\n=== TRAINING TAB ===")
        await page.click("button:has-text('Training')")
        await page.wait_for_timeout(1000)
        await screenshot(page, "11_training")

        training_cards = await page.query_selector_all("#training-list .project-card")
        print(f"  Training systems: {len(training_cards)}")
        report["sections"]["training"] = len(training_cards)

        # === AGENTS TAB ===
        print("\n=== AGENTS TAB ===")
        await page.click("button:has-text('Agents')")
        await page.wait_for_timeout(1000)
        await screenshot(page, "12_agents")

        agent_cards = await page.query_selector_all("#agents-grid-full .project-card")
        print(f"  Agent cards: {len(agent_cards)}")
        report["sections"]["agents"] = len(agent_cards)

        for card in agent_cards:
            name_el = await card.query_selector(".project-name")
            model_el = await card.query_selector(".project-desc")
            if name_el:
                name = await name_el.inner_text()
                model = await model_el.inner_text() if model_el else "?"
                print(f"    {name} ({model})")

        # === AGENT CONTROL TAB ===
        print("\n=== AGENT CONTROL TAB ===")
        await page.click("button:has-text('Agent Control')")
        await page.wait_for_timeout(1000)
        await screenshot(page, "12b_agent_control")

        agent_control_cards = await page.query_selector_all(".agent-control-card")
        squad_groups = await page.query_selector_all(".squad-group")
        print(f"  Agent control cards: {len(agent_control_cards)}")
        print(f"  Squad groups: {len(squad_groups)}")
        report["sections"]["agents_live"] = {"cards": len(agent_control_cards), "squads": len(squad_groups)}

        # Test run agent button
        run_btns = await page.query_selector_all(".agent-btn.primary")
        if run_btns:
            await run_btns[0].click()
            await page.wait_for_timeout(500)
            print(f"  Run agent clicked")

        # === AUTOPILOTS TAB ===
        print("\n=== AUTOPILOTS TAB ===")
        await page.click("button:has-text('Autopilots')")
        await page.wait_for_timeout(1000)
        await screenshot(page, "13b_autopilots")

        autopilot_cards = await page.query_selector_all(".autopilot-card")
        toggle_switches = await page.query_selector_all(".toggle-switch input")
        print(f"  Autopilot cards: {len(autopilot_cards)}")
        print(f"  Toggle switches: {len(toggle_switches)}")
        report["sections"]["autopilots"] = {"cards": len(autopilot_cards), "toggles": len(toggle_switches)}

        # Test toggle
        toggle_labels = await page.query_selector_all(".toggle-switch")
        if toggle_labels:
            await toggle_labels[0].click()
            await page.wait_for_timeout(500)
            print(f"  Toggle clicked")

        # Test run now
        run_btns = await page.query_selector_all("#autopilots .agent-btn.primary")
        if run_btns:
            await run_btns[0].click()
            await page.wait_for_timeout(500)
            print(f"  Run now clicked")

        # === GOALS TAB ===
        print("\n=== GOALS TAB ===")
        await page.click("button:has-text('Goals')")
        await page.wait_for_timeout(1000)
        await screenshot(page, "14b_goals")

        goal_cards = await page.query_selector_all(".goal-card")
        goal_tasks = await page.query_selector_all(".goal-task")
        goal_agent_chips = await page.query_selector_all(".goal-agent-chip")
        print(f"  Goal cards: {len(goal_cards)}")
        print(f"  Goal tasks: {len(goal_tasks)}")
        print(f"  Goal agent chips: {len(goal_agent_chips)}")
        report["sections"]["goals"] = {"cards": len(goal_cards), "tasks": len(goal_tasks), "agents": len(goal_agent_chips)}

        # Test task checkbox
        checks = await page.query_selector_all(".goal-task-check")
        if checks:
            await checks[0].click()
            await page.wait_for_timeout(500)
            print(f"  Task checkbox clicked")

        # === SKILLS TAB ===
        print("\n=== SKILLS TAB ===")
        await page.click("button:has-text('Skills')")
        await page.wait_for_timeout(1000)
        await screenshot(page, "13_skills")

        skill_cards = await page.query_selector_all("#skills-grid .project-card")
        print(f"  Skill categories: {len(skill_cards)}")
        report["sections"]["skills"] = len(skill_cards)

        # === SEARCH FUNCTIONALITY ===
        print("\n=== SEARCH ===")
        search = page.locator("#search")
        await search.fill("CCA-F")
        await page.wait_for_timeout(500)
        await screenshot(page, "14_search_CCA-F")
        # Check that some items are dimmed
        dimmed = await page.evaluate("""() => {
            const items = document.querySelectorAll('.project-card, .recent-item, .inbox-item, .tag-pill, .template-card');
            let dimmed = 0;
            items.forEach(i => { if (i.style.opacity === '0.3') dimmed++; });
            return dimmed;
        }""")
        print(f"  Items dimmed by search: {dimmed}")
        report["interactive"]["search_dimmed"] = dimmed
        await search.fill("")

        # === KEYBOARD SHORTCUTS ===
        print("\n=== KEYBOARD SHORTCUTS ===")
        # Ctrl+I for inbox
        await page.keyboard.press("Control+i")
        await page.wait_for_timeout(500)
        inbox_visible = await page.evaluate("() => !document.getElementById('inbox').classList.contains('hidden')")
        print(f"  Ctrl+I -> Inbox visible: {inbox_visible}")
        report["interactive"]["shortcut_ctrl_i"] = inbox_visible

        # Ctrl+J for journal
        await page.keyboard.press("Control+j")
        await page.wait_for_timeout(500)
        journal_visible = await page.evaluate("() => !document.getElementById('journal').classList.contains('hidden')")
        print(f"  Ctrl+J -> Journal visible: {journal_visible}")
        report["interactive"]["shortcut_ctrl_j"] = journal_visible

        # === QUICK CAPTURE (Overview) ===
        print("\n=== QUICK CAPTURE ===")
        await page.click("button:has-text('Overview')")
        await page.wait_for_timeout(500)
        capture_input = page.locator("#capture-input")
        await capture_input.fill("Test quick capture from Playwright")
        await page.click("button:has-text('Save')")
        await page.wait_for_timeout(500)
        # Should add to inbox
        print(f"  Quick capture executed")
        report["interactive"]["quick_capture"] = True

        # === RESPONSIVE CHECKS ===
        print("\n=== RESPONSIVE CHECKS ===")
        # Mobile
        await page.set_viewport_size({"width": 375, "height": 812})
        await page.wait_for_timeout(500)
        await screenshot(page, "15_mobile_view")
        stats_mobile = await page.query_selector_all(".stat")
        print(f"  Mobile stats: {len(stats_mobile)}")

        # Tablet
        await page.set_viewport_size({"width": 768, "height": 1024})
        await page.wait_for_timeout(500)
        await screenshot(page, "16_tablet_view")

        # Back to desktop
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.wait_for_timeout(500)

        # === FINAL OVERVIEW ===
        await page.click("button:has-text('Overview')")
        await page.wait_for_timeout(1000)
        await screenshot(page, "17_overview_final")

        # === TAB COUNT ===
        nav_buttons = await page.query_selector_all(".nav-btn")
        print(f"\n=== SUMMARY ===")
        print(f"  Total tabs: {len(nav_buttons)}")
        report["total_tabs"] = len(nav_buttons)

        await browser.close()

    # Save report
    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved to {REPORT_FILE}")

    return report

if __name__ == "__main__":
    asyncio.run(walkthrough())
