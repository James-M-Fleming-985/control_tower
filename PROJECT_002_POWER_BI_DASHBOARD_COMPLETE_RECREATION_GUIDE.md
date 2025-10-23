# PROJECT-002 INDUSTRIALIZATION - Complete Power BI Dashboard Recreation Guide

**Project**: ZnNi Line Industrialization Tracking  
**Purpose**: Recreate the exact Power BI dashboard from Laptop A on Laptop B  
**Created**: October 22, 2025  
**Status**: Complete specification including all missing elements

---

## 📊 DASHBOARD OVERVIEW - WHAT YOU HAD ON LAPTOP A

Your original dashboard had **3 tabs/pages** with the following structure:

### **Tab 1: Overview Dashboard**
- **4 KPI Cards** (top row)
- **1 Bar Chart** (parts by stage)
- **1 Pie/Donut Chart** (status distribution with 4+ statuses)
- **1 Parts Table** (bottom - main data view)
- **3-4 Slicers** (filters on left side)
- **Drill-through enabled** → Click part number to jump to Part Detail tab

### **Tab 2: Part Detail** (Drill-through destination)
- Detailed view for a single selected part
- Shows full stage history
- Timeline/Gantt-style visualization
- All metadata for selected part
- Back button to return to Overview

### **Tab 3: Stage Heatmap**
- Matrix view (parts × stages)
- Color-coded completion status
- Shows which parts completed which stages

---

## 🎯 WHY STATUS VALUES ARE LIMITED (At Risk, Delayed, etc.)

**Issue**: You're only seeing "Not Started" and "In Progress" in the pie chart.

**Root Cause**: The `StatusFlag` field is calculated based on:
1. **Current Stage** vs **Target Completion Date**
2. **Days Behind Schedule** 

**Why "At Risk" and "Delayed" aren't showing**:
- These statuses require **Target Completion Dates** to be populated in your Excel file
- Status logic:
  - **Not Started**: Current Stage = 0 or 1
  - **In Progress**: Current Stage > 0 and no target date OR ahead of schedule
  - **At Risk**: Current Stage < expected stage AND 1-14 days behind target
  - **Delayed**: Current Stage < expected stage AND 15+ days behind target
  - **Complete**: Current Stage = 23

**Solution**: You need to add target completion dates to your Excel data (see Section 7 below).

---

## 📋 PHASE 1: PREREQUISITES & DATA VERIFICATION

### Step 1.1: Verify Excel Data Files Exist

Navigate to: `P:\Process\Plating Shop\ZnNi Industrialization\Data\`

Confirm you have these 4 files:
- [ ] `ZnNi_Master_Status.xlsx` (main status table)
- [ ] `ZnNi_Stage_Definitions.xlsx` (23 stages reference)
- [ ] `ZnNi_Part_Master.xlsx` (64 parts metadata)
- [ ] `Stakeholder_Distribution.xlsx` (optional - for email alerts)

### Step 1.2: Verify Data Columns

Open `ZnNi_Master_Status.xlsx` and verify these columns exist:

**Required Columns**:
- `PartNumber` (Text) - e.g., "LowerCardanPin"
- `PartDescription` (Text) - e.g., "Lower Cardan Pin Assembly"
- `CurrentStage` (Number) - 1 to 23
- `CurrentStageName` (Text) - e.g., "Coating Specification"
- `LastUpdated` (Date) - When status last changed
- `Owner` (Text) - Person responsible
- `Customer` (Text) - Airbus, Boeing, etc.
- `Priority` (Text) - High, Medium, Low
- `TargetCompletionDate` (Date) - **REQUIRED for status calculations**
- `ActualCompletionDate` (Date) - When part finished
- `StatusFlag` (Text) - Calculated field (will be replaced by DAX measure)

**If columns are missing**, add them now before proceeding.

---

## 📊 PHASE 2: POWER BI DESKTOP - DATA IMPORT

### Step 2.1: Open Power BI Desktop

- [ ] Launch Power BI Desktop
- [ ] Sign in with organization account
- [ ] File → New

### Step 2.2: Import Excel Data

**Import Master Status Table**:
- [ ] Home → Get Data → Excel Workbook
- [ ] Navigate to: `P:\Process\Plating Shop\ZnNi Industrialization\Data\ZnNi_Master_Status.xlsx`
- [ ] Check **only** the table: `MasterStatus` (or sheet name)
- [ ] Click "Transform Data" (not "Load" yet)

**Power Query Editor Opens**:
- [ ] Verify columns loaded correctly
- [ ] Check data types:
  - `PartNumber` = Text
  - `CurrentStage` = Whole Number
  - `LastUpdated` = Date
  - `TargetCompletionDate` = Date
  - `Owner` = Text
- [ ] If data types wrong, right-click column header → Change Type
- [ ] Close & Apply

**Import Stage Definitions Table**:
- [ ] Home → Get Data → Excel Workbook
- [ ] Navigate to: `P:\Process\Plating Shop\ZnNi Industrialization\Data\ZnNi_Stage_Definitions.xlsx`
- [ ] Select table: `StageDefinitions`
- [ ] Click "Load" (no transformation needed)

**Import Part Master Table**:
- [ ] Home → Get Data → Excel Workbook
- [ ] Navigate to: `P:\Process\Plating Shop\ZnNi Industrialization\Data\ZnNi_Part_Master.xlsx`
- [ ] Select table: `PartMaster`
- [ ] Click "Load"

### Step 2.3: Create Table Relationships

**Quick Explanation**:
- **`MasterStatus`** = Current status of each part (changes frequently)
- **`PartMaster`** = Permanent details about each part (rarely changes)
- **Duplicated fields** (`PartNumber`, `PartDescription`) = Normal. `PartNumber` links them together.
- **Use fields from `PartMaster`** when building visuals (Customer, Description, Aircraft, etc.)

---

- [ ] Click "Model" view (left sidebar - database icon)

**Relationship 1**: MasterStatus → PartMaster
- [ ] Drag `PartNumber` from `MasterStatus` 
- [ ] Drop on `PartNumber` in `PartMaster`
- [ ] Cardinality: Many-to-One (*:1)

**Relationship 2**: MasterStatus → StageDefinitions  
- [ ] Drag `CurrentStage` from `MasterStatus`
- [ ] Drop on `StageNumber` in `StageDefinitions`
- [ ] Cardinality: Many-to-One (*:1)

- [ ] Click "Report" view

---

## 🎨 PHASE 3: BUILD PAGE 1 - OVERVIEW DASHBOARD

### Step 3.1: Rename Page

- [ ] Right-click page tab (bottom) → Rename
- [ ] Name: `Overview Dashboard`

### Step 3.2: Create DAX Measures (Critical!)

Before creating visuals, create these calculated measures:

**Click "Home" → "New Measure"** and enter each formula:

**Measure 1: Total Parts**
```DAX
TotalParts = DISTINCTCOUNT(MasterStatus[PartNumber])
```

**Measure 2: Complete Parts Count**
```DAX
CompleteCount = CALCULATE(
    COUNTROWS(MasterStatus),
    MasterStatus[CurrentStage] = 23
)
```

**Measure 3: Percentage Complete**
```DAX
PercentComplete = 
VAR TotalParts = DISTINCTCOUNT(MasterStatus[PartNumber])
VAR CompleteParts = CALCULATE(
    COUNTROWS(MasterStatus),
    MasterStatus[CurrentStage] = 23
)
RETURN
    DIVIDE(CompleteParts, TotalParts, 0) * 100
```

**Troubleshooting if this shows 1% instead of correct percentage:**
- Check that `CurrentStage` column in Excel is formatted as **Number** (not Text)
- Verify parts that should be complete have exactly **23** in CurrentStage column (not "23" as text)
- In Power BI Desktop → Home → Refresh to reload Excel data
- Check Data view → Click MasterStatus table → Verify CurrentStage shows numbers without quotes

**Measure 4: In Progress Count**
```DAX
InProgressCount = CALCULATE(
    COUNTROWS(MasterStatus),
    MasterStatus[CurrentStage] > 0,
    MasterStatus[CurrentStage] < 23
)
```

**Measure 5: Status Flag with Target Dates** (THIS IS THE KEY!)
```DAX
StatusCalculated = 
VAR CurrentStageNum = MAX(MasterStatus[CurrentStage])
VAR TargetDate = MAX(MasterStatus[TargetCompletionDate])
VAR Today = TODAY()
VAR DaysToTarget = DATEDIFF(Today, TargetDate, DAY)
VAR ExpectedStage = 
    IF(
        ISBLANK(TargetDate),
        BLANK(),
        INT(23 * (1 - DIVIDE(DaysToTarget, 365, 0)))
    )
VAR StageDifference = ExpectedStage - CurrentStageNum

RETURN
    SWITCH(
        TRUE(),
        CurrentStageNum = 23, "Complete",
        CurrentStageNum = 0, "Not Started",
        ISBLANK(TargetDate), "In Progress",
        StageDifference >= 5, "Delayed",
        StageDifference >= 2, "At Risk",
        "On Track"
    )
```

**Measure 6: Delayed Parts Count**
```DAX
DelayedCount = CALCULATE(
    COUNTROWS(MasterStatus),
    [StatusCalculated] = "Delayed"
)
```

**Measure 7: At Risk Count**
```DAX
AtRiskCount = CALCULATE(
    COUNTROWS(MasterStatus),
    [StatusCalculated] = "At Risk"
)
```

### Step 3.3: Create KPI Cards (Top Row - 4 Cards)

**Card 1: Total Parts**
- [ ] Insert → Card (top toolbar)
- [ ] Drag measure `TotalParts` to Fields
- [ ] Resize card: Width ~250px, Height ~120px
- [ ] Position: Top-left corner
- [ ] Format:
  - [ ] Click "Format" tab (paint roller icon)
  - [ ] Callout value → Font size: 48pt, Bold, Navy Blue
  - [ ] Category label → Text: "Total Parts in Pipeline"
  - [ ] Category label → Font size: 14pt
  - [ ] Background: Light gray (#F0F0F0)
  - [ ] Border: 1px solid #CCCCCC

**Card 2: Complete Parts**
- [ ] Insert → Card
- [ ] Drag measure `CompleteCount` to Fields
- [ ] Position: Next to Card 1 (top row)
- [ ] Format:
  - [ ] Callout value → Font size: 48pt, Bold, Green (#008000)
  - [ ] Category label → Text: "Parts Complete"
  - [ ] Category label → Font size: 14pt
  - [ ] Background: Light green (#E8F5E9)
  - [ ] Border: 1px solid #4CAF50

**Card 3: Percentage Complete**
- [ ] Insert → Card
- [ ] Drag measure `PercentComplete` to Fields
- [ ] Position: Next to Card 2 (top row)
- [ ] Format:
  - [ ] Callout value → Display units: None
  - [ ] Callout value → Value decimal places: 1
  - [ ] Callout value → Font size: 48pt, Bold, Blue (#0066CC)
  - [ ] Category label → Text: "% Complete"
  - [ ] Category label → Font size: 14pt
  - [ ] Background: Light blue (#E3F2FD)
  - [ ] Border: 1px solid #2196F3

**Card 4: In Progress Count**
- [ ] Insert → Card
- [ ] Drag measure `InProgressCount` to Fields (created in Step 3.2 - Measure 4)
- [ ] Position: Next to Card 3 (top row)
- [ ] Format:
  - [ ] Callout value → Font size: 48pt, Bold, Orange (#FF9800)
  - [ ] Category label → Text: "In Progress"
  - [ ] Category label → Font size: 14pt
  - [ ] Background: Light orange (#FFF3E0)
  - [ ] Border: 1px solid #FF9800

### Step 3.4: Create Parts by Stage Bar Chart

- [ ] Insert → Stacked Bar Chart
- [ ] Position: Below KPI cards, left side
- [ ] Size: Width ~500px, Height ~350px

**Configure chart**:
- [ ] Y-axis: Drag `CurrentStageName` from `StageDefinitions` table
- [ ] X-axis: Drag `PartNumber` from `MasterStatus` table
- [ ] X-axis aggregation: Count (Distinct)

**Sort the bars**:
- [ ] Click "..." (More options) on visual
- [ ] Sort by: `StageNumber` (from StageDefinitions)
- [ ] Sort ascending

**Format chart**:
- [ ] Title: "Parts Distribution by Stage"
- [ ] Title font: 16pt, Bold
- [ ] Data labels: On, inside end
- [ ] X-axis title: "Number of Parts"
- [ ] Y-axis title: "Stage"
- [ ] Bar color: Blue gradient or your company color

### Step 3.5: Create Status Distribution Pie Chart

- [ ] Insert → Pie Chart (or Donut Chart if you prefer)
- [ ] Position: To the right of bar chart
- [ ] Size: Width ~400px, Height ~350px

**Configure chart**:
- [ ] Legend: Drag measure `StatusCalculated` (the DAX measure you created in Step 3.2 - Measure 5)
  - **Data source**: This measure reads from `MasterStatus[CurrentStage]` and `MasterStatus[TargetCompletionDate]`
  - **It calculates status dynamically** based on stage progress vs target date
- [ ] Values: Drag `PartNumber` from `MasterStatus` table
- [ ] Values aggregation: Count (Distinct)
  - **This counts how many parts have each status**

**What data it uses**:
- Source: `MasterStatus` table (Excel file on P: drive)
- Reads: `CurrentStage` and `TargetCompletionDate` columns
- Calculates: Status text ("Complete", "On Track", "At Risk", "Delayed", etc.)
- Shows: Count of parts per status

**What updates it when implemented**:
1. **You manually update** the Excel file: `P:\Process\Plating Shop\ZnNi Industrialization\Data\ZnNi_Master_Status.xlsx`
2. Change `CurrentStage` values (e.g., from 5 to 6) as parts progress
3. Power BI **auto-refreshes** data:
   - **Desktop**: Click Home → Refresh button
   - **Power BI Service**: Scheduled refresh (e.g., daily at 7 AM, 1 PM) - configured in Phase 8
4. Donut chart **automatically recalculates** status based on new stage values
5. Chart updates instantly to show new status distribution

**Future automation** (optional - mentioned in deployment guide):
- Python file monitor watches P: drive folders
- Detects new evidence files
- Automatically updates Excel file
- Power BI refreshes on schedule → Dashboard updates

**Format chart**:
- [ ] Title: "Status Distribution"
- [ ] Title font: 16pt, Bold
- [ ] Legend position: Right
- [ ] Data labels: Category, Percentage, Both

**Set Status Colors** (Critical for "At Risk", "Delayed" to show correctly):
- [ ] Click "Format" tab
- [ ] Data colors → Expand
- [ ] Set colors for each status:
  - **Complete**: Blue (#2196F3)
  - **On Track**: Green (#4CAF50)
  - **In Progress**: Gray (#9E9E9E)
  - **At Risk**: Yellow/Orange (#FF9800)
  - **Delayed**: Red (#F44336)
  - **Not Started**: Light Gray (#E0E0E0)

**Important**: If you still only see "Not Started" and "In Progress", this means your Excel file needs target completion dates (see Phase 7 below).

### Step 3.6: Create Parts Table (Bottom)

- [ ] Insert → Table
- [ ] Position: Bottom of page, spanning full width
- [ ] Size: Width ~full page, Height ~300px

**Add columns** (drag fields into "Columns" well):
1. `PartNumber` (from MasterStatus)
2. `PartDescription` (from PartMaster)
3. `Customer` (from PartMaster)
4. `CurrentStage` (from MasterStatus)
5. `CurrentStageName` (from StageDefinitions)
6. Measure: `StatusCalculated` (your DAX measure)
7. `TargetCompletionDate` (from MasterStatus)
8. `Owner` (from MasterStatus)
9. `Priority` (from PartMaster)

**Format table**:
- [ ] Title: "Parts Master List"
- [ ] Enable: Column headers
- [ ] Enable: Totals row (optional)
- [ ] Text size: 11pt
- [ ] Alternate row shading: On

**Add Conditional Formatting** (Status column):
- [ ] Click dropdown on `StatusCalculated` column header
- [ ] Conditional formatting → Background color → Rules
- [ ] Rule 1: If `StatusCalculated` is "Complete" → Blue background (#2196F3), White text
- [ ] Rule 2: If `StatusCalculated` is "On Track" → Green background (#4CAF50), White text
- [ ] Rule 3: If `StatusCalculated` is "In Progress" → Gray background (#9E9E9E), Black text
- [ ] Rule 4: If `StatusCalculated` is "At Risk" → Yellow background (#FFC107), Black text
- [ ] Rule 5: If `StatusCalculated` is "Delayed" → Red background (#F44336), White text

### Step 3.7: Add Slicers (Filters - Left Side)

**Slicer 1: Customer**
- [ ] Insert → Slicer
- [ ] Position: Far left, below title area
- [ ] Field: `Customer` (from PartMaster)
- [ ] Style: Vertical list
- [ ] Size: Width ~150px, Height ~200px

**Slicer 2: Priority**
- [ ] Insert → Slicer
- [ ] Position: Below Customer slicer
- [ ] Field: `Priority` (from PartMaster)
- [ ] Style: Vertical list

**Slicer 3: Status**
- [ ] Insert → Slicer
- [ ] Position: Below Priority slicer
- [ ] Field: Use measure `StatusCalculated`
- [ ] Style: Vertical list

**Slicer 4: Owner** (Optional)
- [ ] Insert → Slicer
- [ ] Position: Below Status slicer
- [ ] Field: `Owner` (from MasterStatus)
- [ ] Style: Dropdown (to save space)

**Format all slicers**:
- [ ] Slicer header: On, 12pt Bold
- [ ] Background: Light gray (#F5F5F5)
- [ ] Border: 1px solid #CCCCCC

### Step 3.8: Enable Drill-Through to Part Detail Page

**⚠️ CRITICAL**: **SKIP THIS STEP FOR NOW!** 

You must complete **Phase 4 first** (create the Part Detail page) before drill-through will work.

**Come back here after completing Phase 4, Step 4.2.**

Once Phase 4 is complete, drill-through will automatically work when you:
- [ ] Right-click on any `PartNumber` in the Parts Table
- [ ] You should see "Drill through" → "Part Detail" option
- [ ] Click it to test

**If drill-through option doesn't appear**, see Troubleshooting Issue 2 below.

---

## 🔍 PHASE 4: BUILD PAGE 2 - PART DETAIL (DRILL-THROUGH)

### Step 4.1: Create New Page

- [ ] Click "+" button at bottom of screen (next to Overview Dashboard tab)
- [ ] Right-click new page → Rename to: `Part Detail`

### Step 4.2: Configure Page as Drill-Through Destination

- [ ] Click blank area of page (not on any visual)
- [ ] Visualizations pane → Drill-through section
- [ ] Drag `PartNumber` field to "Drill-through filters" well
- [ ] This creates a back button automatically
- [ ] Optional: Drag `PartDescription` to add more context

### Step 4.3: Create Part Header (Title with Details)

**Text Box 1: Dynamic Title**
- [ ] Insert → Text box
- [ ] Position: Top-left
- [ ] Text: "Part Detail: [Will be dynamic]"
- [ ] Format: 24pt, Bold, Navy

**Card 1: Part Number**
- [ ] Insert → Card
- [ ] Field: `PartNumber` (from MasterStatus)
- [ ] Position: Top-left below title
- [ ] Size: Small ~150x80px
- [ ] Format: 18pt, Bold

**Card 2: Part Description**
- [ ] Insert → Card
- [ ] Field: `PartDescription` (from PartMaster)
- [ ] Position: Next to Part Number card
- [ ] Size: Medium ~300x80px

**Card 3: Current Stage**
- [ ] Insert → Card
- [ ] Field: `CurrentStageName` (from StageDefinitions)
- [ ] Position: Next to Part Description
- [ ] Size: Medium ~250x80px

**Card 4: Status**
- [ ] Insert → Card
- [ ] Field: Measure `StatusCalculated` (created earlier in Phase 3, Step 3.2 - Measure 5)
- [ ] Position: Next to Current Stage
- [ ] Size: Small ~150x80px
- [ ] Format: Conditional background color based on status
  - [ ] Click Format → Callout value → Background color → fx (Conditional formatting)
  - [ ] Format style: Rules
  - [ ] Rule 1: If value is "Complete" → Blue (#2196F3)
  - [ ] Rule 2: If value is "On Track" → Green (#4CAF50)
  - [ ] Rule 3: If value is "At Risk" → Orange (#FF9800)
  - [ ] Rule 4: If value is "Delayed" → Red (#F44336)
  - [ ] Rule 5: If value is "In Progress" → Gray (#9E9E9E)

### Step 4.4: Create Stage Progress Timeline (Gantt-Style)

**Option A: Stacked Bar Chart (Horizontal)**
- [ ] Insert → Stacked Bar Chart
- [ ] Position: Center of page, below header cards
- [ ] Size: Width ~900px, Height ~400px

**Configure**:
- [ ] Y-axis: `StageName` (from StageDefinitions)
- [ ] X-axis: Create a measure to show progress
- [ ] Legend: Show completed vs remaining stages

**Stage Progress Measure** (create this DAX):
```DAX
StageCompletion = 
IF(
    RELATED(StageDefinitions[StageNumber]) <= MAX(MasterStatus[CurrentStage]),
    "Complete",
    "Pending"
)
```

- [ ] X-axis: Use constant value of 1 (for bar length)
- [ ] Legend: `StageCompletion` measure
- [ ] Colors: Green (Complete), Light Gray (Pending)

**Option B: Matrix Heatmap** (Alternative if bar chart doesn't work)
- [ ] Insert → Matrix
- [ ] Rows: `StageName` (from StageDefinitions)
- [ ] Values: Create a checkmark measure:

```DAX
StageCheck = 
IF(
    RELATED(StageDefinitions[StageNumber]) <= MAX(MasterStatus[CurrentStage]),
    "✓",
    "○"
)
```

- [ ] Conditional formatting: Green for ✓, Gray for ○

### Step 4.5: Create Part Details Table (Optional - Can Skip)

**Note**: This table shows metadata for the ONE selected part. Since you're already showing key details in the cards above, you can **skip this step** if you want a cleaner look.

**If you want to include it** (shows all part details in one place):

- [ ] Insert → Table
- [ ] Position: Bottom of page
- [ ] Size: Full width, ~200px height

**Columns** (mix of both tables - these will show ONE row for the selected part):
1. `Customer` (from PartMaster)
2. `AircraftModel` (from PartMaster)
3. `PartFamily` (from PartMaster)
4. `DrawingNumber` (from PartMaster)
5. `Material` (from PartMaster)
6. `Criticality` (from PartMaster)
7. `Priority` (from PartMaster)
8. `Owner` (from MasterStatus)
9. `TargetCompletionDate` (from MasterStatus)
10. `ActualCompletionDate` (from MasterStatus)
11. `LastUpdated` (from MasterStatus)

**Format**:
- [ ] Title: "Part Details"
- [ ] Font: 11pt
- [ ] Because of drill-through filter, this will only show 1 row (the selected part)

**Alternative**: Replace this table with individual **Card visuals** for each field if you prefer a cleaner dashboard look.

### Step 4.6: Add Back Button Styling

The back button is automatically added when you configure drill-through, but you can format it:

- [ ] Click the back arrow button (top-left of page)
- [ ] Format → Button style
- [ ] Text: "← Back to Overview"
- [ ] Font: 14pt, Bold
- [ ] Color: Blue
- [ ] Background: Light blue (#E3F2FD)

---

## 🔥 PHASE 5: BUILD PAGE 3 - STAGE HEATMAP

### Step 5.1: Create New Page

- [ ] Click "+" button at bottom
- [ ] Rename page to: `Stage Heatmap`

### Step 5.2: Create Title

- [ ] Insert → Text box
- [ ] Text: "Industrialization Stage Heatmap - All Parts"
- [ ] Format: 20pt, Bold, Navy
- [ ] Position: Top-center

### Step 5.3: Create Matrix Visual

- [ ] Insert → Matrix
- [ ] Position: Center of page
- [ ] Size: Fill most of the page (~1200x600px)

**Configure Matrix**:
- [ ] Rows: `PartNumber` (from MasterStatus)
- [ ] Columns: `StageName` (from StageDefinitions)
  - Right-click column → Sort by `StageNumber` ascending
- [ ] Values: Create this DAX measure:

```DAX
StageStatusIcon = 
VAR PartCurrentStage = MAX(MasterStatus[CurrentStage])
VAR ThisStageNumber = MAX(StageDefinitions[StageNumber])
RETURN
    SWITCH(
        TRUE(),
        ThisStageNumber < PartCurrentStage, "✓",
        ThisStageNumber = PartCurrentStage, "▶",
        "○"
    )
```

Alternative measure (if you want color cells instead of icons):
```DAX
StageCompletionPercent = 
VAR PartCurrentStage = MAX(MasterStatus[CurrentStage])
VAR ThisStageNumber = MAX(StageDefinitions[StageNumber])
RETURN
    IF(
        ThisStageNumber <= PartCurrentStage,
        1,
        0
    )
```

### Step 5.4: Format Matrix

**Conditional Formatting**:
- [ ] Click dropdown on Values field
- [ ] Conditional formatting → Background color
- [ ] Format by: Rules
- [ ] Rule 1: If value = "✓" → Green (#4CAF50)
- [ ] Rule 2: If value = "▶" → Blue (#2196F3)
- [ ] Rule 3: If value = "○" → Light Gray (#E0E0E0)

**OR** (if using percentage measure):
- [ ] Conditional formatting → Background color → Color scale
- [ ] Minimum (0): Light Gray (#E0E0E0)
- [ ] Maximum (1): Dark Green (#2E7D32)

**Other Formatting**:
- [ ] Row headers: Bold, 10pt
- [ ] Column headers: Bold, 9pt, Rotated 45° (optional)
- [ ] Values: Center-aligned
- [ ] Grid lines: Light gray
- [ ] Stepped layout: Off (for cleaner look)

### Step 5.5: Add Stage Phase Headers (Optional but Recommended)

Create visual separators for the 5 main phases:

- [ ] Insert → Shape → Rectangle (5 times)
- [ ] Position rectangles above column headers
- [ ] Label each phase:
  - **DESIGN** (Stages 1-4) - Blue background
  - **PROCUREMENT** (Stages 5-8) - Purple background
  - **VALIDATION** (Stages 9-12) - Orange background
  - **PRODUCTION** (Stages 13-19) - Green background
  - **INTEGRATION** (Stages 20-23) - Red background

### Step 5.6: Add Summary Cards

**Card 1: Total Stages Completed (Across All Parts)**
```DAX
TotalStagesCompleted = 
SUMX(
    MasterStatus,
    MasterStatus[CurrentStage]
)
```

**Card 2: Average Progress**
```DAX
AvgProgress = 
AVERAGE(MasterStatus[CurrentStage]) / 23 * 100
```

- [ ] Insert 2 cards at top-right
- [ ] Use these measures
- [ ] Format with appropriate titles

---

## 🎨 PHASE 6: THEME AND FINAL FORMATTING

### Step 6.1: Apply Consistent Theme

- [ ] View → Themes → Browse for themes
- [ ] Choose a professional theme (e.g., "Executive", "Innovate")
- [ ] OR use your company's custom theme if available

**Manual Color Palette** (if not using theme):
- Primary: Navy Blue (#003366)
- Secondary: Light Blue (#4A90E2)
- Success: Green (#4CAF50)
- Warning: Orange (#FF9800)
- Danger: Red (#F44336)
- Background: White (#FFFFFF)
- Text: Dark Gray (#333333)

### Step 6.2: Add Company Logo

- [ ] Insert → Image
- [ ] Browse to your company logo file
- [ ] Position: Top-left or top-right corner of each page
- [ ] Size: Small (~100x50px)
- [ ] Lock aspect ratio

### Step 6.3: Add Report Header (All Pages)

- [ ] Insert → Shape → Rectangle
- [ ] Stretch across top of page
- [ ] Height: ~80px
- [ ] Fill color: Navy Blue (#003366)
- [ ] Bring to front (right-click → Bring to front)

- [ ] Insert → Text box (inside rectangle)
- [ ] Text: "ZnNi Industrialization Dashboard"
- [ ] Font: 24pt, Bold, White
- [ ] Position: Left side of header

- [ ] Insert → Text box (inside rectangle)
- [ ] Text: Use DAX for last refresh:
```DAX
LastRefresh = "Last Updated: " & FORMAT(NOW(), "MM/DD/YYYY h:mm AM/PM")
```
- [ ] Font: 12pt, White
- [ ] Position: Right side of header

**Copy header to all pages**:
- [ ] Select all header elements (Ctrl+Click each)
- [ ] Ctrl+C (Copy)
- [ ] Go to Page 2 → Ctrl+V (Paste)
- [ ] Go to Page 3 → Ctrl+V (Paste)

### Step 6.4: Add Page Navigation Buttons

**On Overview Dashboard page**:
- [ ] Insert → Button → Navigator → Page navigator
- [ ] Format as vertical list or horizontal tabs
- [ ] Position: Bottom of page OR top-right
- [ ] Style: Tabs or buttons

**Alternative** (manual buttons):
- [ ] Insert → Button → Blank
- [ ] Action → Type: Page navigation
- [ ] Destination: Part Detail page
- [ ] Button text: "View Part Details"
- [ ] Repeat for Stage Heatmap page

### Step 6.5: Test Interactivity

- [ ] Click "View" → "Reading view" (or F5)
- [ ] Test slicers - verify they filter all visuals
- [ ] Test drill-through:
  - Right-click a part number in the table
  - Select "Drill through" → "Part Detail"
  - Verify you jump to Part Detail page
  - Click back button - returns to Overview
- [ ] Test page navigation buttons
- [ ] Press Escape to exit Reading view

---

## 💾 PHASE 7: ADD TARGET COMPLETION DATES (FIX STATUS ISSUE)

**This is critical to make "At Risk" and "Delayed" statuses appear!**

### Step 7.1: Open Excel Data File

- [ ] Navigate to: `P:\Process\Plating Shop\ZnNi Industrialization\Data\`
- [ ] Open: `ZnNi_Master_Status.xlsx`

### Step 7.2: Verify TargetCompletionDate Column

- [ ] Find column: `TargetCompletionDate`
- [ ] Check if most cells are blank/empty → This is why you only see "In Progress"

### Step 7.3: Add Sample Target Dates

For each part, add a realistic target completion date. Use this formula as a guide:

**Target Date Calculation** (for parts in progress):
- Current date + (Remaining stages × 2 weeks per stage)

**Example**:
- Part: "LowerCardanPin"
- Current Stage: 8 (out of 23)
- Remaining stages: 23 - 8 = 15 stages
- Time needed: 15 × 2 weeks = 30 weeks
- Target date: Today + 30 weeks = ~July 2026

**Quick method** (for testing):
- [ ] Select `TargetCompletionDate` column
- [ ] For parts in early stages (1-10): Set target to 6 months from now
- [ ] For parts in mid stages (11-18): Set target to 3 months from now
- [ ] For parts in late stages (19-22): Set target to 1 month from now
- [ ] For completed parts (stage 23): Use `ActualCompletionDate`

**Create some "Delayed" examples**:
- [ ] Pick 3-5 parts
- [ ] Set their `TargetCompletionDate` to 2 months ago
- [ ] This will make them show as "Delayed" (red) in the dashboard

**Create some "At Risk" examples**:
- [ ] Pick 3-5 parts
- [ ] Set their `TargetCompletionDate` to 2 weeks ago
- [ ] This will make them show as "At Risk" (yellow/orange)

### Step 7.4: Save Excel File

- [ ] File → Save
- [ ] Close Excel

### Step 7.5: Refresh Power BI Data

- [ ] Return to Power BI Desktop
- [ ] Home → Refresh
- [ ] Wait for data to reload (~30 seconds)
- [ ] Check pie chart - you should now see:
  - Not Started (gray)
  - In Progress (blue/gray)
  - On Track (green)
  - At Risk (yellow/orange)
  - Delayed (red)
  - Complete (blue)

---

## 📊 PHASE 8: SAVE AND PUBLISH

### Step 8.1: Save Power BI File Locally

- [ ] File → Save As
- [ ] Location: `C:\Projects\PROJECT-002-INDUSTRIALIZATION\outputs\`
- [ ] Filename: `ZnNi_Industrialization_Dashboard.pbix`
- [ ] Verify file size (should be 5-20 MB)

### Step 8.2: Publish to Power BI Service

- [ ] Home → Publish (top ribbon)
- [ ] Sign in with organization account (if prompted)
- [ ] Select destination workspace:
  - **My workspace** (for personal testing)
  - **Your department workspace** (for team access)
- [ ] Click "Select"
- [ ] Wait for upload (1-3 minutes)
- [ ] Success message appears with link
- [ ] Click "Open [report name] in Power BI"

### Step 8.3: Configure Dataset Refresh (Power BI Service)

Browser opens to Power BI Service (app.powerbi.com):

- [ ] Navigate to your workspace
- [ ] Find the **Dataset** (not the Report): `ZnNi_Industrialization_Dashboard`
- [ ] Click "..." (More options) → Settings

**Configure Data Source Credentials**:
- [ ] Scroll to "Data source credentials"
- [ ] You'll see path to your P: drive Excel files
- [ ] Click "Edit credentials"
- [ ] Authentication method: **Windows** (if P: drive on network)
- [ ] Enter your Windows credentials
- [ ] OR use **OAuth2** if files are in SharePoint/OneDrive
- [ ] Click "Sign in"

**Configure Scheduled Refresh**:
- [ ] Scroll to "Scheduled refresh"
- [ ] Toggle: "Keep your data up to date" → **On**
- [ ] Refresh frequency: **Daily**
- [ ] Time zone: (Select your timezone)
- [ ] Add refresh times:
  - 7:00 AM
  - 1:00 PM
- [ ] Add email for failure notifications
- [ ] Click "Apply"

**Test Refresh**:
- [ ] Scroll up to "Refresh"
- [ ] Click "Refresh now"
- [ ] Wait 30-60 seconds
- [ ] Check "Refresh history" below
- [ ] Should show: ✅ Completed successfully
- [ ] If error: Check credentials, file paths, network access

### Step 8.4: Share Dashboard with Stakeholders

- [ ] Navigate to your workspace
- [ ] Click on the **Report** (not dataset)
- [ ] Click "Share" button (top toolbar)
- [ ] Enter email addresses:
  - Your manager
  - Team members
  - Stakeholders from Stakeholder_Distribution.xlsx
- [ ] Permissions:
  - [ ] "Allow recipients to share this report" (optional)
  - [ ] "Allow recipients to build content with the data" (optional - only for power users)
  - [ ] "Send an email notification to recipients" (recommended)
- [ ] Add message: "ZnNi Industrialization Dashboard is now live. Click link to view."
- [ ] Click "Grant access"

**Recipients will receive an email** with a direct link to the dashboard.

---

## ✅ PHASE 9: VERIFICATION CHECKLIST

### Visual Verification

**Overview Dashboard Tab**:
- [ ] 4 KPI cards at top (Total Parts, Complete, %, In Progress)
- [ ] Bar chart shows parts by stage (23 stages visible)
- [ ] Pie/Donut chart shows 5-6 status categories (including "At Risk" and "Delayed")
- [ ] Parts table at bottom with all 64 parts
- [ ] 3-4 slicers on left side (Customer, Priority, Status, Owner)
- [ ] Company logo and header visible

**Part Detail Tab**:
- [ ] Back button in top-left
- [ ] Part header cards (Part Number, Description, Stage, Status)
- [ ] Timeline/progress visualization showing stage completion
- [ ] Detailed parts table at bottom
- [ ] Can drill-through from Overview table by right-clicking part number

**Stage Heatmap Tab**:
- [ ] Matrix showing Parts (rows) × Stages (columns)
- [ ] Color-coded cells (green=complete, blue=current, gray=pending)
- [ ] All 64 parts visible
- [ ] All 23 stages visible
- [ ] Phase headers (Design, Procurement, etc.) - optional

### Functional Verification

- [ ] **Slicers work**: Select a customer → all visuals filter correctly
- [ ] **Drill-through works**: Right-click part → Drill through → Part Detail page opens
- [ ] **Back button works**: Click back arrow → returns to Overview
- [ ] **Status colors correct**:
  - Green = On Track
  - Yellow/Orange = At Risk
  - Red = Delayed
  - Blue = Complete
  - Gray = In Progress or Not Started
- [ ] **Data refresh works**: Home → Refresh → data updates within 30 seconds
- [ ] **Published version matches desktop**: Open Power BI Service → report looks identical

---

## 🔧 TROUBLESHOOTING COMMON ISSUES

### Issue 1: Percentage Complete Stuck at 1% (or Wrong Value)

**Cause**: `CurrentStage` column formatted as Text instead of Number in Excel

**Solution**:
1. Open `ZnNi_Master_Status.xlsx`
2. Select entire `CurrentStage` column
3. Right-click → Format Cells → Number (0 decimal places)
4. Verify complete parts show exactly **23** (not "23" with quotes)
5. Save Excel file
6. Power BI Desktop → Home → Refresh
7. Check the percentage - should now calculate correctly

**Alternative check**:
- Power BI → Data view (left sidebar)
- Click on `MasterStatus` table
- Look at `CurrentStage` column
- Numbers should align **right** (if left-aligned, they're text)

### Issue 2: Status Pie Chart Only Shows "Not Started" and "In Progress"

**Cause**: Missing target completion dates in Excel

**Solution**:
1. Open `ZnNi_Master_Status.xlsx`
2. Add dates to `TargetCompletionDate` column
3. Save file
4. Refresh Power BI (Home → Refresh)

### Issue 2: Drill-Through Doesn't Work (No "Drill Through" Option When Right-Clicking)

**Cause**: Part Detail page not created yet OR drill-through field not configured

**Solution - Step by Step**:

**Step 1: Verify Part Detail page exists**
- Look at bottom of Power BI Desktop - do you see a tab called "Part Detail"?
- If NO: Complete Phase 4 first (create the Part Detail page)
- If YES: Continue to Step 2

**Step 2: Configure drill-through on Part Detail page**
- [ ] Click on "Part Detail" page tab (at bottom)
- [ ] Click on blank area of the page (NOT on any visual)
- [ ] Look at right side panel → Visualizations pane
- [ ] Find the "Drill through" section (scroll down if needed)
- [ ] Drag `PartNumber` field from Fields pane into "Drill through filters" well
- [ ] You should see `PartNumber` appear in the drill-through section
- [ ] A back arrow button should automatically appear on the page

**Step 3: Test drill-through**
- [ ] Go back to "Overview Dashboard" page
- [ ] Right-click on ANY part number in the Parts Table
- [ ] You should now see "Drill through" in the context menu
- [ ] Hover over it → You'll see "Part Detail" as an option
- [ ] Click "Part Detail" → Page should switch with that part's data

**Step 4: If still not working**
- [ ] Verify the column name is exactly `PartNumber` (case-sensitive)
- [ ] Check that `PartNumber` exists in BOTH MasterStatus and PartMaster tables
- [ ] Try using a different visual (e.g., create a simple table with just PartNumber)
- [ ] Make sure you're right-clicking on the actual data cell, not the column header

**Alternative: Manual drill-through setup on Overview page**
- [ ] Go to Overview Dashboard page
- [ ] Click on the Parts Table visual
- [ ] Visualizations pane → Filters section
- [ ] Look for "Drill through" at bottom
- [ ] If you see "Part Detail" listed → drill-through is already configured
- [ ] If not: The issue is Step 2 above wasn't completed

### Issue 3: Relationships Not Working (Charts Show Wrong Data)

**Cause**: Table relationships not created

**Solution**:
1. Click "Model" view
2. Verify lines connecting tables:
   - MasterStatus[PartNumber] → PartMaster[PartNumber]
   - MasterStatus[CurrentStage] → StageDefinitions[StageNumber]
3. If missing, drag-drop to create
4. Cardinality should be Many-to-One (*:1)

### Issue 4: DAX Measures Not Calculating

**Cause**: Incorrect table references or syntax

**Solution**:
1. Click "Data" view
2. Select the measure in Fields pane
3. Check formula bar for errors (red underline)
4. Common fixes:
   - Table names must match exactly (case-sensitive)
   - Use square brackets for column names: `[ColumnName]`
   - Verify column exists in table

### Issue 5: Power BI Service Refresh Fails

**Cause**: Credentials not configured or P: drive not accessible

**Solution**:
1. Power BI Service → Workspace → Dataset Settings
2. Data source credentials → Edit credentials
3. If P: drive: Use Windows authentication with network credentials
4. If SharePoint: Use OAuth2
5. Test connection
6. Alternative: Copy Excel files to SharePoint/OneDrive instead of P: drive

### Issue 6: Slicers Don't Filter All Visuals

**Cause**: Visual interactions disabled

**Solution**:
1. Select a visual that's not filtering
2. Format → Edit interactions (top toolbar)
3. Click the slicer
4. Icons appear on all visuals
5. Click filter icon (funnel) for visuals that should be filtered
6. Click "None" (crossed circle) for visuals that shouldn't be filtered

---

## 📝 APPENDIX A: COMPLETE DAX MEASURES REFERENCE

Copy-paste these exactly as shown:

```dax
// Basic Counts
TotalParts = DISTINCTCOUNT(MasterStatus[PartNumber])

CompleteCount = CALCULATE(
    COUNTROWS(MasterStatus),
    MasterStatus[CurrentStage] = 23
)

InProgressCount = CALCULATE(
    COUNTROWS(MasterStatus),
    MasterStatus[CurrentStage] > 0,
    MasterStatus[CurrentStage] < 23
)

NotStartedCount = CALCULATE(
    COUNTROWS(MasterStatus),
    MasterStatus[CurrentStage] = 0
)

// Percentages
PercentComplete = 
DIVIDE([CompleteCount], [TotalParts], 0) * 100

PercentInProgress = 
DIVIDE([InProgressCount], [TotalParts], 0) * 100

// Status Calculation (Main Formula)
StatusCalculated = 
VAR CurrentStageNum = MAX(MasterStatus[CurrentStage])
VAR TargetDate = MAX(MasterStatus[TargetCompletionDate])
VAR Today = TODAY()
VAR DaysToTarget = DATEDIFF(Today, TargetDate, DAY)
VAR TotalDays = DATEDIFF(MIN(MasterStatus[LastUpdated]), TargetDate, DAY)
VAR ExpectedStage = 
    IF(
        ISBLANK(TargetDate) || TotalDays <= 0,
        BLANK(),
        23 * (1 - DIVIDE(DaysToTarget, TotalDays, 0))
    )
VAR StageDifference = ExpectedStage - CurrentStageNum

RETURN
    SWITCH(
        TRUE(),
        CurrentStageNum = 23, "Complete",
        CurrentStageNum = 0, "Not Started",
        ISBLANK(TargetDate), "In Progress",
        StageDifference >= 5, "Delayed",
        StageDifference >= 2, "At Risk",
        "On Track"
    )

// Status Counts
DelayedCount = CALCULATE(
    COUNTROWS(MasterStatus),
    [StatusCalculated] = "Delayed"
)

AtRiskCount = CALCULATE(
    COUNTROWS(MasterStatus),
    [StatusCalculated] = "At Risk"
)

OnTrackCount = CALCULATE(
    COUNTROWS(MasterStatus),
    [StatusCalculated] = "On Track"
)

// Stage Heatmap Measures
StageStatusIcon = 
VAR PartCurrentStage = MAX(MasterStatus[CurrentStage])
VAR ThisStageNumber = MAX(StageDefinitions[StageNumber])
RETURN
    SWITCH(
        TRUE(),
        ThisStageNumber < PartCurrentStage, "✓",
        ThisStageNumber = PartCurrentStage, "▶",
        "○"
    )

StageCompletionPercent = 
VAR PartCurrentStage = MAX(MasterStatus[CurrentStage])
VAR ThisStageNumber = MAX(StageDefinitions[StageNumber])
RETURN
    IF(ThisStageNumber <= PartCurrentStage, 1, 0)

// Summary Measures
TotalStagesCompleted = 
SUMX(MasterStatus, MasterStatus[CurrentStage])

AvgProgress = 
AVERAGE(MasterStatus[CurrentStage]) / 23 * 100

// Last Refresh Display
LastRefresh = 
"Last Updated: " & FORMAT(NOW(), "MM/DD/YYYY h:mm AM/PM")
```

---

## 📝 APPENDIX B: EXCEL COLUMN SPECIFICATIONS

### ZnNi_Master_Status.xlsx (MasterStatus table)

| Column Name | Data Type | Description | Example |
|------------|-----------|-------------|---------|
| PartNumber | Text | Unique identifier | "LowerCardanPin" |
| PartDescription | Text | Full name | "Lower Cardan Pin Assembly" |
| CurrentStage | Number | Stage 1-23 | 8 |
| CurrentStageName | Text | Stage name | "Supplier Qualification" |
| LastUpdated | Date | Last change date | 10/15/2025 |
| Owner | Text | Responsible person | "John Smith" |
| Customer | Text | End customer | "Airbus" |
| Priority | Text | High/Medium/Low | "High" |
| TargetCompletionDate | Date | **REQUIRED** | 06/30/2026 |
| ActualCompletionDate | Date | When finished | 05/15/2026 |
| StatusFlag | Text | Can be blank (DAX calculates) | "On Track" |

### ZnNi_Stage_Definitions.xlsx (StageDefinitions table)

| Column Name | Data Type | Description | Example |
|------------|-----------|-------------|---------|
| StageNumber | Number | 1 to 23 | 1 |
| StageName | Text | Full stage name | "Coating Specification" |
| Phase | Text | Design/Procurement/etc | "Design" |
| TypicalDuration | Number | Days to complete | 14 |
| RequiredDocuments | Text | Evidence needed | "Spec sheet, approval" |

### ZnNi_Part_Master.xlsx (PartMaster table)

| Column Name | Data Type | Description | Example |
|------------|-----------|-------------|---------|
| PartNumber | Text | Unique identifier | "LowerCardanPin" |
| PartDescription | Text | Full name | "Lower Cardan Pin Assembly" |
| PartFamily | Text | Group | "Landing Gear" |
| Customer | Text | End customer | "Airbus" |
| AircraftModel | Text | Model | "A330" |
| DrawingNumber | Text | Engineering drawing | "DRW-001" |
| Material | Text | Material spec | "4340 Steel" |
| Criticality | Text | High/Medium/Low | "High" |
| Priority | Text | High/Medium/Low | "High" |

---

## 📞 SUPPORT AND NEXT STEPS

### If You're Still Missing Elements

**Contact Information**:
- Save your .pbix file before reaching out
- Document specific issues (screenshots help)
- Note which visuals are missing or incorrect

### Enhancement Ideas (Post-Recreation)

Once you have the basic dashboard working:
1. **Add trend charts**: Show progress over time
2. **Create alerts**: Power Automate flows for delays
3. **Mobile layout**: Optimize for phone/tablet viewing
4. **Bookmark views**: Save common filter combinations
5. **What-if parameters**: Scenario planning
6. **Python/R visuals**: Advanced analytics

### Regular Maintenance

- **Weekly**: Review data for accuracy
- **Monthly**: Update target dates as needed
- **Quarterly**: Review DAX measures for optimization
- **Annual**: Redesign dashboard based on user feedback

---

## ✅ COMPLETION CHECKLIST

Mark these off as you complete each section:

- [ ] Phase 1: Prerequisites & data verification
- [ ] Phase 2: Power BI data import (3 Excel tables)
- [ ] Phase 3: Overview Dashboard (4 KPI cards, bar chart, pie chart, table, slicers)
- [ ] Phase 4: Part Detail page (drill-through functionality)
- [ ] Phase 5: Stage Heatmap (matrix view)
- [ ] Phase 6: Theme and formatting (logo, headers, colors)
- [ ] Phase 7: Added target completion dates (fixed status issue)
- [ ] Phase 8: Saved and published to Power BI Service
- [ ] Phase 9: Verified all functionality works
- [ ] Troubleshooting: Resolved any issues
- [ ] Dashboard shared with stakeholders
- [ ] Data refresh scheduled (daily at 7 AM and 1 PM)

---

**Congratulations!** You've recreated your Power BI dashboard with all the original features from Laptop A.

**Document Version**: 1.0  
**Created**: October 22, 2025  
**Last Updated**: October 22, 2025
