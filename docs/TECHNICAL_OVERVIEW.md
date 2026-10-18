# HealthGuard-AI Technical Overview

HealthGuard-AI is organized as a reproducible research pipeline plus a secured service layer.

## Data layer

The schema-discovery routine identifies TIHM-shaped CSV files by required columns rather than by filename alone. Column names are normalized before processing. Physiology is pivoted into daily median measurements, activity becomes daily location counts/total activity, and sleep becomes daily heart-rate, respiratory-rate, snoring and sleep-state statistics.

## Personalized temporal layer

For selected physiological, activity and sleep variables the pipeline derives previous-day values, trailing 7-day mean, trailing 7-day standard deviation and patient-specific z-score. Historical windows are shifted before rolling calculations so the current/future target is not used to build historical features.

## Target construction

For horizon `H`, an observation day is positive only when at least one clinically verified label occurs strictly after the current day and no later than `day + H`. Current-day labels are excluded.

## Model-development layer

Patients are separated into train/validation/test partitions with grouped splitting. Isolation Forest is fitted on training rows without future events when sufficient normal rows exist. Logistic Regression, Random Forest and XGBoost are trained on the same prepared feature set plus anomaly score. The validation set selects the model by PR-AUC.

The selected model is sigmoid-calibrated using validation patients. The operating threshold is selected from the validation precision-recall curve by maximum F1. Final metrics are calculated on held-out test patients.

## Explainability

The project produces model-agnostic permutation importance and estimator-specific SHAP global importance where supported. These artifacts are intended to expose which transformed/model inputs have the largest overall influence; they do not prove causality.

## Runtime predictor

The saved predictor loads the calibrated model, anomaly preprocessing/model and metadata. For each request it computes the anomaly score if absent, adds missing trained columns as missing values, obtains calibrated probability and applies the saved decision threshold to classify the result into low, moderate, high or critical bands.

## API/service layer

FastAPI exposes health, authentication, model metadata, patient scoring, patient timeline, alerts, acknowledgements and audit endpoints. SQLAlchemy stores users, pseudonymous patients, readings, alerts and audit events.

## Security layer

Passwords are hashed using Argon2. Successful authentication issues an HS256 JWT containing username, role, issued-at time and expiration. Endpoint dependencies enforce roles. Patient identifiers used by the seeding workflow are deterministic SHA-256-derived pseudonyms. Operational activity is written to the audit-event table.

## Dashboard/deployment layer

The premium Streamlit dashboard communicates with the API over HTTP and does not connect directly to PostgreSQL. The recommended Ubuntu deployment keeps PostgreSQL and FastAPI in Docker while the dashboard runs from a persistent host venv under systemd. This avoids rebuilding the heavy backend ML image during routine UI changes.
