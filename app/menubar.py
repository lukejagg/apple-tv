"""macOS menu bar app — shows Apple TV status, quick actions."""
import json
import os
import threading
import urllib.request

import rumps

from .config import DAEMON_PORT, load_config

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
ICON_ON = os.path.join(ASSETS_DIR, "tv-on.png")
ICON_OFF = os.path.join(ASSETS_DIR, "tv-off.png")
ICON_DISCONNECTED = os.path.join(ASSETS_DIR, "tv-disconnected.png")


class AppleTVApp(rumps.App):
    def __init__(self):
        cfg = load_config()
        name = cfg.get("name") or "Apple TV"
        super().__init__(name, icon=ICON_ON, template=True, quit_button=None)
        self._device_name = name
        self._screenshot_dir = cfg.get("screenshot_dir", "")
        self.menu = [
            rumps.MenuItem(name, callback=None),
            None,
            rumps.MenuItem("Screenshot", callback=self.on_screenshot),
            None,
            rumps.MenuItem("Wake", callback=self.on_wake),
            rumps.MenuItem("Sleep", callback=self.on_sleep),
            None,
            rumps.MenuItem("Home", callback=self.on_home),
            rumps.MenuItem("Menu / Back", callback=self.on_menu),
            rumps.MenuItem("Select", callback=self.on_select),
            None,
            rumps.MenuItem("Play / Pause", callback=self.on_playpause),
            rumps.MenuItem("Next", callback=self.on_next),
            rumps.MenuItem("Previous", callback=self.on_prev),
            None,
            rumps.MenuItem("Quit", callback=self.on_quit),
        ]
        self._poll_timer = rumps.Timer(self._poll_status, 15)
        self._poll_timer.start()

    def _set_icon(self, path):
        """Update the menu bar icon."""
        if os.path.exists(path):
            self.icon = path

    def _api(self, path):
        try:
            url = f"http://127.0.0.1:{DAEMON_PORT}/{path}"
            with urllib.request.urlopen(url, timeout=10) as resp:
                return json.loads(resp.read())
        except Exception:
            return None

    def _poll_status(self, _):
        result = self._api("status")
        if result and "power" in result:
            power = result["power"]
            if "On" in power:
                self._set_icon(ICON_ON)
                self.title = ""
            else:
                self._set_icon(ICON_OFF)
                self.title = ""
            self.menu[self._device_name].title = f"{self._device_name} — {power}"
        else:
            self._set_icon(ICON_DISCONNECTED)
            self.title = ""
            self.menu[self._device_name].title = f"{self._device_name} — Disconnected"

    def _send(self, action):
        threading.Thread(target=self._api, args=(f"remote?action={action}",), daemon=True).start()

    def on_screenshot(self, _):
        def _do():
            result = self._api("screenshot")
            if result and "error" not in result:
                rumps.notification("Apple TV", "Screenshot saved", self._screenshot_dir)
        threading.Thread(target=_do, daemon=True).start()

    def on_wake(self, _): self._send("on")
    def on_sleep(self, _): self._send("off")
    def on_home(self, _): self._send("home")
    def on_menu(self, _): self._send("menu")
    def on_select(self, _): self._send("select")
    def on_playpause(self, _): self._send("playpause")
    def on_next(self, _): self._send("next")
    def on_prev(self, _): self._send("prev")
    def on_quit(self, _): rumps.quit_application()


def run():
    AppleTVApp().run()
