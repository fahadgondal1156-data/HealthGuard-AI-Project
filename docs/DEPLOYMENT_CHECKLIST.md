# Deployment Checklist

- [ ] Ubuntu host patched.
- [ ] Docker/Compose installed from trusted source.
- [ ] `.env` has unique DB password and 32+ byte JWT secret.
- [ ] Raw research data not stored in Git.
- [ ] 24 h model trained on patient-separated data.
- [ ] `pytest -q` passes.
- [ ] PostgreSQL port not publicly exposed.
- [ ] API/dashboard listen on localhost/private interface.
- [ ] Nginx TLS certificate installed.
- [ ] Firewall allows only SSH and HTTPS as required.
- [ ] Admin password changed and least-privilege users created.
- [ ] Audit trail reviewed.
- [ ] Backups tested.
- [ ] SIEM forwarding configured if deployed in an organization.
- [ ] Clinical/research governance approvals documented before real-patient use.
