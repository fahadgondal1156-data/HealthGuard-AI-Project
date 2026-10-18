# HealthGuard-AI v3.0 — GitHub Release Notes

This source package is intentionally clean: no TIHM raw data, synthetic generated datasets, trained model binaries, runtime database or secrets are committed.

For the first local run, follow `docs/LOCAL_INSTALLATION.md`. The repository uses a persistent `.venv`; install dependencies once, then reuse that environment for later code changes.

For an Ubuntu/server deployment, follow `docs/SERVER_DEPLOYMENT.md`. The recommended deployment keeps PostgreSQL and FastAPI in Docker while running the frequently edited Streamlit dashboard from a host virtual environment managed by systemd.

Before a contribution or release:

```bash
python -m py_compile dashboard/app.py api/main.py
pytest -q
```

HealthGuard-AI is a research prototype and not a medical diagnostic device.
