#!/bin/bash
cd /home/ec2-user/imagegen

export PATH="$HOME/.local/bin:$PATH"
if ! command -v poetry &> /dev/null; then
  curl -sSL https://install.python-poetry.org | python3 -
fi

poetry install
