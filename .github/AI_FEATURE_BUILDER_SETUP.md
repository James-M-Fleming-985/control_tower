# 🤖 AI Feature Builder - GitHub Actions Setup

## Overview

Build features autonomously using AI code generation via GitHub Actions. Trigger from web or mobile - no babysitting required.

## Setup (One-Time)

### 1. Create Personal Access Token (PAT)

The workflow needs to push changes to other repositories.

1. Go to: **GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Click **"Generate new token (classic)"**
3. Settings:
   - **Note**: `AI Feature Builder`
   - **Expiration**: 90 days (or your preference)
   - **Scopes**: ✅ `repo` (Full control of private repositories)
4. Click **"Generate token"**
5. **Copy the token immediately** (you won't see it again)

### 2. Add Repository Secrets

Go to: **control_tower repo → Settings → Secrets and variables → Actions**

Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `CROSS_REPO_PAT` | The PAT you just created |

## Usage

### From Web (Desktop)

1. Go to **control_tower** repo on GitHub
2. Click **Actions** tab
3. Select **"🤖 AI Feature Builder"** workflow
4. Click **"Run workflow"** button
5. Choose:
   - **Target repo**: Which repository contains the feature
   - **Target path**: Path within repo (e.g., `Causal_affect`)
   - **Feature**: Which feature to build
   - **Dry run**: Check to validate only (no AI generation)
6. Click **"Run workflow"**

### From Mobile (GitHub App)

1. Open GitHub mobile app
2. Navigate to **control_tower** repo
3. Tap **Actions** (at bottom)
4. Tap **"🤖 AI Feature Builder"**
5. Tap **"Run workflow"**
6. Fill in the options
7. Tap **"Run"**

## Features Available

| Feature ID | Description | Phase |
|------------|-------------|-------|
| `FEATURE-CA-002-06` | Causality API Service | Phase 2 |
| `FEATURE-CA-002-08` | Lag Analysis Service | Phase 3 |
| `FEATURE-CA-002-09` | Regression Service | Phase 4 |
| `FEATURE-CA-002-10` | Prediction Tracking | Phase 5.5 |
| `ALL_IN_ORDER` | Build all features sequentially | All |

## What Happens

1. Workflow checks out control_tower (AI code generator)
2. Workflow checks out target repo
3. Finds feature YAML specification
4. Runs `build_feature.py` with AI generation
5. Commits generated code
6. Pushes to target repo
7. (Railway auto-deploys if configured)

## Monitoring

- Watch progress in the **Actions** tab
- Download artifacts after completion
- Check workflow summary for results

## Troubleshooting

### "Feature YAML not found"
- Ensure feature YAML files exist in the target path
- Check the path structure: `SYSTEM-*/FEATURE-*_*/FEATURE-*.yaml`

### "Push failed"
- Verify `CROSS_REPO_PAT` secret has `repo` scope
- Check token hasn't expired

### "AI generation failed"
- Verify `ANTHROPIC_API_KEY` is set correctly
- Check API quota/rate limits
- Review workflow logs for specific errors
