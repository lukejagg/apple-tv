#!/bin/bash
set -e

REPO_URL="https://github.com/lukejagg/apple-tv.git"
INSTALL_DIR="${APPLE_TV_DIR:-$HOME/Projects/apple-tv}"
LINK_DIR="${HOME}/.local/bin"

echo "=== apple-tv install ==="
echo

# 1. Check for uv
if ! command -v uv &>/dev/null; then
    echo "Error: uv is not installed."
    echo "  brew install uv"
    echo "  or: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 2. Clone or update repo
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Updating $INSTALL_DIR..."
    (cd "$INSTALL_DIR" && git pull --ff-only 2>/dev/null || true)
else
    echo "Cloning to $INSTALL_DIR..."
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

# 3. Install dependencies
echo "Installing dependencies..."
(cd "$INSTALL_DIR" && uv sync)

# 4. Symlink to PATH
mkdir -p "$LINK_DIR"
ln -sf "$INSTALL_DIR/bin/apple-tv" "$LINK_DIR/apple-tv"
echo "Linked: $LINK_DIR/apple-tv"

# 5. Verify PATH
if ! echo "$PATH" | tr ':' '\n' | grep -q "$LINK_DIR"; then
    echo
    echo "Warning: $LINK_DIR is not on your PATH."
    echo "Add to your shell profile:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo
echo "✓ apple-tv installed"
echo
echo "Next steps:"
echo "  apple-tv setup     # discover + pair your Apple TV"
echo "  apple-tv install   # start background daemon + menu bar"
