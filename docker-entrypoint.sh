#!/bin/bash
set -e

# Start Xvfb
echo "Starting Xvfb..."
Xvfb :99 -screen 0 1280x1024x24 -nolisten tcp -ac &
export DISPLAY=:99
sleep 2

# Verify display
echo "DISPLAY=$DISPLAY"

# Activate venv
export PATH="/opt/venv/bin:$PATH"

# Run the app
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info
