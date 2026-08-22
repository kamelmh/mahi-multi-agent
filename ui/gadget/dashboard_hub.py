#!/usr/bin/env python3
"""
LifeWorkspace Gadget — Dashboard Hub server.

Serves the gadget and gives the Dashboard Hub tab live app detection + launching.
Apps that point at localhost ports (Streamlit 8501, Vite 5173, Django 5000) are
detected at runtime; stopped ones can be launched from the UI (deps auto-installed).

Run:
    python dashboard_hub.py [--port 8000] [--open]

Endpoints:
    GET  /                     gadget index.html (and static assets)
    GET  /api/apps             list apps + live status
    GET  /api/apps/<id>/status single app status
    POST /api/apps/<id>/launch start an app (auto-installs deps if needed)
    POST /api/apps/<id>/stop   stop an app (by PID or listening port)
    GET  /api/logs/<id>        recent log tail for an app
"""
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

GADGET_DIR = Path(__file__).parent
LOG_DIR = GADGET_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Apps managed by the Dashboard Hub. `url` + `port` drive detection;
# `launch`/`check`/`requirements` drive starting. type "live" = external URL.
APPS = [
    {
        "id": "teaching",
        "name": "Teaching Platform",
        "icon": "📚",
        "desc": "Streamlit: exercise generator, flashcards, MCQ, mind maps, assessments",
        "url": "http://localhost:8501",
        "port": 8501,
        "type": "local",
        "cwd": r"C:\Users\Admin\projects\active\apps\lifeworkspace-teaching-platform",
        "launch": ["python", "-m", "streamlit", "run", "app.py",
                   "--server.port", "8501", "--server.headless", "true",
                   "--server.address", "127.0.0.1"],
        "check": ["python", "-c", "import streamlit"],
    },
    {
        "id": "spiritual",
        "name": "Spiritual Dashboard",
        "icon": "🕯️",
        "desc": "Astrology + Quran practice dashboard (live)",
        "url": "https://mahi-spiritual.netlify.app",
        "type": "live",
    },
    {
        "id": "academix",
        "name": "Academix DSS Web",
        "icon": "📦",
        "desc": "VBA DSS web viewer (Univer)",
        "url": "http://localhost:5173",
        "port": 5173,
        "type": "local",
        "cwd": r"C:\Users\Admin\projects\active\apps\academix-dss\web",
        "launch": ["npm", "run", "dev"],
    },
    {
        "id": "sis",
        "name": "SIS Ta'allim",
        "icon": "🏫",
        "desc": "Student Information System (Django)",
        "url": "http://localhost:5000",
        "port": 5000,
        "type": "local",
        "cwd": r"C:\Users\Admin\projects\active\apps\sis-taallim",
        "launch": ["python", "manage.py", "runserver", "5000", "--noreload"],
        "check": ["python", "-c", "import django"],
        "requirements": "requirements.txt",
    },
    {
        "id": "floci",
        "name": "Floci AWS Local",
        "icon": "☁️",
        "desc": "Local AWS emulator (S3 + DynamoDB + Lambda)",
        "url": "http://localhost:4566",
        "port": 4566,
        "type": "local",
        "cwd": str(Path(__file__).parent.parent.parent),
        "launch": ["floci", "start"],
        "check": ["floci", "status"],
    },
    {
        "id": "dsh",
        "name": "DeepSeek Harness",
        "icon": "🔍",
        "desc": "DeepSeek agent harness — web UI for coding, file ops, shell, web search",
        "url": "http://localhost:8500",
        "port": 8500,
        "type": "local",
        "cwd": str(Path(__file__).parent.parent.parent),
        "launch": ["npx", "@deepseek-ai/dsh", "web", "--port", "8500"],
        "check": ["npx", "@deepseek-ai/dsh", "--version"],
    },
    {
        "id": "harness",
        "name": "Harness Router (UHP)",
        "icon": "🔗",
        "desc": "UHP-compatible harness router — routes tasks to agents via OpenRouter/Groq",
        "url": "http://localhost:8600",
        "port": 8600,
        "type": "local",
        "cwd": str(Path(__file__).parent.parent.parent),
        "launch": [sys.executable, "harness_router.py", "8600"],
        "check": [sys.executable, "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8600/health')"],
    },
]

WIN_LAUNCH_FLAGS = 0
if os.name == "nt":
    WIN_LAUNCH_FLAGS = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)


def is_port_open(host: str, port: int, timeout: float = 0.8) -> bool:
    """Probe a TCP port on the given host, falling back to the other stack
    (vite binds ::1, streamlit binds 127.0.0.1)."""
    hosts = [host]
    if host in ("127.0.0.1", "localhost"):
        hosts = ["127.0.0.1", "::1"]
    for h in hosts:
        s = socket.socket(socket.AF_INET6 if ":" in h else socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            s.connect((h, port))
            return True
        except OSError:
            pass
        finally:
            s.close()
    return False


def http_probe(url: str, timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout):
            return True
    except Exception:
        return False


def find_app(app_id: str):
    for app in APPS:
        if app["id"] == app_id:
            return app
    return None


def pid_on_port(port: int):
    """Find the PID listening on a TCP port (Windows netstat)."""
    try:
        out = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, timeout=10).stdout
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 5 and parts[3] == "LISTENING":
                addr = parts[1]
                if addr.endswith(f":{port}"):
                    return int(parts[-1])
    except Exception:
        pass
    return None


class AppManager:
    """Tracks app state: detection, dependency setup, background launch/stop."""

    def __init__(self):
        self.state = {}
        for app in APPS:
            self.state[app["id"]] = {
                "phase": "stopped", "pid": None, "busy": False,
                "error": None, "log": str(LOG_DIR / f'{app["id"]}.log'),
            }

    # --- detection -------------------------------------------------------
    def status(self, app):
        st = self.state[app["id"]]
        if app["type"] == "live":
            st["phase"] = "live"
            return {"id": app["id"], "name": app["name"], "icon": app["icon"],
                    "url": app["url"], "status": "live", "running": True}
        port_open = is_port_open("127.0.0.1", app["port"])
        http_ok = port_open and http_probe(app["url"])
        if port_open:
            st["phase"] = "running"
        elif st["phase"] in ("running", "launching") and not st["busy"]:
            st["phase"] = "stopped"
        return {"id": app["id"], "name": app["name"], "icon": app["icon"],
                "url": app["url"], "status": st["phase"], "running": port_open,
                "http_ok": http_ok, "pid": st["pid"], "error": st["error"]}

    def all_status(self):
        return {"apps": [self.status(a) for a in APPS]}

    # --- launch ----------------------------------------------------------
    def launch(self, app):
        if app["type"] == "live":
            return {"ok": True, "status": "live", "running": True}
        st = self.state[app["id"]]
        if self.status(app)["running"]:
            return {"ok": True, "status": "running", "running": True}
        if st["busy"]:
            return {"ok": True, "status": st["phase"]}
        st["busy"] = True
        st["error"] = None
        threading.Thread(target=self._launch_worker, args=(app,), daemon=True).start()
        return {"ok": True, "status": "launching"}

    @staticmethod
    def _resolve_cmd(cmd):
        """Resolve programs to absolute paths; .cmd/.bat shims route via cmd /c."""
        if os.name != "nt":
            return cmd
        prog = cmd[0]
        low = prog.lower()
        if low == "python":
            return [sys.executable] + list(cmd[1:])
        if low == "cmd":
            root = os.environ.get("SystemRoot") or r"C:\Windows"
            return [os.path.join(root, "System32", "cmd.exe")] + list(cmd[1:])
        if low in ("npm", "npx", "yarn", "pnpm") or low.endswith((".cmd", ".bat")):
            root = os.environ.get("SystemRoot") or r"C:\Windows"
            return [os.path.join(root, "System32", "cmd.exe"), "/c"] + cmd
        return cmd

    @staticmethod
    def _child_env(cmd):
        """Child env with System32 + tool dirs on PATH so shims (npm) resolve."""
        env = dict(os.environ)
        extra = []
        root = os.environ.get("SystemRoot") or r"C:\Windows"
        extra += [os.path.join(root, "System32"), root,
                  os.path.join(root, "System32", "Wbem")]
        for prog in ("python", "node", "npm", "streamlit"):
            exe = shutil.which(prog)
            if exe:
                extra.append(os.path.dirname(exe))
        env["PATH"] = os.pathsep.join(extra + [env.get("PATH", "")])
        return env

    def _launch_worker(self, app):
        st = self.state[app["id"]]
        log_path = Path(st["log"])
        try:
            log = open(log_path, "a", encoding="utf-8")
        except OSError:
            log = open(os.devnull, "w")
        def write(msg):
            log.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
            log.flush()
        write(f"=== launch {app['name']} ===")
        try:
            cwd = app.get("cwd")
            env = self._child_env(app["launch"])
            check = app.get("check")
            if check:
                try:
                    r = subprocess.run(check, cwd=cwd, env=env, capture_output=True, text=True, timeout=60)
                    deps_ok = r.returncode == 0
                except Exception as e:
                    write(f"dep check error: {e}")
                    deps_ok = False
                if not deps_ok and app.get("requirements"):
                    st["phase"] = "installing"
                    write("dependencies missing — installing requirements.txt ...")
                    try:
                        r2 = subprocess.run(
                            [sys.executable, "-m", "pip", "install", "-r", app["requirements"]],
                            cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=900)
                        if r2.returncode != 0:
                            write("dependency install FAILED")
                    except Exception as e:
                        write(f"dependency install error: {e}")
            st["phase"] = "launching"
            launch_cmd = self._resolve_cmd(app["launch"])
            proc = subprocess.Popen(
                launch_cmd, cwd=cwd, stdin=subprocess.DEVNULL,
                stdout=log, stderr=subprocess.STDOUT, env=env,
                creationflags=WIN_LAUNCH_FLAGS)
            st["pid"] = proc.pid
            write(f"started pid={proc.pid}: {' '.join(launch_cmd)}")
            deadline = time.time() + 90
            while time.time() < deadline:
                if self.status(app)["running"]:
                    break
                if proc.poll() is not None:
                    st["phase"] = "failed"
                    st["error"] = f"process exited rc={proc.returncode}"
                    write(f"process exited rc={proc.returncode}")
                    break
                time.sleep(1.5)
            if st["phase"] == "launching":
                if self.status(app)["running"]:
                    st["phase"] = "running"
                else:
                    st["phase"] = "failed"
                    st["error"] = "app did not open its port within 90s"
                    write("app did not open its port within 90s")
        except Exception as e:
            st["phase"] = "failed"
            st["error"] = str(e)
            write(f"launch error: {e}")
        finally:
            st["busy"] = False
            log.close()

    # --- stop ------------------------------------------------------------
    def stop(self, app):
        if app["type"] == "live":
            return {"ok": True, "status": "live"}
        st = self.state[app["id"]]
        killed = []
        pid = st.get("pid")
        if pid:
            try:
                subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                               capture_output=True, timeout=15)
                killed.append(f"pid {pid}")
            except Exception:
                pass
        port_pid = pid_on_port(app["port"]) if not killed else None
        if port_pid and port_pid not in (pid,):
            try:
                subprocess.run(["taskkill", "/PID", str(port_pid), "/T", "/F"],
                               capture_output=True, timeout=15)
                killed.append(f"pid {port_pid} (port {app['port']})")
            except Exception:
                pass
        st["pid"] = None
        st["phase"] = "stopped"
        st["error"] = None
        return {"ok": True, "killed": killed}

    # --- CI status --------------------------------------------------------
    REPOS = [
        {"name": "mahi-multi-agent", "path": r"C:\Users\Admin\projects\active\agents\mahi-multi-agent"},
        {"name": "digital-services-center", "path": r"C:\Users\Admin\projects\active\apps\digital-services-center"},
        {"name": "academix-dss", "path": r"C:\Users\Admin\projects\active\apps\academix-dss"},
        {"name": "logistics-public-sector-refactor", "path": r"C:\Users\Admin\projects\active\umbrella\logistics-public-sector-refactor"},
        {"name": "lsm-vba-core", "path": r"C:\Users\Admin\projects\active\libs\lsm-vba-core"},
        {"name": "mahi-spiritual", "path": r"C:\Users\Admin\projects\active\apps\mahi-spiritual"},
    ]

    def ci_status(self):
        """Check git status + last commit for each repo."""
        results = []
        for repo in self.REPOS:
            p = Path(repo["path"])
            if not p.exists():
                results.append({"name": repo["name"], "status": "missing", "branch": "", "last_commit": "", "dirty": False})
                continue
            try:
                branch = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=str(p), capture_output=True, text=True, timeout=10
                ).stdout.strip()
                last = subprocess.run(
                    ["git", "log", "-1", "--format=%h %s (%cr)"],
                    cwd=str(p), capture_output=True, text=True, timeout=10
                ).stdout.strip()
                dirty = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=str(p), capture_output=True, text=True, timeout=10
                ).stdout.strip()
                results.append({
                    "name": repo["name"],
                    "status": "dirty" if dirty else "clean",
                    "branch": branch,
                    "last_commit": last,
                    "dirty": bool(dirty),
                    "uncommitted": len(dirty.splitlines()) if dirty else 0,
                })
            except Exception as e:
                results.append({"name": repo["name"], "status": "error", "error": str(e)})
        return {"repos": results}


class HubHandler(BaseHTTPRequestHandler):
    manager = AppManager()

    def log_message(self, fmt, *args):
        sys.stderr.write(f"[hub] {fmt % args}\n")

    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length:
                return json.loads(self.rfile.read(length))
        except Exception:
            pass
        return {}

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/apps":
            return self._send(200, self.manager.all_status())
        if path == "/api/ci-status":
            return self._send(200, self.manager.ci_status())
        m = re.match(r"^/api/apps/([\w-]+)/status$", path)
        if m:
            app = find_app(m.group(1))
            if not app:
                return self._send(404, {"error": "app not found"})
            return self._send(200, self.manager.status(app))
        m = re.match(r"^/api/logs/([\w-]+)$", path)
        if m:
            log = LOG_DIR / f'{m.group(1)}.log'
            if log.exists():
                tail = log.read_text(encoding="utf-8", errors="replace")[-4000:]
                return self._send(200, {"log": tail})
            return self._send(200, {"log": ""})
        self._serve_static(path)

    def do_POST(self):
        path = urlparse(self.path).path
        m = re.match(r"^/api/apps/([\w-]+)/(launch|stop)$", path)
        if m:
            app = find_app(m.group(1))
            if not app:
                return self._send(404, {"error": "app not found"})
            result = self.manager.launch(app) if m.group(2) == "launch" else self.manager.stop(app)
            return self._send(200, result)
        if path == "/api/apps":
            return self._send(400, {"error": "POST /api/apps not supported"})
        self._send(404, {"error": "not found"})

    def _serve_static(self, path):
        if path in ("/", ""):
            path = "/index.html"
        target = (GADGET_DIR / path.lstrip("/")).resolve()
        if not str(target).startswith(str(GADGET_DIR.resolve())) or not target.is_file():
            return self._send(404, "Not Found", "text/plain")
        ctype = {
            ".html": "text/html", ".js": "application/javascript",
            ".css": "text/css", ".json": "application/json",
            ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml",
        }.get(target.suffix.lower(), "application/octet-stream")
        self._send(200, target.read_bytes(), ctype)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="LifeWorkspace Gadget Dashboard Hub")
    parser.add_argument("--port", type=int, default=8000, help="port to serve the gadget (default 8000)")
    parser.add_argument("--open", action="store_true", help="open the gadget in the default browser")
    parser.add_argument("--host", default="127.0.0.1", help="bind host (default 127.0.0.1)")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), HubHandler)
    print(f"\n  LifeWorkspace Gadget Dashboard Hub")
    print(f"  Serving:  http://{args.host}:{args.port}")
    print(f"  Apps:     {', '.join(a['id'] for a in APPS)}")
    print(f"  Press Ctrl+C to stop.\n")
    if args.open:
        import webbrowser
        threading.Timer(0.6, lambda: webbrowser.open(f"http://{args.host}:{args.port}")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Hub stopped.")


if __name__ == "__main__":
    main()