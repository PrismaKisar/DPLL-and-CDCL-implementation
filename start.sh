#!/bin/bash
cd "$(dirname "$0")"
echo "Starting SAT Solver Web Interface..."
echo "The server will automatically find a free port"
echo "Check the console output for the actual URL"
echo "Press Ctrl+C to stop the server"
echo ""
.venv/bin/python app.py