#!/usr/bin/env python3
"""
apple-tv — Control your Apple TV from the command line.

Usage:
  apple-tv                     Show this help
  apple-tv <command>           Send a command

Setup:
  setup                        Interactive first-time setup (discover, pair)
  install                      Install LaunchDaemon + LaunchAgent
  uninstall                    Remove LaunchDaemon + LaunchAgent

Service:
  start                        Start daemon + menu bar
  stop                         Stop daemon + menu bar
  restart                      Restart daemon + menu bar

Control:
  on / off                     Power on/off
  up / down / left / right     Navigation
  select / ok                  Confirm selection
  menu / back                  Go back
  home                         Home button
  play / pause / playpause     Playback
  next / prev                  Skip track
  volume-up / volume-down      Volume

Info:
  screenshot [path]            Take screenshot
  status                       Show what's playing + power state
  doctor                       Check if everything is configured and working
  rediscover                   Update Apple TV IP if it changed
  logs                         Tail daemon and menu bar logs
"""
import asyncio
import os
import sys
import tempfile

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from app.config import DAEMON_PORT, load_config, CONFIG_FILE, CREDS_FILE


def _check_setup(need_creds=True):
    """Exit with a helpful message if not configured."""
    cfg = load_config()
    if not cfg.get("ip"):
        print("Apple TV not configured. Run 'apple-tv setup' first.")
        sys.exit(1)
    if need_creds and not CREDS_FILE.exists():
        print("Not paired. Run 'apple-tv setup' to pair with your Apple TV.")
        sys.exit(1)
    return cfg


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print(__doc__.strip())
        return

    cmd = sys.argv[1].replace("-", "_")

    # ── Internal modes (called by launchd) ──
    if cmd in ("__daemon", "_daemon", "daemon"):
        from app.daemon import run
        run()
    elif cmd in ("__menubar", "_menubar", "menubar"):
        from app.menubar import run
        run()

    # ── Setup & lifecycle ──
    elif cmd == "setup":
        from app.setup import run_setup
        asyncio.run(run_setup())
    elif cmd == "install":
        from app.install import install
        install()
    elif cmd == "uninstall":
        from app.install import uninstall
        uninstall()
    elif cmd == "start":
        from app.install import start
        start()
    elif cmd == "stop":
        from app.install import stop
        stop()
    elif cmd == "restart":
        from app.install import restart
        restart()

    # ── Diagnostics ──
    elif cmd == "doctor":
        from app.doctor import run
        run()
    elif cmd == "rediscover":
        from app.rediscover import run
        asyncio.run(run())
    elif cmd == "logs":
        os.execlp("tail", "tail", "-f",
                   "/tmp/apple-tv-daemon.log", "/tmp/apple-tv-menubar.log")

    # ── Power ──
    elif cmd in ("on", "turn_on"):
        _check_setup()
        from app.remote import power
        asyncio.run(power(True))
    elif cmd in ("off", "turn_off"):
        _check_setup()
        from app.remote import power
        asyncio.run(power(False))

    # ── Status ──
    elif cmd == "status":
        _check_setup()
        from app.remote import status
        result = asyncio.run(status())
        print(f"Power: {result['power']}")
        print(f"State: {result['state']}")
        if result.get("title"):
            print(f"Title: {result['title']}")
        if result.get("artist"):
            print(f"Artist: {result['artist']}")

    # ── Screenshot ──
    elif cmd == "screenshot":
        _check_setup()
        out = sys.argv[2] if len(sys.argv) > 2 else None
        cfg = load_config()
        default_path = os.path.join(cfg["screenshot_dir"], "appletv-screen.png")
        path = out or default_path

        if os.geteuid() == 0:
            from app.screenshot import take
            asyncio.run(take(path))
            print(f"Screenshot saved to {path}")
        else:
            import urllib.request
            try:
                url = f"http://127.0.0.1:{DAEMON_PORT}/screenshot?nosave=1"
                with urllib.request.urlopen(url, timeout=30) as resp:
                    data = resp.read()
                os.makedirs(os.path.dirname(path), exist_ok=True)
                fd, tmp = tempfile.mkstemp(suffix=".png", dir=os.path.dirname(path))
                with os.fdopen(fd, "wb") as f:
                    f.write(data)
                os.replace(tmp, path)
                print(f"Screenshot saved to {path}")
            except ConnectionRefusedError:
                print("Daemon not running. Run 'apple-tv install' or 'apple-tv start'.")
            except Exception as e:
                print(f"Error: {e}")
                print("Is the daemon running? Try: apple-tv start")

    # ── Remote control ──
    elif cmd in ("up", "down", "left", "right", "select", "ok",
                 "menu", "back", "home", "top_menu",
                 "play", "pause", "playpause",
                 "next", "prev", "volume_up", "volume_down"):
        _check_setup()
        from app.remote import send
        asyncio.run(send(cmd))
    else:
        print(f"Unknown command: {sys.argv[1]}")
        print(f"\nRun 'apple-tv --help' for usage.")


if __name__ == "__main__":
    main()
