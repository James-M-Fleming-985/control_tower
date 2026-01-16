# Communication Improvement Project - CSV Task Import Workflow

**Created:** December 30, 2025  
**Purpose:** Zero-writing task management for the Strategic Communication Improvement project

---

## 🎯 Overview

The communication improvement project uses a **CSV-based task import** system that eliminates manual task creation. You simply:

1. **Review** the CSV task list
2. **Upload** to the application via Data Management tab
3. **Execute** tasks from the Calendar tab
4. **Update** task status after each interaction

No documentation writing, no risk management docs - all strategic discussions happen transparently with the actor.

---

## 📁 File Location

**Task CSV:** `/workspaces/control_tower/COMMUNICATION_IMPROVEMENT_TASKS.csv`

This file contains 21 pre-defined tasks spanning 6 months (January - June 2026):
- **Phase 1:** Foundation & Assessment (4 tasks)
- **Phase 2:** Active Listening & Verification (3 tasks)
- **Phase 3:** Pattern Recognition & Adaptation (3 tasks)
- **Phase 4:** Incremental Trust Building (3 tasks)
- **Phase 5:** Complex Topic Navigation (3 tasks)
- **Phase 6:** Sustainable System & Refinement (3 tasks)

---

## 🔄 Workflow

### Step 1: Review Task List (One-Time)

```bash
# View the CSV file
cat /workspaces/control_tower/COMMUNICATION_IMPROVEMENT_TASKS.csv
```

Check that:
- Task titles are clear and actionable
- Due dates align with your schedule
- Phases make sense
- Estimated hours are reasonable

If you want to modify tasks, edit the CSV directly (it's just a text file).

### Step 2: Upload to Application (One-Time)

1. Open the PROJECT-006 application
2. Go to **Data Management** tab
3. Find the **"Import Tasks from CSV"** section at the top
4. Click **"Choose Task CSV File"**
5. Select: `/workspaces/control_tower/COMMUNICATION_IMPROVEMENT_TASKS.csv`
6. Click Upload

**What happens:**
- System creates project: "Strategic Communication Improvement"
- Creates 21 tasks with due dates, descriptions, phases
- Tasks appear in Calendar tab automatically
- Tasks are organized by phase in descriptions

### Step 3: Daily Execution (Ongoing)

1. Open **Calendar** tab
2. View tasks scheduled for today/this week
3. Read the task title and description
4. **Execute** the task (have the interaction, run the simulation)
5. Update task status:
   - Click task on calendar
   - Mark as "In Progress" when starting
   - Mark as "Completed" when done
   - Add actual hours if tracking time

**No Writing Required:**
- No scope documents
- No risk management docs
- No progress reports
- No retrospectives

### Step 4: Strategic Discussions (Transparent)

When risk management or strategic decisions are needed:

**❌ Don't:** Write internal risk documents  
**✅ Do:** Discuss openly with the actor

Example:
- "I'm noticing we're both getting tense in these conversations. Can we talk about what's working and what isn't?"
- "I want to be transparent - I'm tracking my emotional state before our talks to see patterns. Is that okay with you?"
- "This approach isn't working. Can we try a different strategy together?"

The project document explicitly says: "Any thing like risk management etc should be a discussion with the actor completely transparent."

---

## 📊 CSV Format Reference

```csv
project_name,task_title,task_description,status,priority,due_date,phase,estimated_hours
Strategic Communication Improvement,Create Actor Profile Document,"Documentation of patterns...",todo,high,2025-01-06,Phase 1: Foundation,120
```

**Columns:**
- `project_name` (required): Auto-creates project if doesn't exist
- `task_title` (required): Appears in calendar
- `task_description` (optional): Details shown when you click task
- `status` (optional): todo, in_progress, blocked, completed
- `priority` (optional): low, medium, high, urgent
- `due_date` (optional): Format YYYY-MM-DD
- `phase` (optional): Added to description for context
- `estimated_hours` (optional): Minutes (not hours, legacy field name)

---

## 🗓️ Calendar Integration

Once imported, tasks automatically appear in the Calendar tab:

**Day View:**
- Shows today's tasks in timeline format
- Hourly slots for scheduling

**Week View:**
- 7-column grid showing upcoming tasks
- Easy to see what's coming

**Month View:**
- Traditional calendar with task indicators
- Color-coded by project

**Task Actions:**
- Click task to view full details
- Update status (todo → in_progress → completed)
- Mark as "needs follow-up" for multi-stage interactions
- Drag-and-drop to reschedule (if needed)

---

## 📈 Metrics Dashboard

Calendar tab shows:
- **Pending Communications:** Tasks not yet started
- **This Week Scheduled:** Upcoming 7 days
- **Late/Overdue:** Past due date, not completed
- **Further Communication Required:** Flagged for follow-up

These metrics help you track progress without writing reports.

---

## 🔧 Making Changes

### Add More Tasks

1. Open the CSV file in VS Code or Excel
2. Add new row with project_name, task_title, etc.
3. Save file
4. Upload again via Data Management tab
5. New tasks appear in Calendar

### Modify Existing Tasks

**Option A: Edit in Application**
- Click task in Calendar
- Update directly in the UI

**Option B: Re-import CSV**
- Edit CSV file
- Delete old tasks from project board
- Re-upload CSV

### Adjust Timeline

If you need to extend the 6-month timeline:
1. Edit CSV due dates
2. Re-upload (will create new tasks)
3. Delete old tasks if needed

---

## 💡 Key Principles

### 1. Read, Execute, Update
- **Read** what the task is
- **Execute** (run simulation, have interaction)
- **Update** status after completion

### 2. Zero Documentation Burden
- No internal memos
- No risk registers
- No progress reports
- Just tasks and execution

### 3. Transparent Communication
- All strategic decisions discussed with actor
- No hidden risk management
- Open about methods and tracking
- Honest about what's working/not working

### 4. Incremental Learning
- Small tasks over 6 months
- Focus on patterns and consistency
- Celebrate small wins
- Adjust as you learn

---

## 🚀 Getting Started Checklist

Before uploading tasks:
- [ ] Review COMMUNICATION_IMPROVEMENT_TASKS.csv
- [ ] Verify due dates align with your availability
- [ ] Confirm you understand each task's purpose
- [ ] Ensure PROJECT-006 application is accessible

After uploading:
- [ ] Verify all 21 tasks appear in Calendar
- [ ] Check project "Strategic Communication Improvement" was created
- [ ] Review first week's tasks
- [ ] Set reminder to check Calendar daily

During execution:
- [ ] Open Calendar tab daily
- [ ] Read task details before interactions
- [ ] Update status immediately after completion
- [ ] Use "needs follow-up" flag for multi-stage communications
- [ ] Have transparent discussions about strategy with actor

---

## 📝 Example Daily Routine

**Morning (2 minutes):**
1. Open PROJECT-006 Calendar tab
2. Check tasks scheduled for today
3. Read task titles and descriptions
4. Mental preparation for interactions

**After Interaction (1 minute):**
1. Click completed task in Calendar
2. Mark as "Completed"
3. Add any actual hours if tracking
4. Flag "needs follow-up" if multi-stage

**Weekly (5 minutes):**
1. Review upcoming week's tasks
2. Check if any tasks need rescheduling
3. Review completed tasks count
4. Adjust if falling behind

---

## 🎓 Success Metrics (From Project Plan)

Track these through the Calendar metrics dashboard:

**Month 1-2:**
- Misunderstandings reduced by 20-30%
- Verification protocol used in 90% of interactions
- Daily logging maintained

**Month 3-4:**
- Trust index improvement +20%
- Trigger prediction accuracy 80%+
- Successful de-escalations 70%+

**Month 5-6:**
- Overall misunderstandings -60% vs baseline
- Trust index +40%
- Emotional stability +50%
- Communication clarity +60%

These aren't tracked through documents - they're tracked through:
- Subjective assessment (how do interactions feel?)
- Outcome quality (are we achieving goals together?)
- Actor feedback (do they notice improvement?)

---

## ⚠️ Important Notes

1. **CSV Upload is Additive:** Each upload creates new tasks. Delete old tasks first if re-importing.

2. **Project Auto-Creation:** If "Strategic Communication Improvement" doesn't exist, it's created automatically.

3. **Task IDs are Unique:** Each task gets a unique UUID, so you can't accidentally duplicate by title.

4. **Calendar Permissions:** Uses your PROJECT-006 login, so tasks are private to your account.

5. **No Undo:** Once tasks are created, edit them in the UI or delete and re-import.

6. **Date Format:** Must be YYYY-MM-DD (ISO format). Invalid dates are ignored.

---

## 🔗 Related Files

- **Project Plan:** `/workspaces/control_tower/PROJECT_COMMUNICATION_IMPROVEMENT_VOLATILE_ACTOR.md`
- **Task CSV:** `/workspaces/control_tower/COMMUNICATION_IMPROVEMENT_TASKS.csv`
- **Application:** PROJECT-006 Communication Variable Modelling System
- **Backend Endpoint:** `/api/projects/tasks/import`
- **Frontend:** Data Management tab → Import Tasks section

---

## 🆘 Troubleshooting

**Tasks don't appear in Calendar:**
- Check Data Management tab for import success message
- Verify CSV format (required columns present)
- Check browser console for errors
- Try refreshing Calendar tab

**Wrong due dates:**
- Edit CSV and re-upload
- Or edit tasks individually in Calendar

**Can't upload file:**
- Check file is .csv format
- Ensure you're logged into PROJECT-006
- Try smaller batch (split CSV)

**Tasks in wrong project:**
- Check `project_name` column in CSV
- Delete tasks and re-import with correct name

---

**Ready to start? Upload the CSV and begin Phase 1!** 🚀
