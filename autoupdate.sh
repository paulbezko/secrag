#!/bin/bash
sudo systemctl stop secrag

sudo git pull origin main

cd /home/ubuntu/secrag/Collab-Project-1
cd client
sudo npm run build
cd ..

sudo systemctl start secrag
# sudo systemctl restart secrag.service