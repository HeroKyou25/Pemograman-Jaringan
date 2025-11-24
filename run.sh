#!/usr/bin/env bash
set -euo pipefail

# Simple runner that installs deps to user site (if missing) and starts the app
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

REQ_FILE="requirements.txt"

# Check if dependencies are installed
echo "Checking dependencies..."
if python3 -c "import uvicorn, fastapi" 2>/dev/null; then
  echo "✓ Dependencies already installed"
else
  echo "Installing dependencies to user site..."
  if [ -f "$REQ_FILE" ]; then
    pip install --user -r "$REQ_FILE"
  else
    pip install --user "uvicorn[standard]" fastapi requests jinja2 aiofiles websockets
  fi
fi

echo ""
echo "=========================================="
echo "Starting server on http://0.0.0.0:5000"
echo "=========================================="
echo ""
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 5000
