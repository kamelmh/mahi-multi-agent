#!/usr/bin/env python3
"""
Session Auto-Save
Automatically saves session state and archives to session store.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

LWS = Path("C:/Users/Admin/My Drive/LifeWorkspace")
SESSION_STATE = LWS / ".session-state.json"
SESSIONS_DIR = LWS / "15_Advanced_Tools" / "sessions"
SESSION_INDEX = SESSIONS_DIR / "index.json"

def auto_save_session():
    """Auto-save current session state."""
    if not SESSION_STATE.exists():
        print("No session state to save")
        return
    
    state = json.loads(SESSION_STATE.read_text(encoding="utf-8-sig"))
    
    # Update timestamp
    state["last_session"] = datetime.now(timezone.utc).isoformat()
    
    # Save updated state
    SESSION_STATE.write_text(json.dumps(state, indent=4, ensure_ascii=False), encoding="utf-8")
    print("Session state auto-saved")
    
    # Create session archive entry
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load or create index
    if SESSION_INDEX.exists():
        index = json.loads(SESSION_INDEX.read_text(encoding="utf-8"))
    else:
        index = {"sessions": [], "last_session_id": None}
    
    # Create session entry
    session_id = f"session-{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%SZ')}"
    session_entry = {
        "id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": f"Auto-save: {state.get('active_project', 'Unknown')}",
        "tags": ["auto-save"],
        "active_project": state.get("active_project"),
        "decisions": state.get("recent_decisions", [])[-3:],
        "tasks": state.get("pending_tasks", [])[:3]
    }
    
    # Save session file
    session_file = SESSIONS_DIR / f"{session_id}.json"
    session_file.write_text(json.dumps(session_entry, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Update index
    index["sessions"].append(session_id)
    index["last_session_id"] = session_id
    SESSION_INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"Session archived: {session_id}")

if __name__ == "__main__":
    auto_save_session()
