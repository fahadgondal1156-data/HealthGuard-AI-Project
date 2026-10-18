# HealthGuard-AI Complete Feature Catalog

| Category | Feature | Detailed purpose |
|---|---|---|
| Data | Five-table schema discovery | Detects Activity, Sleep, Physiology, Labels and Demographics using required column signatures rather than depending on exact filenames. |
| Data | Column normalization | Converts source headers into predictable lower-case underscore names for reproducible processing. |
| Data | TIHM downloader | Downloads the official archive and verifies the expected MD5 checksum before extraction. |
| Data | Dataset inspection CLI | Reports detected tables, row counts, patient counts, columns and date ranges. |
| Data | Synthetic demo generator | Creates non-clinical TIHM-shaped records for end-to-end software validation. |
| Data | Physiology aggregation | Produces daily median measurements by device type. |
| Data | Activity aggregation | Counts activity events per location and computes total activity and active-location count. |
| Data | Sleep aggregation | Derives daily sleep observation minutes, HR/RR statistics, snoring rate and sleep-state ratios. |
| Data | Demographic merge | Adds de-identified sex and age-group context to daily patient observations. |
| Personalization | Previous-day feature | Adds lag-1 values for supported physiological/activity/sleep measures. |
| Personalization | Seven-day historical mean | Captures each patient's recent baseline without using future observations. |
| Personalization | Seven-day historical standard deviation | Quantifies recent patient-specific variability. |
| Personalization | Personal z-score | Expresses current values relative to the individual historical baseline. |
| Labels | Strict future-event target | Excludes same-day labels and uses only events after the feature day within the selected horizon. |
| Labels | 24-hour horizon | Builds `target_24h` for next-day event prediction. |
| Labels | 48-hour horizon | Builds `target_48h` for two-day event prediction. |
| Validation | Patient-level split | Prevents a patient's rows from being intentionally mixed between train and held-out test partitions. |
| Anomaly detection | Isolation Forest | Learns an unsupervised anomaly signal from training data, preferentially normal rows. |
| Baseline | Static physiological rules | Provides a threshold-based comparison using blood pressure, heart rate, temperature, body water and weight change. |
| ML | Logistic Regression | Provides a strong interpretable linear baseline with class balancing. |
| ML | Random Forest | Provides nonlinear tree-ensemble modeling with balanced sampling. |
| ML | XGBoost | Provides gradient-boosted tabular classification with imbalance weighting. |
| ML | Validation PR-AUC selection | Chooses the deployable candidate using validation precision-recall area. |
| Calibration | Sigmoid probability calibration | Calibrates the selected fitted classifier on validation patients. |
| Thresholding | Validation F1 threshold | Selects the operating decision threshold from the validation precision-recall curve. |
| Metrics | PR-AUC | Measures precision-recall performance for an imbalanced event prediction problem. |
| Metrics | AUROC | Measures ranking discrimination across thresholds. |
| Metrics | Precision/PPV | Quantifies the fraction of positive predictions that are true positives. |
| Metrics | Sensitivity/Recall | Quantifies the fraction of positive events detected. |
| Metrics | F1 | Harmonic mean of precision and recall. |
| Metrics | Specificity | Quantifies the fraction of negatives correctly classified. |
| Metrics | NPV | Quantifies the fraction of negative predictions that are true negatives. |
| Metrics | Brier score | Measures probability error and contributes to calibration assessment. |
| Metrics | Expected calibration error | Measures average calibration gap across probability bins. |
| Metrics | Missed-event rate | Reports false negatives relative to all positive events. |
| Metrics | False alerts per patient-day | Expresses false-positive burden in monitoring terms. |
| Explainability | Permutation importance | Measures performance degradation when each original feature is permuted. |
| Explainability | SHAP global importance | Produces mean absolute SHAP importance for supported selected estimators. |
| Artifacts | Saved calibrated model | Persists the deployable probability model with joblib. |
| Artifacts | Saved base model | Retains the pre-calibration selected model for explanation and analysis. |
| Artifacts | Saved anomaly model | Persists the Isolation Forest and its preprocessing pipeline. |
| Artifacts | Metadata JSON | Stores horizon, model, threshold, features, cohort counts and metrics. |
| API | Health endpoint | Provides unauthenticated service status. |
| API | Login endpoint | Verifies Argon2 password hash and issues a JWT. |
| API | Model metadata endpoint | Returns the deployed model's stored metadata to authenticated users. |
| API | Patient scoring endpoint | Scores a pseudonymous patient, stores the reading and creates an alert when positive. |
| API | Patient list endpoint | Returns demographics and latest risk for pseudonymous patients. |
| API | Patient timeline endpoint | Returns chronological risk readings and feature payloads for one patient. |
| API | Alert list endpoint | Returns recent alerts with optional status filtering. |
| API | Alert acknowledgement | Stores acknowledgement status, user and time. |
| API | Security audit endpoint | Returns recent audit events for administrators and auditors. |
| Security | Argon2 password hashing | Stores one-way password hashes rather than plaintext passwords. |
| Security | JWT authentication | Uses signed bearer tokens with issue and expiry timestamps. |
| Security | Role-based authorization | Enforces admin, clinician, researcher and auditor permissions on API routes. |
| Security | Pseudonymous patient IDs | Seed workflow converts source patient IDs to `HG-<hash>` identifiers. |
| Security | Audit logging | Records login, model inference, patient views, alert views and acknowledgements. |
| Security | Private database network | Final Docker configuration does not publish PostgreSQL to the host network. |
| Dashboard | Full-screen healthcare-AI login | Responsive login hero with neural-network/ECG styling and live API status. |
| Dashboard | Role-aware sidebar | Shows session, API/model status and authorized command-center pages. |
| Dashboard | Top workspace selector | Allows page navigation from a compact top control. |
| Dashboard | Global patient search | Provides patient-ID search input in the top navigation. |
| Dashboard | Notifications | Displays open-alert count and recent alert details for authorized roles. |
| Dashboard | Profile popover | Shows current user/role/API status and provides logout. |
| Dashboard | Quick-action buttons | Provides direct access to refresh, patients, alerts, AI model and system pages. |
| Dashboard | Overview KPIs | Displays monitored patients, high/critical count, open alerts, average risk, horizon and engine status. |
| Dashboard | Risk distribution | Visualizes current patient counts by risk band. |
| Dashboard | Model snapshot | Shows key test metadata and deployed model configuration. |
| Dashboard | Highest-risk list | Prioritizes patients by latest stored risk probability. |
| Dashboard | Recent activity | Presents recent auditable platform actions. |
| Dashboard | Patient risk cards | Shows pseudonym, latest risk, risk band, age group and sex. |
| Dashboard | Risk gauge and timeline | Visualizes current probability and longitudinal risk change. |
| Dashboard | Feature views | Provides latest model inputs and observation-history views. |
| Dashboard | Alert analytics | Shows open/critical/high/acknowledged KPIs, severity chart and daily alert activity. |
| Dashboard | Alert filters/export | Filters by status, severity and patient; exports filtered alerts to CSV. |
| Dashboard | Alert acknowledgement UI | Allows admin/clinician users to close reviewed alerts with audit preservation. |
| Dashboard | AI performance KPIs | Displays PR-AUC, AUROC, precision, sensitivity, F1 and Brier metrics. |
| Dashboard | Model comparison | Visualizes validation PR-AUC for static rules and candidate ML models. |
| Dashboard | Cohort split visualization | Shows patient counts in train/validation/test groups. |
| Dashboard | Performance radar | Summarizes multiple performance dimensions in one chart. |
| Dashboard | Model configuration | Displays selected model, horizon, threshold and engineered feature count. |
| Dashboard | Security audit analytics | Shows audit counts, failures, actors, actions, filters and CSV export. |
| Dashboard | System diagnostics | Shows API latency, model status, patient store, alert queue and live health check. |
| Deployment | Backend-only Docker Compose | Runs PostgreSQL and FastAPI in containers while keeping the GUI independent. |
| Deployment | Persistent dashboard venv | Installs dashboard packages once and reuses the environment for future UI changes. |
| Deployment | systemd dashboard service | Starts the dashboard automatically and restarts it on failure. |
| Deployment | Compile-before-restart helper | Prevents restarting the GUI when Python syntax is invalid. |
| Deployment | Health-check helper | Checks API response, dashboard HTTP status and systemd service state. |
| Deployment | Nginx reference config | Provides a starting reverse-proxy configuration for API/dashboard routing and TLS termination. |
| Testing | Future-label leakage test | Confirms same-day events are excluded from the 24-hour target. |
| Testing | Security helper test | Confirms password hashing/verification and JWT payload behavior. |
| GitHub | CI workflow | Compiles critical modules and runs tests on pushes/pull requests. |
