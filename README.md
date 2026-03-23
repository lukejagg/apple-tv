# apple-tv

Give your AI agent full control of your Apple TV.

`apple-tv` is a CLI that lets AI coding agents (Claude Code, Cursor, Copilot, etc.) navigate your Apple TV, take screenshots of what's on screen, read the UI, control playback, and manage power — all programmatically. No remote needed.

**What can an agent do with this?**
- Browse your streaming apps, read what's on screen, and tell you what to watch
- Navigate menus, search for shows, and start playback
- Take screenshots to analyze your TV's UI state
- Turn your TV on/off as part of automations
- Build workflows that react to what's currently playing

It also works great as a standalone CLI for humans who want to control their Apple TV from the terminal.

## How It Works

Uses [pyatv](https://github.com/postlund/pyatv) (Media Remote Protocol) for remote control and [pymobiledevice3](https://github.com/doronz88/pymobiledevice3) (Apple developer services) for screenshots.

| Component | Purpose | Runs as |
|-----------|---------|---------|
| **CLI** (`bin/apple-tv`) | Remote control, screenshots, setup | User |
| **Daemon** (`com.apple-tv.daemon`) | Maintains tunnel for screenshots, HTTP API on `:7654` | Root (LaunchDaemon) |
| **Menu bar** (`com.apple-tv.menubar`) | 📺 status display + quick actions in macOS menu bar | User (LaunchAgent) |

Remote control goes through pyatv — no root needed. Screenshots require the daemon because pymobiledevice3 needs a TUN interface for Apple's developer services tunnel.

## Quick Start

```bash
git clone https://github.com/lukejagg/apple-tv.git
cd apple-tv
uv sync
./bin/apple-tv setup      # discover + pair (interactive, ~2 min)
./bin/apple-tv install    # start background daemon + menu bar
```

See [INSTALL.md](INSTALL.md) for detailed setup instructions including Developer Mode setup for screenshots.

## Usage

```bash
# Power
apple-tv on
apple-tv off

# Navigation
apple-tv up / down / left / right
apple-tv select                       # confirm
apple-tv menu                         # back
apple-tv home                         # home screen

# Playback
apple-tv play / pause / playpause
apple-tv next / prev
apple-tv volume-up / volume-down

# Screenshots
apple-tv screenshot                   # save to ~/Pictures/apple-tv/
apple-tv screenshot /tmp/tv.png       # save to specific path

# Info
apple-tv status                       # power state + now playing
apple-tv doctor                       # verify everything is configured
apple-tv rediscover                   # update IP if it changed
apple-tv logs                         # tail daemon + menu bar logs

# Service management
apple-tv start / stop / restart
apple-tv install / uninstall
```

## Agent Integration

### Claude Code Skill

This repo ships as a [Claude Code skill](SKILL.md). Install it so Claude can control your TV:

```bash
npx skills add lukejagg/apple-tv
```

### Example: Agent browsing Crunchyroll

```
User: "What anime do I have on my watchlist?"

Agent runs:
  apple-tv home                              # go to home screen
  apple-tv right → right → select            # open Crunchyroll
  apple-tv screenshot /tmp/cr1.png           # capture what's on screen
  [reads screenshot, sees watchlist]
  apple-tv down → screenshot /tmp/cr2.png    # scroll and capture more
  ...
  "You have 90 anime on your Crunchyroll watchlist, including..."
```

The agent uses `screenshot` + vision to see the TV, and navigation commands to interact with it. No API needed — it controls the TV the same way a human would with a remote.

## Requirements

- macOS 13+ (uses CoreBluetooth, launchd)
- [uv](https://docs.astral.sh/uv/)
- Apple TV 4K on the same local network
- Xcode (for initial developer pairing, required for screenshots only)
