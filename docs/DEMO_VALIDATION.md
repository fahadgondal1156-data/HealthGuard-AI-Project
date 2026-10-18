# Synthetic Validation Status

The packaged reference implementation was exercised end-to-end with generated TIHM-shaped synthetic data.

Validated workflow:

- schema discovery for the five tables;
- daily multimodal aggregation;
- strict future 24 h / 48 h labels;
- patient-level train/validation/test split;
- Isolation Forest anomaly scoring;
- Logistic Regression / Random Forest / XGBoost training;
- probability calibration;
- saved-model reload and inference;
- global SHAP generation;
- unit tests for label leakage and password/JWT helpers.

The synthetic model scores are intentionally **not research results**. Synthetic data were generated with an embedded predictive signal to verify that software components work. Only properly run TIHM experiments should be used in a manuscript.
