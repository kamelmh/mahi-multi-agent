"""MAHI Hooks — lifecycle callbacks for agent events.

Usage:
    from hooks import HookManager
    hooks = HookManager()
    hooks.register("before_task", my_callback)
    hooks.fire("before_task", task=task, agent=agent)
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Callable, Any

log = logging.getLogger(__name__)


@dataclass
class HookEvent:
    name: str
    data: dict = field(default_factory=dict)


HookCallback = Callable[[HookEvent], None]


class HookManager:
    """Registry of lifecycle hooks. Fire them at the right moments."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._hooks: dict[str, list[HookCallback]] = {}
        return cls._instance

    def register(self, event: str, callback: HookCallback):
        self._hooks.setdefault(event, []).append(callback)

    def fire(self, event: str, **kwargs) -> list[Exception]:
        """Fire all callbacks for an event. Returns list of errors (empty = success)."""
        errors = []
        hook_event = HookEvent(name=event, data=kwargs)
        for cb in self._hooks.get(event, []):
            try:
                cb(hook_event)
            except Exception as e:
                log.warning(f"Hook {event}/{cb.__name__} failed: {e}")
                errors.append(e)
        return errors

    def list_hooks(self) -> dict[str, list[str]]:
        return {ev: [cb.__name__ for cbs in callbacks for cb in [cbs]] 
                for ev, callbacks in self._hooks.items()}


# Built-in hooks ----------------------------------------------------------------

def log_task_start(event: HookEvent):
    """Log when a task starts."""
    task = event.data.get("task")
    agent = event.data.get("agent")
    if task and agent:
        log.info(f"[HOOK] {agent.name} starting task {task.id}: {task.user_input[:60]}...")


def log_task_complete(event: HookEvent):
    """Log when a task completes."""
    task = event.data.get("task")
    agent = event.data.get("agent")
    if task and agent:
        status = "OK" if task.result else f"FAIL: {task.error}"
        log.info(f"[HOOK] {agent.name} finished task {task.id} in {task.elapsed}s — {status}")


def log_tool_call(event: HookEvent):
    """Log tool invocations."""
    tool = event.data.get("tool_name", "?")
    log.info(f"[HOOK] Tool call: {tool}({event.data.get('kwargs', {})})")


def autosave_on_complete(event: HookEvent):
    """Auto-save session state after task completion."""
    try:
        import json, time, os
        from pathlib import Path
        state_file = Path(os.environ.get("MAHI_ROOT", ".")) / "tmp" / "last_session.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        task = event.data.get("task")
        if task and task.result:
            state = {
                "last_task_id": task.id,
                "last_agent": event.data.get("agent", "").id if event.data.get("agent") else "?",
                "completed_at": time.time(),
                "result_preview": task.result[:200],
            }
            state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception:
        pass


def register_defaults(hooks: HookManager):
    """Register the default hook set."""
    hooks.register("before_task", log_task_start)
    hooks.register("after_task", log_task_complete)
    hooks.register("before_tool", log_tool_call)
    hooks.register("after_task", autosave_on_complete)
