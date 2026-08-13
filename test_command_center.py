"""Tests for MAHI Command Center."""
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent))

from command_center import CommandCenter, SessionIntelligence, ObsidianVault, WORKSPACE


def test_session_intelligence_load_state():
    si = SessionIntelligence()
    state = si.load_session_state()
    assert isinstance(state, dict)


def test_session_intelligence_load_archive():
    si = SessionIntelligence()
    sessions = si.load_session_archive()
    assert isinstance(sessions, list)


def test_session_intelligence_analyze():
    si = SessionIntelligence()
    analysis = si.analyze_patterns()
    assert "timestamp" in analysis
    assert "active_project" in analysis
    assert "next_actions" in analysis
    assert "context_suggestions" in analysis
    assert isinstance(analysis["next_actions"], list)


def test_session_intelligence_summary():
    si = SessionIntelligence()
    summary = si.get_smart_summary()
    assert "SESSION INTELLIGENCE REPORT" in summary
    assert "NEXT ACTIONS" in summary


def test_obsidian_vault_search():
    vault = ObsidianVault()
    results = vault.search_notes("Brain Map", 5)
    assert isinstance(results, list)


def test_obsidian_vault_list():
    vault = ObsidianVault()
    items = vault.list_directory("")
    assert isinstance(items, list)
    assert len(items) > 0


def test_obsidian_vault_stats():
    vault = ObsidianVault()
    stats = vault.get_vault_info()
    assert "total_md" in stats
    assert "total_pdf" in stats
    assert "sections" in stats
    assert stats["total_md"] > 0


def test_obsidian_vault_read_nonexistent():
    vault = ObsidianVault()
    result = vault.read_note("nonexistent-file-12345.md")
    assert "error" in result


def test_command_center_briefing():
    cc = CommandCenter()
    briefing = cc.briefing()
    assert "COMMAND CENTER" in briefing
    assert "NEXT ACTIONS" in briefing


def test_command_center_status():
    cc = CommandCenter()
    status = cc.status()
    assert "timestamp" in status
    assert "systems" in status


def test_command_center_session():
    cc = CommandCenter()
    result = cc.session("summary")
    assert "SESSION INTELLIGENCE REPORT" in result


def test_command_center_vault_vault():
    cc = CommandCenter()
    result = cc.vault("vault")
    data = json.loads(result)
    assert "total_md" in data


def test_command_center_vault_search():
    cc = CommandCenter()
    result = cc.vault("search", "Brain Map")
    data = json.loads(result)
    assert isinstance(data, list)


def test_command_center_run():
    cc = CommandCenter()
    result = cc.run("briefing")
    assert "COMMAND CENTER" in result
    result = cc.run("status")
    data = json.loads(result)
    assert "systems" in data


def test_command_center_run_unknown():
    cc = CommandCenter()
    result = cc.run("unknown")
    assert "Commands:" in result


if __name__ == "__main__":
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pytest", __file__, "-v"],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
