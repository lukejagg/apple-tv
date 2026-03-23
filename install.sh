#!/bin/bash
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
LINK_DIR="${HOME}/.local/bin"

echo "=== apple-tv install ==="
echo

# 1. Install dependencies
echo "Installing dependencies..."
if command -v uv &>/dev/null; then
    (cd "$REPO_DIR" && uv sync)
else
    echo "Error: uv is not installed. Install it: brew install uv"
    exit 1
fi

# 2. Symlink to PATH
echo
mkdir -p "$LINK_DIR"
ln -sf "$REPO_DIR/bin/apple-tv" "$LINK_DIR/apple-tv"
echo "Linked: $LINK_DIR/apple-tv → $REPO_DIR/bin/apple-tv"

# 3. Verify PATH
if ! echo "$PATH" | tr ':' '\n' | grep -q "$LINK_DIR"; then
    echo
    echo "Warning: $LINK_DIR is not on your PATH."
    echo "Add this to your ~/.zshrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

# 4. Verify it works
echo
if command -v apple-tv &>/dev/null; then
    echo "✓ apple-tv is on your PATH"
else
    echo "Open a new terminal and run: apple-tv --help"
fi

echo
echo "Next steps:"
echo "  apple-tv setup     # discover + pair your Apple TV"
echo "  apple-tv install   # start background daemon + menu bar"
