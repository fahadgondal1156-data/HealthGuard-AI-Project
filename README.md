# HealthGuard-AI

**Secure, personalized and explainable AI for remote patient monitoring and early adverse-event prediction.**

HealthGuard-AI is an end-to-end research prototype that converts longitudinal remote-monitoring data into patient-level risk estimates, explainable model outputs, alerts, operational dashboards and auditable user activity. The implementation combines schema-aware data engineering, personalized temporal features, supervised machine learning, Isolation Forest anomaly scoring, probability calibration, role-based access control and a modern Streamlit command-center interface.

> **Research prototype only.** HealthGuard-AI is not a medical device and must not be used for diagnosis, treatment, autonomous clinical decision-making or emergency response. Prospective clinical validation, governance review and applicable regulatory processes are required before any real-patient deployment.

## What the project includes

- TIHM-shaped five-table ingestion for Activity, Sleep, Physiology, Labels and Demographics.
- Strict 24-hour and 48-hour future-event targets that exclude the current day from the label window.
- Patient-specific temporal features: previous-day values, 7-day historical mean/std and personal z-scores.
- Static threshold baseline, Logistic Regression, Random Forest and XGBoost comparison.
- Isolation Forest anomaly score learned from training data and added to the supervised feature set.
- Patient-level train/validation/test separation to reduce identity leakage.
- Sigmoid probability calibration and validation-selected operating threshold.
- PR-AUC, AUROC, precision, sensitivity, F1, specificity, PPV, NPV, Brier score, ECE, missed-event rate and false-alert burden.
- Permutation importance and SHAP-based global explainability artifacts.
- FastAPI REST service with JWT authentication and role-aware endpoints.
- Argon2 password hashing, pseudonymous patient IDs and auditable actions.
- PostgreSQL production backend or SQLite for simple local development.
- Premium Streamlit dashboard with Overview, Patient Monitoring, Alert Center, AI Analytics, Security Audit and System pages.
- Lightweight host-venv dashboard deployment so GUI edits do not trigger repeated Docker dependency builds.

## Architecture

```text
Remote / research data
        |
        v
Schema-aware ingestion
        |
        v
Daily physiology + activity + sleep aggregation
        |
        v
Patient-specific temporal baselines
        |
        +----------------------+
        |                      |
        v                      v
Isolation Forest          Supervised models
anomaly score         LR / RF / XGBoost
        |                      |
        +----------+-----------+
                   v
          Calibrated risk model
                   |
                   v
         Risk probability + band
                   |
          +--------+--------+
          |                 |
          v                 v
      FastAPI           Explainability
          |
          v
      PostgreSQL
          |
          v
  Premium Streamlit UI
          |
          v
Alerts + audit + human review
```

## Repository layout

```text
HealthGuard-AI/
├── api/                       # FastAPI application
├── dashboard/                 # Premium Streamlit UI
├── data/                      # ignored raw/demo/processed data locations
├── deploy/                    # Docker/Nginx deployment material
├── docs/                      # technical and operational documentation
├── models/                    # generated model artifacts (ignored for GitHub)
├── reports/                   # generated evaluation/explainability reports
├── scripts/                   # data, training, database and deployment utilities
├── src/healthguard/           # ML/data/security/database package
├── tests/                     # regression/unit tests
├── .env.example               # PostgreSQL/server template
├── .env.local.example         # SQLite/local template
├── requirements.txt           # complete research/backend environment
└── requirements-dashboard.txt # lightweight dashboard-only environment
```

## Quick local run — no Docker required

This is the easiest way to evaluate the complete project on a local computer. It uses SQLite and a Python virtual environment.

### 1. Requirements

- Python 3.11 or newer in the supported 3.11 family used by the project.
- Git is optional if you are using the ZIP package.
- Approximately 4 GB free disk space is recommended for environments and generated research artifacts.

### 2. Create the environment

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure local mode

Linux/macOS:

```bash
cp .env.local.example .env
python scripts/generate_secret.py
```

Windows:

```powershell
Copy-Item .env.local.example .env
python scripts/generate_secret.py
```

Paste the generated random value into `JWT_SECRET` in `.env`.

### 4. Generate safe demo data and train a demo model

```bash
python scripts/generate_demo_data.py --patients 24 --days 75
python scripts/prepare_data.py --input data/demo --horizons 24 48
python scripts/train_models.py --dataset data/processed/healthguard_24h.csv --horizon 24
```

The generated model is for software demonstration only. Do not report synthetic performance as clinical/research evidence.

### 5. Initialize the local database and create an administrator

```bash
python scripts/init_db.py
python scripts/create_admin.py --username healthguard --role admin
python scripts/seed_db.py --dataset data/processed/healthguard_24h.csv --limit-per-patient 20 --model-dir models/24h
```

### 6. Start the API

Linux/macOS:

```bash
bash scripts/run_api_local.sh
```

Windows PowerShell:

```powershell
.\scripts\run_api_local.ps1
```

API: `http://127.0.0.1:8000`  
Swagger: `http://127.0.0.1:8000/docs`

### 7. Start the dashboard in a second terminal

Linux/macOS:

```bash
bash scripts/run_dashboard_local.sh
```

Windows PowerShell:

```powershell
.\scripts\run_dashboard_local.ps1
```

Dashboard: `http://127.0.0.1:8501`

For a complete local-computer guide, see [`docs/LOCAL_INSTALLATION.md`](docs/LOCAL_INSTALLATION.md).

## Ubuntu server deployment

The final recommended server architecture runs PostgreSQL + FastAPI in Docker and the frequently edited dashboard from a persistent host virtual environment managed by systemd. This prevents a dashboard change from rebuilding the heavy ML image.

See [`docs/SERVER_DEPLOYMENT.md`](docs/SERVER_DEPLOYMENT.md).

## Real TIHM research workflow

HealthGuard-AI does **not** redistribute the TIHM dataset. Follow the official dataset terms and the notice in [`docs/DATASET_NOTICE.md`](docs/DATASET_NOTICE.md).

Typical workflow:

```bash
python scripts/download_tihm.py
python scripts/inspect_tihm.py --input data/raw/tihm
python scripts/prepare_data.py --input data/raw/tihm --horizons 24 48
python scripts/train_models.py --dataset data/processed/healthguard_24h.csv --horizon 24
python scripts/train_models.py --dataset data/processed/healthguard_48h.csv --horizon 48
python scripts/explain_model.py --dataset data/processed/healthguard_24h.csv --model-dir models/24h --max-rows 500
```

## Security roles

| Role | Main permissions |
|---|---|
| `admin` | Patient views, model scoring, alerts, acknowledgement, audit trail and administration-oriented views |
| `clinician` | Patient monitoring, scoring, alerts and acknowledgement |
| `researcher` | Read-only pseudonymous patient monitoring and model analytics |
| `auditor` | Read-only patient monitoring, alert visibility and security audit trail |

## Validation

Before committing or delivering changes:

```bash
python -m py_compile dashboard/app.py api/main.py
pytest -q
```

## Documentation

- `docs/FEATURE_CATALOG.md` — complete feature inventory.
- `docs/TECHNICAL_OVERVIEW.md` — architecture and implementation details.
- `docs/USER_GUIDE.md` — operator workflow.
- `docs/LOCAL_INSTALLATION.md` — local computer installation.
- `docs/SERVER_DEPLOYMENT.md` — Ubuntu/server deployment.
- `docs/API_REFERENCE.md` — supported API endpoints.
- `docs/RESEARCH_PROTOCOL.md` — evaluation methodology.
- `docs/SECURITY.md` — security model and production requirements.

## Dataset and licensing boundaries

Raw TIHM data are intentionally excluded from GitHub packages. The project also does not grant a public software license by default; see `LICENSE.md`. Select an explicit license before publishing the repository for third-party reuse.
