#!/bin/bash
echo "START.SH RAN at $(date)" >> /home/ec2-user/imagegen/debug.log

set -euxo pipefail

cd /home/ec2-user/imagegen

# fetch all under /imagegen, export as ENV_VAR=VAL
for P in $(aws ssm get-parameters-by-path --path /imagegen --with-decryption --query "Parameters[].Name" --output text); do
  K=${P#"/imagegen/"}                     # strip prefix
  V=$(aws ssm get-parameter --name "$P" --with-decryption --query "Parameter.Value" --output text)
  export "$K"="$V"
done

# Ensure poetry is in path
export PATH="/opt/poetry/bin:$PATH"

# Kill any old process
pkill -f "python.*app/main.py" || true

# Start server
nohup poetry run python app/main.py > server.log 2>&1 &
