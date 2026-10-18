# v3.0 Final

- Moved Streamlit dashboard from Docker to persistent host Python venv.
- Reuses existing `.venv` automatically when compatible.
- Added a configurable systemd dashboard service; the bind address is supplied at installation time.
- Docker Compose is backend-only (PostgreSQL + FastAPI).
- Redesigned sidebar button colors and active states.
- Expanded sidebar navigation with Security Audit and System.
- Made login experience full-height/responsive on large screens.
- Improved login hero scaling and card positioning.
- Preserved patient monitoring and AI analytics dashboards.
- Added compile-before-restart helper.
- Verified all literal Streamlit widget keys are unique.
