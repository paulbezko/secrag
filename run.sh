#!/bin/bash

# Script to run Gunicorn with specific options

# Navigate to the application directory (modify this to your app's path if needed)
cd /home/ubuntu/secrag/Collab-Project-1

# Make a backup of the vectorstore on startup
sudo mkdir -p database/vectorstore_backup && sudo cp -rf database/vectorstore/* database/vectorstore_backup/

# Activate the environment
source ./venv/bin/activate

# Run Gunicorn with the desired settings
uvicorn app:app --port 8000
