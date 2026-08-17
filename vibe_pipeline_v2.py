#!/usr/bin/env python3
"""
MAHI Vibe Pipeline v2 — Extended Edition
Build anything in one session with 10 agent roles.

Usage:
    python vibe_pipeline_v2.py "Build a task management app with auth"
    python vibe_pipeline_v2.py --from-prd path/to/prd.md
    python vibe_pipeline_v2.py --roles all "Build a dashboard"
    python vibe_pipeline_v2.py --roles pm,ui,code,security "Quick build"

Roles:
    pm          - Product Manager (PRD generation)
    ui          - UI/UX Designer (dashboard HTML)
    code        - Code Agent (Flask backend)
    security    - Security Agent (vulnerability audit)
    growth      - Growth Agent (launch materials)
    testing     - Testing Agent (unit/integration tests)
    docs        - Documentation Agent (README, API docs)
    database    - Database Agent (schema design)
    devops      - DevOps Agent (Docker, CI/CD)
    accessibility - Accessibility Agent (a11y audit)
"""

import os
import sys
import json
import time
import concurrent.futures
from datetime import datetime
from pathlib import Path
from typing import Optional

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).parent.resolve()
TEMPLATES_DIR = PROJECT_ROOT / "brain" / "templates"
OUTPUT_DIR = PROJECT_ROOT / "vibe-output"

sys.path.insert(0, str(PROJECT_ROOT))
from MAHI import MahiSystem
from agents.base import Task


# === Role Definitions ===
ROLES = {
    "pm": {"agent": "write", "phase": 1, "parallel": False, "depends": []},
    "ui": {"agent": "code", "phase": 2, "parallel": True, "depends": ["pm"]},
    "code": {"agent": "code", "phase": 2, "parallel": True, "depends": ["pm"]},
    "security": {"agent": "code", "phase": 3, "parallel": False, "depends": ["code"]},
    "testing": {"agent": "code", "phase": 3, "parallel": True, "depends": ["code"]},
    "docs": {"agent": "write", "phase": 3, "parallel": True, "depends": ["pm", "code"]},
    "database": {"agent": "code", "phase": 2, "parallel": True, "depends": ["pm"]},
    "devops": {"agent": "code", "phase": 4, "parallel": False, "depends": ["code", "security"]},
    "accessibility": {"agent": "code", "phase": 3, "parallel": True, "depends": ["ui"]},
    "growth": {"agent": "write", "phase": 4, "parallel": True, "depends": ["pm"]},
}


class VibePipelineV2:
    """Extended vibe coding pipeline with 10 agent roles and parallel execution."""

    def __init__(self, project_name: str = None, roles: list[str] = None):
        self.project_name = project_name or f"vibe-{datetime.now().strftime('%Y%m%d-%H%M')}"
        self.output_dir = OUTPUT_DIR / self.project_name
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = {}
        self.timings = {}
        self.mahi = MahiSystem()
        self.roles = roles or list(ROLES.keys())

    def run(self, description: str) -> dict:
        """Run the pipeline with parallel execution where possible."""
        start_time = time.time()

        print(f"\n{'='*60}")
        print(f"MAHI VIBE PIPELINE v2")
        print(f"Project: {self.project_name}")
        print(f"Roles: {', '.join(self.roles)}")
        print(f"{'='*60}\n")

        # Group roles by phase
        phases = {}
        for role_name in self.roles:
            role = ROLES[role_name]
            phase = role["phase"]
            if phase not in phases:
                phases[phase] = []
            phases[phase].append(role_name)

        # Execute phases in order
        for phase_num in sorted(phases.keys()):
            phase_roles = phases[phase_num]
            print(f"\n--- Phase {phase_num} ---")

            # Check if roles can run in parallel
            parallel_roles = [r for r in phase_roles if ROLES[r]["parallel"]]
            sequential_roles = [r for r in phase_roles if not ROLES[r]["parallel"]]

            # Run parallel roles
            if parallel_roles:
                self._run_parallel(parallel_roles)

            # Run sequential roles
            for role_name in sequential_roles:
                self._run_role(role_name)

        # Generate summary
        total_time = time.time() - start_time
        self._print_summary(total_time)
        return self.results

    def _run_parallel(self, role_names: list[str]):
        """Run multiple roles in parallel using ThreadPoolExecutor."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(role_names)) as executor:
            futures = {}
            for role_name in role_names:
                future = executor.submit(self._run_role, role_name)
                futures[future] = role_name

            for future in concurrent.futures.as_completed(futures):
                role_name = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"  [ERROR] {role_name}: {e}")

    def _run_role(self, role_name: str) -> any:
        """Run a specific role and store its result."""
        start = time.time()
        print(f"\n  [{role_name.upper()}] Running...")

        try:
            if role_name == "pm":
                result = self._run_pm()
            elif role_name == "ui":
                result = self._run_ui()
            elif role_name == "code":
                result = self._run_code()
            elif role_name == "security":
                result = self._run_security()
            elif role_name == "testing":
                result = self._run_testing()
            elif role_name == "docs":
                result = self._run_docs()
            elif role_name == "database":
                result = self._run_database()
            elif role_name == "devops":
                result = self._run_devops()
            elif role_name == "accessibility":
                result = self._run_accessibility()
            elif role_name == "growth":
                result = self._run_growth()
            else:
                print(f"  [SKIP] Unknown role: {role_name}")
                return None

            self.results[role_name] = result
            self.timings[role_name] = time.time() - start
            print(f"  [OK] {role_name} completed ({self.timings[role_name]:.1f}s)")
            return result

        except Exception as e:
            self.timings[role_name] = time.time() - start
            print(f"  [ERROR] {role_name} failed: {e}")
            self.results[role_name] = {"error": str(e)}
            return None

    def _get_agent(self, agent_id: str):
        """Get agent from MAHI system."""
        return self.mahi.agents.get(agent_id)

    def _run_llm(self, agent_id: str, prompt: str, extract_code: bool = True) -> str:
        """Run LLM and optionally extract code from markdown."""
        agent = self._get_agent(agent_id)
        if not agent:
            return None

        task = Task(
            user_input=prompt,
            category="code" if agent_id == "code" else "writing",
            agent_id=agent_id,
            model="nvidia/nemotron-3-super-120b-a12b:free",
        )
        task = agent.run(task)

        if not task.result:
            return None

        result = task.result
        if extract_code:
            # Extract code from markdown fences
            extracted = False
            for lang in ["python", "javascript", "html", "json", "bash", "yaml"]:
                if f"```{lang}" in result:
                    result = result.split(f"```{lang}")[1].split("```")[0]
                    extracted = True
                    break
            if not extracted and "```" in result:
                result = result.split("```")[1].split("```")[0]

        return result.strip()

    def _save(self, filename: str, content: str | dict):
        """Save content to output directory."""
        path = self.output_dir / filename
        if isinstance(content, dict):
            content = json.dumps(content, indent=2, ensure_ascii=False)
        path.write_text(content, encoding="utf-8")
        return str(path)

    # === Role Implementations ===

    def _run_pm(self) -> str:
        """PM Agent: Generate PRD from description."""
        template = ""
        template_path = TEMPLATES_DIR / "PRD_TEMPLATE.md"
        if template_path.exists():
            template = template_path.read_text()

        prompt = f"""You are a Product Manager. Generate a complete PRD for:

PROJECT: {self.project_name}
DESCRIPTION: {self._get_description()}

{template if template else "Create a comprehensive PRD with: Problem, Solution, Users, Features, Tech Stack, API Design, Data Model, Out of Scope"}

Return ONLY the filled-in PRD markdown."""
        return self._save("PRD.md", self._run_llm("write", prompt, extract_code=False))

    def _run_ui(self) -> str:
        """UI/UX Agent: Generate dashboard HTML."""
        prd = self._read_result("PRD.md")

        prompt = f"""Generate a complete HTML dashboard for:

{prd}

Requirements:
- Single index.html (inline CSS + JS)
- Dark theme (#0f172a, gradient accents)
- Responsive (mobile-first)
- Sidebar navigation
- Dashboard cards with stats
- Modern design (Outfit font)
- Include: header, main, footer

Return ONLY the HTML code."""
        return self._save("index.html", self._run_llm("code", prompt))

    def _run_code(self) -> str:
        """Code Agent: Build Flask backend."""
        prd = self._read_result("PRD.md")

        prompt = f"""Generate a complete Flask backend for:

{prd}

Requirements:
- Single app.py
- Flask + CORS + JWT auth
- SQLite + SQLAlchemy
- RESTful API endpoints
- Input validation
- Error handling
- Environment config

Return ONLY the Python code."""
        return self._save("app.py", self._run_llm("code", prompt))

    def _run_security(self) -> dict:
        """Security Agent: Validate code."""
        code = self._read_result("app.py")

        prompt = f"""Review this Python code for security vulnerabilities:

{code}

Check: input validation, SQL injection, XSS, secrets, auth, rate limiting, CORS

Return JSON:
{{"score": 0-100, "checks": {{"check": bool}}, "recommendations": ["..."]}}

Return ONLY valid JSON."""
        result = self._run_llm("code", prompt)
        try:
            return json.loads(result)
        except:
            return {"score": 0, "checks": {}, "recommendations": ["Review failed"]}

    def _run_testing(self) -> str:
        """Testing Agent: Generate unit tests."""
        code = self._read_result("app.py")

        prompt = f"""Generate comprehensive unit tests for this Flask app:

{code}

Requirements:
- pytest tests
- Test all API endpoints
- Mock external dependencies
- Test auth flow
- Test error cases
- Include fixtures

Return ONLY the test code."""
        return self._save("test_app.py", self._run_llm("code", prompt))

    def _run_docs(self) -> str:
        """Documentation Agent: Generate README."""
        prd = self._read_result("PRD.md")

        prompt = f"""Generate comprehensive documentation for:

{prd[:1000]}

Create:
1. README.md with: description, setup, usage, API docs
2. API.md with endpoint documentation

Return the README.md content."""
        return self._save("README.md", self._run_llm("write", prompt, extract_code=False))

    def _run_database(self) -> str:
        """Database Agent: Design schema."""
        prd = self._read_result("PRD.md")

        prompt = f"""Design the database schema for:

{prd}

Create SQLAlchemy models with:
- All required tables
- Relationships
- Indexes
- Constraints

Return ONLY the Python models code."""
        return self._save("models.py", self._run_llm("code", prompt))

    def _run_devops(self) -> str:
        """DevOps Agent: Create Docker and CI/CD config."""
        prompt = f"""Create deployment configuration for {self.project_name}:

Create:
1. Dockerfile (Python/Flask)
2. docker-compose.yml
3. .github/workflows/deploy.yml

Return the Dockerfile content."""
        return self._save("Dockerfile", self._run_llm("code", prompt))

    def _run_accessibility(self) -> dict:
        """Accessibility Agent: Audit HTML for a11y."""
        html = self._read_result("index.html")

        prompt = f"""Audit this HTML for accessibility issues:

{html[:3000]}

Check:
- ARIA labels
- Color contrast
- Keyboard navigation
- Screen reader support
- Form labels

Return JSON:
{{"score": 0-100, "issues": ["..."], "fixes": ["..."]}}

Return ONLY valid JSON."""
        result = self._run_llm("code", prompt)
        try:
            return json.loads(result)
        except:
            return {"score": 0, "issues": [], "fixes": []}

    def _run_growth(self) -> dict:
        """Growth Agent: Generate launch materials."""
        prd = self._read_result("PRD.md")

        prompt = f"""Generate launch materials for:

{prd[:500]}

Create:
1. One-line pitch (100 chars)
2. Short description (2-3 sentences)
3. 5 SEO tags
4. Launch checklist (7 items)

Return JSON:
{{"pitch": "...", "description": "...", "tags": [...], "launch_checklist": [...]}}"""
        result = self._run_llm("write", prompt)
        try:
            return json.loads(result)
        except:
            return {"pitch": self.project_name, "tags": ["ai", "vibe-coding"]}

    # === Helpers ===

    def _get_description(self) -> str:
        """Get description from results or return placeholder."""
        return self.results.get("_description", "A modern web application")

    def _read_result(self, filename: str) -> str:
        """Read a previously saved result file."""
        path = self.output_dir / filename
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def _print_summary(self, total_time: float):
        """Print pipeline completion summary."""
        print(f"\n{'='*60}")
        print(f"PIPELINE COMPLETE — {self.project_name}")
        print(f"{'='*60}")
        print(f"\nTotal time: {total_time:.1f}s")
        print(f"\nOutput: {self.output_dir}")
        print(f"\nFiles:")
        for f in sorted(self.output_dir.iterdir()):
            if f.is_file():
                size = f.stat().st_size
                print(f"  {f.name:30s} {size:>8,} bytes")

        print(f"\nTimings:")
        for role, t in sorted(self.timings.items()):
            print(f"  {role:20s} {t:>6.1f}s")

        sec = self.results.get("security", {})
        if isinstance(sec, dict):
            print(f"\nSecurity score: {sec.get('score', 0):.0f}%")

        print(f"\nRun:")
        print(f"  cd {self.output_dir}")
        print(f"  pip install flask pyjwt flask-cors flask-sqlalchemy pytest")
        print(f"  python app.py")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    roles = None
    args = sys.argv[1:]

    # Parse --roles flag
    if "--roles" in args:
        idx = args.index("--roles")
        roles = args[idx + 1].split(",")
        args = args[:idx] + args[idx + 2:]

    if args[0] == "--from-prd":
        description = f"Build from PRD: {args[1]}"
    else:
        description = " ".join(args)

    pipeline = VibePipelineV2(roles=roles)
    pipeline.results["_description"] = description
    pipeline.run(description)


if __name__ == "__main__":
    main()
