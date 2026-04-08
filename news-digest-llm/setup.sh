#!/bin/bash
# One-time setup for news-digest on Jetson Orin NX
set -e

PROJ_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJ_DIR"

echo "==> Creating directories..."
mkdir -p data logs

echo "==> Creating Python venv..."
python3 -m venv nd-venv
source nd-venv/bin/activate

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Setting up .env..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "    Edit .env and add your Gmail credentials, then re-run install-crontab.sh"
else
    echo "    .env already exists, skipping."
fi

echo "==> Done. Next steps:"
echo "    1. Edit .env with your Gmail credentials"
echo "    2. Run: bash install-crontab.sh"
echo "    3. Test: source nd-venv/bin/activate && python fetch.py"
