#!/bin/bash
echo "Starting Victor Visual Engine..."
python3 launch_visual_engine.py --demo &
SERVER_PID=$!
echo "Backend server started (PID: $SERVER_PID)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
wait $SERVER_PID
