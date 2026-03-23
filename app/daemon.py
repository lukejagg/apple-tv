"""HTTP daemon — runs as root via LaunchDaemon, serves screenshot + remote API."""
import asyncio
import json
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

from .config import DAEMON_PORT
from . import remote, screenshot


def run():
    loop = asyncio.new_event_loop()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path.strip("/")
            params = urllib.parse.parse_qs(parsed.query)

            if path == "":
                self._json({"status": "ok", "service": "apple-tv daemon"})
            elif path == "status":
                try:
                    result = loop.run_until_complete(remote.status())
                    self._json(result)
                except Exception as e:
                    self._json({"error": str(e)}, 500)
            elif path == "screenshot":
                try:
                    nosave = params.get("nosave", ["0"])[0] == "1"
                    out = None if nosave else params.get("path", [None])[0]
                    _, data = loop.run_until_complete(screenshot.take(out))
                    self.send_response(200)
                    self.send_header("Content-Type", "image/png")
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                except Exception as e:
                    self._json({"error": str(e), "traceback": traceback.format_exc()}, 500)
            elif path == "remote":
                action = params.get("action", [None])[0]
                if not action:
                    self._json({"error": "missing ?action="}, 400)
                    return
                try:
                    if action in ("on", "turn_on"):
                        loop.run_until_complete(remote.power(True))
                    elif action in ("off", "turn_off"):
                        loop.run_until_complete(remote.power(False))
                    else:
                        loop.run_until_complete(remote.send(action))
                    self._json({"ok": True, "action": action})
                except Exception as e:
                    self._json({"error": str(e)}, 500)
            else:
                self._json({"error": "not found"}, 404)

        def _json(self, data, code=200):
            body = json.dumps(data).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = HTTPServer(("127.0.0.1", DAEMON_PORT), Handler)
    print(f"apple-tv daemon running on http://127.0.0.1:{DAEMON_PORT}")
    server.serve_forever()
