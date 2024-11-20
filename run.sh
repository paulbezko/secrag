#!/bin/bash

# Script to run Gunicorn with specific options

# Navigate to the application directory (modify this to your app's path if needed)
cd /home/ubuntu/secrag/Collab-Project-1

# Activate the environment
source ./venv/bin/activate

# Run Gunicorn with the desired settings
uvicorn app:app --port 8000
