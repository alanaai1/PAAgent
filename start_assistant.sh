#!/bin/bash
cd ~/Documents/MVP\ builds/PAAgent

# Start the calendar assistant in background
echo "Starting Calendar Assistant..."
python3 calendar_assistant.py &

# Start the API server
echo "Starting API Server..."
python3 api_server.py
