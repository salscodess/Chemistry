# Dashboard Credentials

## Default Login

**Username:** admin  
**Password:** chemistry2026

## Changing Credentials

Edit `/workspaces/Chemistry/backend/dash/dashboard_api.py`:

```python
# Dashboard credentials (change these!)
DASHBOARD_USERNAME = "Sal"
DASHBOARD_PASSWORD = "chemistry"  # Change this in production!
```

After changing, restart the dashboard server:
```bash
# Kill the current server
pkill -f "uvicorn dashboard_api"

# Restart
cd /workspaces/Chemistry/backend/dash
uvicorn dashboard_api:app --host 0.0.0.0 --port 8001 --reload
```

## Security Notes

⚠️ **Important:**
1. Change the default password before deploying to production
2. Use environment variables for credentials in production
3. Consider using more secure authentication methods (OAuth, JWT, etc.)
4. Always use HTTPS in production to encrypt credentials in transit
