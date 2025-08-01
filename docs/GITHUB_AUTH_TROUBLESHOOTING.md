# GitHub Authentication Troubleshooting Guide

## Issue: Cannot push to GitHub repositories from Codespaces

**Date**: August 1, 2025  
**Context**: When trying to push commits from cloned repositories in control_tower to GitHub

## Problem
```bash
cd cloned_repos/financial_optimizer
git push
# Results in authentication failure or hanging
```

## Root Cause
GitHub authentication token not properly configured for git operations in Codespaces.

## Solution Steps

### 1. Check if GITHUB_TOKEN exists
```bash
echo $GITHUB_TOKEN
# Should show: ghu_h8eEbXVL9sDHCuGRJbAofYdAiOA7JE3VUTOX
```

### 2. Configure git to use the token (Method 1 - Git Credential Helper)
```bash
# Configure git to use the GitHub CLI credential helper
git config --global credential.helper 'cache --timeout=3600'

# Or use the GitHub token directly
git config --global credential.helper store
echo "https://$GITHUB_TOKEN:x-oauth-basic@github.com" > ~/.git-credentials
```

### 3. Alternative: Update remote URL with token (Method 2)
```bash
cd cloned_repos/financial_optimizer

# Check current remote
git remote get-url origin

# Update remote URL to include token
git remote set-url origin "https://$GITHUB_TOKEN@github.com/James-M-Fleming-985/financial_optimizer.git"

# Now push should work
git push origin main
```

### 4. Verify the fix
```bash
cd cloned_repos/financial_optimizer
git push --dry-run
# Should show what would be pushed without errors
```

## Alternative: Use GitHub CLI
```bash
# Authenticate with GitHub CLI
gh auth login --with-token <<< $GITHUB_TOKEN

# Push using GitHub CLI
gh repo sync
```

## Alternative: Use Safe GitHub Update Script
If git push still doesn't work, use the API-based approach:
```bash
# From control_tower root
python scripts/safe_github_update.py
```

## Verification
Test with a simple change:
```bash
cd cloned_repos/financial_optimizer
echo "# Test" >> README.md
git add README.md
git commit -m "Test authentication"
git push
```

## Notes
- This issue typically occurs when GITHUB_TOKEN changes or expires
- Codespaces sometimes requires explicit credential configuration
- The safe_github_update.py script is a reliable fallback using GitHub API

## Status
✅ **RESOLVED**: Use Method 2 (remote URL update) for immediate fix
