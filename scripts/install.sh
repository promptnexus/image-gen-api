#!/bin/bash
set -e  # fail on any error

cd /home/ec2-user/imagegen

# Install poetry to a known location under /opt
curl -sSL https://install.python-poetry.org | python3 - --yes --install-dir /opt/poetry

# Make poetry available in PATH for this script
export PATH="/opt/poetry/bin:$PATH"

# Install project dependencies
/opt/poetry/bin/poetry install --no-interaction
