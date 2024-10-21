#!/bin/bash
cd /home/ubuntu/secrag/Collab-Project-1
sudo git pull origin main
sudo kill -9 $(lsof -t -i:8000)
# sudo systemctl restart secrag.service