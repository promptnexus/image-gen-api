#!/bin/bash
set -euxo pipefail

cd /home/ec2-user/imagegen

# Ensure poetry is in path
export PATH="/opt/poetry/bin:$PATH"

# Kill any old process
pkill -f "python.*app/main.py" || true

# Start server
nohup PYTHONPATH=. poetry run python app/main.py > server.log 2>&1 &
