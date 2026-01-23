#!/bin/bash
# Chemistry Project - Start Script

echo "🧪 Chemistry Project Startup"
echo "=============================="
echo ""

# Check if running from correct directory
if [ ! -d "backend" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "⚠️  Warning: Port $1 is already in use"
        return 1
    fi
    return 0
}

# Start Dashboard
echo "📊 Starting Dashboard on port 8001..."
check_port 8001
cd backend/dash
uvicorn dashboard_api:app --host 0.0.0.0 --port 8001 --reload > /tmp/chemistry-dashboard.log 2>&1 &
DASH_PID=$!
echo "   Dashboard PID: $DASH_PID"
cd ../..

sleep 2

# Verify dashboard started
if ps -p $DASH_PID > /dev/null; then
    echo "✅ Dashboard running at http://localhost:8001"
else
    echo "❌ Dashboard failed to start. Check /tmp/chemistry-dashboard.log"
    exit 1
fi

echo ""
echo "🎉 Chemistry Project is running!"
echo ""
echo "📌 Access Points:"
echo "   Dashboard: http://localhost:8001"
echo "   API Docs:  http://localhost:8000/docs (when started from dashboard)"
echo ""
echo "💡 Use the dashboard to start/stop/restart the API server"
echo "📝 Logs: /tmp/chemistry-dashboard.log"
echo ""
echo "To stop all services, run: pkill -f 'uvicorn dashboard_api'"
