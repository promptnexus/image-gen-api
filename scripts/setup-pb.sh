# scripts/setup-pb.sh
#!/bin/bash
set -euxo pipefail

APP_DIR=/home/ec2-user/imagegen
PB_BIN=$APP_DIR/pocketbase
PB_DATA=/home/ec2-user/pb_data

# ensure data dir exists (won’t clobber if present)
mkdir -p "$PB_DATA"

# download binary only if missing
if [ ! -x "$PB_BIN" ]; then
  curl -sSL https://github.com/pocketbase/pocketbase/releases/download/v0.20.7/pocketbase_0.20.7_linux_amd64.zip \
    -o /tmp/pb.zip
  unzip /tmp/pb.zip -d "$APP_DIR"
  chmod +x "$PB_BIN"
fi
