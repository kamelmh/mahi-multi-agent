"""
MAHI Command Center — Unified CLI
Combines: Session Intelligence + Obsidian Vault + System Status
Replaces: automation/command-center/, automation/session-intelligence/, automation/obsidian-mcp/
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

MAHI_ROOT = Path(__file__).parent
WORKSPACE = Path(r"C:\Users\Admin\My Drive\LifeWorkspace")
SESSION_ARCHIVE = WORKSPACE / "15_Advanced_Tools" / "sessions"
SESSION_STATE = WORKSPACE / ".session-state.json"
CONTEXT_ENGINE = WORKSPACE / "15_Advanced_Tools" / "context-engine"


class SessionIntelligence:
    """Analyzes past sessions, detects patterns, suggests next actions."""

    def load_session_state(self) -> Dict:
        if SESSION_STATE.exists():
            return json.loads(SESSION_STATE.read_text(encoding="utf-8"))
        return {}

    def load_session_archive(self) -> List[Dict]:
        index_file = SESSION_ARCHIVE / "index.json"
        if index_file.exists():
            data = json.loads(index_file.read_text(encoding="utf-8"))
            return data.get("sessions", [])
        return []

    def analyze_patterns(self) -> Dict:
        state = self.load_session_state()
        sessions = self.load_session_archive()

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "active_project": state.get("active_project", "Unknown"),
            "recent_decisions": state.get("recent_decisions", [])[-10:],
            "pending_tasks": state.get("pending_tasks", []),
            "session_count": len(sessions),
            "project_frequency": self._calc_project_frequency(sessions),
            "time_patterns": self._calc_time_patterns(sessions),
            "task_completion_rate": self._calc_completion_rate(state),
            "next_actions": [],
            "context_suggestions": [],
        }
        analysis["next_actions"] = self._generate_next_actions(analysis)
        analysis["context_suggestions"] = self._suggest_context(analysis)
        return analysis

    def _calc_project_frequency(self, sessions: List[Dict]) -> Dict:
        projects = Counter()
        for s in sessions:
            for tag in s.get("tags", []):
                projects[tag] += 1
        return dict(projects.most_common(10))

    def _calc_time_patterns(self, sessions: List[Dict]) -> Dict:
        hours, days = Counter(), Counter()
        for s in sessions:
            ts = s.get("timestamp", "")
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    hours[dt.hour] += 1
                    days[dt.strftime("%A")] += 1
                except Exception:
                    pass
        return {
            "peak_hour": hours.most_common(1)[0][0] if hours else "Unknown",
            "peak_day": days.most_common(1)[0][0] if days else "Unknown",
            "total_sessions": sum(hours.values()),
        }

    def _calc_completion_rate(self, state: Dict) -> float:
        pending = len(state.get("pending_tasks", []))
        decisions = len(state.get("recent_decisions", []))
        if decisions + pending == 0:
            return 0.0
        return decisions / (decisions + pending) * 100

    def _generate_next_actions(self, analysis: Dict) -> List[Dict]:
        actions = []
        project = analysis["active_project"]
        project_actions = {
            "CCA-F Certification": [
                {"action": "Review Domain 1 flashcards", "priority": "high", "time": "15 min"},
                {"action": "Practice quiz (10 questions)", "priority": "high", "time": "20 min"},
            ],
            "Education Project": [
                {"action": "Test Exercise Generator with students", "priority": "high", "time": "1 hour"},
                {"action": "Add new grammar topics", "priority": "medium", "time": "45 min"},
            ],
        }
        if project in project_actions:
            actions.extend(project_actions[project])
        actions.extend([
            {"action": "Update Brain Map with today's progress", "priority": "low", "time": "5 min"},
            {"action": "Review astrological transits", "priority": "low", "time": "5 min"},
        ])
        return actions

    def _suggest_context(self, analysis: Dict) -> List[str]:
        suggestions = []
        project = analysis["active_project"]
        context_map = {
            "CCA-F Certification": [
                "02_Skills_&_Development/CCA-F/00-MOC-CCA-F.md",
            ],
            "Education Project": [
                "10_Education_Project/00-MOC-Education.md",
            ],
        }
        if project in context_map:
            suggestions.extend(context_map[project])
        suggestions.append("00-Brain-Map.md")
        return suggestions

    def get_smart_summary(self) -> str:
        analysis = self.analyze_patterns()
        lines = [
            "=" * 50,
            "SESSION INTELLIGENCE REPORT",
            "=" * 50,
            f"Generated: {analysis['timestamp'][:19]}",
            f"Active Project: {analysis['active_project']}",
            f"Session Count: {analysis['session_count']}",
            f"Completion Rate: {analysis['task_completion_rate']:.1f}%",
            "",
        ]
        tp = analysis["time_patterns"]
        if tp["peak_hour"] != "Unknown":
            lines.append(f"Peak Activity: {tp['peak_hour']}:00 on {tp['peak_day']}")
        lines.append("")
        lines.append("NEXT ACTIONS:")
        for i, a in enumerate(analysis["next_actions"][:5], 1):
            lines.append(f"  {i}. [{a['priority'].upper()}] {a['action']} ({a['time']})")
        lines.append("")
        lines.append("SUGGESTED CONTEXT:")
        for c in analysis["context_suggestions"]:
            lines.append(f"  - {c}")
        lines.append("=" * 50)
        return "\n".join(lines)


class ObsidianVault:
    """Access LifeWorkspace vault — search, read, create, list."""

    def __init__(self, vault_path: Path = WORKSPACE):
        self.vault_path = vault_path

    def search_notes(self, query: str, limit: int = 10) -> List[Dict]:
        results = []
        query_lower = query.lower()
        for md_file in self.vault_path.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                if query_lower in content.lower() or query_lower in md_file.stem.lower():
                    rel_path = str(md_file.relative_to(self.vault_path))
                    snippet = content[:200].replace("\n", " ").strip()
                    results.append({"path": rel_path, "name": md_file.stem, "snippet": snippet})
                    if len(results) >= limit:
                        break
            except Exception:
                continue
        return results

    def read_note(self, path: str) -> Dict:
        full_path = self.vault_path / path
        if full_path.exists():
            return {"content": full_path.read_text(encoding="utf-8")}
        return {"error": f"Note not found: {path}"}

    def list_directory(self, directory: str = "") -> List[Dict]:
        dir_path = self.vault_path / directory if directory else self.vault_path
        items = []
        try:
            for item in sorted(dir_path.iterdir()):
                if item.name.startswith(".") or item.name.startswith("~"):
                    continue
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "path": str(item.relative_to(self.vault_path)),
                })
        except Exception:
            pass
        return items

    def get_moc(self, section: str = "") -> Dict:
        if section:
            moc_path = self.vault_path / section / "00-MOC-" + section.split("_", 1)[-1].split("\\")[-1].split("/")[-1] + ".md"
            if not moc_path.exists():
                for f in (self.vault_path / section).glob("00-MOC-*.md") if (self.vault_path / section).exists() else []:
                    moc_path = f
                    break
        else:
            moc_path = self.vault_path / "00-BRAIN-MAP.md"
        if moc_path.exists():
            return {"content": moc_path.read_text(encoding="utf-8")}
        return {"error": f"MOC not found: {section}"}

    def get_vault_info(self) -> Dict:
        md_files = list(self.vault_path.rglob("*.md"))
        pdf_files = list(self.vault_path.rglob("*.pdf"))
        total_size = sum(f.stat().st_size for f in self.vault_path.rglob("*") if f.is_file())
        sections = [d.name for d in self.vault_path.iterdir() if d.is_dir() and not d.name.startswith(".")]
        return {
            "total_md": len(md_files),
            "total_pdf": len(pdf_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "sections": sorted(sections),
            "vault_path": str(self.vault_path),
        }


class CommandCenter:
    """Unified command center — briefing, status, session, vault."""

    def __init__(self):
        self.session_intel = SessionIntelligence()
        self.obsidian = ObsidianVault()
        self.systems = {
            "education": WORKSPACE / "10_Education_Project",
            "skills": WORKSPACE / "02_Skills_&_Development",
            "career": WORKSPACE / "03_Career_&_Planning",
        }

    def briefing(self) -> str:
        lines = [
            "=" * 50,
            "COMMAND CENTER — DAILY BRIEFING",
            "=" * 50,
            f"Date: {datetime.now().strftime('%A, %B %d, %Y %H:%M')}",
            "",
        ]
        for name, path in self.systems.items():
            if path.exists():
                count = len(list(path.rglob("*.md")))
                lines.append(f"  {name.title()}: {count} files")
            else:
                lines.append(f"  {name.title()}: MISSING")
        lines.append("")
        analysis = self.session_intel.analyze_patterns()
        lines.append(f"Active project: {analysis.get('active_project', 'Unknown')}")
        lines.append(f"Session count: {analysis.get('session_count', 0)}")
        lines.append("")
        actions = analysis.get("next_actions", [])[:3]
        if actions:
            lines.append("NEXT ACTIONS:")
            for a in actions:
                lines.append(f"  [{a['priority'].upper()}] {a['action']} ({a['time']})")
        lines.append("=" * 50)
        return "\n".join(lines)

    def status(self) -> Dict:
        result = {"timestamp": datetime.now().isoformat(), "systems": {}}
        for name, path in self.systems.items():
            if path.exists():
                files = list(path.rglob("*.md"))
                result["systems"][name] = {
                    "files": len(files),
                    "size_mb": round(sum(f.stat().st_size for f in files) / 1024 / 1024, 2),
                }
            else:
                result["systems"][name] = {"status": "missing"}
        return result

    def session(self, cmd: str = "summary") -> str:
        if cmd == "summary":
            return self.session_intel.get_smart_summary()
        elif cmd == "next":
            analysis = self.session_intel.analyze_patterns()
            lines = ["NEXT ACTIONS:"]
            for i, a in enumerate(analysis["next_actions"], 1):
                lines.append(f"  {i}. [{a['priority'].upper()}] {a['action']} ({a['time']})")
            return "\n".join(lines)
        elif cmd == "context":
            analysis = self.session_intel.analyze_patterns()
            lines = ["SUGGESTED CONTEXT:"]
            for c in analysis["context_suggestions"]:
                lines.append(f"  - {c}")
            return "\n".join(lines)
        return self.session_intel.get_smart_summary()

    def vault(self, cmd: str, *args) -> str:
        if cmd == "search":
            results = self.obsidian.search_notes(args[0] if args else "", 10)
            return json.dumps(results, indent=2, ensure_ascii=False)
        elif cmd == "read":
            result = self.obsidian.read_note(args[0] if args else "00-BRAIN-MAP.md")
            if "error" in result:
                return f"Error: {result['error']}"
            return result["content"]
        elif cmd == "list":
            results = self.obsidian.list_directory(args[0] if args else "")
            return "\n".join(
                f"{'[DIR] ' if i.get('type') == 'directory' else '      '}{i['name']}"
                for i in results
            )
        elif cmd == "moc":
            result = self.obsidian.get_moc(args[0] if args else "")
            if "error" in result:
                return f"Error: {result['error']}"
            return result["content"]
        elif cmd == "vault":
            return json.dumps(self.obsidian.get_vault_info(), indent=2)
        return "Commands: search, read, list, moc, vault"

    def run(self, command: str, args: List[str] = None) -> str:
        args = args or []
        if command == "briefing":
            return self.briefing()
        elif command == "status":
            return json.dumps(self.status(), indent=2)
        elif command == "session":
            return self.session(args[0] if args else "summary")
        elif command == "vault":
            return self.vault(args[0] if args else "vault", *args[1:])
        else:
            return (
                "Commands:\n"
                "  briefing              — Daily briefing\n"
                "  status                — System status\n"
                "  session [summary|next|context] — Session intelligence\n"
                "  vault [search|read|list|moc|vault] — Obsidian vault"
            )


def main():
    center = CommandCenter()
    if len(sys.argv) > 1:
        print(center.run(sys.argv[1], sys.argv[2:]))
    else:
        print(center.briefing())


if __name__ == "__main__":
    main()
