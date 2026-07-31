"""Task Orchestrator Engine for MAHI Multi-Agent System."""
from __future__ import annotations
import json
import os
import time
import threading
from dataclasses import dataclass, field, asdict
from typing import Optional

from agents.base import BaseAgent, Task, TaskState, AgentState, MAHI_ROOT


class Orchestrator:
    """Manages task queue, agent coordination, and state."""

    def __init__(self):
        self.agents: dict[str, BaseAgent] = {}
        self.task_queue: list[Task] = []
        self.active_tasks: dict[str, Task] = {}
        self.completed_tasks: list[Task] = []
        self.max_concurrent = 3
        self.state_file = os.path.join(MAHI_ROOT, "orchestrator", "state.json")
        self._lock = threading.Lock()

    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator."""
        self.agents[agent.id] = agent

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        return self.agents.get(agent_id)

    def submit(self, task: Task) -> Task:
        """Submit a task to the queue."""
        task.state = TaskState.QUEUED
        self.task_queue.append(task)
        self._process_queue()
        return task

    def _process_queue(self):
        """Start queued tasks if under concurrent limit."""
        with self._lock:
            while len(self.active_tasks) < self.max_concurrent and self.task_queue:
                task = self.task_queue.pop(0)
                agent = self.agents.get(task.agent_id)

                if agent is None:
                    task.fail(f"Agent '{task.agent_id}' not registered")
                    self.completed_tasks.append(task)
                    continue

                if not agent.is_available:
                    # Re-queue if agent is busy
                    self.task_queue.insert(0, task)
                    break

                self.active_tasks[task.id] = task
                thread = threading.Thread(
                    target=self._run_task,
                    args=(agent, task),
                    daemon=True
                )
                thread.start()

    def _run_task(self, agent: BaseAgent, task: Task):
        """Run task in background thread."""
        try:
            agent.run(task)
        except Exception as e:
            task.fail(str(e))
        finally:
            with self._lock:
                self.active_tasks.pop(task.id, None)
                self.completed_tasks.append(task)
            self._save_state()
            self._process_queue()

    def get_status(self) -> dict:
        """Get overall orchestrator status."""
        return {
            "queued": len(self.task_queue),
            "running": len(self.active_tasks),
            "completed": len(self.completed_tasks),
            "agents": {
                aid: agent.get_status()
                for aid, agent in self.agents.items()
            }
        }

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID from any state."""
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        for task in self.completed_tasks:
            if task.id == task_id:
                return task
        for task in self.task_queue:
            if task.id == task_id:
                return task
        return None

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a queued task."""
        for i, task in enumerate(self.task_queue):
            if task.id == task_id:
                task.state = TaskState.FAILED
                task.error = "Cancelled by user"
                self.completed_tasks.append(self.task_queue.pop(i))
                return True
        return False

    def _save_state(self):
        """Persist state to disk."""
        state = {
            "last_updated": time.time(),
            "stats": {
                "queued": len(self.task_queue),
                "running": len(self.active_tasks),
                "completed": len(self.completed_tasks),
            },
            "recent_completed": [
                t.to_dict() for t in self.completed_tasks[-20:]
            ]
        }
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def clear_completed(self):
        """Clear completed tasks list."""
        self.completed_tasks.clear()
        self._save_state()
