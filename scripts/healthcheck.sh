#!/usr/bin/env bash
set -euo pipefail
SERVER_IP="${SERVER_IP:-127.0.0.1}"
printf 'API: '
curl -fsS "http://$SERVER_IP:8000/health" && echo
printf 'Dashboard HTTP: '
curl -s -o /dev/null -w '%{http_code}\n' "http://$SERVER_IP:8501"
systemctl is-active --quiet healthguard-dashboard && echo 'Dashboard service: active' || echo 'Dashboard service: NOT active'
