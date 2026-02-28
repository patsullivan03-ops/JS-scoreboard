#!/bin/bash
# Update NCAAB Scores script

# Run the fetcher
python3 /home/openclaw/.openclaw/workspace/fetch_ncaab.py

# Copy results to repo
cp /home/openclaw/.openclaw/workspace/SCOREBOARD.md /home/openclaw/.openclaw/workspace/scores.json /home/openclaw/.openclaw/workspace/repo/

# Commit and push
cd /home/openclaw/.openclaw/workspace/repo
git add SCOREBOARD.md scores.json
git commit -m "Update NCAAB scores $(date)"
git push
