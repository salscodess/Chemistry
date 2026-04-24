# Backend setup and shortcuts

## Build dependencies

From repository root:

```bash
./backend/build.sh
```

This creates:
- `backend/.venv-api` for API dependencies
- `backend/.venv-dash` for dashboard dependencies

## Start backend services

From repository root:

```bash
./backend/start.sh
```

By default this starts:
- API at `http://localhost:8000`
- Dashboard at `http://localhost:8001`

Logs are written to:
- `/tmp/chemistry-api.log`
- `/tmp/chemistry-dashboard.log`

Use environment variables to customize host/ports:

```bash
CHEM_API_HOST=0.0.0.0 CHEM_API_PORT=8000 CHEM_DASH_PORT=8001 ./backend/start.sh
```
