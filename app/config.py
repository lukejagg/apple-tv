"""Configuration management for apple-tv."""
import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "apple-tv"
CONFIG_FILE = CONFIG_DIR / "config.json"
CREDS_FILE = CONFIG_DIR / "credentials.json"
DAEMON_PORT = 7654
DAEMON_LABEL = "com.apple-tv.daemon"
AGENT_LABEL = "com.apple-tv.menubar"
DAEMON_PLIST = Path(f"/Library/LaunchDaemons/{DAEMON_LABEL}.plist")
AGENT_PLIST = Path.home() / "Library" / "LaunchAgents" / f"{AGENT_LABEL}.plist"

DEFAULT_CONFIG = {
    "ip": None,
    "name": None,
    "pmd3_pairing_id": None,
    "pmd3_tunnel_port": 49152,
    "screenshot_dir": str(Path.home() / "Pictures" / "apple-tv"),
}


def load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
        return {**DEFAULT_CONFIG, **cfg}
    return dict(DEFAULT_CONFIG)


def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def load_credentials() -> dict:
    if not CREDS_FILE.exists():
        raise FileNotFoundError(
            "No credentials found. Run 'apple-tv setup' to pair with your Apple TV."
        )
    with open(CREDS_FILE) as f:
        return json.load(f)


def save_credentials(creds: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CREDS_FILE, "w") as f:
        json.dump(creds, f, indent=2)


def get_python() -> str:
    """Return the path to the Python interpreter running this script."""
    import sys
    return sys.executable


def get_user_home() -> str:
    """Return the real user's home dir (even when running as root via sudo)."""
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user:
        import pwd
        return pwd.getpwnam(sudo_user).pw_dir
    return str(Path.home())


def get_user_uid() -> int:
    """Return the real user's UID (even when running as root)."""
    sudo_uid = os.environ.get("SUDO_UID")
    if sudo_uid:
        return int(sudo_uid)
    return os.getuid()


def get_user_gid() -> int:
    """Return the real user's GID (even when running as root)."""
    sudo_gid = os.environ.get("SUDO_GID")
    if sudo_gid:
        return int(sudo_gid)
    return os.getgid()
