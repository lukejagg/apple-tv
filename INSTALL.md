# Installation

## Prerequisites

- macOS (tested on macOS 15+)
- [uv](https://docs.astral.sh/uv/) — `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Xcode (for initial Apple TV developer pairing)
- Apple TV on the same local network

## 1. Clone and install dependencies

```bash
git clone <repo-url> ~/Projects/apple-tv
cd ~/Projects/apple-tv
uv sync
```

## 2. Enable Developer Mode on Apple TV (for screenshots)

1. On your Apple TV, go to **Settings → Privacy & Security → Developer Mode**
2. Toggle **ON** — the Apple TV will reboot
3. After reboot, confirm when prompted

This is required for pymobiledevice3 to access developer services (screenshots). If you only need remote control (power, navigation, playback), you can skip this step.

## 3. Run interactive setup

```bash
./bin/apple-tv setup
```

This walks you through:

### Step 1: pyatv pairing (remote control)

The setup discovers your Apple TV on the network, then pairs the **Companion** and **AirPlay** protocols. For each:
- A PIN appears on the Apple TV screen
- Enter it in the terminal

Credentials are saved to `~/.config/apple-tv/credentials.json`.

### Step 2: pymobiledevice3 pairing (screenshots)

This requires the Apple TV to be on **Settings → Remotes and Devices → Remote App and Devices** during pairing.

The setup uses macOS native `dns-sd` to discover the device (pymobiledevice3's built-in Bonjour browse is unreliable for Apple TVs), then connects directly by IP.

A PIN appears on the TV — enter it when prompted.

Config is saved to `~/.config/apple-tv/config.json`.

## 4. Install background services

```bash
./bin/apple-tv install
```

This creates two launchd services (asks for sudo password once):

| Service | Type | Purpose |
|---------|------|---------|
| `com.apple-tv.daemon` | LaunchDaemon (root) | HTTP API on `127.0.0.1:7654` — maintains tunnel for screenshots |
| `com.apple-tv.menubar` | LaunchAgent (user) | Menu bar app (📺) — status display, quick actions |

Both auto-start on boot/login. The daemon runs as root because pymobiledevice3 needs a TUN interface for the developer services tunnel.

## 5. Symlink the CLI (optional)

```bash
ln -sf ~/Projects/apple-tv/bin/apple-tv ~/bin/apple-tv
# or wherever your PATH includes
```

## Verify

```bash
apple-tv status          # Should show power state
apple-tv home            # Should press home on the TV
apple-tv screenshot      # Should save a screenshot
```

## Uninstall

```bash
apple-tv uninstall       # Removes LaunchDaemon + LaunchAgent
```

To fully remove:
```bash
apple-tv uninstall
rm -rf ~/Projects/apple-tv
rm -rf ~/.config/apple-tv
rm ~/.pymobiledevice3/remote_*.plist  # pymobiledevice3 pairing records
```
