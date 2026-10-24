#!/usr/bin/env bash
set -euo pipefail

# Ensure ~/.local/bin is in PATH if it exists
if [ -d "$HOME/.local/bin" ] && [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    export PATH="$HOME/.local/bin:$PATH"
fi

# Ensure pyproject-build is installed
if ! command -v pyproject-build &> /dev/null; then
    echo "Installation of package 'build' (for pyproject-build) via uv..."
    uv tool install build
    if [ -d "$HOME/.local/bin" ] && [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        export PATH="$HOME/.local/bin:$PATH"
    fi
fi

# Execute isolated build
echo "Start isolated build with pyproject-build..."
if command -v pyproject-build &> /dev/null; then
    pyproject-build "$@"
else
    uvx --from build pyproject-build "$@"
fi
