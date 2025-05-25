#!/bin/bash
echo "START.SH RAN at $(date)" >> /home/ec2-user/imagegen/debug.log

set -euxo pipefail

APP_DIR=/home/ec2-user/imagegen

cd "$APP_DIR"

"$APP_DIR/scripts/setup-pb.sh"

nohup "$APP_DIR/pocketbase" serve --dir /home/ec2-user/pb_data --http "0.0.0.0:8090" > /home/ec2-user/imagegen/pb.log 2>&1 &

# fetch all under /imagegen, export as ENV_VAR=VAL
for P in $(aws ssm get-parameters-by-path --path /imagegen --with-decryption --query "Parameters[].Name" --output text); do
  K=${P#"/imagegen/"}                     # strip prefix
  V=$(aws ssm get-parameter --name "$P" --with-decryption --query "Parameter.Value" --output text)
  export "$K"="$V"
  echo "exported $K=$V" >> "$APP_DIR/debug.log"
done

# Ensure poetry is in path
export PATH="/opt/poetry/bin:$PATH"


# Kill any old process
pkill -f "python.*app/main.py" || true


# Start server
nohup poetry run python app/main.py > "$APP_DIR/server.log" 2>&1 &
