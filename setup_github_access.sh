#!/bin/bash
# Setup script for GitHub Personal Access Token
# Run this after creating your PAT at: https://github.com/settings/tokens/new

echo "=== GitHub Cross-Repo Access Setup ==="
echo ""
echo "Step 1: Create PAT at https://github.com/settings/tokens/new"
echo "  - Note: Control Tower Codespace Access"
echo "  - Expiration: 90 days"
echo "  - Scopes: repo (all), workflow, read:org"
echo ""
echo "Step 2: Copy the token and paste it when prompted"
echo ""

read -s -p "Enter your Personal Access Token: " GH_PAT
echo ""

# Save to environment
export GH_TOKEN="$GH_PAT"

# Authenticate gh CLI
echo "$GH_TOKEN" | gh auth login --with-token

echo ""
echo "=== Testing Access ==="
echo ""

# Test access
echo "Your repositories:"
gh repo list --limit 10

echo ""
echo "Checking business_ventures access..."
gh repo view James-M-Fleming-985/business_ventures

echo ""
echo "✅ Setup complete! You can now clone business_ventures:"
echo "   cd /workspaces"
echo "   gh repo clone James-M-Fleming-985/business_ventures"
echo ""
echo "To make this permanent, add to your Codespace secrets:"
echo "   https://github.com/settings/codespaces"
echo "   Secret name: GH_PERSONAL_TOKEN"
echo "   Secret value: <your PAT>"
