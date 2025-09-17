#!/bin/bash
cd "$(dirname "$0")"
echo "Starting SAT Solver Web Interface..."
echo "Server will be available at: http://127.0.0.1:5000"
echo "Press Ctrl+C to stop the server"
echo ""
.venv/bin/python app.py