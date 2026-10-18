# Security Model

HealthGuard-AI uses pseudonymous patient identifiers, JWT authentication, Argon2 password hashing, role-based authorization, audit records, a private database network and TLS termination guidance.

## Roles
- `admin`: user/system administration and all operational views.
- `clinician`: patient monitoring, scoring and alert acknowledgement.
- `researcher`: read-only pseudonymous patient/model analytics.
- `auditor`: read-only patient monitoring plus security audit trail.

## Production requirements
1. Replace every default secret.
2. Require HTTPS/TLS and preferably MFA/SSO through an organizational identity provider.
3. Keep PostgreSQL private; never expose 5432 publicly.
4. Use network segmentation and a reverse proxy/WAF where appropriate.
5. Back up the database and encryption keys separately.
6. Forward authentication/audit logs to the organization's SIEM.
7. Patch the OS, containers and Python dependencies routinely.
8. Restrict filesystem permissions on `.env`, model artifacts and backups.
9. Do not put direct identifiers or raw clinical records in source control.
10. Perform organizational privacy, clinical-safety and security reviews before any real-patient use.

## Example permissions
```bash
sudo chown -R root:healthguard /opt/healthguard-ai
sudo chmod 750 /opt/healthguard-ai
sudo chmod 640 /opt/healthguard-ai/.env
```
