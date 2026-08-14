#!/usr/bin/env python3
"""
Daily Journal Automation
Creates daily note from template and updates session state.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

LWS = Path("C:/Users/Admin/My Drive/LifeWorkspace")
JOURNAL_DIR = LWS / "06_Journal_&_Reflections"
TEMPLATE = LWS / "Templates" / "Daily Note Template.md"
SESSION_STATE = LWS / ".session-state.json"

def create_daily_note():
    """Create today's daily note from template."""
    today = datetime.now(timezone.utc)
    filename = today.strftime("%Y-%m-%d") + ".md"
    target = JOURNAL_DIR / filename
    
    if target.exists():
        print(f"Daily note already exists: {filename}")
        return target
    
    # Read template
    if TEMPLATE.exists():
        content = TEMPLATE.read_text(encoding="utf-8")
        # Replace template variables
        content = content.replace("{{date:YYYY-MM-DD}}", today.strftime("%Y-%m-%d"))
        content = content.replace("{{date:YYYY}}", today.strftime("%Y"))
        content = content.replace("{{date:MM}}", today.strftime("%m"))
    else:
        content = f"""# {today.strftime('%Y-%m-%d')}

---

## Today's Focus

- **Project:**
- **Task:**
- **Priority:**

---

## Accomplished

- [ ]

---

## Insights

-

---

## Tomorrow

- [ ]

---

## Related

- [[Decision_Log]]
- [[Weekly_Plans]]
- [[Journal_Index]]

---

**Tags:** #daily-note #{today.strftime('%Y')} #{today.strftime('%m')}
"""
    
    target.write_text(content, encoding="utf-8")
    print(f"Created daily note: {filename}")
    return target

def update_session_state():
    """Update session state with current date."""
    if SESSION_STATE.exists():
        state = json.loads(SESSION_STATE.read_text(encoding="utf-8-sig"))
        state["last_session"] = datetime.now(timezone.utc).isoformat()
        SESSION_STATE.write_text(json.dumps(state, indent=4, ensure_ascii=False), encoding="utf-8")
        print("Updated session state")

if __name__ == "__main__":
    create_daily_note()
    update_session_state()
