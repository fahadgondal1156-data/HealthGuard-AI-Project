# HealthGuard-AI Research Protocol

## Objective
Retrospectively evaluate whether multimodal, personalized and explainable machine learning can predict a clinically verified TIHM adverse event in the next 24 or 48 hours while controlling alert burden.

## Primary endpoint
Binary future event: at least one verified TIHM label occurs strictly after the feature day and inside the selected prediction horizon.

## Primary metric
PR-AUC because events are expected to be imbalanced.

## Secondary metrics
AUROC, precision/PPV, recall/sensitivity, F1, specificity, NPV, Brier score, expected calibration error, missed-event rate and false-positive alerts per patient-day.

## Baselines
1. Published-style static physiological thresholds.
2. Logistic Regression.
3. Random Forest.
4. XGBoost.
5. Hybrid model with anomaly score.

## Leakage controls
- No random row split.
- `patient_id` is the grouping variable.
- Imputation, scaling, encoding and Isolation Forest are fit only on training patients.
- Validation patients select the model, probability threshold and calibration.
- Test patients are used once for final evaluation.
- Features use current and historical observations only; future labels are excluded from predictors.

## Ablation study
Run variants using: physiology only; +activity; +sleep; +historical/personalized features; +Isolation Forest anomaly score. Compare PR-AUC, recall and false alerts/patient-day.

## Generalization study
Use grouped cross-validation or leave-one-patient-out analysis as a supplementary experiment. Do not tune against the final held-out test set.

## Explainability
Primary implementation provides global model-agnostic permutation importance. For the manuscript, add SHAP analyses for the selected estimator and evaluate explanation stability under small, plausible input perturbations.

## Calibration
Report raw vs calibrated probabilities where feasible. The deployable model uses sigmoid calibration on validation patients.

## Interpretation boundary
The project demonstrates retrospective decision-support research. It does not establish clinical safety, clinical effectiveness, reduction in hospitalizations, or suitability as a regulated medical device. Those claims require prospective validation and appropriate governance.
