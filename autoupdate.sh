#!/bin/bash
sudo systemctl stop secrag


cd /home/ubuntu/secrag/Collab-Project-1

sudo git pull origin main

sudo venv/bin/pip3 install -r requirements.txt

cd client
sudo npm run build
cd ..

sudo systemctl start secrag
# sudo systemctl restart secrag.service