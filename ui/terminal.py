"""Terminal UI for MAHI Multi-Agent System."""
from __future__ import annotations
import os
import sys
import time

# Fix Windows encoding for Unicode
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Rich import with fallback
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.prompt import Prompt
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


class TerminalUI:
    """Rich terminal interface for the orchestrator."""

    def __init__(self):
        if HAS_RICH:
            self.console = Console()
        self.WIDTH = 60

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def print_banner(self):
        banner = """
╔══════════════════════════════════════════════════════════╗
║               M A H I   S Y S T E M   v2.0              ║
║               Multi-Agent Orchestrator                   ║
╚══════════════════════════════════════════════════════════╝"""
        if HAS_RICH:
            self.console.print(Panel(
                Text("M A H I   S Y S T E M   v2.0", style="bold cyan", justify="center"),
                subtitle="Multi-Agent Orchestrator",
                border_style="bright_blue"
            ))
        else:
            print(banner)

    def print_classification(self, category: str, agent: str, model: str, confidence: float):
        if HAS_RICH:
            table = Table(show_header=False, border_style="cyan", width=self.WIDTH)
            table.add_column("Key", style="bold")
            table.add_column("Value")
            table.add_row("Category", category)
            table.add_row("Agent", agent)
            table.add_row("Model", model)
            table.add_row("Confidence", f"{confidence:.0%}")
            self.console.print(Panel(table, title="[bold]Classification[/bold]", border_style="cyan"))
        else:
            print(f"\n  Category:  {category}")
            print(f"  Agent:     {agent}")
            print(f"  Model:     {model}")
            print(f"  Confidence: {confidence:.0%}")

    def print_task_result(self, task):
        if HAS_RICH:
            style = "green" if task.state.value == "complete" else "red"
            result_text = task.result or task.error or "No output"
            # Truncate long results
            if len(result_text) > 1500:
                result_text = result_text[:1500] + "\n... (truncated)"
            self.console.print(Panel(
                result_text,
                title=f"[{style}]{task.state.value.upper()}[/{style}] -- {task.id}",
                subtitle=f"Elapsed: {task.elapsed}s | Agent: {task.agent_id}",
                border_style=style
            ))
        else:
            status = "OK" if task.state.value == "complete" else "FAIL"
            print(f"\n  [{status}] {task.id} ({task.elapsed}s)")
            print(f"  {(task.result or task.error)[:300]}")

    def print_status(self, status: dict):
        if HAS_RICH:
            table = Table(title="Orchestrator Status", border_style="blue")
            table.add_column("Metric", style="bold")
            table.add_column("Value", justify="right")
            table.add_row("Queued", str(status["queued"]))
            table.add_row("Running", str(status["running"]))
            table.add_row("Completed", str(status["completed"]))
            table.add_row("", "")
            for aid, agent_status in status["agents"].items():
                state_icon = {
                    "idle": "[dim]●[/dim]",
                    "running": "[green]●[/green]",
                    "waiting": "[yellow]●[/yellow]",
                }.get(agent_status["state"], "[red]●[/red]")
                table.add_row(
                    f"  {state_icon} {agent_status['name']}",
                    f"{agent_status['active_tasks']} active | {agent_status['model']}"
                )
            self.console.print(table)
        else:
            print(f"\n  Queued: {status['queued']} | Running: {status['running']} | Completed: {status['completed']}")
            for aid, s in status["agents"].items():
                print(f"    {s['name']}: {s['state']} ({s['model']})")

    def print_agents_menu(self):
        if HAS_RICH:
            table = Table(title="Available Agents", border_style="green", width=self.WIDTH)
            table.add_column("#", style="bold", width=3)
            table.add_column("Agent", width=20)
            table.add_column("Model", width=25)
            table.add_column("Purpose", width=30)

            agents = [
                ("1", "Code Agent", "GPT-OSS 20B", "Code generation"),
                ("2", "Code Pro", "GPT-5.5", "Complex architecture"),
                ("3", "Writing Agent", "Llama 3.3 70B", "Emails, docs"),
                ("4", "Writing Pro", "GPT-5.5", "Client-facing"),
                ("5", "Research", "Llama 3.3 70B", "Web research"),
                ("6", "Career", "Llama 3.3 70B", "CV, jobs"),
                ("7", "Teaching", "GPT-OSS 20B", "Education"),
                ("8", "DSS/ERP", "GPT-OSS 120B", "VBA, Excel"),
                ("9", "Spiritual", "Allam 2 7B", "Astrology"),
                ("Q", "Quick", "Llama 3.1 8B", "Simple questions"),
            ]
            for row in agents:
                table.add_row(*row)
            self.console.print(table)
        else:
            print("\n  Available Agents:")
            print("  [1] Code Agent     [6] Career       [Q] Quick")
            print("  [2] Code Pro       [7] Teaching")
            print("  [3] Writing Agent  [8] DSS/ERP")
            print("  [4] Writing Pro    [9] Spiritual")
            print("  [5] Research")

    def print_help(self):
        if HAS_RICH:
            self.console.print(Panel(
                "[bold]Commands:[/bold]\n"
                "  Type any task description to auto-classify and execute\n"
                "  [bold]/agents[/bold]  — Show all agents\n"
                "  [bold]/status[/bold]  — Show orchestrator status\n"
                "  [bold]/history[/bold] — Show recent tasks\n"
                "  [bold]/model[/bold]   — Show model routing\n"
                "  [bold]/help[/bold]    — Show this help\n"
                "  [bold]/exit[/bold]    — Exit\n\n"
                "[dim]Tips:[/dim]\n"
                "  - Tasks auto-classify based on keywords\n"
                "  - Use /model to see which model is selected\n"
                "  - Simple questions use fast models automatically",
                title="Help",
                border_style="yellow"
            ))
        else:
            print("\n  Commands:")
            print("  /agents  — Show agents")
            print("  /status  — Show status")
            print("  /model   — Show models")
            print("  /help    — Help")
            print("  /exit    — Exit")

    def get_input(self) -> str:
        try:
            return input("\n  > ").strip()
        except (EOFError, KeyboardInterrupt):
            return "/exit"

    def print_model_info(self):
        if HAS_RICH:
            table = Table(title="Model Routing", border_style="magenta", width=self.WIDTH)
            table.add_column("Task Type", style="bold")
            table.add_column("Provider")
            table.add_column("Model")
            table.add_column("Cost")
            table.add_row("Quick", "Groq", "Llama 3.1 8B", "Free ∞")
            table.add_row("Code", "Groq", "GPT-OSS 20B", "Free ∞")
            table.add_row("Writing", "Groq", "Llama 3.3 70B", "Free ∞")
            table.add_row("Research", "Groq", "Llama 3.3 70B", "Free ∞")
            table.add_row("DSS/ERP", "Groq", "GPT-OSS 120B", "Free ∞")
            table.add_row("Premium", "AIHubMix", "GPT-5.5", "Free 10-try")
            table.add_row("Privacy", "Ollama", "Phi-4 Mini", "Free local")
            self.console.print(table)
        else:
            print("\n  Model Routing:")
            print("  Quick    → Groq Llama 3.1 8B (Free)")
            print("  Code     → Groq GPT-OSS 20B (Free)")
            print("  Writing  → Groq Llama 3.3 70B (Free)")
            print("  DSS      → Groq GPT-OSS 120B (Free)")
            print("  Premium  → AIHubMix GPT-5.5 (10-try)")
            print("  Privacy  → Ollama Phi-4 Mini (Local)")
