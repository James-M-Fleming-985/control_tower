# PROJECT-002 INDUSTRIALIZATION - Complete Setup Guide for Laptop B (Windows)

**Target Environment**: Organization Laptop (Laptop B) - Windows 10/11  
**Source Environment**: Development Laptop A  
**Project**: PROJECT-002 INDUSTRIALIZATION - ZnNi Line Part Tracking  
**Date Created**: October 21, 2025  
**Date Updated**: October 21, 2025 (Corrected)  
**Implementation Type**: Python File Monitor + Excel + Power BI Dashboard

---

## 📋 WHAT THIS PROJECT ACTUALLY DOES

This is a **Python-based automated file monitoring system** with Power BI visualization:

- **Python File Monitor** → Continuously watches P: drive folders for new evidence files (runs in Spyder IDE)
- **23 Industrialization Stages** → Parts progress through Design, Procurement, Validation, Production, System Integration
- **64 Landing Gear Parts** → Track aircraft parts from Cadmium to Zinc Nickel coating conversion
- **Excel Data Storage** → 4 Excel files store part status, stage definitions, master list
- **Power BI Dashboard** → 3-page visual dashboard (Overview, Part Detail, Stage Heatmap)
- **Email Notifications** → Python sends HTML emails for delays and milestone completions

**CRITICAL**: Python is **NOT optional** - it's the core automation engine that drives the entire system!

---

## 🎯 IMPLEMENTATION OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                  YOUR ORGANIZATION LAPTOP B                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  � Python File Monitor (Runs 24/7 in Spyder/Background)    │
│      ↓ watches P: drive                                      │
│  📁 23 Stage Folders (P:\...\ZnNi Industrialization\)       │
│      ↓ updates                                               │
│  � 4 Excel Files (Master Status, Stage Definitions, etc)    │
│      ↓ connected via Power Query (auto)                      │
│  📈 Power BI Dashboard (Web - app.powerbi.com)              │
│      ↓ alerts triggered by                                   │
│  � Python Email Alerter (Daily 8 AM + Hourly Milestones)   │
│      ↓ sends                                                  │
│  � HTML Email Notifications (Outlook/Graph API)             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**File Locations**:
- **Monitored Folders**: `P:\Process\Plating Shop\ZnNi Industrialization\[01-23_Stage_Name]\`
- **Excel Data Files**: `P:\Process\Plating Shop\ZnNi Industrialization\Data\`
- **Power BI Dashboard**: Published to organization Power BI Service
- **Python Code**: `C:\Projects\PROJECT-002-INDUSTRIALIZATION\src\znni_tracker\`

---

## ⚠️ PREREQUISITES - VERIFY BEFORE STARTING

### Access & Permissions Checklist

- [ ] **Windows 10/11** - Organization laptop with admin rights
- [ ] **P: Drive Access** - Mapped network drive with read/write permissions
  - Path: `P:\Process\Plating Shop\ZnNi Industrialization\`
- [ ] **Python 3.12+** - **REQUIRED** (check if Spyder IDE already installed)
  - Check: Open Command Prompt → `python --version`
  - If Spyder installed, Python is already there
- [ ] **Power BI Pro License** - Required for publishing dashboards
  - Check: Open Power BI Service (app.powerbi.com) and verify you can create workspaces
- [ ] **Microsoft Outlook** - Configured and working (for email alerts)
- [ ] **Microsoft Graph API Access** - For sending emails via Python (optional - can use SMTP)
  - Alternative: Use SMTP with Outlook credentials

---

## 📦 PHASE 1: TRANSFER FILES FROM LAPTOP A TO LAPTOP B

### Step 1.1: Create ZIP Package on Laptop A (Development)

On your development laptop:

- [ ] Open terminal/command prompt
- [ ] Navigate to project: 
  ```bash
  cd "/workspaces/professional_excellence/projects/PROJECT-002 INDUSTRIALIZATION"
  ```
- [ ] Create deployment package:
  ```bash
  # If on Linux/Mac (Laptop A):
  zip -r PROJECT-002-DEPLOYMENT.zip \
    src/ \
    tests/ \
    config/ \
    scripts/ \
    FEATURE-002-*/ \
    *.yaml \
    *.md \
    requirements.txt \
    pytest.ini \
    .gitignore
  ```
- [ ] Verify ZIP file created successfully
- [ ] Check ZIP file size (should be < 50 MB)

### Step 1.2: Transfer ZIP to Laptop B

- [ ] **Method 1 - Email**: Email ZIP file to yourself
  - [ ] Send from personal email on Laptop A
  - [ ] Receive on organization email on Laptop B
  - [ ] Download attachment to `C:\Projects\`

- [ ] **Method 2 - USB Drive**: Copy via USB stick
  - [ ] Copy ZIP to USB drive
  - [ ] Plug into Laptop B
  - [ ] Copy to `C:\Projects\`

- [ ] **Method 3 - Cloud Storage**: OneDrive/Google Drive
  - [ ] Upload ZIP on Laptop A
  - [ ] Download ZIP on Laptop B to `C:\Projects\`

### Step 1.3: Extract Files on Laptop B

- [ ] Create project directory:
  ```powershell
  New-Item -ItemType Directory -Path "C:\Projects" -Force
  cd C:\Projects
  ```
- [ ] Extract ZIP file:
  - Right-click ZIP → "Extract All..."
  - Or use PowerShell:
  ```powershell
  Expand-Archive -Path "PROJECT-002-DEPLOYMENT.zip" -DestinationPath "C:\Projects\PROJECT-002-INDUSTRIALIZATION"
  ```
- [ ] Verify extraction:
  ```powershell
  dir "C:\Projects\PROJECT-002-INDUSTRIALIZATION"
  ```
- [ ] You should see folders: `src/`, `tests/`, `config/`, `FEATURE-002-*/`, etc.

---

## 🐍 PHASE 2: PYTHON ENVIRONMENT SETUP (OPTIONAL BUT RECOMMENDED)

**Note**: Python scripts are for validation only. The actual system uses Power BI + Power Automate.

### Step 2.1: Install Python (if not already installed)

- [ ] Check if Python installed:
  ```powershell
  python --version
  ```
- [ ] If NOT installed, download Python 3.11:
  - [ ] Go to: https://www.python.org/downloads/
  - [ ] Download "Windows installer (64-bit)"
  - [ ] Run installer
  - [ ] ✅ **CRITICAL**: Check "Add Python to PATH" during installation
  - [ ] Choose "Install Now"
  - [ ] Wait for installation to complete
- [ ] Verify installation:
  ```powershell
  python --version
  pip --version
  ```
- [ ] Should see Python 3.11.x and pip version

### Step 2.2: Create Virtual Environment

- [ ] Open PowerShell as Administrator
- [ ] Navigate to project:
  ```powershell
  cd "C:\Projects\PROJECT-002-INDUSTRIALIZATION"
  ```
- [ ] Create virtual environment:
  ```powershell
  python -m venv venv
  ```
- [ ] Activate virtual environment:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- [ ] If you get execution policy error:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  # Then try activate again
  .\venv\Scripts\Activate.ps1
  ```
- [ ] Verify activation - prompt should show `(venv)` prefix

### Step 2.3: Install Python Dependencies

- [ ] Ensure virtual environment is activated
- [ ] Install required packages:
  ```powershell
  pip install --upgrade pip
  pip install pandas openpyxl pytest pyyaml python-dotenv
  ```
- [ ] Verify installation:
  ```powershell
  pip list
  ```
- [ ] Should see: pandas, openpyxl, pytest, pyyaml, python-dotenv

### Step 2.4: Test Python Setup

- [ ] Run a quick test:
  ```powershell
  python -c "import pandas; import openpyxl; print('Python environment ready!')"
  ```
- [ ] Should print: "Python environment ready!"

---

## 📂 PHASE 3: SHAREPOINT FOLDER STRUCTURE SETUP

### Step 3.1: Identify Your SharePoint Sites

- [ ] Open Microsoft Edge or Chrome
- [ ] Navigate to your SharePoint site
- [ ] Identify and document these locations:

**Department Area** (where monitored files will be):
- [ ] URL: `_________________________________`
- [ ] Example: `https://yourorg.sharepoint.com/sites/Manufacturing/Shared Documents/Industrialization`

**Power BI Report Area** (where dashboard will be published):
- [ ] URL: `_________________________________`
- [ ] Example: `https://yourorg.sharepoint.com/sites/Manufacturing/Shared Documents/Reports`

### Step 3.2: Create Stage Folders in Department Area

Navigate to your Department SharePoint folder, then:

- [ ] Create main folder: `Part_Industrialization`
- [ ] Inside `Part_Industrialization`, create subfolders:
  - [ ] `01_CONCEPT_FEASIBILITY`
  - [ ] `02_DESIGN_DEVELOPMENT`
  - [ ] `03_PROTOTYPE_VALIDATION`
  - [ ] `04_INDUSTRIALIZATION_TRIALS`
  - [ ] `05_PRODUCTION_LAUNCH`
  - [ ] `06_SERIAL_PRODUCTION`
  - [ ] `ARCHIVE_COMPLETED`

**Folder structure should look like**:
```
Part_Industrialization/
├── 01_CONCEPT_FEASIBILITY/
├── 02_DESIGN_DEVELOPMENT/
├── 03_PROTOTYPE_VALIDATION/
├── 04_INDUSTRIALIZATION_TRIALS/
├── 05_PRODUCTION_LAUNCH/
├── 06_SERIAL_PRODUCTION/
└── ARCHIVE_COMPLETED/
```

### Step 3.3: Document SharePoint Paths

Write down the full paths (you'll need them later):

```
Base Path: _________________________________________________

Stage 1 Path: _________________________________________________

Stage 2 Path: _________________________________________________

Stage 3 Path: _________________________________________________

Stage 4 Path: _________________________________________________

Stage 5 Path: _________________________________________________

Stage 6 Path: _________________________________________________

Archive Path: _________________________________________________
```

---

## 📊 PHASE 4: EXCEL DATA FILES SETUP

### Step 4.1: Create Master Parts List Excel File

- [ ] Open Excel on Laptop B
- [ ] Create new workbook
- [ ] Create a table with these columns:

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| PartNumber | Text | Unique part identifier | P-2024-001 |
| PartName | Text | Descriptive name | Housing Assembly |
| CurrentStage | Number | 1-6 | 3 |
| CurrentStageDate | Date | When entered stage | 2025-10-01 |
| TargetLaunchDate | Date | Expected launch | 2025-12-15 |
| Status | Text | On Track / Delayed / At Risk | On Track |
| LastUpdated | Date | Last modification | 2025-10-21 |
| Owner | Text | Responsible person | John Smith |

- [ ] Format as Excel Table:
  - Select all data including headers
  - Insert → Table
  - Check "My table has headers"
  - Name the table: `PartsData`

### Step 4.2: Add Sample Data

Add at least 5 sample parts to test the system:

- [ ] Part 1: P-2024-001, Housing Assembly, Stage 3
- [ ] Part 2: P-2024-002, Bracket Support, Stage 2
- [ ] Part 3: P-2024-003, Fastener Set, Stage 4
- [ ] Part 4: P-2024-004, Seal Kit, Stage 5
- [ ] Part 5: P-2024-005, Cover Panel, Stage 1

### Step 4.3: Save to SharePoint

- [ ] Save workbook as: `Parts_Industrialization_Data.xlsx`
- [ ] Upload to SharePoint Department Area:
  ```
  [Your Department SharePoint]/Part_Industrialization/Parts_Industrialization_Data.xlsx
  ```
- [ ] Verify file is accessible:
  - [ ] Click file in SharePoint
  - [ ] File opens in Excel Online
  - [ ] Can you edit it?

### Step 4.4: Create Stage Evidence Tracking Sheet

- [ ] Create second Excel workbook
- [ ] Columns:

| Column Name | Description | Example |
|-------------|-------------|---------|
| PartNumber | Part ID | P-2024-001 |
| FileName | Evidence file name | P-2024-001_Stage3_Test_Results.pdf |
| Stage | Stage number | 3 |
| DateUploaded | Upload timestamp | 2025-10-21 14:30 |
| DetectedBy | System/Manual | System |
| FilePath | SharePoint path | /03_PROTOTYPE_VALIDATION/P-2024-001... |

- [ ] Format as table named `StageEvidence`
- [ ] Save as: `Stage_Evidence_Log.xlsx`
- [ ] Upload to SharePoint Department Area

---

## 🎨 PHASE 5: POWER BI DASHBOARD CREATION

### Step 5.1: Install Power BI Desktop

- [ ] Check if Power BI Desktop is installed:
  - Search Windows Start Menu for "Power BI Desktop"
- [ ] If NOT installed:
  - [ ] Go to: https://powerbi.microsoft.com/desktop/
  - [ ] Click "Download Free"
  - [ ] Run installer
  - [ ] Sign in with organization Microsoft 365 account
  - [ ] Wait for installation

### Step 5.2: Create New Power BI Report

- [ ] Open Power BI Desktop
- [ ] Click "Get Data"
- [ ] Select "Excel"
- [ ] Navigate to your SharePoint file:
  - Option A: Click "SharePoint folder" → Enter SharePoint URL
  - Option B: Download Excel file locally first (easier for first time)
- [ ] Select `Parts_Industrialization_Data.xlsx`
- [ ] Check the `PartsData` table
- [ ] Click "Load"

### Step 5.3: Verify Data Import

- [ ] In Power BI Desktop, click "Data" view (left sidebar, table icon)
- [ ] You should see your `PartsData` table
- [ ] Verify all columns appear correctly
- [ ] Check data types are correct (dates as dates, numbers as numbers)

### Step 5.4: Create Visualizations - Page 1: Overview Dashboard

- [ ] Click "Report" view (left sidebar, bar chart icon)
- [ ] Rename page to: "Overview Dashboard"

**Visual 1: Total Parts Card**
- [ ] Insert → Card visual
- [ ] Drag `PartNumber` field to Values
- [ ] Change aggregation to "Count (Distinct)"
- [ ] Resize and position top-left
- [ ] Add title: "Total Parts in Pipeline"

**Visual 2: Parts by Stage (Bar Chart)**
- [ ] Insert → Stacked Bar Chart
- [ ] Axis: `CurrentStage`
- [ ] Values: `PartNumber` (Count)
- [ ] Add title: "Parts by Stage"
- [ ] Position top-center

**Visual 3: Status Breakdown (Donut Chart)**
- [ ] Insert → Donut Chart
- [ ] Legend: `Status`
- [ ] Values: `PartNumber` (Count)
- [ ] Add title: "Status Distribution"
- [ ] Position top-right

**Visual 4: Parts List Table**
- [ ] Insert → Table
- [ ] Add columns: `PartNumber`, `PartName`, `CurrentStage`, `Status`, `TargetLaunchDate`, `Owner`
- [ ] Position bottom, spanning full width
- [ ] Enable sorting

### Step 5.5: Create Visualizations - Page 2: Stage Timeline

- [ ] Add new page (click + at bottom)
- [ ] Rename to: "Stage Timeline"

**Visual 1: Gantt Chart (Timeline)**
- [ ] Insert → Stacked Bar Chart (horizontal)
- [ ] Axis: `PartNumber`
- [ ] Values: `CurrentStageDate` and `TargetLaunchDate`
- [ ] Format as timeline view
- [ ] Add title: "Parts Timeline by Stage"

**Visual 2: Delayed Parts Table**
- [ ] Insert → Table
- [ ] Add filter: `Status` = "Delayed"
- [ ] Columns: `PartNumber`, `PartName`, `TargetLaunchDate`, `Owner`
- [ ] Add conditional formatting (red background)
- [ ] Add title: "⚠️ Delayed Parts Requiring Action"

### Step 5.6: Add Slicers (Filters)

- [ ] On Overview Dashboard page
- [ ] Insert → Slicer
- [ ] Add `CurrentStage` slicer
- [ ] Position left side
- [ ] Insert another Slicer for `Status`
- [ ] Insert another Slicer for `Owner`

### Step 5.7: Format Dashboard

- [ ] Choose theme: View → Themes → (pick professional theme)
- [ ] Add report title: Insert → Text box → "Part Industrialization Dashboard"
- [ ] Format title: Large font, bold, company colors
- [ ] Add your organization logo: Insert → Image
- [ ] Add refresh timestamp: Insert → Text box → Use DAX for last refresh

### Step 5.8: Save Power BI File

- [ ] File → Save As
- [ ] Save to local folder: `C:\Projects\PROJECT-002-INDUSTRIALIZATION\outputs\`
- [ ] Filename: `Part_Industrialization_Dashboard.pbix`
- [ ] Verify file saved successfully

---

## 🌐 PHASE 6: PUBLISH POWER BI TO SHAREPOINT

### Step 6.1: Sign In to Power BI Service

- [ ] In Power BI Desktop, click "Publish" (top ribbon)
- [ ] Sign in with your organization Microsoft 365 account
- [ ] Wait for authentication

### Step 6.2: Select Workspace

- [ ] Choose destination workspace:
  - Option A: "My workspace" (for testing)
  - Option B: Department workspace (for production)
- [ ] Click "Select"
- [ ] Wait for upload (may take 1-2 minutes)

### Step 6.3: Configure Data Refresh (SharePoint Connection)

- [ ] When upload completes, click "Open [report name] in Power BI"
- [ ] Browser opens to Power BI Service (app.powerbi.com)
- [ ] Click "Workspaces" → Your workspace
- [ ] Find the dataset (not the report): `Part_Industrialization_Dashboard`
- [ ] Click "..." (More options) → "Settings"

### Step 6.4: Setup Data Source Credentials

- [ ] Expand "Data source credentials"
- [ ] You'll see your Excel file path
- [ ] Click "Edit credentials"
- [ ] Authentication method: **OAuth2**
- [ ] Click "Sign in"
- [ ] Grant permissions
- [ ] Click "Save"

### Step 6.5: Configure Scheduled Refresh

- [ ] In same Settings page, scroll to "Scheduled refresh"
- [ ] Turn on: "Keep your data up to date"
- [ ] Set refresh frequency:
  - [ ] Daily (recommended)
  - [ ] Times: 8:00 AM, 2:00 PM (or your preference)
- [ ] Time zone: (Select your timezone)
- [ ] Click "Apply"

### Step 6.6: Test Data Refresh

- [ ] In dataset settings, find "Refresh now" section
- [ ] Click "Refresh now"
- [ ] Wait 30 seconds
- [ ] Check "Refresh history" - should show success ✅
- [ ] If error ❌:
  - Check SharePoint file permissions
  - Verify OAuth credentials
  - Check file path is correct

### Step 6.7: Share Dashboard

- [ ] Go back to workspace
- [ ] Click on the **Report** (not dataset)
- [ ] Click "Share" button
- [ ] Add email addresses of stakeholders
- [ ] Permissions:
  - [ ] Allow recipients to share (optional)
  - [ ] Allow recipients to build content (optional)
- [ ] Click "Share"
- [ ] Recipients will get email with link

### Step 6.8: Embed in SharePoint (Optional)

- [ ] Navigate to your SharePoint Power BI report area
- [ ] Edit the page
- [ ] Add web part → "Power BI"
- [ ] Select your report: `Part_Industrialization_Dashboard`
- [ ] Choose page: "Overview Dashboard"
- [ ] Resize web part
- [ ] Publish SharePoint page

---

## 🤖 PHASE 7: POWER AUTOMATE FLOW - FILE MONITORING

### Step 7.1: Access Power Automate

- [ ] Open browser
- [ ] Go to: https://make.powerautomate.com
- [ ] Sign in with organization account
- [ ] Verify you're in correct environment (check top right)

### Step 7.2: Create New Flow

- [ ] Click "+ Create" (left sidebar)
- [ ] Select "Automated cloud flow"
- [ ] Flow name: `Part_Industrialization_File_Monitor`
- [ ] Choose trigger: "When a file is created (SharePoint)"
- [ ] Click "Create"

### Step 7.3: Configure SharePoint Trigger

- [ ] Site Address: Select your SharePoint site from dropdown
- [ ] Library Name: `Shared Documents` (or your document library)
- [ ] Folder: Browse to your `Part_Industrialization` folder
- [ ] Click "New step"

### Step 7.4: Parse File Name (Get Part Number)

- [ ] Action: "Compose"
- [ ] Rename to: "Extract Part Number"
- [ ] Inputs: Use expression:
  ```
  split(triggerOutputs()?['body/{FilenameWithExtension}'], '_')[0]
  ```
- [ ] This extracts "P-2024-001" from "P-2024-001_Stage3_TestResults.pdf"
- [ ] Click "New step"

### Step 7.5: Get Stage Number

- [ ] Action: "Compose"
- [ ] Rename to: "Extract Stage Number"
- [ ] Inputs: Use expression to parse stage from filename
  ```
  if(
    contains(triggerOutputs()?['body/{FilenameWithExtension}'], 'Stage1'), 1,
    if(contains(triggerOutputs()?['body/{FilenameWithExtension}'], 'Stage2'), 2,
    if(contains(triggerOutputs()?['body/{FilenameWithExtension}'], 'Stage3'), 3,
    if(contains(triggerOutputs()?['body/{FilenameWithExtension}'], 'Stage4'), 4,
    if(contains(triggerOutputs()?['body/{FilenameWithExtension}'], 'Stage5'), 5,
    if(contains(triggerOutputs()?['body/{FilenameWithExtension}'], 'Stage6'), 6, 0))))))
  )
  ```
- [ ] Click "New step"

### Step 7.6: Log to Excel (Stage Evidence Tracking)

- [ ] Action: "Add a row into a table" (Excel Online)
- [ ] Location: `SharePoint Site`
- [ ] Document Library: Your library
- [ ] File: Browse to `Stage_Evidence_Log.xlsx`
- [ ] Table: `StageEvidence`
- [ ] Fill in columns:
  - PartNumber: `[Output from Extract Part Number]`
  - FileName: `[File name with extension]`
  - Stage: `[Output from Extract Stage Number]`
  - DateUploaded: `[utcNow()]`
  - DetectedBy: `System`
  - FilePath: `[File path]`
- [ ] Click "New step"

### Step 7.7: Send Email Notification

- [ ] Action: "Send an email (V2)" (Office 365 Outlook)
- [ ] To: (Your email or stakeholder email)
- [ ] Subject: 
  ```
  New Stage Evidence Uploaded - Part: [PartNumber]
  ```
- [ ] Body (use HTML):
  ```html
  <h2>New Stage Evidence Detected</h2>
  <p><strong>Part Number:</strong> [PartNumber from compose]</p>
  <p><strong>Stage:</strong> [Stage from compose]</p>
  <p><strong>File Name:</strong> [File name with extension]</p>
  <p><strong>Upload Time:</strong> [Created time]</p>
  <p><strong>File Location:</strong> [SharePoint link]</p>
  <br>
  <p><a href="[Link to file]">View File in SharePoint</a></p>
  <p><a href="[Link to Power BI]">View Dashboard</a></p>
  ```
- [ ] Click "Save" (top right)

### Step 7.8: Test the Flow

- [ ] Click "Test" button (top right)
- [ ] Select "Manually"
- [ ] Click "Test"
- [ ] Now go to SharePoint and upload a test file:
  - Filename: `P-2024-001_Stage3_Test.pdf`
  - Upload to `Part_Industrialization/03_PROTOTYPE_VALIDATION/`
- [ ] Wait 1-2 minutes
- [ ] Check flow run history - should show success ✅
- [ ] Check your email - should receive notification
- [ ] Check `Stage_Evidence_Log.xlsx` - should have new row

### Step 7.9: Enable Flow

- [ ] Click "Turn on" (top right)
- [ ] Flow is now live and monitoring!

---

## 📧 PHASE 8: POWER AUTOMATE FLOW - SCHEDULE DELAY ALERTS

### Step 8.1: Create Second Flow

- [ ] Go back to Power Automate home
- [ ] Click "+ Create"
- [ ] Select "Scheduled cloud flow"
- [ ] Flow name: `Part_Industrialization_Delay_Alerts`
- [ ] Schedule: **Daily** at **8:00 AM**
- [ ] Click "Create"

### Step 8.2: Get Parts Data from Excel

- [ ] Action: "List rows present in a table" (Excel Online)
- [ ] Location: SharePoint
- [ ] Document Library: Your library
- [ ] File: `Parts_Industrialization_Data.xlsx`
- [ ] Table: `PartsData`
- [ ] Click "New step"

### Step 8.3: Filter for Delayed Parts

- [ ] Action: "Filter array"
- [ ] From: `[value from List rows]`
- [ ] Condition: 
  - `Status` is equal to `Delayed`
- [ ] Click "New step"

### Step 8.4: Check If Any Delays

- [ ] Action: "Condition"
- [ ] Condition: 
  - `length(body('Filter_array'))` is greater than `0`
- [ ] This checks if there are any delayed parts

### Step 8.5: Send Alert Email (If Delays Found)

In the **"If yes"** branch:

- [ ] Action: "Create HTML table"
- [ ] From: `[Output from Filter array]`
- [ ] Columns: Automatic
- [ ] Click "Add an action"

- [ ] Action: "Send an email (V2)"
- [ ] To: (Stakeholder emails - comma separated)
- [ ] Subject: 
  ```
  ⚠️ ALERT: Delayed Parts Requiring Attention - [utcNow('yyyy-MM-dd')]
  ```
- [ ] Body:
  ```html
  <h2 style="color: red;">⚠️ Schedule Delay Alert</h2>
  <p>The following parts are currently delayed and require immediate attention:</p>
  <br>
  [Output from Create HTML table]
  <br>
  <p><strong>Action Required:</strong></p>
  <ul>
    <li>Review delayed parts in the dashboard</li>
    <li>Contact part owners for status update</li>
    <li>Update target launch dates if necessary</li>
  </ul>
  <br>
  <p><a href="[Your Power BI Dashboard Link]">View Full Dashboard</a></p>
  ```
- [ ] Importance: **High**

In the **"If no"** branch:

- [ ] Action: "Send an email (V2)"
- [ ] To: (Your email)
- [ ] Subject: `✅ No Delays - Part Industrialization Status`
- [ ] Body:
  ```
  All parts are on track. No delayed parts detected.
  ```

- [ ] Click "Save"

### Step 8.6: Test Delay Alert Flow

- [ ] Temporarily change a part's status to "Delayed" in Excel
- [ ] Click "Test" → "Manually"
- [ ] Click "Run flow"
- [ ] Wait 1-2 minutes
- [ ] Check email - should receive delay alert
- [ ] Verify HTML table shows the delayed part
- [ ] Change part status back to "On Track"
- [ ] Test again - should receive "No Delays" email

### Step 8.7: Enable Flow

- [ ] Click "Turn on"
- [ ] Flow will now run daily at 8 AM

---

## 🔔 PHASE 9: ADDITIONAL NOTIFICATIONS (OPTIONAL)

### Step 9.1: Teams Notifications (Optional)

If you want alerts in Microsoft Teams:

- [ ] In Power Automate, add action: "Post message in a chat or channel"
- [ ] Team: Select your team
- [ ] Channel: Select channel
- [ ] Message: Same as email body
- [ ] Add after email action

### Step 9.2: Mobile Push Notifications (Optional)

- [ ] Install "Power Automate" mobile app on phone
- [ ] In flow, add action: "Send me a mobile notification"
- [ ] Text: "New stage evidence uploaded for part [PartNumber]"

---

## 🧪 PHASE 10: END-TO-END TESTING

### Test 10.1: File Detection Test

- [ ] Create test PDF file named: `P-TEST-001_Stage2_TestDoc.pdf`
- [ ] Upload to SharePoint: `Part_Industrialization/02_DESIGN_DEVELOPMENT/`
- [ ] Wait 2 minutes
- [ ] Verify:
  - [ ] Email received with file details
  - [ ] New row added to `Stage_Evidence_Log.xlsx`
  - [ ] Flow run history shows success

### Test 10.2: Dashboard Refresh Test

- [ ] Open `Parts_Industrialization_Data.xlsx`
- [ ] Add new part:
  - PartNumber: P-TEST-002
  - PartName: Test Component
  - CurrentStage: 4
  - Status: On Track
  - TargetLaunchDate: [Next month]
- [ ] Save file
- [ ] Go to Power BI Service
- [ ] Manually refresh dataset
- [ ] Open dashboard
- [ ] Verify new part appears in visualizations

### Test 10.3: Delay Alert Test

- [ ] Open `Parts_Industrialization_Data.xlsx`
- [ ] Change one part's Status to "Delayed"
- [ ] Save file
- [ ] Manually run the delay alert flow (Test → Manually)
- [ ] Wait 1 minute
- [ ] Verify:
  - [ ] Email received with delayed part details
  - [ ] HTML table shows correct data
  - [ ] Links work correctly

### Test 10.4: Complete Workflow Test

Simulate real usage:

- [ ] **Day 1**: Upload stage evidence for a part
- [ ] **Day 2**: Update part status in Excel to "At Risk"
- [ ] **Day 3**: Verify dashboard shows updated status
- [ ] **Day 4**: Update to "Delayed" and verify alert received
- [ ] **Day 5**: Complete stage and update to next stage

### Test 10.5: Multiple Files Test

- [ ] Upload 5 files at once to different stage folders
- [ ] Each should trigger separate flow runs
- [ ] Each should generate separate email
- [ ] All should be logged in Excel

---

## 📝 PHASE 11: DOCUMENTATION FOR YOUR TEAM

### Step 11.1: Create User Guide

- [ ] Create Word document: `Part_Industrialization_User_Guide.docx`
- [ ] Include:
  - [ ] How to access dashboard
  - [ ] How to upload stage evidence (file naming convention!)
  - [ ] How to update part status in Excel
  - [ ] What alerts mean and how to respond
  - [ ] Who to contact for issues

### Step 11.2: Document File Naming Convention

**CRITICAL**: Everyone must follow this:

```
Format: [PartNumber]_Stage[N]_[Description].[ext]

Examples:
✅ P-2024-001_Stage3_TestResults.pdf
✅ P-2024-002_Stage2_DesignDrawing.dwg
✅ P-2024-003_Stage4_TrialReport.xlsx

❌ TestResults_P-2024-001.pdf  (part number not first)
❌ P-2024-001-Stage3.pdf  (missing underscore)
❌ 2024-001_Stage3_Test.pdf  (missing P- prefix)
```

### Step 11.3: Create Quick Reference

- [ ] Create one-page PDF with:
  - SharePoint folder structure
  - File naming rules
  - Dashboard link
  - Support contact
  - Emergency escalation

### Step 11.4: Record Video Walkthrough (Optional)

- [ ] Use Zoom/Teams to record screen
- [ ] Show:
  - How to upload file
  - How to update Excel
  - How to view dashboard
  - What happens when alerts trigger
- [ ] Upload to SharePoint

---

## 🔧 PHASE 12: MAINTENANCE & MONITORING

### Step 12.1: Weekly Checks

Set calendar reminders to check:

- [ ] **Monday 9 AM**: Review flow run history (both flows)
- [ ] **Wednesday 9 AM**: Check Excel data quality
- [ ] **Friday 9 AM**: Review dashboard for delayed parts

### Step 12.2: Monthly Tasks

- [ ] Review and archive completed parts
- [ ] Update stakeholder email list in flows
- [ ] Check Power BI dataset refresh history
- [ ] Review SharePoint storage usage
- [ ] Update user guide if process changes

### Step 12.3: Monitor Flow Health

- [ ] Go to Power Automate portal
- [ ] Check "My flows"
- [ ] Look for error indicators (red icons)
- [ ] Review failed runs and fix issues

### Step 12.4: Backup Important Files

Monthly backup:

- [ ] Download `Parts_Industrialization_Data.xlsx`
- [ ] Download `Stage_Evidence_Log.xlsx`
- [ ] Export Power BI report (.pbix file)
- [ ] Export Power Automate flows (Export → Package)
- [ ] Store backups in separate SharePoint folder or OneDrive

---

## 🆘 TROUBLESHOOTING GUIDE

### Issue: Flow Not Triggering

**Symptoms**: File uploaded but no email received

Checks:
- [ ] Is flow turned on? (Check in Power Automate)
- [ ] Is file in correct SharePoint folder?
- [ ] Does filename follow naming convention?
- [ ] Check flow run history for errors
- [ ] Verify SharePoint permissions

**Fix**:
```
1. Go to Power Automate → My flows
2. Find flow → Click name → Click "Edit"
3. Test connection to SharePoint
4. Re-save flow
5. Upload test file again
```

### Issue: Power BI Not Refreshing

**Symptoms**: Dashboard shows old data

Checks:
- [ ] Check scheduled refresh is enabled
- [ ] Check refresh history for errors
- [ ] Verify SharePoint file permissions
- [ ] Verify OAuth credentials still valid

**Fix**:
```
1. Power BI Service → Dataset Settings
2. Data source credentials → Edit credentials
3. Re-authenticate with OAuth2
4. Test with "Refresh now"
```

### Issue: Email Not Sending

**Symptoms**: Flow runs successfully but no email

Checks:
- [ ] Check spam/junk folder
- [ ] Verify email address is correct
- [ ] Check Outlook connection in flow
- [ ] Verify organization email policies allow automated emails

**Fix**:
```
1. Power Automate → My flows → Edit flow
2. Find "Send email" action
3. Click "..." → Delete action
4. Add new "Send an email" action
5. Re-configure and save
```

### Issue: Excel Table Not Found

**Symptoms**: Flow fails with "Table not found" error

Checks:
- [ ] Excel file is actually an Excel file (.xlsx not .xls)
- [ ] Table is properly formatted (Insert → Table)
- [ ] Table has correct name (check in Excel: Table Design → Table Name)
- [ ] File path in flow is correct

**Fix**:
```
1. Open Excel file
2. Select data range
3. Insert → Table → Check "My table has headers"
4. Table Design tab → Rename table to expected name
5. Save and close
6. Test flow again
```

### Issue: Permission Denied

**Symptoms**: "Access denied" or "Forbidden" errors

Checks:
- [ ] Do you have edit permissions on SharePoint files?
- [ ] Is file checked out by someone else?
- [ ] Are Power Automate connections authenticated?

**Fix**:
```
1. SharePoint → Check file isn't checked out
2. Power Automate → Data → Connections
3. Find SharePoint connection → Click "..." → Fix connection
4. Re-authenticate
```

### Issue: Python Scripts Won't Run

**Symptoms**: Import errors or "module not found"

Checks:
- [ ] Virtual environment activated? (see `(venv)` in prompt)
- [ ] Packages installed in virtual environment?
- [ ] Using correct Python version?

**Fix**:
```powershell
# Activate venv
cd C:\Projects\PROJECT-002-INDUSTRIALIZATION
.\venv\Scripts\Activate.ps1

# Reinstall packages
pip install --upgrade pip
pip install -r requirements.txt

# Test
python -c "import pandas; print('OK')"
```

---

## 📞 SUPPORT & CONTACTS

### Technical Issues

- **Power BI Issues**: Contact your IT helpdesk or Power BI admin
- **SharePoint Access**: Contact SharePoint site administrator
- **Power Automate**: Contact Microsoft 365 admin

### Project Questions

- **Your Name**: _______________________
- **Your Email**: _______________________
- **Your Phone**: _______________________

### Escalation

If critical issue affecting multiple users:
1. Email your manager
2. CC: IT helpdesk
3. Subject: "URGENT: Part Industrialization System Issue"

---

## ✅ FINAL VERIFICATION CHECKLIST

Before considering deployment complete:

### System Functionality
- [ ] Power BI dashboard displays data correctly
- [ ] Dashboard refreshes on schedule
- [ ] File upload triggers monitoring flow
- [ ] Emails are received within 2 minutes of file upload
- [ ] Delay alerts run daily at scheduled time
- [ ] All links in emails work correctly
- [ ] SharePoint folders organized correctly

### Data Quality
- [ ] Excel files have correct structure
- [ ] Sample data loaded and displays correctly
- [ ] Table names are correct
- [ ] File naming convention documented
- [ ] Data types correct (dates, numbers, text)

### Access & Permissions
- [ ] All stakeholders can access dashboard
- [ ] Stakeholders can edit Excel files
- [ ] Stakeholders can upload to SharePoint folders
- [ ] Email recipients receiving alerts

### Documentation
- [ ] User guide created and shared
- [ ] File naming convention documented
- [ ] Quick reference available
- [ ] Support contacts documented
- [ ] Backup procedure documented

### Training
- [ ] Key users trained on dashboard
- [ ] Key users trained on file upload process
- [ ] Key users trained on Excel updates
- [ ] Support process communicated

---

## 🎉 DEPLOYMENT COMPLETE!

Congratulations! Your Part Industrialization monitoring system is now live.

### What You've Built:

✅ **Automated File Monitoring** - SharePoint folders watched 24/7  
✅ **Real-Time Alerts** - Email notifications within minutes  
✅ **Visual Dashboard** - Power BI insights accessible anywhere  
✅ **Schedule Tracking** - Daily delay alerts keep projects on track  
✅ **Evidence Logging** - Complete audit trail of all uploads  

### Next Steps:

1. **Week 1**: Monitor closely, fix any issues
2. **Week 2**: Gather user feedback, make adjustments
3. **Week 3**: Train additional users
4. **Week 4**: Review and optimize

### Success Metrics (Track These):

- Number of files processed per week
- Average time from upload to email notification
- Number of delay alerts sent
- Dashboard views per week
- User adoption rate

---

## 📚 APPENDIX A: FILE NAMING STANDARDS (DETAILED)

### Standard Format

```
[PartNumber]_Stage[N]_[Description]_[YYYYMMDD].[extension]
```

### Component Breakdown

| Component | Required | Format | Example |
|-----------|----------|--------|---------|
| PartNumber | ✅ Yes | P-YYYY-NNN | P-2024-001 |
| Stage | ✅ Yes | Stage[1-6] | Stage3 |
| Description | ✅ Yes | No spaces or special chars | TestResults |
| Date | ⚪ Optional | YYYYMMDD | 20251021 |
| Extension | ✅ Yes | Standard file ext | .pdf, .xlsx, .docx |

### Valid Examples

```
✅ P-2024-001_Stage1_ConceptDrawing.pdf
✅ P-2024-002_Stage3_PrototypeTest_20251021.xlsx
✅ P-2024-003_Stage5_LaunchChecklist.docx
✅ P-2024-004_Stage2_DesignReview.pptx
```

### Invalid Examples (Will NOT Trigger Alerts)

```
❌ TestResults.pdf (no part number)
❌ P-2024-001_Test.pdf (no stage)
❌ 2024-001_Stage3_Test.pdf (wrong part number format)
❌ P-2024-001 Stage3 Test.pdf (spaces instead of underscores)
❌ P-2024-001_StageThree_Test.pdf (stage must be number)
```

---

## 📚 APPENDIX B: PYTHON VALIDATION SCRIPTS (OPTIONAL USE)

The Python code in this project is for **validation and testing only**. The actual system runs on Power Platform.

### When to Use Python Scripts

- ✅ Validate Excel file structure before upload
- ✅ Test file naming convention compliance
- ✅ Generate test data for system testing
- ❌ Do NOT use for production automation (use Power Automate instead)

### Available Scripts

Located in `C:\Projects\PROJECT-002-INDUSTRIALIZATION\`

1. **`execute_requirement.py`** - Run TDD tests
2. **`tests/`** - Unit tests for validation logic
3. **`src/`** - Core validation modules

### Running Tests

```powershell
# Activate virtual environment
cd C:\Projects\PROJECT-002-INDUSTRIALIZATION
.\venv\Scripts\Activate.ps1

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_file_detection.py -v
```

---

## 📚 APPENDIX C: POWER BI DAX FORMULAS

### Useful Calculated Columns

Add these in Power BI Desktop → Data view:

**Days Until Launch**:
```DAX
DaysUntilLaunch = DATEDIFF([CurrentStageDate], [TargetLaunchDate], DAY)
```

**Is Delayed**:
```DAX
IsDelayed = IF([Status] = "Delayed", 1, 0)
```

**Stage Name**:
```DAX
StageName = 
SWITCH([CurrentStage],
    1, "Concept",
    2, "Design",
    3, "Prototype",
    4, "Trials",
    5, "Launch",
    6, "Production",
    "Unknown"
)
```

**Risk Level**:
```DAX
RiskLevel = 
SWITCH(TRUE(),
    [DaysUntilLaunch] < 0, "Overdue",
    [DaysUntilLaunch] < 7, "Critical",
    [DaysUntilLaunch] < 30, "Warning",
    "On Track"
)
```

---

## 📚 APPENDIX D: POWER AUTOMATE EXPRESSIONS REFERENCE

### Common Expressions

**Current Date/Time**:
```
utcNow()
```

**Format Date**:
```
formatDateTime(utcNow(), 'yyyy-MM-dd HH:mm')
```

**Get Filename Without Extension**:
```
replace(triggerOutputs()?['body/{FilenameWithExtension}'], '.pdf', '')
```

**Split String**:
```
split(triggerOutputs()?['body/{FilenameWithExtension}'], '_')
```

**String Contains Check**:
```
contains(triggerOutputs()?['body/{FilenameWithExtension}'], 'Stage3')
```

**Array Length**:
```
length(body('Filter_array'))
```

---

## 📚 APPENDIX E: EXCEL TABLE SETUP DETAILED GUIDE

### Creating Proper Excel Tables

1. **Enter Data**:
   - Row 1: Column headers
   - Row 2+: Data rows

2. **Format as Table**:
   - Select all cells (Ctrl+A)
   - Home → Format as Table → Choose style
   - Check "My table has headers"
   - Click OK

3. **Name the Table**:
   - Click anywhere in table
   - Table Design tab appears
   - Change "Table Name" field
   - Use names without spaces: `PartsData` not `Parts Data`

4. **Verify Table**:
   - Formulas → Name Manager
   - Should see your table name listed
   - Type should be "Table"

### Table Maintenance

- **Add Rows**: Click last cell, press Tab
- **Add Columns**: Table Design → Resize Table
- **Delete Rows**: Right-click row → Delete Table Rows
- **Sort**: Click dropdown arrow in header

---

## 🔄 VERSION HISTORY

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-21 | Initial deployment guide created | [Your Name] |

---

**END OF DEPLOYMENT GUIDE**

This guide was generated for PROJECT-002 INDUSTRIALIZATION deployment from Development Laptop A to Organization Laptop B (Windows environment) with Power BI, SharePoint, and Power Automate integration.

For questions or issues, refer to the Troubleshooting section or contact your IT support team.
