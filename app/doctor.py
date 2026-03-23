"""Health check — verify everything is configured and working."""
import asyncio
import json
import os
import subprocess
import urllib.request

from .config import (
    CONFIG_FILE, CREDS_FILE, DAEMON_PORT, DAEMON_PLIST, AGENT_PLIST,
    DAEMON_LABEL, load_config,
)


def run():
    ok = True

    def check(label, passed, detail=""):
        nonlocal ok
        icon = "✓" if passed else "✗"
        msg = f"  {icon} {label}"
        if detail:
            msg += f" — {detail}"
        print(msg)
        if not passed:
            ok = False

    print("apple-tv doctor\n")

    # Config
    print("Configuration:")
    cfg = load_config()
    check("Config file", CONFIG_FILE.exists(), str(CONFIG_FILE))
    check("IP configured", bool(cfg.get("ip")), cfg.get("ip", "not set"))
    check("Device name", bool(cfg.get("name")), cfg.get("name", "not set"))

    # Credentials
    print("\nPairing:")
    creds_exist = CREDS_FILE.exists()
    check("Credentials file", creds_exist, str(CREDS_FILE))
    if creds_exist:
        with open(CREDS_FILE) as f:
            creds = json.load(f)
        check("Companion paired", bool(creds.get("Companion")))
        check("AirPlay paired", bool(creds.get("AirPlay")))
    check("Screenshot pairing ID", bool(cfg.get("pmd3_pairing_id")),
          cfg.get("pmd3_pairing_id", "not set")[:16] + "..." if cfg.get("pmd3_pairing_id") else "not set")

    # Network
    print("\nNetwork:")
    ip = cfg.get("ip")
    if ip:
        ret = subprocess.run(["ping", "-c", "1", "-t", "2", ip],
                             capture_output=True)
        check("Apple TV reachable", ret.returncode == 0, ip)
    else:
        check("Apple TV reachable", False, "no IP configured")

    # Daemon
    print("\nServices:")
    check("Daemon plist", DAEMON_PLIST.exists(), str(DAEMON_PLIST))
    check("Agent plist", AGENT_PLIST.exists(), str(AGENT_PLIST))

    try:
        url = f"http://127.0.0.1:{DAEMON_PORT}/"
        with urllib.request.urlopen(url, timeout=3) as resp:
            data = json.loads(resp.read())
        check("Daemon running", data.get("status") == "ok", f"port {DAEMON_PORT}")
    except Exception:
        check("Daemon running", False, f"not responding on port {DAEMON_PORT}")

    # Menu bar
    ret = subprocess.run(["pgrep", "-f", "apple-tv.*menubar"], capture_output=True)
    check("Menu bar running", ret.returncode == 0)

    # Remote control
    print("\nRemote control:")
    if creds_exist and ip:
        try:
            from .remote import status
            result = asyncio.run(status())
            check("pyatv connection", True, result.get("power", "?"))
        except Exception as e:
            check("pyatv connection", False, str(e)[:60])
    else:
        check("pyatv connection", False, "missing credentials or IP")

    print()
    if ok:
        print("All checks passed!")
    else:
        print("Some checks failed. Run 'apple-tv setup' to fix configuration issues.")
