#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/healthguard-ai/HealthGuard-AI}"
SERVER_IP="${SERVER_IP:-127.0.0.1}"
RUN_USER="${RUN_USER:-${SUDO_USER:-ubuntu}}"
RUN_GROUP="${RUN_GROUP:-$RUN_USER}"

if [[ ! -d "$PROJECT_ROOT" ]]; then
  echo "ERROR: project root not found: $PROJECT_ROOT" >&2
  exit 1
fi

cd "$PROJECT_ROOT"

# Prefer the project's existing venv so already-downloaded Python packages are reused.
if [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
  VENV="$PROJECT_ROOT/.venv"
else
  VENV="$PROJECT_ROOT/.venv-dashboard"
  if [[ ! -x "$VENV/bin/python" ]]; then
    echo "Creating dashboard virtual environment once: $VENV"
    sudo -u "$RUN_USER" python3 -m venv "$VENV"
  fi
fi

# Install only when required. Normal source-code updates never run pip.
if ! sudo -u "$RUN_USER" "$VENV/bin/python" - <<'PY' >/dev/null 2>&1
import pandas, streamlit, plotly, requests
PY
then
  echo "Dashboard dependencies are missing in $VENV; installing them once..."
  sudo -u "$RUN_USER" "$VENV/bin/python" -m pip install --upgrade pip
  sudo -u "$RUN_USER" "$VENV/bin/python" -m pip install -r "$PROJECT_ROOT/requirements-dashboard.txt"
else
  echo "Existing virtual environment already contains dashboard dependencies; skipping pip install."
fi

# Compile before enabling the service.
sudo -u "$RUN_USER" "$VENV/bin/python" -m py_compile "$PROJECT_ROOT/dashboard/app.py"

# Remove the old Docker dashboard container so port 8501 belongs to the host venv service.
if command -v docker >/dev/null 2>&1; then
  mapfile -t OLD_DASH < <(docker ps -aq --filter "name=healthguard-ai-dashboard" 2>/dev/null || true)
  if (( ${#OLD_DASH[@]} )); then
    echo "Removing old Docker dashboard container(s)..."
    docker rm -f "${OLD_DASH[@]}" >/dev/null
  fi
fi

HOME_DIR="$(getent passwd "$RUN_USER" | cut -d: -f6)"
if [[ -z "$HOME_DIR" ]]; then HOME_DIR="/home/$RUN_USER"; fi

cat > /etc/systemd/system/healthguard-dashboard.service <<SERVICE
[Unit]
Description=HealthGuard-AI Premium Dashboard
After=network-online.target docker.service
Wants=network-online.target

[Service]
Type=simple
User=$RUN_USER
Group=$RUN_GROUP
WorkingDirectory=$PROJECT_ROOT
Environment=HOME=$HOME_DIR
Environment=API_BASE_URL=http://$SERVER_IP:8000
Environment=DASHBOARD_REQUEST_TIMEOUT=20
Environment=STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ExecStart=$VENV/bin/streamlit run $PROJECT_ROOT/dashboard/app.py --server.address=$SERVER_IP --server.port=8501 --server.headless=true --server.fileWatcherType=none --browser.gatherUsageStats=false
Restart=on-failure
RestartSec=3
TimeoutStopSec=20
KillSignal=SIGINT
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable --now healthguard-dashboard
sleep 3
systemctl --no-pager --full status healthguard-dashboard || true

echo
echo "Dashboard URL: http://$SERVER_IP:8501"
echo "API URL:       http://$SERVER_IP:8000"
echo "Venv in use:   $VENV"
echo
echo "Future app.py changes require only:"
echo "  sudo systemctl restart healthguard-dashboard"
