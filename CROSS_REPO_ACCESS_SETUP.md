# Cross-Repository Access Setup Guide

**Issue:** Cannot access business_ventures repo from control_tower Codespace  
**Date:** October 13, 2025

---

## Problem Diagnosis

### Current State
- ✅ GitHub CLI authenticated as James-M-Fleming-985
- ✅ Can access control_tower repo
- ❌ Cannot access business_ventures repo
- ❌ GITHUB_TOKEN has limited scopes (only sees control_tower)
- ❌ SSH keys not configured in Codespace

### Root Cause
The automatic GITHUB_TOKEN provided by Codespaces has restricted permissions:
- Only has access to the repository where the Codespace was created (control_tower)
- Cannot clone or access other repositories in your account
- Limited API scopes

---

## Solution Options

### Option 1: Create Personal Access Token (RECOMMENDED) ✅

**Steps:**

1. **Create PAT on GitHub:**
   ```
   Go to: https://github.com/settings/tokens
   Click: "Generate new token (classic)"
   
   Select scopes:
   ✅ repo (all)
   ✅ workflow
   ✅ admin:org (read:org)
   ✅ gist
   
   Generate token and copy it
   ```

2. **Add PAT to Codespace:**
   ```bash
   # Set as environment variable (temporary)
   export GH_TOKEN="your_personal_access_token_here"
   
   # Or add to .bashrc (persistent)
   echo 'export GH_TOKEN="your_pat_here"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Re-authenticate GitHub CLI:**
   ```bash
   echo $GH_TOKEN | gh auth login --with-token
   ```

4. **Test access:**
   ```bash
   gh repo list James-M-Fleming-985 --limit 20
   gh repo clone James-M-Fleming-985/business_ventures
   ```

---

### Option 2: Configure SSH Keys

**Steps:**

1. **Generate SSH key:**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   # Press Enter for default location
   # Set passphrase (optional)
   ```

2. **Add to GitHub:**
   ```bash
   # Display public key
   cat ~/.ssh/id_ed25519.pub
   
   # Copy the output and add to:
   # https://github.com/settings/keys
   ```

3. **Test SSH connection:**
   ```bash
   ssh -T git@github.com
   ```

4. **Clone repos:**
   ```bash
   git clone git@github.com:James-M-Fleming-985/business_ventures.git
   ```

---

### Option 3: Work Within control_tower (ALTERNATIVE)

**Concept:** Create a projects structure that mirrors external repos

```
/workspaces/control_tower/
├── projects/
│   ├── PROJECT-003 TDD ENFORCER/
│   ├── PROJECT-004 AI CODE GENERATOR/
│   └── PROJECT-005 BUSINESS VENTURES/     ← NEW
│       └── causal-affect/
│           ├── features/
│           ├── src/
│           └── README.md
```

**Pros:**
- No authentication issues
- All work in one place
- Can still sync to business_ventures later

**Cons:**
- Need to manually sync changes to business_ventures repo
- Not ideal for long-term

---

## Recommended Immediate Action

**Quick Fix (5 minutes):**

1. Create PAT: https://github.com/settings/tokens
   - Name: "Codespace Control Tower Access"
   - Expiration: 90 days
   - Scopes: `repo`, `workflow`, `read:org`

2. Add to Codespace secrets:
   - Go to: https://github.com/settings/codespaces
   - Add secret: `GH_PERSONAL_TOKEN`
   - Value: Your PAT

3. Restart Codespace or run:
   ```bash
   export GH_TOKEN="<your_pat>"
   echo $GH_TOKEN | gh auth login --with-token
   ```

4. Verify:
   ```bash
   gh repo list | grep business
   ```

---

## Long-term Setup

### Codespace Secrets
Store PAT as Codespace secret so it's available automatically:

1. GitHub Settings → Codespaces → Secrets
2. Add: `GH_PERSONAL_TOKEN` with your PAT
3. Scope: Select `control_tower` repository
4. In your Codespace `.devcontainer/devcontainer.json`:
   ```json
   {
     "containerEnv": {
       "GH_TOKEN": "${localEnv:GH_PERSONAL_TOKEN}"
     }
   }
   ```

---

## Testing Checklist

After setup, verify you can:

- [ ] List all your repositories: `gh repo list`
- [ ] View business_ventures: `gh repo view James-M-Fleming-985/business_ventures`
- [ ] Clone business_ventures: `gh repo clone James-M-Fleming-985/business_ventures`
- [ ] Push to control_tower: `git push origin main`
- [ ] Create branches across repos

---

## Next Steps (After Access Fixed)

1. ✅ Clone business_ventures to `/workspaces/business_ventures`
2. ✅ Navigate into causal-affect project
3. ✅ Add control_tower as Git submodule
4. ✅ Create `features/` directory for YAML specs
5. ✅ Build first feature using control_tower tools

---

## Need Help?

Run this diagnostic:
```bash
echo "=== GitHub CLI Status ==="
gh auth status

echo -e "\n=== Available Repos ==="
gh repo list --limit 10

echo -e "\n=== Git Config ==="
git config --global user.name
git config --global user.email

echo -e "\n=== SSH Keys ==="
ls -la ~/.ssh/

echo -e "\n=== Environment ==="
env | grep -E "(GITHUB|GH_)"
```

Send the output and we can troubleshoot further!
