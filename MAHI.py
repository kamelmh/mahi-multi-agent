#!/usr/bin/env python3
"""
MAHI Multi-Agent Orchestrator v2.0
Main entry point - run this to start the system.

Usage:
  python MAHI.py              # Interactive mode
  python MAHI.py --task "..."  # Single task mode
  python MAHI.py --batch       # Batch mode (read from stdin)
  python MAHI.py --status      # Show system status
"""
import sys
import os
import json
import time
import argparse

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure MAHI root is in path
MAHI_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MAHI_ROOT)

from agents.code_agent import create_code_agent, create_code_pro_agent
from agents.quick_agent import create_quick_agent
from agents.writing_agent import create_writing_agent, create_writing_pro_agent
from agents.research_agent import create_research_agent
from agents.career_agent import create_career_agent
from agents.teaching_agent import create_teaching_agent
from agents.dss_agent import create_dss_agent
from agents.spiritual_agent import create_spiritual_agent
from router.classifier import classify
from orchestrator.engine import Orchestrator
from agents.base import Task, TaskState


# Registry of all agents
AGENT_FACTORIES = {
    "code": create_code_agent,
    "code-pro": create_code_pro_agent,
    "quick": create_quick_agent,
    "write": create_writing_agent,
    "write-pro": create_writing_pro_agent,
    "research": create_research_agent,
    "career": create_career_agent,
    "teaching": create_teaching_agent,
    "dss": create_dss_agent,
    "spiritual": create_spiritual_agent,
}


class MahiSystem:
    """Main orchestrator controller."""

    def __init__(self):
        self.orchestrator = Orchestrator()
        self.agents = {}
        self._register_agents()

    def _register_agents(self):
        for agent_id, factory in AGENT_FACTORIES.items():
            agent = factory()
            self.orchestrator.register_agent(agent)
            self.agents[agent_id] = agent

    def process(self, user_input: str, verbose: bool = False) -> Task:
        """Classify and execute a single task."""
        classification = classify(user_input)

        task = Task(
            user_input=user_input,
            category=classification.category,
            agent_id=classification.agent_id,
            model=classification.model,
            urgency=classification.urgency
        )

        agent = self.orchestrator.get_agent(classification.agent_id)
        if agent is None:
            task.fail(f"Agent '{classification.agent_id}' not available")
            return task

        if verbose:
            print(f"  Category:  {classification.category}")
            print(f"  Agent:     {agent.name}")
            print(f"  Model:     {classification.model}")
            print(f"  Confidence: {classification.confidence:.0%}")

        task = agent.run(task)
        return task

    def run_interactive(self):
        """Interactive loop."""
        try:
            from ui.terminal import TerminalUI
            ui = TerminalUI()
        except ImportError:
            ui = None

        if ui:
            ui.clear()
            ui.print_banner()
            ui.console.print("[dim]Type a task or /help for commands[/dim]")
        else:
            print("MAHI System v2.0")
            print("Type a task or /help for commands")

        while True:
            try:
                user_input = input("\n  > ").strip()
                if not user_input:
                    continue

                if user_input.startswith("/"):
                    if self._handle_command(user_input, ui):
                        break
                    continue

                if ui:
                    classification = classify(user_input)
                    ui.print_classification(
                        classification.category,
                        classification.agent_id,
                        classification.model,
                        classification.confidence
                    )
                    print(f"\n  Running...", end="", flush=True)

                task = self.process(user_input)

                if ui:
                    print("\r", end="")
                    ui.print_task_result(task)
                else:
                    status = "OK" if task.state == TaskState.COMPLETE else "FAIL"
                    print(f"  [{status}] {task.elapsed}s")
                    if task.result:
                        print(f"  {task.result[:500]}")
                    if task.error:
                        print(f"  ERROR: {task.error}")

            except (EOFError, KeyboardInterrupt):
                print("\n  Goodbye!")
                break

    def run_single(self, task_text: str):
        """Run a single task and print result."""
        task = self.process(task_text, verbose=True)
        print(f"\n  State:   {task.state.value}")
        print(f"  Elapsed: {task.elapsed}s")
        if task.result:
            print(f"  Result:\n{task.result}")
        if task.error:
            print(f"  Error: {task.error}")

    def run_batch(self):
        """Read tasks from stdin, one per line."""
        print("MAHI Batch Mode - Enter tasks (one per line, Ctrl+D to finish):")
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            print(f"\n> {line}")
            task = self.process(line)
            status = "OK" if task.state == TaskState.COMPLETE else "FAIL"
            print(f"  [{status}] {task.elapsed}s | {task.agent_id}")
            if task.result:
                print(f"  {task.result[:200]}")
            sys.stdout.flush()

    def show_status(self):
        """Print system status."""
        print("\n  MAHI System Status")
        print("  " + "=" * 40)
        print(f"  Agents: {len(self.agents)}")
        for aid, agent in self.agents.items():
            print(f"    {agent.name:20s} | {agent.config.model_primary}")
        print(f"\n  Completed tasks: {len(self.orchestrator.completed_tasks)}")

    def _handle_command(self, cmd: str, ui=None) -> bool:
        cmd = cmd.lower().strip()

        if cmd in ("/exit", "/quit", "/q"):
            print("  Goodbye!")
            return True

        elif cmd in ("/help", "/h"):
            print("\n  Commands:")
            print("    /agents  - List all agents")
            print("    /status  - System status")
            print("    /model   - Model routing")
            print("    /history - Recent tasks")
            print("    /help    - This help")
            print("    /exit    - Exit")

        elif cmd in ("/agents", "/a"):
            print("\n  Agents:")
            for aid, agent in self.agents.items():
                print(f"    {aid:12s} | {agent.name:20s} | {agent.config.model_primary}")

        elif cmd in ("/status", "/s"):
            self.show_status()

        elif cmd in ("/model", "/m"):
            print("\n  Model Routing:")
            print("    Quick    -> Gemma 4 26B (OpenRouter, Free)")
            print("    Code     -> Nemotron Nano 30B (OpenRouter, Free)")
            print("    Writing  -> Nemotron Super 120B (OpenRouter, Free)")
            print("    Research -> Nemotron Super 120B (OpenRouter, Free)")
            print("    DSS      -> Nemotron Super 120B (OpenRouter, Free)")
            print("    Spiritual -> Gemma 4 26B (OpenRouter, Free)")
            print("    Premium  -> GPT-5.5 (AIHubMix, 10-try)")

        elif cmd == "/history":
            completed = self.orchestrator.completed_tasks[-10:]
            if completed:
                for t in completed:
                    icon = "v" if t.state == TaskState.COMPLETE else "x"
                    print(f"  [{icon}] {t.id} | {t.agent_id} | {t.elapsed}s | {t.category}")
            else:
                print("  No tasks completed yet")

        else:
            print(f"  Unknown command: {cmd}")

        return False


def main():
    parser = argparse.ArgumentParser(description="MAHI Multi-Agent Orchestrator v2.0")
    parser.add_argument("--task", "-t", help="Run a single task")
    parser.add_argument("--batch", "-b", action="store_true", help="Batch mode (stdin)")
    parser.add_argument("--status", "-s", action="store_true", help="Show status")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    system = MahiSystem()

    if args.task:
        system.run_single(args.task)
    elif args.batch:
        system.run_batch()
    elif args.status:
        system.show_status()
    else:
        system.run_interactive()


if __name__ == "__main__":
    main()
