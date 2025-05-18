#!/bin/bash
set -e

cd /home/ec2-user/imagegen

# Make poetry available
export PATH="/opt/poetry/bin:$PATH"

# Kill old app
pkill -f "python app/main.py" || true

# Start new app
nohup poetry run python app/main.py > server.log 2>&1 &
