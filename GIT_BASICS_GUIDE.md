# Git Basics: How It Actually Works

## 🎯 **What Git Does**
Git is a **time machine** for your code. It takes "snapshots" of your files at different points in time so you can:
- Go back to any previous version
- See what changed between versions
- Work on different features simultaneously
- Collaborate with others without conflicts

## 📸 **The Snapshot System**

Think of Git like taking photos:
```
Photo 1: "Initial project setup"
Photo 2: "Added login feature" 
Photo 3: "Fixed bug in payment"
Photo 4: "Added user dashboard"
```

Each "photo" is called a **commit** - it's a complete snapshot of all your files at that moment.

## 🏗️ **The Three Main Areas**

### 1. **Working Directory** 
- The files you can see and edit
- Like your desk where you're working
- Changes here are NOT saved yet

### 2. **Staging Area**
- Files prepared to be saved
- Like a "draft" before publishing
- Use `git add` to put files here

### 3. **Repository** 
- Your saved history of snapshots
- Like a photo album of all your commits
- Use `git commit` to save the snapshot

## 🔄 **Basic Git Workflow**

```bash
# 1. Make changes to files
# (edit, create, delete files)

# 2. Stage the changes
git add filename.txt        # Stage one file
git add .                   # Stage all changes

# 3. Commit (take the snapshot)
git commit -m "Description of what I did"

# 4. (Optional) Share with others
git push                    # Send to GitHub/remote server
```

## 🌿 **Branches: Parallel Timelines**

Imagine you're writing a book:
- **main branch**: Your main story
- **feature branch**: A "what if" alternative chapter

```bash
git branch feature-login    # Create new timeline
git checkout feature-login  # Switch to that timeline
# Make changes...
git checkout main          # Switch back to main timeline
git merge feature-login    # Combine the timelines
```

## 📡 **Local vs Remote**

### **Local Repository**
- Lives on your computer/codespace
- Only you can see it
- Fast to work with

### **Remote Repository** (GitHub)
- Lives on the internet
- Others can see/access it
- Backup of your work

```bash
git clone <url>     # Copy remote repo to local
git pull            # Get updates from remote
git push            # Send your commits to remote
```

## 📊 **Essential Commands**

### **Getting Information**
```bash
git status          # What's changed? What needs to be committed?
git log             # Show history of commits
git diff            # Show exactly what changed
```

### **Basic Operations**
```bash
git add .                    # Stage all changes
git commit -m "message"      # Save snapshot with description
git push                     # Send to remote (GitHub)
git pull                     # Get latest from remote
```

### **Branching**
```bash
git branch                   # List all branches
git branch new-feature       # Create new branch
git checkout new-feature     # Switch to branch
git checkout main            # Switch back to main
```

## 🚨 **Common Mistakes**

### **1. Not Committing Often Enough**
❌ Work for hours, then commit once
✅ Commit every 15-30 minutes with small changes

### **2. Not Pushing to Remote**
❌ Only commit locally
✅ Push frequently so work is backed up

### **3. Poor Commit Messages**
❌ `git commit -m "stuff"`
✅ `git commit -m "Add user login validation"`

### **4. Working Only in Working Directory**
❌ Edit files for days without committing
✅ Regular: edit → add → commit → push cycle

## 🎭 **Git States of Files**

Files can be in different states:

1. **Untracked**: New files Git doesn't know about
2. **Modified**: Changed files in working directory
3. **Staged**: Files ready to be committed
4. **Committed**: Files saved in repository history

```bash
git status    # Shows which state each file is in
```

## 💡 **Mental Model**

Think of Git like:
- **Saving a video game**: Each commit is a save point
- **Photo album**: Each commit is a snapshot
- **Time machine**: You can go back to any commit
- **Collaboration tool**: Multiple people can work on same project

## 🔧 **Your Situation Explained**

**What happened to your work:**
1. You worked for months ✅
2. Made changes in Working Directory ✅  
3. Never used `git add` ❌
4. Never used `git commit` ❌
5. Codespace crashed = ALL LOST ❌

**Why it was lost:**
- Changes only existed in Working Directory
- No snapshots (commits) were taken
- No backup (push) to GitHub

**How to prevent:**
```bash
# Every 30 minutes:
git add .
git commit -m "Work in progress"
git push
```

This creates a backup chain:
Working Directory → Staging → Local Repository → GitHub

---

## 🔍 **Tracking Multiple Files: What's Committed vs Not**

### **The Essential Command: `git status`**
This shows you EXACTLY what's happening with all your files:

```bash
$ git status
On branch main
Your branch is up to date with 'origin/main'.

Changes to be committed:        # ✅ STAGED (ready to commit)
  (use "git restore --staged <file>..." to unstage)
	modified:   src/main.py
	new file:   src/helper.py

Changes not staged for commit:  # ⚠️  MODIFIED but NOT staged
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes)
	modified:   README.md
	modified:   docs/guide.md

Untracked files:               # 🆕 NEW files Git doesn't know about
  (use "git add <file>..." to include in what will be committed)
	temp_notes.txt
	config/settings.json
```

### **Translation:**
- **Green files** (Changes to be committed): ✅ Will be included in next commit
- **Red files** (Changes not staged): ⚠️ Modified but WON'T be committed yet
- **Red files** (Untracked): 🆕 New files that won't be committed yet

### **Quick Status Check**
```bash
git status --short    # Compact view
```

Shows:
```
M  src/main.py       # Modified and staged (green)
 M docs/guide.md     # Modified but not staged (red)  
A  src/helper.py     # Added/new and staged (green)
?? temp_notes.txt    # Untracked (red)
```

### **The Safe Workflow for Multiple Files**

#### **1. Check what's changed:**
```bash
git status           # See all file states
git diff             # See exact changes in unstaged files
git diff --staged    # See exact changes in staged files
```

#### **2. Stage specific files:**
```bash
# Option A: Stage specific files
git add src/main.py docs/guide.md

# Option B: Stage all changes
git add .

# Option C: Interactive staging (choose what to stage)
git add -p
```

#### **3. Verify before committing:**
```bash
git status           # Double-check what will be committed
git diff --staged    # Review exact changes going into commit
```

#### **4. Commit with confidence:**
```bash
git commit -m "Add user authentication and update documentation"
```

### **Pro Tips for Multiple Files**

#### **See what changed since last commit:**
```bash
git diff HEAD        # All changes since last commit
git diff HEAD~1      # All changes since 2 commits ago
```

#### **Check specific file history:**
```bash
git log --oneline src/main.py    # Commits that touched this file
git log -p src/main.py           # See actual changes to this file
```

#### **Compare files between commits:**
```bash
git diff HEAD~1 HEAD src/main.py  # See what changed in this file
```

### **🚨 Common Multi-File Mistakes**

#### **Mistake 1: Assuming all changes are staged**
```bash
# ❌ BAD: Only commits staged files
git commit -m "Updated everything"

# ✅ GOOD: Check first, then stage what you want
git status
git add file1.py file2.py
git commit -m "Updated user login and dashboard"
```

#### **Mistake 2: Committing unwanted files**
```bash
# ❌ BAD: Stages everything including temp files
git add .

# ✅ GOOD: Be selective or use .gitignore
git add src/ docs/
# Or create .gitignore for temp files
```

#### **Mistake 3: Not reviewing before commit**
```bash
# ✅ ALWAYS do this before committing:
git status           # What will be committed?
git diff --staged    # What exactly changed?
git commit -m "..." # Then commit
```

### **🛡️ Safety Checklist for Multiple Files**

Before every commit:
1. ✅ `git status` - Know what's staged vs not
2. ✅ `git diff --staged` - Review exact changes
3. ✅ Meaningful commit message describing what changed
4. ✅ `git push` regularly to backup to GitHub

### **Example Workflow:**
```bash
# Working on 5 files...
# feature.py, tests.py, README.md, config.json, temp.log

# 1. Check status
git status
# Shows: 3 modified, 2 new files

# 2. Stage only the files I want to commit
git add feature.py tests.py README.md
# (leaving out config.json and temp.log)

# 3. Verify what's staged
git status
git diff --staged

# 4. Commit the staged files
git commit -m "Add user feature with tests and documentation"

# 5. Handle remaining files later
git add config.json
git commit -m "Update configuration for new feature"
# (temp.log stays uncommitted - maybe add to .gitignore)
```