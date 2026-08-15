#!/usr/bin/env python3
"""
MAHI Vibe Coding Pipeline — Wired Edition
Build anything in one session — describe it, MAHI builds it.

Usage:
    python vibe_pipeline.py "Build a task management app with auth"
    python vibe_pipeline.py --from-prd path/to/prd.md
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).parent.resolve()
TEMPLATES_DIR = PROJECT_ROOT / "brain" / "templates"
OUTPUT_DIR = PROJECT_ROOT / "vibe-output"

# Import MAHI system
sys.path.insert(0, str(PROJECT_ROOT))
from MAHI import MahiSystem
from agents.base import Task


class VibePipeline:
    """Orchestrate the 5-role vibe coding pipeline using real MAHI agents."""

    def __init__(self, project_name: str = None):
        self.project_name = project_name or f"vibe-{datetime.now().strftime('%Y%m%d-%H%M')}"
        self.output_dir = OUTPUT_DIR / self.project_name
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = {}
        self.mahi = MahiSystem()

    def run(self, description: str) -> dict:
        """Run the full pipeline from description to launch."""
        print(f"\n{'='*60}")
        print(f"MAHI VIBE CODING PIPELINE")
        print(f"Project: {self.project_name}")
        print(f"{'='*60}\n")

        # Phase 1: PM Agent (write) -> PRD
        print("[1/5] PM Agent: Generating PRD...")
        prd = self._run_pm(description)
        self.results["prd"] = prd

        # Phase 2: UI/UX Agent (code) -> HTML
        print("[2/5] UI/UX Agent: Building dashboard...")
        ui = self._run_ui(prd)
        self.results["ui"] = ui

        # Phase 3: Code Agent (code) -> Backend
        print("[3/5] Code Agent: Building backend...")
        code = self._run_code(prd)
        self.results["code"] = code

        # Phase 4: Security Agent (code) -> Validation
        print("[4/5] Security Agent: Validating...")
        security = self._run_security(code)
        self.results["security"] = security

        # Phase 5: Growth Agent (write) -> Launch materials
        print("[5/5] Growth Agent: Generating launch materials...")
        growth = self._run_growth(prd, code)
        self.results["growth"] = growth

        # Summary
        self._print_summary()
        return self.results

    def _run_pm(self, description: str) -> str:
        """PM Agent: Generate PRD from description using /write agent."""
        template = (TEMPLATES_DIR / "PRD_TEMPLATE.md").read_text()

        task = Task(
            user_input=f"""You are a Product Manager. Generate a complete PRD for this project:

PROJECT: {self.project_name}
DESCRIPTION: {description}

Use this template structure and fill in ALL sections with specific, actionable details:

{template}

Return ONLY the filled-in PRD markdown. No explanations.""",
            category="writing",
            agent_id="write",
            model="nvidia/nemotron-3-super-120b-a12b:free",
        )

        agent = self.mahi.agents.get("write")
        if agent:
            task = agent.run(task)
            if task.result:
                prd_path = self.output_dir / "PRD.md"
                prd_path.write_text(task.result, encoding="utf-8")
                print(f"  [OK] PRD saved ({task.elapsed}s)")
                return str(prd_path)

        # Fallback to template
        print("  [WARN] Write agent unavailable, using template fallback")
        prd = template.replace("{PROJECT_NAME}", self.project_name)
        prd = prd.replace("{PROBLEM_STATEMENT}", description)
        prd = prd.replace("{DATE}", datetime.now().strftime("%Y-%m-%d"))
        for key, val in [
            ("{TARGET_USERS}", "To be defined"), ("{FEATURE_NAME}", "Core Feature"),
            ("{FRONTEND_TECH}", "HTML/CSS/JS"), ("{BACKEND_TECH}", "Python"),
            ("{DATABASE}", "SQLite"), ("{AUTH_METHOD}", "JWT"),
            ("{DATA_MODEL}", "To be defined"), ("{API_ENDPOINTS}", "To be defined"),
            ("{DESCRIPTION}", "To be defined"), ("{OUT_OF_SCOPE_1}", "Mobile app"),
            ("{OUT_OF_SCOPE_2}", "Multi-tenant"),
        ]:
            prd = prd.replace(key, val)

        prd_path = self.output_dir / "PRD.md"
        prd_path.write_text(prd, encoding="utf-8")
        print(f"  [OK] PRD saved (template fallback)")
        return str(prd_path)

    def _run_ui(self, prd_path: str) -> str:
        """UI/UX Agent: Generate dashboard HTML from PRD using /code agent."""
        prd_content = Path(prd_path).read_text()

        task = Task(
            user_input=f"""Generate a complete, production-ready HTML dashboard for this project:

{prd_content}

Requirements:
- Single index.html file (inline CSS + JS)
- Dark theme (#0f172a background, gradient accents)
- Responsive (mobile-first)
- Navigation sidebar
- Dashboard cards with stats
- Clean, modern design (Outfit font, rounded corners)
- Include: header, main content area, footer

Return ONLY the HTML code. No explanations.""",
            category="code",
            agent_id="code",
            model="nvidia/nemotron-3-super-120b-a12b:free",
        )

        agent = self.mahi.agents.get("code")
        if agent:
            task = agent.run(task)
            if task.result:
                # Extract HTML if wrapped in markdown
                result = task.result
                if "```html" in result:
                    result = result.split("```html")[1].split("```")[0]
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0]

                html_path = self.output_dir / "index.html"
                html_path.write_text(result.strip(), encoding="utf-8")
                print(f"  [OK] UI saved ({task.elapsed}s)")
                return str(html_path)

        # Fallback to basic HTML
        print("  [WARN] Code agent unavailable, using fallback HTML")
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.project_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Outfit', sans-serif; background: #0f172a; color: #e2e8f0; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
        .header {{ text-align: center; padding: 40px 0; }}
        .header h1 {{ font-size: 2.5rem; background: linear-gradient(135deg, #3b82f6, #06b6d4); -webkit-background-clip: text; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }}
        .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 24px; }}
        .card h3 {{ color: #3b82f6; margin-bottom: 8px; }}
        .card p {{ color: #94a3b8; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{self.project_name}</h1>
            <p style="color:#94a3b8;margin-top:12px">Generated by MAHI Vibe Pipeline</p>
        </div>
        <div class="grid">
            <div class="card"><h3>Dashboard</h3><p>Real-time overview</p></div>
            <div class="card"><h3>Settings</h3><p>Configure preferences</p></div>
            <div class="card"><h3>API</h3><p>RESTful endpoints</p></div>
        </div>
    </div>
</body>
</html>"""
        html_path = self.output_dir / "index.html"
        html_path.write_text(html, encoding="utf-8")
        print(f"  [OK] UI saved (fallback)")
        return str(html_path)

    def _run_code(self, prd_path: str) -> str:
        """Code Agent: Build backend from PRD using /code agent."""
        prd_content = Path(prd_path).read_text()

        task = Task(
            user_input=f"""Generate a complete Flask backend for this project:

{prd_content}

Requirements:
- Single app.py file
- Flask with CORS
- JWT authentication (using PyJWT)
- SQLite database with SQLAlchemy
- RESTful API endpoints
- Input validation
- Error handling
- Environment variable config

Return ONLY the Python code. No explanations.""",
            category="code",
            agent_id="code",
            model="nvidia/nemotron-3-super-120b-a12b:free",
        )

        agent = self.mahi.agents.get("code")
        if agent:
            task = agent.run(task)
            if task.result:
                result = task.result
                if "```python" in result:
                    result = result.split("```python")[1].split("```")[0]
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0]

                app_path = self.output_dir / "app.py"
                app_path.write_text(result.strip(), encoding="utf-8")
                print(f"  [OK] Backend saved ({task.elapsed}s)")
                return str(app_path)

        # Fallback
        print("  [WARN] Code agent unavailable, using fallback backend")
        app_code = f'''#!/usr/bin/env python3
""" {self.project_name} -- Backend (fallback) """
from flask import Flask, jsonify, request
from functools import wraps
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key")

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({{"error": "Missing auth"}}), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def index():
    return jsonify({{"name": "{self.project_name}", "status": "running"}})

@app.route("/api/health")
def health():
    return jsonify({{"status": "ok"}})

@app.route("/api/data")
@require_auth
def get_data():
    return jsonify({{"items": []}})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
'''
        app_path = self.output_dir / "app.py"
        app_path.write_text(app_code, encoding="utf-8")
        print(f"  [OK] Backend saved (fallback)")
        return str(app_path)

    def _run_security(self, code_path: str) -> dict:
        """Security Agent: Validate code using /code agent."""
        code_content = Path(code_path).read_text()

        task = Task(
            user_input=f"""Review this Python code for security vulnerabilities:

{code_content}

Check for:
1. Input validation
2. SQL injection
3. XSS prevention
4. Secret management
5. Authentication/authorization
6. Rate limiting
7. CORS configuration
8. Error handling

Return a JSON object with:
- score (0-100)
- checks (dict of check_name: true/false)
- recommendations (list of strings)

Return ONLY valid JSON.""",
            category="code",
            agent_id="code",
            model="nvidia/nemotron-3-super-120b-a12b:free",
        )

        agent = self.mahi.agents.get("code")
        if agent:
            task = agent.run(task)
            if task.result:
                try:
                    result = task.result
                    if "```json" in result:
                        result = result.split("```json")[1].split("```")[0]
                    elif "```" in result:
                        result = result.split("```")[1].split("```")[0]
                    security = json.loads(result.strip())
                    report_path = self.output_dir / "security-report.json"
                    report_path.write_text(json.dumps(security, indent=2), encoding="utf-8")
                    score = security.get("score", 0)
                    print(f"  [OK] Security score: {score}% ({task.elapsed}s)")
                    return security
                except json.JSONDecodeError:
                    pass

        # Fallback
        print("  [WARN] Security review failed, using basic checks")
        checks = {
            "input_validation": "validate" in code_content.lower() or "required" in code_content,
            "secrets_in_env": "os.environ" in code_content or "getenv" in code_content,
            "auth_required": "auth" in code_content.lower(),
            "rate_limiting": "limiter" in code_content.lower(),
            "cors_configured": "cors" in code_content.lower(),
        }
        score = sum(checks.values()) / len(checks) * 100
        security = {
            "score": score,
            "checks": checks,
            "recommendations": [
                "Add rate limiting with flask-limiter",
                "Configure CORS with flask-cors",
                "Add input validation with marshmallow",
            ]
        }
        report_path = self.output_dir / "security-report.json"
        report_path.write_text(json.dumps(security, indent=2), encoding="utf-8")
        print(f"  [OK] Security score: {score}% (basic)")
        return security

    def _run_growth(self, prd_path: str, code_path: str) -> dict:
        """Growth Agent: Generate launch materials using /write agent."""
        prd_content = Path(prd_path).read_text()

        task = Task(
            user_input=f"""Generate launch materials for this project:

PRD: {prd_content[:500]}

Create:
1. One-line pitch (max 100 chars)
2. Short description (2-3 sentences)
3. 5 SEO tags
4. Launch checklist (7 items)

Return as JSON:
{{"pitch": "...", "description": "...", "tags": [...], "launch_checklist": [...]}}""",
            category="writing",
            agent_id="write",
            model="nvidia/nemotron-3-super-120b-a12b:free",
        )

        agent = self.mahi.agents.get("write")
        if agent:
            task = agent.run(task)
            if task.result:
                try:
                    result = task.result
                    if "```json" in result:
                        result = result.split("```json")[1].split("```")[0]
                    elif "```" in result:
                        result = result.split("```")[1].split("```")[0]
                    growth = json.loads(result.strip())
                    growth_path = self.output_dir / "growth.json"
                    growth_path.write_text(json.dumps(growth, indent=2), encoding="utf-8")
                    print(f"  [OK] Launch materials saved ({task.elapsed}s)")
                    return growth
                except json.JSONDecodeError:
                    pass

        # Fallback
        print("  [WARN] Growth agent failed, using fallback")
        growth = {
            "pitch": f"{self.project_name} -- Built with MAHI in one session",
            "description": "A complete app generated by AI pipeline",
            "tags": ["ai", "vibe-coding", "mahi"],
            "launch_checklist": [
                "[OK] PRD generated",
                "[OK] UI built",
                "[OK] Backend built",
                "[OK] Security validated",
                "[TODO] Deploy to production",
                "[TODO] Set up monitoring",
                "[TODO] Write documentation",
            ]
        }
        growth_path = self.output_dir / "growth.json"
        growth_path.write_text(json.dumps(growth, indent=2), encoding="utf-8")
        print(f"  [OK] Launch materials saved (fallback)")
        return growth

    def _print_summary(self):
        """Print pipeline completion summary."""
        print(f"\n{'='*60}")
        print(f"PIPELINE COMPLETE -- {self.project_name}")
        print(f"{'='*60}")
        print(f"\nOutput: {self.output_dir}")
        print(f"\nFiles:")
        for f in sorted(self.output_dir.iterdir()):
            size = f.stat().st_size
            print(f"  {f.name:30s} {size:>6,} bytes")

        sec = self.results.get("security", {})
        print(f"\nSecurity: {sec.get('score', 0):.0f}%")
        print(f"\nRun:")
        print(f"  cd {self.output_dir}")
        print(f"  pip install flask pyjwt flask-cors flask-sqlalchemy")
        print(f"  python app.py")


def main():
    if len(sys.argv) < 2:
        print("Usage: python vibe_pipeline.py 'Build a task management app'")
        print("       python vibe_pipeline.py --from-prd path/to/prd.md")
        sys.exit(1)

    if sys.argv[1] == "--from-prd":
        prd_path = sys.argv[2]
        description = f"Build from PRD: {prd_path}"
    else:
        description = " ".join(sys.argv[1:])

    pipeline = VibePipeline()
    pipeline.run(description)


if __name__ == "__main__":
    main()
