#!/usr/bin/env python3
"""
Weekly Review Automation
Creates weekly review note and updates journal index.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

LWS = Path("C:/Users/Admin/My Drive/LifeWorkspace")
JOURNAL_DIR = LWS / "06_Journal_&_Reflections"
TEMPLATE = LWS / "Templates" / "Weekly Review Template.md"
INDEX = JOURNAL_DIR / "Journal_Index.md"

def create_weekly_review():
    """Create this week's review note from template."""
    today = datetime.now(timezone.utc)
    week_num = today.isocalendar()[1]
    filename = f"Week-{today.year}-W{week_num:02d}.md"
    target = JOURNAL_DIR / filename
    
    if target.exists():
        print(f"Weekly review already exists: {filename}")
        return target
    
    # Read template
    if TEMPLATE.exists():
        content = TEMPLATE.read_text(encoding="utf-8")
        content = content.replace("{{date:YYYY-WW}}", f"{today.year}-W{week_num:02d}")
        content = content.replace("{{date:YYYY-MM-DD}}", today.strftime("%Y-%m-%d"))
        content = content.replace("{{date:YYYY}}", str(today.year))
    else:
        content = f"""# Weekly Review — {today.year}-W{week_num:02d}

---

## Week of {today.strftime('%Y-%m-%d')}

### Accomplished

-

### Challenges

-

### Insights

-

---

## Next Week

### Goals

- [ ]

### Tasks

- [ ]

---

## Related

- [[Weekly_Plans]]
- [[Decision_Log]]
- [[Time_Management]]

---

**Tags:** #weekly-review #{today.year}
"""
    
    target.write_text(content, encoding="utf-8")
    print(f"Created weekly review: {filename}")
    return target

def update_journal_index():
    """Add weekly review to journal index."""
    today = datetime.now(timezone.utc)
    week_num = today.isocalendar()[1]
    week_link = f"Week-{today.year}-W{week_num:02d}"
    
    if INDEX.exists():
        content = INDEX.read_text(encoding="utf-8")
        if week_link not in content:
            # Add to current year section
            year_header = f"## {today.year}"
            if year_header in content:
                # Find the year section and add after it
                lines = content.split("\n")
                new_lines = []
                found_year = False
                for line in lines:
                    new_lines.append(line)
                    if line.strip() == year_header:
                        found_year = True
                    elif found_year and line.strip().startswith("### "):
                        # Add before the first month header
                        new_lines.insert(-1, f"- [[{week_link}]]")
                        break
                content = "\n".join(new_lines)
            else:
                # Add new year section
                content += f"\n\n## {today.year}\n\n- [[{week_link}]]\n"
            INDEX.write_text(content, encoding="utf-8")
            print("Updated Journal Index")

if __name__ == "__main__":
    create_weekly_review()
    update_journal_index()
