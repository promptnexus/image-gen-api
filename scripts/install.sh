#!/bin/bash
set -euxo pipefail

cd /home/ec2-user/imagegen

# Install poetry into a known system-wide location
curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 -

# Add to PATH for this session
export PATH="/opt/poetry/bin:$PATH"

# Install project dependencies
poetry install --no-interaction
