#!/bin/bash
# Arcade Server Screensaver — Earth C-137
# Launches the live server dashboard as a fullscreen screensaver
# Usage: arcade-screensaver.sh [--window-id WID]
#
# Works with:
#   - xscreensaver (as a hack)
#   - KDE screensaver (via QML WebView wrapper)
#   - Standalone: just run it

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HTML_PATH="$SCRIPT_DIR/index.html"

# Check for window-id (xscreensaver compatibility)
if [[ "$1" == "--window-id" ]] || [[ "$1" == "-window-id" ]]; then
    WINDOW_ID="$2"
fi

# Try different browsers in order of preference
if command -v firefox &>/dev/null; then
    exec firefox --kiosk --private-window "file://$HTML_PATH" 2>/dev/null
elif command -v chromium &>/dev/null; then
    exec chromium --kiosk --app="file://$HTML_PATH" --disable-extensions --no-first-run 2>/dev/null
elif command -v falkon &>/dev/null; then
    exec falkon --fullscreen "file://$HTML_PATH" 2>/dev/null
elif command -v qutebrowser &>/dev/null; then
    exec qutebrowser --target window "file://$HTML_PATH" 2>/dev/null
else
    echo "No suitable browser found. Install firefox or chromium."
    exit 1
fi
