#!/bin/bash

set -e

echo "🔧 Setting up TRON Transaction Cloner"

# Ensure Python 3.10+
PYVER=$(python3 -c 'import sys; print("".join(map(str, sys.version_info[:2])))')
if [[ $PYVER -lt 310 ]]; then
  echo "❌ Python 3.10+ required"
  exit 1
fi

# Install pip if needed
command -v pip3 >/dev/null 2>&1 || { echo >&2 "Installing pip..."; sudo apt-get install -y python3-pip; }

# Install dependencies
pip3 install -r requirements.txt

# Install GPG
if ! command -v gpg &> /dev/null; then
    echo "Installing GPG..."
    sudo apt-get update && sudo apt-get install -y gnupg
fi

# Generate encrypted env file
python3 gen_env_gpg.py

echo "✅ Setup complete. You may now run the tool."
