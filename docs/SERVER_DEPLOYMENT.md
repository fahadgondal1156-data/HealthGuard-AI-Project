# HealthGuard-AI — Ubuntu Server Deployment

## Recommended final architecture

HealthGuard-AI uses two deployment layers on the server:

1. PostgreSQL and FastAPI run under Docker Compose.
2. The Streamlit dashboard runs from a persistent host Python virtual environment managed by systemd.

This arrangement keeps the database/API isolated while making GUI updates fast. Editing `dashboard/app.py` does not rebuild the API image or redownload machine-learning packages.

## 1. Configure `.env`

Copy `.env.example` to `.env` and set a strong PostgreSQL password and JWT secret. `DATABASE_URL` and `POSTGRES_PASSWORD` must contain the same database password.

Example private-server binding:

```text
BIND_IP=<SERVER_IP>
```

## 2. Start backend services

```bash
sudo docker compose config
sudo docker compose up -d db api
sudo docker compose ps
```

Do not add `--build` during routine restarts. Build the API only when its Dockerfile, dependencies or image content actually changes.

Initialize the database:

```bash
sudo docker compose exec api python scripts/init_db.py
```

Create users:

```bash
sudo docker compose exec -it api python scripts/create_admin.py --username healthguard --role admin
```

## 3. Install the host dashboard once

```bash
sudo PROJECT_ROOT=/opt/healthguard-ai/HealthGuard-AI \
     SERVER_IP=<SERVER_IP> \
     RUN_USER=ubuntu \
     bash scripts/install_dashboard_host_venv.sh
```

The installer reuses an existing compatible project `.venv` when available. Otherwise it creates `.venv-dashboard` and installs only `pandas`, `streamlit`, `plotly` and `requests`.

## 4. Routine dashboard update

```bash
python3 -m py_compile dashboard/app.py
sudo systemctl restart healthguard-dashboard
```

or:

```bash
bash scripts/restart_dashboard.sh
```

No Docker build is required.

## 5. Health checks

```bash
bash scripts/healthcheck.sh
sudo systemctl status healthguard-dashboard
sudo journalctl -u healthguard-dashboard -n 100 --no-pager
```

## 6. Reverse proxy and TLS

`deploy/nginx-healthguard.conf` contains a starting Nginx reverse-proxy configuration. Production deployments should terminate HTTPS/TLS, restrict firewall exposure and keep PostgreSQL private.

## 7. Production hardening

- Use unique secrets and restrict `.env` permissions.
- Use an organizational identity provider/MFA if the application is adapted for real use.
- Keep port 5432 private.
- Restrict 8000/8501 to private networks or proxy them behind HTTPS.
- Forward application/audit logs to the organization’s SIEM.
- Back up PostgreSQL and model artifacts.
- Patch the OS, Docker images and Python dependencies.
- Do not place direct patient identifiers in the repository or model input pipeline.
- Complete privacy, security, clinical-safety and governance reviews before using real patient data.
