#!/bin/bash

# Setup script for dot-claude
# Creates symbolic links in ~/.claude to this repository's files

set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Define the target directory
CLAUDE_DIR="$HOME/.claude"

# Check if ~/.claude exists
if [ ! -d "$CLAUDE_DIR" ]; then
    echo "Error: $CLAUDE_DIR does not exist. Please ensure Claude Code is installed."
    exit 1
fi

echo "Setting up dot-claude symbolic links..."

# Create symbolic links
ln -sfn "$SCRIPT_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
echo "✓ Linked CLAUDE.md"

ln -sfn "$SCRIPT_DIR/commands" "$CLAUDE_DIR/commands"
echo "✓ Linked commands directory"

ln -sfn "$SCRIPT_DIR/docs" "$CLAUDE_DIR/docs"
echo "✓ Linked docs directory"

ln -sfn "$SCRIPT_DIR/tools" "$CLAUDE_DIR/tools"
echo "✓ Linked tools directory"

# Optional: link settings.json if you want to version control it
# ln -sfn "$SCRIPT_DIR/settings.json" "$CLAUDE_DIR/settings.json"
# echo "✓ Linked settings.json"

echo ""
echo "Setup complete! Your dot-claude configuration is now linked to ~/.claude"
echo ""
echo "Next steps:"
echo "1. Run 'python3 tools/link-to-obsidian.py' to set up Obsidian vault integration"
echo "2. Ensure CLAUDE_VAULT environment variable is set to your Obsidian vault path"