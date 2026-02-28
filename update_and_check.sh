#!/bin/bash
# 1. Update Scores
git reset --hard origin/main
python3 fetch_ncaab.py
git add SCOREBOARD.md scores.json
git commit -m "NCAAB Scores Update - $(date -u)"
git push origin main

# 2. Check Time and Disable Job if past 8:30 PM EST (01:30 AM UTC next day)
# Target: 2026-02-15 01:30:00 UTC
CURRENT_EPOCH=$(date +%s)
TARGET_EPOCH=$(date -d "2026-02-15 01:30:00 UTC" +%s)

if [ $CURRENT_EPOCH -ge $TARGET_EPOCH ]; then
    echo "Time limit reached. Attempting to disable cron job 41ed2e10-b0c3-4b69-82df-23e19c2d62cb..."
    # Since the cron tool is timing out, we will rely on the agent to disable it 
    # or this script can exit with a specific message for the agent.
    echo "STATUS_LIMIT_REACHED"
fi
