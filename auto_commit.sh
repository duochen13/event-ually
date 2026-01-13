#!/bin/zsh

# cd spaghetti/playground || exit 1

# Ask Claude to generate something
claude "keep working and don't ask me again, choose the option that you think is the best, write changelog with date to README.md, finishes until 3 prompts"

# Stage everything
git add .

# Only commit if something changed
if ! git diff --cached --quiet; then
  git commit -m "Daily AI update: $(date '+%Y-%m-%d')"
  git push
fi