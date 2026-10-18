# HealthGuard-AI — Local Computer Installation Guide

This guide runs HealthGuard-AI on one computer without Docker. SQLite is used for the local database. This mode is intended for development, demonstrations, research reproduction and UI review.

## 1. Supported local layouts

### Windows 11
Use PowerShell and Python 3.11. The API and Streamlit dashboard run as two local Python processes.

### Ubuntu/Linux
Use Bash and Python 3.11. The same `.venv` can run preprocessing, training, API and dashboard tasks.

### macOS
The Linux/macOS Bash commands apply if Python 3.11 is installed.

## 2. Obtain the project

Either clone the repository or extract the GitHub-ready ZIP. Open a terminal in the repository root, where `requirements.txt`, `api/`, `dashboard/` and `scripts/` are visible.

## 3. Create a persistent virtual environment

The virtual environment is created once. Do not recreate it every time the UI changes.

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On later sessions, activate only:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Ubuntu/Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On later sessions:

```bash
source .venv/bin/activate
```

## 4. Create local configuration

Copy `.env.local.example` to `.env`.

Windows:

```powershell
Copy-Item .env.local.example .env
```

Linux/macOS:

```bash
cp .env.local.example .env
```

Generate a JWT secret:

```bash
python scripts/generate_secret.py
```

Edit `.env` and replace `CHANGE_ME_TO_RANDOM_64_HEX` with the generated value.

The local file should contain:

```text
APP_NAME=HealthGuard-AI
APP_ENV=development
DATABASE_URL=sqlite:///./healthguard.db
JWT_SECRET=<generated-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_MINUTES=30
MODEL_DIR=models/24h
```

## 5. Prepare a safe demonstration model

The following data are synthetic and exist only to prove the software workflow.

```bash
python scripts/generate_demo_data.py --patients 24 --days 75
python scripts/prepare_data.py --input data/demo --horizons 24 48
python scripts/train_models.py --dataset data/processed/healthguard_24h.csv --horizon 24
```

Optional 48-hour model:

```bash
python scripts/train_models.py --dataset data/processed/healthguard_48h.csv --horizon 48
```

## 6. Initialize the application database

```bash
python scripts/init_db.py
```

Create an administrator. Passwords must contain at least 12 characters.

```bash
python scripts/create_admin.py --username healthguard --role admin
```

Seed pseudonymous demonstration observations:

```bash
python scripts/seed_db.py --dataset data/processed/healthguard_24h.csv --limit-per-patient 20 --model-dir models/24h
```

## 7. Start FastAPI

Open terminal 1 and activate the venv.

Windows:

```powershell
.\scripts\run_api_local.ps1
```

Linux/macOS:

```bash
bash scripts/run_api_local.sh
```

Verify:

```text
http://127.0.0.1:8000/health
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## 8. Start the dashboard

Open terminal 2 and activate the same venv.

Windows:

```powershell
.\scripts\run_dashboard_local.ps1
```

Linux/macOS:

```bash
bash scripts/run_dashboard_local.sh
```

Open:

```text
http://127.0.0.1:8501
```

Use the administrator account created in Step 6.

## 9. Normal development workflow

When only `dashboard/app.py` changes, do not reinstall packages. Stop and restart only the dashboard process. The `.venv` remains unchanged.

When backend Python code changes, restart the API process. Reinstall dependencies only if `requirements.txt` itself changes.

## 10. Run tests

```bash
python -m py_compile dashboard/app.py api/main.py
pytest -q
```

## 11. Common problems

### Model unavailable
Confirm that `models/24h/model_calibrated.joblib`, `models/24h/anomaly.joblib` and `models/24h/metadata.json` exist, or train the model again.

### Invalid credentials
The `.env` file does not define application-user passwords. Application users live in the database. Create a new user with `scripts/create_admin.py` or reset the database in a disposable local environment.

### Dashboard cannot reach API
Confirm the API is running at `127.0.0.1:8000`. The local dashboard launcher sets `API_BASE_URL=http://127.0.0.1:8000`.

### Empty dashboard
Seed observations with `scripts/seed_db.py`.

### TIHM dataset missing
Use synthetic demo data for software testing, or obtain TIHM separately according to its source terms. Raw TIHM data are intentionally not included in the repository.
