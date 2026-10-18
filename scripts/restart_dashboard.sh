#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="${PROJECT_ROOT:-/opt/healthguard-ai/HealthGuard-AI}"
VENV="$PROJECT_ROOT/.venv"
if [[ ! -x "$VENV/bin/python" ]]; then VENV="$PROJECT_ROOT/.venv-dashboard"; fi
"$VENV/bin/python" -m py_compile "$PROJECT_ROOT/dashboard/app.py"
sudo systemctl restart healthguard-dashboard
sleep 2
sudo systemctl --no-pager --full status healthguard-dashboard
