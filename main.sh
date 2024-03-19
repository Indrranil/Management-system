#!/bin/bash

# Prompt user for commit message
echo "Message:"
read commit_message

# Add all changes
git add .

# Commit changes with the message provided by the user
git commit -m "$commit_message"

# Push changes to the specified branch
git push origin main
