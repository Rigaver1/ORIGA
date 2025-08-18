#!/usr/bin/env bash
set -euo pipefail

PYTHON=${PYTHON:-python3}
VENV_DIR=.venv

if [ ! -d "$VENV_DIR" ]; then
  $PYTHON -m venv $VENV_DIR
fi
source $VENV_DIR/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# Optional: install playwright browsers if available (ignore failures)
if command -v playwright >/dev/null 2>&1; then
  playwright install --with-deps chromium || true
else
  python -m playwright install chromium || true
fi

export PYTHONPATH=.

exec uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload