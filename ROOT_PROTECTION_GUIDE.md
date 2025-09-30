# Repository File Protection Quick Reference
# ==========================================

## 🚨 FAILSAFES IN PLACE:

### 1. **Automated Checker**
```bash
# Before creating any file, run:
python scripts/repo_file_guard.py "filename.py"
```

### 2. **Git Protection**  
`.gitignore` rules prevent common temp files from being committed to root:
- `/temp_*.py`, `/tmp_*.py`, `/test_*.py` 
- `/debug_*.py`, `/quick_*.py`, `/scratch_*.py`
- `/*_temp.md`, `/*_draft.md`, `/*_backup.*`

### 3. **Manual Verification**
```bash
# Check current directory before saving
pwd
# Should NOT be: /workspaces/control_tower
```

## 📁 PROPER LOCATIONS:

### PROJECT-003 Files:
- **Source Code**: `projects/PROJECT-003 TDD ENFORCER/src/`
- **Tests**: `projects/PROJECT-003 TDD ENFORCER/tests/` 
- **Documentation**: `projects/PROJECT-003 TDD ENFORCER/docs/`

### General Files:
- **Source Code**: `src/`
- **Tests**: `tests/`
- **Documentation**: `docs/`
- **Scripts**: `scripts/`
- **Configuration**: `config/`
- **Data**: `data/`
- **Reports**: `reports/`

## 🛡️ WORKFLOW PROTECTION:

### Safe File Creation Pattern:
```bash
# 1. Navigate to proper directory FIRST
cd projects/PROJECT-003 TDD ENFORCER/src/

# 2. Verify location  
python /workspaces/control_tower/scripts/repo_file_guard.py "new_file.py"

# 3. Create file only after ✅ confirmation
```

### Emergency Cleanup:
```bash
# If file accidentally created in root:
mkdir -p proper/location/
mv accidental_file.py proper/location/
```

## 📊 CURRENT SITUATION:
- **91 existing files** in root need eventual relocation
- **Gradual cleanup** recommended during normal development
- **New files** should follow proper structure immediately

## 🔧 QUICK COMMANDS:

```bash
# Check where you are
pwd

# Check if file placement is safe
python scripts/repo_file_guard.py "filename"

# Get cleanup suggestions for root
python -c "from scripts.repo_file_guard import RepoFileGuard; guard = RepoFileGuard(); [print(s['command']) for s in guard.get_root_cleanup_suggestions()[:5]]"
```

**Remember: When in doubt, ask before saving to root!** 🚨