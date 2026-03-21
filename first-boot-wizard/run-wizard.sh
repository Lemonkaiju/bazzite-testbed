#!/bin/bash
# LemonKaijuOS First-Boot Wizard Launcher

set -euo pipefail

WIZARD_DIR="/usr/share/lemonkaijuos/first-boot-wizard"
STATE_DIR="/var/lib/lemonkaijuos"
COMPLETE_FLAG="${STATE_DIR}/first-boot-complete"

# Check if already completed
if [ -f "$COMPLETE_FLAG" ]; then
    echo "First-boot wizard already completed"
    exit 0
fi

# Launch wizard in fullscreen browser
cd "$WIZARD_DIR"

# Start Flask server in background
python3 wizard.py &
WIZARD_PID=$!

# Wait for server to start
sleep 2

# Open in Firefox fullscreen (kiosk mode)
firefox --kiosk http://localhost:5555 &
FIREFOX_PID=$!

# Wait for Firefox to close (user completes wizard)
wait $FIREFOX_PID

# Stop Flask server
kill $WIZARD_PID 2>/dev/null || true

# Mark as complete
touch "$COMPLETE_FLAG"

echo "First-boot wizard completed"
