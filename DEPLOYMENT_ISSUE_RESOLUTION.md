# Deployment Issue Resolution - Version Display Fix

**Date:** December 30, 2025  
**Project:** life_quality/PROJECT-006_COMMUNICATION_VARIABLE_MODELLING  
**Issue:** Frontend showing git commit hash (f892dbba) instead of semantic version (2.30.0/2.31.0)

---

## Problem Summary

The application footer was displaying:
- **Expected:** `Frontend: v2.31.0 | Backend: 2.31.0`
- **Actual:** `Frontend: v2.29.0 | Backend: 2.8.0 (f892dbba)`

The frontend version was showing an old git commit hash instead of the semantic version from package.json.

---

## Root Causes Identified

### 1. Vite Config Reading Git Commit Instead of Version
**File:** `vite.config.ts`

The build configuration was injecting the git commit hash:
```typescript
const getGitHash = () => {
  return execSync('git rev-parse --short HEAD').toString().trim()
}

define: {
  __GIT_COMMIT__: JSON.stringify(getGitHash()),
  __BUILD_TIME__: JSON.stringify(getBuildTime()),
}
```

The DeploymentInfo component displayed this commit hash as the version.

### 2. Pre-built Dist Folder Committed to Git
**Location:** `frontend/dist/`

The `dist/` folder with stale build files from December 29 was checked into version control. Railway was serving this pre-built folder instead of building fresh, so version updates never took effect.

### 3. Dockerfile Overriding Nixpacks Configuration
**File:** `frontend/Dockerfile`

A Dockerfile was present that expected a pre-built dist folder:
```dockerfile
# USE PRE-BUILT DIST FOLDER - DO NOT REBUILD
COPY dist ./dist
```

Railway prioritized this Dockerfile over `nixpacks.toml`. When we removed the dist folder, the Docker build failed with:
```
ERROR: "/dist": not found
```

### 4. Nixpacks Originally Skipping Build Phase
**File:** `frontend/nixpacks.toml`

The nixpacks configuration was set to skip the build:
```toml
[phases.install]
cmds = ["echo 'Using pre-built dist folder'"]
```

This meant even if nixpacks ran, it wouldn't build the application.

---

## Solutions Implemented

### Fix 1: Modified Vite Config to Read Version from package.json

**File:** `frontend/vite.config.ts`

Added function to read version from package.json:
```typescript
import { readFileSync } from 'fs'
import { join } from 'path'

// Get version from package.json
const getVersion = () => {
  try {
    const packageJson = JSON.parse(
      readFileSync(join(__dirname, 'package.json'), 'utf-8')
    )
    return packageJson.version
  } catch {
    return 'unknown'
  }
}

// Updated define section
define: {
  __APP_VERSION__: JSON.stringify(getVersion()),
  __GIT_COMMIT__: JSON.stringify(getGitHash()),
  __BUILD_TIME__: JSON.stringify(getBuildTime()),
}
```

### Fix 2: Updated DeploymentInfo Component

**File:** `frontend/src/components/DeploymentInfo.tsx`

Changed from displaying git commit to app version:
```typescript
// Before
declare const __GIT_COMMIT__: string;
const gitCommit = typeof __GIT_COMMIT__ !== 'undefined' ? __GIT_COMMIT__ : 'unknown';

<div>
  <strong>v:</strong> {gitCommit}
</div>

// After
declare const __APP_VERSION__: string;
const appVersion = typeof __APP_VERSION__ !== 'undefined' ? __APP_VERSION__ : 'unknown';

<div>
  <strong>v:</strong> {appVersion}
</div>
```

### Fix 3: Removed Dist Folder from Git

**Actions:**
1. Removed pre-built dist folder from version control:
   ```bash
   git rm -rf frontend/dist
   ```

2. Added dist to .gitignore:
   ```bash
   echo "dist/" >> frontend/.gitignore
   ```

### Fix 4: Removed Dockerfile

**Action:** Deleted `frontend/Dockerfile` to allow Railway to use nixpacks.toml

### Fix 5: Updated Nixpacks Configuration

**File:** `frontend/nixpacks.toml`

Updated to properly build the application:
```toml
[phases.setup]
nixPkgs = ["nodejs_20"]

[phases.install]
cmds = ["npm ci --legacy-peer-deps"]

[phases.build]
cmds = ["npm run build"]

[start]
cmd = "npx serve dist -p $PORT"
```

### Fix 6: Synchronized Backend Version

**File:** `backend/app/version.py`

Updated backend version to match frontend:
```python
VERSION = "2.31.0"
BUILD_ID = "version-display-fix"
```

---

## Deployment Flow (After Fixes)

1. **Railway receives push** to main branch
2. **Nixpacks detects** `nixpacks.toml` (no Dockerfile to override)
3. **Install phase:** `npm ci --legacy-peer-deps`
4. **Build phase:** `npm run build`
   - Vite reads version "2.31.0" from package.json
   - Injects `__APP_VERSION__ = "2.31.0"` at build time
   - Generates fresh dist folder
5. **Start phase:** `npx serve dist -p $PORT`
6. **Application displays:** `Frontend: v2.31.0 | Backend: 2.31.0`

---

## Commits Applied

1. `d353ab79` - Fix: Display package.json version instead of git commit in footer
2. `1c4db645` - Bump version to 2.31.0
3. `2f4592c1` - v2.31.0: Force Railway redeploy with version fix
4. `495479e2` - Sync backend version to 2.31.0
5. `1913557f` - Force Railway cache clear for v2.31.0 frontend build
6. `fbdd113e` - Add nixpacks config to ensure clean builds
7. `fd2a6d43` - Enable proper build in nixpacks - was skipping build phase
8. `a167f27f` - Remove old dist folder - force fresh build on Railway
9. `56afba21` - Ignore dist folder - should be built on deployment
10. `d650f7a1` - Remove Dockerfile - use nixpacks.toml for proper build process

---

## Key Lessons Learned

1. **Never commit build artifacts** (dist/, build/) to version control
2. **Railway prioritizes Dockerfile** over nixpacks.toml - ensure only one build system
3. **Version should come from package.json**, not git commit hash for user-facing display
4. **Git commit hash is still valuable** for debugging but should be logged to console, not shown as version
5. **Test Railway deployments** can be verified by checking the actual deployed commit hash vs expected

---

## Verification

After all fixes are deployed, verify:
- ✅ Footer shows semantic version from package.json
- ✅ Version updates when package.json is bumped
- ✅ Railway builds fresh on every deployment
- ✅ No dist folder in git repository
- ✅ Console logs show git commit for debugging

**Status:** ✅ RESOLVED
