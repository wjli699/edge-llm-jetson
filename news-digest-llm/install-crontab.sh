#!/bin/bash
# Installs cron jobs for news-digest
PROJ_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON="$PROJ_DIR/nd-venv/bin/python"

# Remove existing news-digest cron entries
crontab -l 2>/dev/null | grep -v "news-digest" > /tmp/crontab_clean || true

cat >> /tmp/crontab_clean << EOF

# news-digest: fetch articles 4x per day
0 */6 * * * cd $PROJ_DIR && $PYTHON fetch.py >> $PROJ_DIR/logs/fetch.log 2>&1

# news-digest: summarize and email daily at 8am
0 8 * * * cd $PROJ_DIR && $PYTHON summarize.py >> $PROJ_DIR/logs/digest.log 2>&1
EOF

crontab /tmp/crontab_clean
rm /tmp/crontab_clean

echo "Cron jobs installed:"
crontab -l | grep news-digest
