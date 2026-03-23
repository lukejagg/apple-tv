---
name: apple-tv
description: Control Apple TV from the command line — remote control, screenshots, power management, and status. Use this skill when any task involves Apple TV interaction.
argument-hint: [command like screenshot, on, off, up, down, select, status]
---

# Apple TV Control

Control an Apple TV over the local network using the `apple-tv` CLI. Requires the CLI to be installed and on PATH — see https://github.com/lukejagg/apple-tv for setup.

## Step 1: Check if apple-tv is available

```bash
apple-tv doctor
```

If this fails, the CLI isn't installed. Tell the user to follow the setup at https://github.com/lukejagg/apple-tv.

## Step 2: Use the CLI

### Remote Control

```bash
apple-tv on                          # Power on / wake
apple-tv off                         # Power off / sleep
apple-tv up                          # Navigate up
apple-tv down                        # Navigate down
apple-tv left                        # Navigate left
apple-tv right                       # Navigate right
apple-tv select                      # Confirm / press OK
apple-tv menu                        # Go back
apple-tv home                        # Home screen
apple-tv play                        # Play
apple-tv pause                       # Pause
apple-tv playpause                   # Toggle play/pause
apple-tv next                        # Next track
apple-tv prev                        # Previous track
apple-tv volume-up                   # Volume up
apple-tv volume-down                 # Volume down
```

### Screenshots

```bash
apple-tv screenshot                  # Save to default location
apple-tv screenshot /tmp/tv.png      # Save to specific path
```

Use screenshots to **see what's on the TV screen**. Read the screenshot image to understand the current UI state, then send navigation commands to interact with it.

### Status

```bash
apple-tv status                      # Power state + now playing info
```

### Diagnostics

```bash
apple-tv doctor                      # Verify config, pairing, network, daemon
apple-tv rediscover                  # Update Apple TV IP if it changed (DHCP)
apple-tv logs                        # Tail daemon and menu bar logs
apple-tv restart                     # Restart background services
```

## How to Navigate the Apple TV

The Apple TV UI works like a grid. Use `up`/`down`/`left`/`right` to move focus, `select` to press, and `menu` to go back.

**Pattern for browsing apps:**
1. `apple-tv home` — go to home screen
2. `apple-tv screenshot` — see what's on screen
3. Navigate to the app with arrow commands
4. `apple-tv select` — open the app
5. `apple-tv screenshot` — see the app's UI
6. Continue navigating + screenshotting

**Important:** Always `sleep 1` between a navigation command and a screenshot — the UI needs time to update.

**Scrolling:** The Apple TV has no scroll command. Use `down`/`right` repeatedly to scroll through lists. Take screenshots after each move to track position.

## Daemon API (Advanced)

The background daemon runs on `http://127.0.0.1:7654`. You can use it directly:

| Endpoint | Description |
|----------|-------------|
| `GET /status` | Power state + now playing (JSON) |
| `GET /screenshot?nosave=1` | Take screenshot, return raw PNG bytes |
| `GET /remote?action=<cmd>` | Send remote command |

## Troubleshooting

- **"Apple TV not found"**: IP may have changed. Run `apple-tv rediscover`.
- **Screenshot fails**: Daemon may not be running. Run `apple-tv restart`.
- **TV not responding**: It might be asleep. Run `apple-tv on` first.
