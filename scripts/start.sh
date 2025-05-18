#!/bin/bash
cd /home/ec2-user/imagegen

pkill -f "poetry run python app/main.py" || true

nohup poetry run python app/main.py > server.log 2>&1 &
