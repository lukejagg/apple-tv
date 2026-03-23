# Apple TV

CLI + menu bar app for controlling Apple TV over the local network.

## Skill

Read `.claude/skills/apple-tv/SKILL.md` before working on this project.

## Dev

Uses `uv` for dependency management. Dependencies in `pyproject.toml`.

```bash
uv sync
```

## Test

```bash
./bin/apple-tv status
./bin/apple-tv screenshot /tmp/test.png
```
