# HealthGuard-AI API Reference

Base service: FastAPI. Authentication uses an HTTP Bearer JWT for all endpoints except health and login.

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | `/health` | Public | Service health response |
| POST | `/auth/login` | Public | Validate application credentials and issue JWT |
| GET | `/model/metadata` | Authenticated | Return deployed model metadata and evaluation information |
| POST | `/monitoring/score` | admin, clinician | Score one pseudonymous patient feature set; store reading; open alert when positive |
| GET | `/monitoring/patients` | admin, clinician, researcher, auditor | List pseudonymous patients and their latest risk |
| GET | `/monitoring/patients/{patient_id}/timeline` | admin, clinician, researcher, auditor | Return longitudinal risk/readings for one patient |
| GET | `/monitoring/alerts` | admin, clinician, auditor | List up to 500 alerts with optional status filter |
| POST | `/monitoring/alerts/{alert_id}/acknowledge` | admin, clinician | Acknowledge an alert and record actor/time |
| GET | `/security/audit` | admin, auditor | Return recent audit events, capped at 1,000 |

## Login payload

```json
{
  "username": "healthguard",
  "password": "<password>"
}
```

## Score payload

```json
{
  "patient_id": "HG-EXAMPLE001",
  "observed_at": "2026-10-03T10:00:00Z",
  "features": {
    "phys_heart_rate": 82.0,
    "phys_systolic_blood_pressure": 136.0,
    "activity_total_count": 77
  }
}
```

The predictor adds the Isolation Forest anomaly feature internally when it is not supplied, fills absent trained features with missing values, applies the fitted preprocessing pipeline and returns a calibrated probability, decision threshold, risk band and positive/negative decision.
