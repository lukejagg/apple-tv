---
name: apple-tv
description: Control Apple TV from the command line — remote control, screenshots, power management, and status. Use this skill when any task involves Apple TV interaction.
argument-hint: [command like screenshot, on, off, up, down, select, status]
---

# Apple TV Control

CLI tool for controlling Apple TV over the local network. Combines pyatv (remote control) and pymobiledevice3 (screenshots via developer services tunnel).

## Quick Reference

```bash
# Remote control
apple-tv on                    # Wake
apple-tv off                   # Sleep
apple-tv up / down / left / right  # Navigate
apple-tv select                # Confirm
apple-tv menu                  # Back
apple-tv home                  # Home screen
apple-tv play / pause / playpause
apple-tv next / prev
apple-tv volume-up / volume-down

# Screenshots (requires daemon running)
apple-tv screenshot            # Save to default location
apple-tv screenshot /tmp/tv.png  # Save to specific path

# Status
apple-tv status                # Power state, now playing

# Service management
apple-tv start                 # Start daemon + menu bar
apple-tv stop                  # Stop both
apple-tv restart               # Restart both
apple-tv install               # Install LaunchDaemon + LaunchAgent (persistent)
apple-tv uninstall             # Remove everything

# Diagnostics
apple-tv doctor                # Check everything is configured and working
apple-tv rediscover            # Update Apple TV IP if it changed
apple-tv logs                  # Tail daemon and menu bar logs
```

## Architecture

Three components, one CLI:

1. **LaunchDaemon** (`com.apple-tv.daemon`) — runs as root, maintains pymobiledevice3 tunnel for screenshots, serves HTTP API on `127.0.0.1:7654`
2. **LaunchAgent** (`com.apple-tv.menubar`) — menu bar app (📺), polls daemon for status, quick actions
3. **CLI** (`bin/apple-tv`) — for remote control uses pyatv directly (no root needed), for screenshots hits the daemon API

Remote control commands (navigation, power, playback) go through **pyatv** and do NOT need the daemon. Only screenshots need the daemon (because pymobiledevice3 requires root for the TUN tunnel).

## Setup (First Time)

### Prerequisites

Install dependencies with uv:
```bash
uv sync
```

### Step 1: Remote Control Pairing (pyatv)

```bash
apple-tv setup
```

This discovers your Apple TV, then pairs the Companion and AirPlay protocols. A PIN will appear on the TV for each — enter it when prompted. Credentials are saved to `~/.config/apple-tv/credentials.json`.

### Step 2: Screenshot Pairing (pymobiledevice3)

Screenshots require Apple's developer services protocol, which needs extra setup:

1. **Enable Developer Mode** on Apple TV: Settings → Privacy & Security → Developer Mode → ON (reboots)
2. **Pair via Xcode** (optional but helps): Open Xcode → Window → Devices and Simulators → your Apple TV should appear
3. **Pair pymobiledevice3**: The `apple-tv setup` command handles this. Navigate to Settings → Remotes and Devices → Remote App and Devices on the Apple TV, then follow the prompts.

**Known issue:** pymobiledevice3's Bonjour discovery often fails to find Apple TVs. The setup script works around this by using macOS native `dns-sd` to discover the device and connecting directly by IP.

### Step 3: Install Background Services

```bash
apple-tv install
```

This creates:
- `/Library/LaunchDaemons/com.apple-tv.daemon.plist` (root, auto-starts on boot)
- `~/Library/LaunchAgents/com.apple-tv.menubar.plist` (user, auto-starts on login)

Asks for sudo password once. After this, everything just works.

> The pymobiledevice3 buffer size is automatically patched at runtime — no manual step needed.

## Configuration

All config lives in `~/.config/apple-tv/`:

- `config.json` — device IP, name, pairing IDs, screenshot directory
- `credentials.json` — pyatv Companion + AirPlay credentials

## Daemon API

The daemon exposes these endpoints on `http://127.0.0.1:7654`:

| Endpoint | Description |
|----------|-------------|
| `GET /` | Health check |
| `GET /status` | Power state + now playing |
| `GET /screenshot` | Take screenshot, return PNG bytes |
| `GET /screenshot?nosave=1` | Return PNG bytes without saving to disk |
| `GET /remote?action=<action>` | Send remote command (up/down/select/home/on/off/etc) |

## Logs

- Daemon: `/tmp/apple-tv-daemon.log`
- Menu bar: `/tmp/apple-tv-menubar.log`

## Troubleshooting

- **Screenshot fails with "Device is not connected"**: Apple TV might be asleep. Wake it first with `apple-tv on`.
- **Screenshot fails with "ConnectionTerminatedError"**: Pairing may have expired. Re-run `apple-tv setup` for the pymobiledevice3 step.
- **"Apple TV not found"**: Device IP may have changed. Re-run `apple-tv setup` or update `~/.config/apple-tv/config.json`.
- **Menu bar not visible**: Check if it's behind the notch or in the overflow area. Run `apple-tv restart` to cycle it.

## Project Structure

```
apple-tv/
├── app/
│   ├── config.py       # Configuration management
│   ├── daemon.py       # HTTP daemon (root, screenshots + remote API)
│   ├── install.py      # LaunchDaemon/Agent install/uninstall
│   ├── menubar.py      # macOS menu bar app (rumps)
│   ├── remote.py       # pyatv remote control
│   ├── screenshot.py   # pymobiledevice3 screenshot
│   └── setup.py        # Interactive pairing/discovery
├── bin/
│   └── apple-tv        # CLI entry point
└── .claude/
    └── skills/
        └── apple-tv/
            └── SKILL.md
```
