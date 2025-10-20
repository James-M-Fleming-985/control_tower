#!/bin/bash
# Git Push Helper - Workaround for Codespaces GITHUB_TOKEN conflict
# 
# The Codespaces GITHUB_TOKEN env var has read-only access
# This script temporarily unsets it so git uses your stored PAT instead

echo "🔓 Temporarily unsetting GITHUB_TOKEN to use stored credentials..."
unset GITHUB_TOKEN

echo "📤 Pushing to origin main..."
git push origin main

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "✅ Push successful!"
else
    echo "❌ Push failed with exit code $exit_code"
fi

exit $exit_code
