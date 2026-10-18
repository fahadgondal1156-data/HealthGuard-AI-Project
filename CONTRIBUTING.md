# Contributing

HealthGuard-AI is a research prototype. Contributions should preserve patient-level leakage controls, pseudonymization, role-based access restrictions, audit logging, and the research-only interpretation boundary.

1. Create a feature branch.
2. Add or update tests for behavioral changes.
3. Run `python -m py_compile dashboard/app.py api/main.py` and `pytest -q`.
4. Do not commit raw TIHM data, `.env`, database files, credentials, or identifiable clinical data.
5. Describe changes and validation steps in the pull request.
