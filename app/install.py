"""Install/uninstall LaunchDaemon + LaunchAgent."""
import os
import subprocess
import sys

from .config import (
    DAEMON_LABEL, AGENT_LABEL, DAEMON_PLIST, AGENT_PLIST,
    get_python, get_user_home,
)

SCRIPT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin", "_main.py")


def install():
    python = get_python()
    home = get_user_home()

    daemon_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{DAEMON_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python}</string>
        <string>{SCRIPT_PATH}</string>
        <string>--daemon</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HOME</key>
        <string>{home}</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/apple-tv-daemon.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/apple-tv-daemon.log</string>
</dict>
</plist>"""

    agent_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{AGENT_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python}</string>
        <string>{SCRIPT_PATH}</string>
        <string>--menubar</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/apple-tv-menubar.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/apple-tv-menubar.log</string>
</dict>
</plist>"""

    print("Installing LaunchDaemon (requires sudo)...")
    subprocess.run(
        ["sudo", "tee", str(DAEMON_PLIST)],
        input=daemon_plist.encode(), stdout=subprocess.DEVNULL, check=True,
    )
    subprocess.run(["sudo", "launchctl", "bootout", f"system/{DAEMON_LABEL}"], capture_output=True)
    subprocess.run(["sudo", "launchctl", "bootstrap", "system", str(DAEMON_PLIST)], check=True)
    print("  ✓ Daemon installed and started")

    print("Installing LaunchAgent (menu bar)...")
    AGENT_PLIST.parent.mkdir(parents=True, exist_ok=True)
    with open(AGENT_PLIST, "w") as f:
        f.write(agent_plist)
    subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}/{AGENT_LABEL}"], capture_output=True)
    subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(AGENT_PLIST)], capture_output=True)
    print("  ✓ Menu bar agent installed and started")
    print("\nDone! You should see 📺 in your menu bar.")


def uninstall():
    stop()
    print("Removing LaunchAgent...")
    subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}/{AGENT_LABEL}"], capture_output=True)
    if AGENT_PLIST.exists():
        AGENT_PLIST.unlink()
    print("  ✓ Agent removed")

    print("Removing LaunchDaemon (requires sudo)...")
    subprocess.run(["sudo", "launchctl", "bootout", f"system/{DAEMON_LABEL}"], capture_output=True)
    subprocess.run(["sudo", "rm", "-f", str(DAEMON_PLIST)], capture_output=True)
    print("  ✓ Daemon removed")


def start():
    subprocess.run(["sudo", "launchctl", "kickstart", "-k", f"system/{DAEMON_LABEL}"], capture_output=True)
    subprocess.run(["launchctl", "kickstart", "-k", f"gui/{os.getuid()}/{AGENT_LABEL}"], capture_output=True)
    print("Started apple-tv daemon and menu bar.")


def stop():
    subprocess.run(["sudo", "launchctl", "kill", "SIGTERM", f"system/{DAEMON_LABEL}"], capture_output=True)
    subprocess.run(["launchctl", "kill", "SIGTERM", f"gui/{os.getuid()}/{AGENT_LABEL}"], capture_output=True)
    print("Stopped.")


def restart():
    subprocess.run(["sudo", "launchctl", "kickstart", "-k", f"system/{DAEMON_LABEL}"])
    subprocess.run(["launchctl", "kickstart", "-k", f"gui/{os.getuid()}/{AGENT_LABEL}"], capture_output=True)
    print("Restarted.")
