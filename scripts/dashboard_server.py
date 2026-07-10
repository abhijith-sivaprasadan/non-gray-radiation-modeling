"""Live, interactive local dashboard for the thermal radiation portfolio.

Stdlib-only HTTP server (no Flask/FastAPI dependency) exposing:

  GET  /                 the interactive single-page app
  GET  /api/data         JSON payload (see scripts/_dashboard_data.py)
  GET  /outputs/<path>   static files from outputs/ (figures)
  POST /api/run          {"target": "all"|"project1".."project5"} - runs the
                          matching workflow script synchronously and returns
                          {"ok": bool, "log_tail": [...]}

Run with: python scripts/dashboard_server.py
Then open the printed URL. Ctrl+C to stop.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

import json
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

from _dashboard_data import build_payload
from dashboard_app import PAGE_HTML

PROJECT_ROOT = _bootstrap.PROJECT_ROOT
OUTPUT_DIR = PROJECT_ROOT / "outputs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
PORT = int(os.environ.get("DASHBOARD_PORT", "8765"))

TARGETS: dict[str, str] = {
    "all": "run_all.py",
    "project1": "run_project1_real_hydrogen.py",
    "project2": "run_project2_real_particles.py",
    "project3": "run_project3_real_dom.py",
    "project4": "run_project4_real_surrogate.py",
    "project5": "run_radcal_asset.py",
}

CONTENT_TYPES = {
    ".png": "image/png",
    ".html": "text/html; charset=utf-8",
    ".csv": "text/csv; charset=utf-8",
    ".md": "text/markdown; charset=utf-8",
}


class DashboardHandler(BaseHTTPRequestHandler):
    server_version = "RadiationDashboard/1.0"

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        sys.stderr.write(f"{self.address_string()} - {format % args}\n")

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/":
            self._send_html(PAGE_HTML)
        elif path == "/api/data":
            self._send_json(build_payload(OUTPUT_DIR))
        elif path.startswith("/outputs/"):
            self._send_static_file(path[len("/outputs/") :])
        else:
            self._send_json({"error": "not found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path != "/api/run":
            self._send_json({"error": "not found"}, status=404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length) if length > 0 else b"{}"
        try:
            body = json.loads(raw_body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send_json({"error": "invalid JSON body"}, status=400)
            return

        target = body.get("target")
        script_name = TARGETS.get(target)
        if script_name is None:
            self._send_json(
                {"error": f"unknown target {target!r}; expected one of {sorted(TARGETS)}"},
                status=400,
            )
            return

        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / script_name)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        log_tail = (result.stdout + result.stderr).splitlines()[-40:]
        self._send_json({"ok": result.returncode == 0, "log_tail": log_tail})

    def _send_static_file(self, relative_path: str) -> None:
        candidate = (OUTPUT_DIR / unquote(relative_path)).resolve()
        try:
            candidate.relative_to(OUTPUT_DIR.resolve())
        except ValueError:
            self._send_json({"error": "forbidden"}, status=403)
            return
        if not candidate.is_file():
            self._send_json({"error": "not found"}, status=404)
            return

        content_type = CONTENT_TYPES.get(candidate.suffix.lower(), "application/octet-stream")
        data = candidate.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_html(self, text: str) -> None:
        data = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload: object, status: int = 200) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        server = ThreadingHTTPServer(("127.0.0.1", PORT), DashboardHandler)
    except OSError:
        # Most likely the port is already bound by a previous instance of this same
        # server - that instance is already serving, so this is not a failure.
        print(
            f"Dashboard server already running (or port {PORT} is busy): http://127.0.0.1:{PORT}/"
        )
        return

    print(f"Serving the radiation portfolio dashboard at http://127.0.0.1:{PORT}/")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
