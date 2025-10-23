# PROJECT-002 INDUSTRIALIZATION - Laptop B Deployment Guide

**Project**: ZnNi Line Industrialization Tracking System  
**Target**: Organization Laptop B (Windows)  
**Source**: Development Laptop A  
**Created**: October 21, 2025  
**Type**: Python File Monitor + Excel Data + Power BI Dashboard

---

## 📋 WHAT THIS SYSTEM DOES

Track 64 aircraft landing gear parts through 23 industrialization stages as they transition from Cadmium to Zinc Nickel coating.

**Core Components**:
- ✅ **Python File Monitor** - Detects evidence files in 23 stage folders (P: drive)
- ✅ **23 Industrialization Stages** - Across 5 phases (Design → Production → Integration)
- ✅ **4 Excel Data Files** - Store part status, stage definitions, master list, stakeholders
- ✅ **Power BI Dashboard** - 3 pages: Overview, Part Detail, Stage Heatmap
- ✅ **Email Alerts** - Python sends HTML emails for delays and milestones

**Python is REQUIRED** - it's the automation engine, not optional!

---

## 🎯 SYSTEM ARCHITECTURE

```text
P:\Process\Plating Shop\ZnNi Industrialization\
├── 01_Coating_Specification/          ← Stage folders (23 total)
├── 02_Process_Flow_Diagram/
├── ...
├── 23_Post_Production_Optimization/
└── Data/
    ├── ZnNi_Master_Status.xlsx        ← Part status table
    ├── ZnNi_Stage_Definitions.xlsx    ← 23 stage reference
    ├── ZnNi_Part_Master.xlsx          ← 64 parts metadata
    └── Stakeholder_Distribution.xlsx  ← Email list

Python Monitor (Spyder IDE on Laptop B)
    ↓ Scans folders every 5 minutes
    ↓ Detects: PartNumber_StageName_Date_Status.xlsx
    ↓ Parses filename with regex
    ↓ Updates Excel files
    ↓ Triggers email alerts

Power BI Dashboard (app.powerbi.com)
    ↓ Connects to Excel files (Power Query auto-refresh every 10 min)
    ↓ Shows real-time status of 64 parts
```

**23 Industrialization Stages**:

**DESIGN** (1-4): Coating Spec → Process Flow → FMEA → Design Review  
**PROCUREMENT** (5-8): Equipment → Supplier Qual → Tooling → Chemical Bath  
**VALIDATION** (9-12): Parameter Dev → FAI → Salt Spray → Adhesion Test  
**PRODUCTION PREP** (13-15): Training → Work Instructions → QC Plan  
**PRODUCTION VAL** (16-19): Pilot Run → SPC → Customer Approval → Release  
**SYSTEM INTEGRATION** (20-22): ERP → Quality → Traceability  
**CONTINUOUS IMPROVEMENT** (23): Post-Production Optimization

---

## ✅ PREREQUISITES CHECKLIST

### Before You Start

- [ ] **Laptop B** - Windows 10/11 with admin rights
- [ ] **P: Drive Access** - Mapped network drive with read/write permissions
  - Path must be: `P:\Process\Plating Shop\ZnNi Industrialization\`
  - Can you create folders? Can you create/edit Excel files?
- [ ] **Python 3.12+** - Check if installed (Spyder IDE usually includes Python)
  - Open Command Prompt: `python --version`
  - If "Python 3.12" or higher shows → ✅ Good
  - If error or older version → Install Python (see Phase 2)
- [ ] **Spyder IDE** - For running Python monitor (or VS Code as alternative)
- [ ] **Microsoft Excel** - For editing data files
- [ ] **Power BI Desktop** - For creating dashboard
- [ ] **Power BI Pro License** - For publishing to web
- [ ] **Outlook Email** - For sending alerts

### Information You'll Need

Write these down before starting:

```text
P: Drive Path: _____________________________________________

Your Email: ________________________________________________

Stakeholder Emails (comma-separated): ____________________
_____________________________________________________________

Power BI Workspace Name: ___________________________________
```

---

## 📦 PHASE 1: TRANSFER PROJECT FROM LAPTOP A TO LAPTOP B

### Step 1.1: Create Deployment ZIP on Laptop A ✅

On development laptop (Laptop A):

- [ ] Open terminal in project folder
- [ ] Run ZIP command:

```bash
cd "/workspaces/professional_excellence/projects/PROJECT-002 INDUSTRIALIZATION"

# Create deployment package
zip -r PROJECT-002-DEPLOYMENT.zip \
  src/ \
  tests/ \
  config/ \
  scripts/ \
  FEATURE-002-*/ \
  requirements.txt \
  pytest.ini \
  *.yaml \
  *.md \
  --exclude "*.pyc" \
  --exclude "__pycache__" \
  --exclude ".pytest_cache"
```

- [ ] Verify ZIP created: `ls -lh PROJECT-002-DEPLOYMENT.zip`
- [ ] Should be ~5-15 MB

### Step 1.2: Transfer to Laptop B ✅

Choose ONE method:

**Option A: USB Drive**
- [ ] Copy ZIP to USB drive
- [ ] Insert USB into Laptop B
- [ ] Copy to `C:\Users\YourName\Documents\`

**Option B: Email**
- [ ] Email ZIP to your organization email
- [ ] Open email on Laptop B
- [ ] Download to `C:\Users\YourName\Documents\`

**Option C: Network Share**
- [ ] Copy ZIP to shared network drive
- [ ] Access from Laptop B
- [ ] Copy to `C:\Users\YourName\Documents\`

### Step 1.3: Extract on Laptop B ✅

- [ ] Open File Explorer
- [ ] Navigate to `C:\Users\YourName\Documents\`
- [ ] Right-click ZIP → "Extract All..."
- [ ] Extract to: `C:\Users\YourName\Documents\ZnNi_Tracker\`
- [ ] Verify extraction:
  - [ ] Folder exists: `C:\Users\YourName\Documents\ZnNi_Tracker\`
  - [ ] Contains: `src/`, `tests/`, `requirements.txt`, etc.

---

## 🐍 PHASE 2: PYTHON ENVIRONMENT SETUP

### Step 2.1: Check if Python Already Installed ✅

- [ ] Open **Command Prompt** (Win+R → `cmd` → Enter)
- [ ] Type: `python --version`
- [ ] Check result:
  - ✅ Shows "Python 3.12.x" or higher → Skip to Step 2.3
  - ❌ Shows error or version < 3.12 → Continue to Step 2.2

### Step 2.2: Install Python 3.12 (If Needed) ✅

- [ ] Go to: <https://www.python.org/downloads/>
- [ ] Download: "Python 3.12.x" Windows installer (64-bit)
- [ ] Run installer
- [ ] ⚠️ **CRITICAL**: Check ✅ "Add Python 3.12 to PATH"
- [ ] Click "Install Now"
- [ ] Wait for installation (3-5 minutes)
- [ ] Close installer
- [ ] Open **NEW** Command Prompt (previous one won't see PATH)
- [ ] Verify: `python --version` → Should show Python 3.12.x

### Step 2.3: Install Python Dependencies ✅

- [ ] Open Command Prompt
- [ ] Navigate to project:

```cmd
cd C:\Users\YourName\Documents\ZnNi_Tracker
```

- [ ] Install packages:

```cmd
pip install -r requirements.txt
```

- [ ] Expected packages (will take 2-3 minutes):
  - `schedule` - Job scheduling
  - `openpyxl` - Excel file manipulation
  - `pandas` - Data processing
  - `msal` - Microsoft authentication
  - `jinja2` - Email templates
  - `pytest` - Testing framework
  
- [ ] Verify installation:

```cmd
pip list
```

- [ ] Should see all packages listed with versions

### Step 2.4: Test Python Installation ✅

- [ ] Run quick test:

```cmd
python -c "import schedule, openpyxl, pandas; print('Python environment ready!')"
```

- [ ] Should print: "Python environment ready!"
- [ ] If error → check which package failed and reinstall:

```cmd
pip install --upgrade <package_name>
```

---

## 📁 PHASE 3: P: DRIVE FOLDER STRUCTURE SETUP

### Step 3.1: Verify P: Drive Access ✅

- [ ] Open File Explorer
- [ ] Navigate to: `P:\`
- [ ] Can you see folders? ✅
- [ ] If "P:\" doesn't exist → contact IT to map P: drive

### Step 3.2: Create Base Folder ✅

- [ ] Navigate to: `P:\Process\Plating Shop\`
- [ ] Create folder: `ZnNi Industrialization`
- [ ] Full path should be: `P:\Process\Plating Shop\ZnNi Industrialization\`

### Step 3.3: Create 23 Stage Folders ✅

**Manual Method** (if PowerShell script doesn't work):

In `P:\Process\Plating Shop\ZnNi Industrialization\`, create these folders:

**DESIGN PHASE**:
- [ ] `01_Coating_Specification_Development`
- [ ] `02_Process_Flow_Diagram_Creation`
- [ ] `03_FMEA_Completion`
- [ ] `04_Design_Review_Approval`

**PROCUREMENT PHASE**:
- [ ] `05_Equipment_Procurement`
- [ ] `06_Material_Supplier_Qualification`
- [ ] `07_Tooling_Fixtures_Fabrication`
- [ ] `08_Chemical_Bath_Setup`

**VALIDATION PHASE**:
- [ ] `09_Process_Parameter_Development`
- [ ] `10_First_Article_Inspection_FAI`
- [ ] `11_Salt_Spray_Testing`
- [ ] `12_Adhesion_Testing`

**PRODUCTION PREPARATION**:
- [ ] `13_Operator_Training`
- [ ] `14_Work_Instruction_Creation`
- [ ] `15_Quality_Control_Plan`

**PRODUCTION VALIDATION**:
- [ ] `16_Pilot_Production_Run`
- [ ] `17_Statistical_Process_Control_SPC`
- [ ] `18_Customer_Approval_Submission`
- [ ] `19_Production_Release`

**SYSTEM INTEGRATION**:
- [ ] `20_ERP_System_Integration`
- [ ] `21_Quality_System_Integration`
- [ ] `22_Traceability_System_Setup`

**CONTINUOUS IMPROVEMENT**:
- [ ] `23_Post_Production_Optimization`

**PowerShell Method** (faster, if you're comfortable):

- [ ] Open PowerShell
- [ ] Copy and run this script:

```powershell
$stages = @(
    "01_Coating_Specification_Development",
    "02_Process_Flow_Diagram_Creation",
    "03_FMEA_Completion",
    "04_Design_Review_Approval",
    "05_Equipment_Procurement",
    "06_Material_Supplier_Qualification",
    "07_Tooling_Fixtures_Fabrication",
    "08_Chemical_Bath_Setup",
    "09_Process_Parameter_Development",
    "10_First_Article_Inspection_FAI",
    "11_Salt_Spray_Testing",
    "12_Adhesion_Testing",
    "13_Operator_Training",
    "14_Work_Instruction_Creation",
    "15_Quality_Control_Plan",
    "16_Pilot_Production_Run",
    "17_Statistical_Process_Control_SPC",
    "18_Customer_Approval_Submission",
    "19_Production_Release",
    "20_ERP_System_Integration",
    "21_Quality_System_Integration",
    "22_Traceability_System_Setup",
    "23_Post_Production_Optimization"
)

$basePath = "P:\Process\Plating Shop\ZnNi Industrialization"
foreach ($stage in $stages) {
    New-Item -Path "$basePath\$stage" -ItemType Directory -Force
    Write-Host "Created: $stage" -ForegroundColor Green
}
```

### Step 3.4: Create Data Subfolder ✅

- [ ] In `P:\Process\Plating Shop\ZnNi Industrialization\`, create folder: `Data`
- [ ] This will store the 4 Excel files

### Step 3.5: Add README Files to Stage Folders ✅

For each stage folder, create a `README.txt` file with this content:

```text
FILE NAMING CONVENTION

Format: [PartNumber]_[StageName]_[Date]_[Status].ext

Examples:
✅ LowerCardanPin_FAI_20251021_PASS.xlsx
✅ A330Axel_SaltSpray_20251022_FAIL.pdf
✅ RetractionLink_Training_20251023.docx

Rules:
- Part Number: No spaces, use exact part ID
- Stage Name: Use abbreviation (FAI, SPC, FMEA, etc.)
- Date: YYYYMMDD format
- Status: PASS, FAIL, IN_PROGRESS (optional)
- Extension: .xlsx, .pdf, .docx, .csv

Upload your evidence file to this folder and Python monitor will detect it within 5 minutes!
```

- [ ] Copy README.txt to all 23 stage folders (or create once and copy 23 times)

---

## 📊 PHASE 4: EXCEL DATA FILES SETUP

### Step 4.1: Create Master Status Table ✅

- [ ] Open Excel
- [ ] Create new workbook
- [ ] Create table with these columns:

| Column Name | Data Type | Example |
|-------------|-----------|---------|
| PartNumber | Text | LowerCardanPin |
| PartDescription | Text | Lower Cardan Pin Assembly |
| Customer | Text | Airbus A330 |
| Priority | Text | Critical |
| CurrentStage | Number | 10 |
| CurrentStageName | Text | First Article Inspection |
| TargetCompletionDate | Date | 2025-11-30 |
| LastUpdatedDate | Date | 2025-10-21 |
| StatusFlag | Text | On Track |
| EvidenceFilePath | Text | P:\...\10_FAI\file.xlsx |

- [ ] Add 4 baseline parts (already industrialized):

**Part 1**:
- PartNumber: `LowerCardanPin`
- Description: `Lower Cardan Pin`
- Customer: `Airbus A330`
- Priority: `Critical`
- CurrentStage: `23`
- CurrentStageName: `Post Production Optimization`
- TargetCompletionDate: `2025-11-30`
- StatusFlag: `Complete`

**Part 2**:
- PartNumber: `A330Axel`
- Description: `A330 Axels`
- Customer: `Airbus A330`
- Priority: `High`
- CurrentStage: `23`
- StatusFlag: `Complete`

**Part 3**:
- PartNumber: `RetractionLink`
- Description: `Retraction Link`
- Customer: `Boeing 737`
- Priority: `High`
- CurrentStage: `23`
- StatusFlag: `Complete`

**Part 4**:
- PartNumber: `UpperCardanPin`
- Description: `Upper Cardan Pin`
- Customer: `Airbus A330`
- Priority: `Critical`
- CurrentStage: `23`
- StatusFlag: `Complete`

- [ ] Format as Table:
  - Select all data including headers
  - Insert → Table
  - Check "My table has headers"
  - Table Name: `MasterStatus`

- [ ] Save as: `ZnNi_Master_Status.xlsx`
- [ ] Save to: `P:\Process\Plating Shop\ZnNi Industrialization\Data\`

### Step 4.2: Create Stage Definitions Table ✅

- [ ] Open new Excel workbook
- [ ] Create table:

| StageNumber | StageName | Phase | Abbreviation |
|-------------|-----------|-------|--------------|
| 1 | Coating Specification Development | DESIGN | CoatSpec |
| 2 | Process Flow Diagram Creation | DESIGN | PFD |
| 3 | FMEA Completion | DESIGN | FMEA |
| 4 | Design Review Approval | DESIGN | DesignReview |
| 5 | Equipment Procurement | PROCUREMENT | EquipProc |
| 6 | Material Supplier Qualification | PROCUREMENT | SupplierQual |
| 7 | Tooling Fixtures Fabrication | PROCUREMENT | Tooling |
| 8 | Chemical Bath Setup | PROCUREMENT | ChemBath |
| 9 | Process Parameter Development | VALIDATION | ParamDev |
| 10 | First Article Inspection | VALIDATION | FAI |
| 11 | Salt Spray Testing | VALIDATION | SaltSpray |
| 12 | Adhesion Testing | VALIDATION | Adhesion |
| 13 | Operator Training | PROD_PREP | Training |
| 14 | Work Instruction Creation | PROD_PREP | WorkInst |
| 15 | Quality Control Plan | PROD_PREP | QCPlan |
| 16 | Pilot Production Run | PROD_VAL | PilotRun |
| 17 | Statistical Process Control Setup | PROD_VAL | SPC |
| 18 | Customer Approval Submission | PROD_VAL | CustApproval |
| 19 | Production Release | PROD_VAL | ProdRelease |
| 20 | ERP System Integration | INTEGRATION | ERP |
| 21 | Quality System Integration | INTEGRATION | QualityInt |
| 22 | Traceability System Setup | INTEGRATION | Traceability |
| 23 | Post Production Optimization | IMPROVEMENT | PostProd |

- [ ] Format as Table: `StageDefinitions`
- [ ] Save as: `ZnNi_Stage_Definitions.xlsx`
- [ ] Save to: `P:\Process\Plating Shop\ZnNi Industrialization\Data\`

### Step 4.3: Create Part Master List ✅

- [ ] Create new Excel workbook
- [ ] Add 4 baseline parts plus columns for 60 more:

| PartNumber | PartDescription | PartType | Customer | AircraftProgram | DrawingNumber |
|------------|-----------------|----------|----------|-----------------|---------------|
| LowerCardanPin | Lower Cardan Pin | Landing Gear | Airbus | A330 | DRW-001 |
| A330Axel | A330 Axels | Landing Gear | Airbus | A330 | DRW-002 |
| RetractionLink | Retraction Link | Landing Gear | Boeing | 737 | DRW-003 |
| UpperCardanPin | Upper Cardan Pin | Landing Gear | Airbus | A330 | DRW-004 |
| | | | | | |
| ...60 more rows to add later... | | | | | |

- [ ] Format as Table: `PartMaster`
- [ ] Save as: `ZnNi_Part_Master.xlsx`
- [ ] Save to: `P:\Process\Plating Shop\ZnNi Industrialization\Data\`

### Step 4.4: Create Stakeholder Distribution List ✅

- [ ] Create new Excel workbook
- [ ] Add stakeholders:

| Name | Email | Role | AlertType |
|------|-------|------|-----------|
| James Fleming | james.fleming@company.com | Project Manager | All |
| Production Lead | prod.lead@company.com | User | Delays Only |
| Quality Manager | quality.mgr@company.com | Approver | Milestones Only |

- [ ] Format as Table: `Stakeholders`
- [ ] Save as: `Stakeholder_Distribution.xlsx`
- [ ] Save to: `P:\Process\Plating Shop\ZnNi Industrialization\Data\`

### Step 4.5: Verify All Excel Files ✅

Check that you have all 4 files in Data folder:

- [ ] `P:\Process\Plating Shop\ZnNi Industrialization\Data\ZnNi_Master_Status.xlsx`
- [ ] `P:\Process\Plating Shop\ZnNi Industrialization\Data\ZnNi_Stage_Definitions.xlsx`
- [ ] `P:\Process\Plating Shop\ZnNi Industrialization\Data\ZnNi_Part_Master.xlsx`
- [ ] `P:\Process\Plating Shop\ZnNi Industrialization\Data\Stakeholder_Distribution.xlsx`

---

## 🐍 PHASE 5: CONFIGURE AND TEST PYTHON FILE MONITOR

### Step 5.1: Update Configuration File ✅

- [ ] Open: `C:\Users\YourName\Documents\ZnNi_Tracker\src\znni_tracker\config.py`
- [ ] Find line: `ROOT_PATH_DEFAULT = ...`
- [ ] Update to YOUR P: drive path:

```python
ROOT_PATH_DEFAULT = r"P:\Process\Plating Shop\ZnNi Industrialization"
```

- [ ] Save file

### Step 5.2: Test File Monitor (Command Line) ✅

- [ ] Open Command Prompt
- [ ] Navigate to project:

```cmd
cd C:\Users\YourName\Documents\ZnNi_Tracker\src\znni_tracker
```

- [ ] Run monitor:

```cmd
python main.py
```

- [ ] You should see:

```text
======================================================================
ZnNi Tracker - File Monitor Starting
======================================================================
Root Path: P:\Process\Plating Shop\ZnNi Industrialization
Polling Interval: 5 minutes
Monitoring 23 stage folders

Monitoring started. Press Ctrl+C to stop.
======================================================================

[2025-10-21 14:30:00] INFO - Checking for new files...
[2025-10-21 14:30:01] INFO - No new files detected
```

- [ ] Leave running and go to next step

### Step 5.3: Upload Test File ✅

While Python monitor is running:

- [ ] Create test Excel file: `Test_Part_123_FAI_20251021_PASS.xlsx`
- [ ] Upload to: `P:\Process\Plating Shop\ZnNi Industrialization\10_First_Article_Inspection_FAI\`
- [ ] Wait 1-2 minutes
- [ ] Check Command Prompt - should see:

```text
[2025-10-21 14:31:00] INFO - Checking for new files...
[2025-10-21 14:31:01] INFO - ✓ Detected 1 new file(s):
[2025-10-21 14:31:01] INFO -   📄 Test_Part_123_FAI_20251021_PASS.xlsx
[2025-10-21 14:31:01] INFO -      Part: Test_Part_123
[2025-10-21 14:31:01] INFO -      Stage: FAI
[2025-10-21 14:31:01] INFO -      Date: 2025-10-21
[2025-10-21 14:31:01] INFO -      Status: PASS
[2025-10-21 14:31:01] INFO -      Folder: 10_First_Article_Inspection_FAI
```

- [ ] If you see this → ✅ File monitor working!
- [ ] Press Ctrl+C to stop monitor

### Step 5.4: Run in Spyder IDE (Production Mode) ✅

**If Spyder IDE is installed**:

- [ ] Open Spyder IDE
- [ ] File → Open → Navigate to: `C:\Users\YourName\Documents\ZnNi_Tracker\src\znni_tracker\main.py`
- [ ] Press F5 (or click green "Run" button)
- [ ] Monitor runs in Spyder console
- [ ] Upload another test file
- [ ] Verify detection in console
- [ ] Leave Spyder open - monitor will run continuously

**If Spyder NOT installed**:

- [ ] Use Command Prompt method from Step 5.2
- [ ] Or install Spyder: `pip install spyder`
- [ ] Or use VS Code with Python extension

---

## 📊 PHASE 6: POWER BI DASHBOARD CREATION

### Step 6.1: Install Power BI Desktop ✅

- [ ] Check if installed: Search Windows for "Power BI Desktop"
- [ ] If NOT installed:
  - [ ] Go to: <https://powerbi.microsoft.com/desktop/>
  - [ ] Click "Download Free"
  - [ ] Run installer
  - [ ] Sign in with organization Microsoft 365 account

### Step 6.2: Connect to Excel Data ✅

- [ ] Open Power BI Desktop
- [ ] Home → Get Data → Excel Workbook
- [ ] Navigate to: `P:\Process\Plating Shop\ZnNi Industrialization\Data\ZnNi_Master_Status.xlsx`
- [ ] Select table: `MasterStatus`
- [ ] Click "Load"
- [ ] Repeat for other Excel files:
  - `ZnNi_Stage_Definitions.xlsx` → `StageDefinitions` table
  - `ZnNi_Part_Master.xlsx` → `PartMaster` table

### Step 6.3: Create Relationships ✅

- [ ] Click "Model" view (left sidebar)
- [ ] Drag `PartNumber` from `MasterStatus` to `PartNumber` in `PartMaster`
- [ ] Drag `CurrentStage` from `MasterStatus` to `StageNumber` in `StageDefinitions`
- [ ] Click "Report" view

### Step 6.4: Build Page 1 - Overview Dashboard ✅

**KPI Cards** (Top Row):

- [ ] Insert → Card
- [ ] Field: `PartNumber` (Count Distinct)
- [ ] Title: "Total Parts"
- [ ] Format: Large number, bold

- [ ] Insert → Card
- [ ] Field: Create measure:

```DAX
CompleteCount = CALCULATE(COUNT(MasterStatus[PartNumber]), MasterStatus[CurrentStage] = 23)
```

- [ ] Title: "Complete Parts"

- [ ] Insert → Card
- [ ] Field: Create measure:

```DAX
PercentComplete = DIVIDE([CompleteCount], COUNT(MasterStatus[PartNumber]), 0) * 100
```

- [ ] Title: "% Complete"
- [ ] Format: Percentage

**Parts by Stage (Bar Chart)**:

- [ ] Insert → Stacked Bar Chart
- [ ] Y-axis: `CurrentStageName`
- [ ] X-axis: `PartNumber` (Count)
- [ ] Title: "Parts by Stage"
- [ ] Sort by Stage Number

**Status Distribution (Donut Chart)**:

- [ ] Insert → Donut Chart
- [ ] Legend: `StatusFlag`
- [ ] Values: `PartNumber` (Count)
- [ ] Title: "Status Distribution"
- [ ] Colors: Green (On Track), Yellow (At Risk), Red (Delayed), Blue (Complete)

**Parts Table** (Bottom):

- [ ] Insert → Table
- [ ] Columns: `PartNumber`, `PartDescription`, `Customer`, `CurrentStageName`, `StatusFlag`, `TargetCompletionDate`
- [ ] Enable conditional formatting:
  - Green background for "On Track"
  - Red background for "Delayed"

### Step 6.5: Build Page 2 - Part Detail Timeline ✅

- [ ] Add new page (click + at bottom)
- [ ] Rename to "Part Detail"

**Gantt Chart** (or Stacked Bar):

- [ ] Insert → Stacked Bar Chart (horizontal)
- [ ] Y-axis: `PartNumber`
- [ ] X-axis: `CurrentStage`
- [ ] Title: "Part Progress Timeline"

**Part Details Table**:

- [ ] Insert → Table
- [ ] Filter: Selected part from chart (enable drill-through)
- [ ] Show all metadata for selected part

### Step 6.6: Build Page 3 - Stage Heatmap ✅

- [ ] Add new page: "Stage Heatmap"
- [ ] Insert → Matrix
- [ ] Rows: `PartNumber`
- [ ] Columns: `StageName` (from StageDefinitions)
- [ ] Values: Create measure:

```DAX
StageStatus = 
IF(
    MasterStatus[CurrentStage] >= RELATED(StageDefinitions[StageNumber]),
    "✓",
    BLANK()
)
```

- [ ] Format: Conditional formatting
  - Green cell if stage complete
  - Gray if not started

### Step 6.7: Add Slicers and Filters ✅

On Overview page:

- [ ] Insert → Slicer → `Customer`
- [ ] Insert → Slicer → `Priority`
- [ ] Insert → Slicer → `StatusFlag`
- [ ] Position on left side

### Step 6.8: Save Report ✅

- [ ] File → Save As
- [ ] Save to: `C:\Users\YourName\Documents\ZnNi_Tracker\`
- [ ] Filename: `ZnNi_Industrialization_Dashboard.pbix`

---

## 🌐 PHASE 7: PUBLISH POWER BI TO SERVICE

### Step 7.1: Publish Dashboard ✅

- [ ] In Power BI Desktop, click "Publish" (top ribbon)
- [ ] Sign in with organization account
- [ ] Select workspace:
  - "My workspace" (for testing)
  - Or your department workspace
- [ ] Click "Select"
- [ ] Wait for upload (1-2 minutes)
- [ ] Click "Open in Power BI" when complete

### Step 7.2: Configure Dataset Refresh ✅

- [ ] Browser opens to Power BI Service
- [ ] Go to workspace → Datasets
- [ ] Find: `ZnNi_Industrialization_Dashboard`
- [ ] Click "..." → Settings
- [ ] Expand "Data source credentials"
- [ ] Click "Edit credentials"
- [ ] Authentication: Windows (or OAuth2)
- [ ] Enter credentials
- [ ] Click "Sign in"

### Step 7.3: Schedule Refresh ✅

- [ ] In same Settings page, scroll to "Scheduled refresh"
- [ ] Toggle ON: "Keep your data up to date"
- [ ] Refresh frequency: Daily
- [ ] Times: 8:00 AM, 2:00 PM, 6:00 PM
- [ ] Time zone: (Your timezone)
- [ ] Click "Apply"

### Step 7.4: Test Refresh ✅

- [ ] Click "Refresh now"
- [ ] Wait 30 seconds
- [ ] Check "Refresh history" → Should show ✅ Success

### Step 7.5: Share Dashboard ✅

- [ ] Go to Reports (not Datasets)
- [ ] Click report name
- [ ] Click "Share"
- [ ] Add stakeholder emails
- [ ] Optional: Allow recipients to share
- [ ] Click "Share"
- [ ] Recipients receive email with link

---

## 📧 PHASE 8: EMAIL ALERTS SETUP (PYTHON)

### Step 8.1: Configure Email Settings ✅

- [ ] Open: `C:\Users\YourName\Documents\ZnNi_Tracker\src\znni_tracker\config.py`
- [ ] Update email settings:

```python
# Email Configuration
EMAIL_ENABLED = True
SMTP_SERVER = "smtp.office365.com"  # or your org's SMTP
SMTP_PORT = 587
SMTP_USERNAME = "your.email@company.com"
SMTP_PASSWORD = "your_password"  # or use environment variable
EMAIL_FROM = "znni.tracker@company.com"
EMAIL_ALERT_RECIPIENTS = [
    "james.fleming@company.com",
    "production.lead@company.com"
]
```

**Security Note**: Never commit passwords to Git. Use environment variable:

```cmd
set ZNNI_EMAIL_PASSWORD=your_password
```

### Step 8.2: Create Email Alert Script ✅

- [ ] Create new file: `C:\Users\YourName\Documents\ZnNi_Tracker\src\znni_tracker\email_alerter.py`
- [ ] Copy this code:

```python
"""
Email Alerter - Sends delay and milestone notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import openpyxl

from config import Config


class EmailAlerter:
    def check_delays(self):
        """Check for delayed parts and send alert email"""
        # Load Master Status Excel
        wb = openpyxl.load_workbook(Config.MASTER_STATUS_FILE)
        ws = wb.active
        
        delayed_parts = []
        today = datetime.now().date()
        
        for row in ws.iter_rows(min_row=2, values_only=False):
            part_number = row[0].value
            target_date = row[6].value  # TargetCompletionDate
            current_stage = row[4].value
            
            if target_date and target_date < today and current_stage < 23:
                delayed_parts.append({
                    'part': part_number,
                    'stage': current_stage,
                    'target': target_date,
                    'days_late': (today - target_date).days
                })
        
        if delayed_parts:
            self.send_delay_alert(delayed_parts)
    
    def send_delay_alert(self, delayed_parts):
        """Send email alert for delayed parts"""
        html = f"""
        <html>
          <body>
            <h2 style="color: red;">⚠️ ZnNi Industrialization - Delayed Parts Alert</h2>
            <p>The following parts are behind schedule:</p>
            <table border="1" style="border-collapse: collapse;">
              <tr style="background-color: #f2f2f2;">
                <th>Part Number</th>
                <th>Current Stage</th>
                <th>Target Date</th>
                <th>Days Late</th>
              </tr>
        """
        
        for part in delayed_parts:
            html += f"""
              <tr>
                <td>{part['part']}</td>
                <td>{part['stage']}</td>
                <td>{part['target']}</td>
                <td style="color: red; font-weight: bold;">{part['days_late']}</td>
              </tr>
            """
        
        html += """
            </table>
            <br>
            <p><a href="https://app.powerbi.com/...">View Dashboard</a></p>
          </body>
        </html>
        """
        
        msg = MIMEMultipart()
        msg['From'] = Config.EMAIL_FROM
        msg['To'] = ", ".join(Config.EMAIL_ALERT_RECIPIENTS)
        msg['Subject'] = f"⚠️ ALERT: {len(delayed_parts)} Parts Delayed - ZnNi Industrialization"
        
        msg.attach(MIMEText(html, 'html'))
        
        # Send email
        server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
        server.starttls()
        server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✉️ Delay alert sent to {len(Config.EMAIL_ALERT_RECIPIENTS)} recipients")
```

### Step 8.3: Schedule Daily Alerts ✅

**Option A: Windows Task Scheduler**

- [ ] Open Task Scheduler (search Windows)
- [ ] Create Basic Task
- [ ] Name: "ZnNi Delay Alerts"
- [ ] Trigger: Daily at 8:00 AM
- [ ] Action: Start a program
  - Program: `python`
  - Arguments: `C:\Users\YourName\Documents\ZnNi_Tracker\src\znni_tracker\email_alerter.py`
- [ ] Finish

**Option B: Add to main.py**

- [ ] Edit `main.py`
- [ ] Add schedule for alerts:

```python
# Schedule delay check daily at 8 AM
schedule.every().day.at("08:00").do(check_delays)
```

### Step 8.4: Test Email Alerts ✅

- [ ] Temporarily change a part's TargetCompletionDate to yesterday in Excel
- [ ] Run: `python email_alerter.py`
- [ ] Check email inbox - should receive alert
- [ ] Change date back after test

---

## 🧪 PHASE 9: END-TO-END TESTING

### Test 9.1: File Detection Test ✅

- [ ] Create test file: `TestPart_FAI_20251021_PASS.xlsx`
- [ ] Upload to: `P:\...\10_First_Article_Inspection_FAI\`
- [ ] Check Python monitor console - should detect within 5 minutes
- [ ] Verify file info logged correctly

### Test 9.2: Excel Update Test ✅

- [ ] Manually update `ZnNi_Master_Status.xlsx`
- [ ] Change `LowerCardanPin` CurrentStage to 12
- [ ] Save Excel file
- [ ] Wait 10 minutes
- [ ] Check Power BI dashboard
- [ ] Verify LowerCardanPin shows Stage 12

### Test 9.3: Dashboard Refresh Test ✅

- [ ] In Power BI Service, click "Refresh now"
- [ ] Wait 30 seconds
- [ ] Open dashboard
- [ ] Verify data matches Excel file

### Test 9.4: Email Alert Test ✅

- [ ] Change a part's status to "Delayed" in Excel
- [ ] Set TargetCompletionDate to yesterday
- [ ] Run delay check (or wait for scheduled run)
- [ ] Check email
- [ ] Verify HTML table shows delayed part

### Test 9.5: Complete Workflow Test ✅

Simulate real usage:

- [ ] **Day 1**: Upload file for LowerCardanPin Stage 10
- [ ] **Day 2**: Verify Python detected file
- [ ] **Day 3**: Manually update Excel with new stage
- [ ] **Day 4**: Verify dashboard shows update
- [ ] **Day 5**: Change to "At Risk" status
- [ ] **Day 6**: Verify alert email received

---

## 📝 PHASE 10: USER DOCUMENTATION

### Step 10.1: Create File Naming Guide ✅

- [ ] Create: `P:\Process\Plating Shop\ZnNi Industrialization\FILE_NAMING_GUIDE.pdf`
- [ ] Content:

```text
FILE NAMING CONVENTION FOR ZnNi INDUSTRIALIZATION

MANDATORY FORMAT:
[PartNumber]_[StageName]_[Date]_[Status].ext

RULES:
1. Part Number: Must match Part Master list (no spaces)
2. Stage Name: Use abbreviation from Stage Definitions
3. Date: YYYYMMDD format (e.g., 20251021)
4. Status: PASS, FAIL, IN_PROGRESS, PENDING (optional)
5. Extension: .xlsx, .pdf, .docx, .csv

EXAMPLES:
✅ LowerCardanPin_FAI_20251021_PASS.xlsx
✅ A330Axel_SaltSpray_20251022_FAIL.pdf
✅ RetractionLink_Training_20251023.docx
✅ UpperCardanPin_SPC_20251024_IN_PROGRESS.xlsx

❌ Test File.xlsx (no part number, no stage, has space)
❌ LowerCardanPin.xlsx (missing stage and date)
❌ Part 123_Stage10.pdf (wrong format, has space)

STAGE ABBREVIATIONS:
FAI - First Article Inspection
SPC - Statistical Process Control
FMEA - Failure Mode Effects Analysis
PFD - Process Flow Diagram
...etc
```

### Step 10.2: Create Quick Reference Card ✅

- [ ] Create one-page PDF with:
  - How to upload evidence file
  - File naming rules
  - Dashboard link
  - Who to contact for issues

### Step 10.3: Train Production Team ✅

- [ ] Schedule 30-minute training session
- [ ] Demonstrate:
  - [ ] How to name files correctly
  - [ ] Where to upload (which stage folder)
  - [ ] How to check dashboard
  - [ ] What alerts mean
- [ ] Provide handout with rules
- [ ] Answer questions

---

## 🔧 PHASE 11: PRODUCTION DEPLOYMENT

### Step 11.1: Run Python Monitor as Service ✅

**Option A: Spyder IDE** (Simple, for testing):

- [ ] Open Spyder
- [ ] Open `main.py`
- [ ] Press F5
- [ ] Minimize Spyder (don't close)
- [ ] Monitor runs continuously

**Option B: Windows Service** (Production):

- [ ] Install `pywin32`: `pip install pywin32`
- [ ] Create Windows Service wrapper
- [ ] Register service
- [ ] Set to auto-start on boot

**Option C: Task Scheduler** (Alternative):

- [ ] Create Task: Run `main.py` at startup
- [ ] Run whether user logged on or not
- [ ] Restart on failure

### Step 11.2: Monitor Health Check ✅

- [ ] Create monitoring checklist:
  - [ ] Check Python console every morning
  - [ ] Verify files being detected
  - [ ] Check for error messages
  - [ ] Verify Excel files updating
  - [ ] Check dashboard refresh history

### Step 11.3: Backup System ✅

- [ ] **Weekly**: Backup Excel files
  - Copy `Data\` folder to: `Data\Backups\YYYY-MM-DD\`
- [ ] **Monthly**: Backup entire P: drive folder
- [ ] **Quarterly**: Export Power BI report (.pbix file)

---

## 🆘 TROUBLESHOOTING

### Issue: Python Monitor Not Detecting Files

**Symptoms**: File uploaded but not showing in console

**Checks**:
- [ ] Is Python script running? (Check Spyder console)
- [ ] Is file in correct folder?
- [ ] Does filename follow naming convention?
- [ ] Is P: drive accessible? (Check in File Explorer)
- [ ] Is file older than 5 minutes? (Script only detects recent files)

**Fix**:
1. Stop Python script
2. Check `config.py` has correct P: drive path
3. Verify 23 folders exist
4. Restart Python script
5. Upload new test file

### Issue: Power BI Not Refreshing

**Symptoms**: Dashboard shows old data

**Checks**:
- [ ] Check scheduled refresh is enabled
- [ ] Check refresh history for errors
- [ ] Verify Excel file paths correct
- [ ] Check data source credentials

**Fix**:
1. Power BI Service → Dataset Settings
2. Data source credentials → Edit credentials
3. Re-enter Windows credentials
4. Test with "Refresh now"

### Issue: Email Not Sending

**Symptoms**: No alert emails received

**Checks**:
- [ ] Check email configuration in `config.py`
- [ ] Verify SMTP server and port
- [ ] Check username/password correct
- [ ] Check firewall not blocking port 587

**Fix**:
1. Test SMTP connection manually
2. Verify organization allows SMTP
3. Use Graph API instead of SMTP (if available)
4. Check spam folder

### Issue: Excel File Locked

**Symptoms**: "Permission denied" when Python tries to update

**Checks**:
- [ ] Is Excel file open in Excel?
- [ ] Does another process have file locked?
- [ ] Do you have write permissions?

**Fix**:
1. Close Excel file
2. Check Task Manager for Excel processes
3. Add retry logic to Python script
4. Use network share permissions troubleshooter

### Issue: Python Import Errors

**Symptoms**: "ModuleNotFoundError" when running script

**Fix**:
```cmd
pip install -r requirements.txt --upgrade
```

Or install specific package:
```cmd
pip install schedule openpyxl pandas msal jinja2
```

---

## ✅ FINAL CHECKLIST - DEPLOYMENT COMPLETE

Before going live, verify:

### Infrastructure
- [ ] 23 stage folders created on P: drive
- [ ] 4 Excel data files created and populated
- [ ] README.txt in each stage folder

### Python Monitor
- [ ] Python 3.12+ installed
- [ ] All dependencies installed
- [ ] Config file updated with correct paths
- [ ] File monitor running continuously (Spyder or service)
- [ ] Test file detected successfully

### Power BI Dashboard
- [ ] Dashboard created with 3 pages
- [ ] Connected to Excel files
- [ ] Published to Power BI Service
- [ ] Scheduled refresh configured (every 10 min)
- [ ] Shared with stakeholders

### Email Alerts
- [ ] Email config updated
- [ ] Alert script tested
- [ ] Daily schedule configured (8 AM)
- [ ] Test alert email received

### Documentation
- [ ] File naming guide created
- [ ] Quick reference card distributed
- [ ] Production team trained

### Testing
- [ ] End-to-end test completed
- [ ] File upload → detection → Excel → dashboard flow works
- [ ] Alert email received for test delay
- [ ] All 4 baseline parts showing correctly

---

## 📞 SUPPORT

### For Issues Contact:

**Technical Issues**:
- Python errors → Check logs in console
- Power BI → Organization BI admin
- P: drive access → IT helpdesk

**Project Questions**:
- Your Name: ___________________
- Your Email: ___________________
- Your Phone: ___________________

### Escalation Path:

1. Check this guide's Troubleshooting section
2. Check Python console logs
3. Contact IT helpdesk
4. Escalate to project manager

---

## 🎉 SUCCESS! SYSTEM IS LIVE

Your ZnNi Industrialization tracking system is now operational:

✅ **Automated** - Python monitors 23 folders 24/7  
✅ **Real-time** - Dashboard updates every 10 minutes  
✅ **Proactive** - Daily email alerts for delays  
✅ **Scalable** - Ready for remaining 60 parts  
✅ **Compliant** - Complete audit trail in Excel

### What Happens Next:

**Week 2**: Monitor usage, fix any issues  
**Week 3**: Add remaining 60 parts  
**Week 4**: Enhance dashboard based on feedback  
**Month 2**: Add advanced features (trends, predictions)

### Success Metrics to Track:

- Files detected per week
- Average detection time
- Dashboard views per day
- Alert accuracy rate
- User adoption rate (% correct file naming)

---

**END OF DEPLOYMENT GUIDE**

Last Updated: October 21, 2025
Version: 1.0 (Corrected)
Project: PROJECT-002 INDUSTRIALIZATION
