#!/bin/bash
# Start the FinACCAI API server with port forwarding instructions

echo "======================================"
echo "Starting FinACCAI API Server"
echo "======================================"
echo ""
echo "The server will start on port 5000"
echo ""
echo "If running in GitHub Codespaces:"
echo "  1. VS Code will detect port 5000"
echo "  2. Click 'Open in Browser' when prompted"
echo "  3. Or go to PORTS tab and forward port 5000"
echo "  4. Your extension can access via the forwarded URL"
echo ""
echo "If running locally:"
echo "  - Extension will connect to http://localhost:5000"
echo ""
echo "======================================"
echo ""

cd "$(dirname "$0")"
python3 api_server.py
