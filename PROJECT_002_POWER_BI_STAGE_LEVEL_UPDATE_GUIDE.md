# PROJECT-002 POWER BI STAGE-LEVEL GRANULARITY UPDATE GUIDE

**Project**: ZnNi Line Industrialization Tracking System  
**Update Type**: Stage-Level Target Date Tracking  
**Excel Changes**: Columns I to BC (Stage Targets + Yes/No + Final Target Date)  
**Created**: October 30, 2025  
**Purpose**: Enable Power BI to detect stage-level status (Late, On Track, Delayed, At Risk)

---

## 📊 WHAT CHANGED IN EXCEL

### Previous Structure (Single Target Date)
- **Old**: One column for `TargetCompletionDate` (single date for entire part)
- **Power BI Used**: Simple comparison of CurrentStage vs. TargetCompletionDate

### New Structure (Stage-Level Granularity)
- **Columns I to BB**: Stage-specific target dates and completion status
- **Column BC**: Final `TargetCompletionDate` (overall project completion)
- **Pattern**: Each stage has TWO columns:
  1. Target Date column (e.g., "Stage 01 Target")
  2. Yes/No completion column (e.g., "Stage 01 Complete")

**Example Excel Layout**:
```
| Col I: Stage 01 Target | Col J: Stage 01 Complete | Col K: Stage 02 Target | Col L: Stage 02 Complete | ... | Col BC: Target Completion Date |
|------------------------|---------------------------|------------------------|---------------------------|-----|--------------------------------|
| 2025-10-15            | Yes                       | 2025-10-22            | Yes                       | ... | 2025-11-30                    |
| 2025-10-20            | No                        | 2025-10-25            | No                        | ... | 2025-12-15                    |
```

---

## 🎯 POWER BI UPDATE OBJECTIVES

1. **Load New Columns** - Import all stage target dates and completion flags
2. **Unpivot Stage Data** - Transform wide format to long format for analysis
3. **Create Status Measures** - Detect Late, On Track, Delayed, At Risk per stage
4. **Update Visuals** - Show stage-level timeline with color-coded status
5. **Maintain Compatibility** - Keep existing overall dashboard working

---

## 📋 STEP-BY-STEP IMPLEMENTATION

### PHASE 1: BACKUP CURRENT POWER BI FILE

**Before making ANY changes**:

1. **Close Power BI Desktop** if open
2. **Navigate to**: `C:\Users\YourName\Documents\ZnNi_Tracker\`
3. **Copy File**: `ZnNi_Industrialization_Dashboard.pbix`
4. **Paste As**: `ZnNi_Industrialization_Dashboard_BACKUP_20251030.pbix`
5. **Verify backup** exists before proceeding

---

### PHASE 2: REFRESH DATA SOURCE (GET NEW COLUMNS)

#### Step 2.1: Open Power BI and Refresh

1. **Open**: `ZnNi_Industrialization_Dashboard.pbix`
2. **Home Tab** → Click **Refresh**
3. **Wait** for refresh to complete (should see new columns I-BC)

#### Step 2.2: Verify New Columns Loaded

1. Click **Transform Data** (Power Query Editor opens)
2. Select **MasterStatus** table in left panel
3. **Scroll right** to verify you see:
   - Column I: `Stage 01 Target` (or similar name)
   - Column J: `Stage 01 Complete` (Yes/No)
   - Column K: `Stage 02 Target`
   - Column L: `Stage 02 Complete`
   - ... (continuing pattern)
   - Column BC: `Target Completion Date` (final overall date)

4. **IMPORTANT**: Note the exact column names from your Excel file (might be slightly different)

---

### PHASE 3: CREATE UNPIVOTED STAGE TABLE

To analyze stage-level data, we need to transform the wide format (each stage = 2 columns) into a long format (one row per part per stage).

#### Step 3.1: Duplicate MasterStatus Table

1. In **Power Query Editor**, right-click **MasterStatus** table
2. Select **Duplicate**
3. Rename duplicate to: **`StageProgress`**

#### Step 3.2: Remove Non-Stage Columns

1. Select **StageProgress** table
2. **Right-click** on columns A-H (PartNumber, Description, Customer, etc.)
3. Select **"Remove Other Columns"** to keep ONLY stage columns (I-BC)
4. You should now see only:
   - Stage 01 Target, Stage 01 Complete
   - Stage 02 Target, Stage 02 Complete
   - ... 
   - Stage 23 Target, Stage 23 Complete
   - Target Completion Date

#### Step 3.3: Add PartNumber Reference Back

1. Click **Add Column** tab
2. Click **Custom Column**
3. **Column Name**: `PartNumber`
4. **Formula**:
```M
= MasterStatus[PartNumber]{[Index]}
```
5. Click **OK**

**Alternative (Easier Method)**:
1. Delete the duplicate table
2. Right-click **MasterStatus** again → **Reference** (instead of Duplicate)
3. Rename to **StageProgress**
4. Now continue with unpivot...

#### Step 3.4: Unpivot Stage Target Dates

1. Select ONLY the **Target Date columns** (Stage 01 Target, Stage 02 Target, ..., Stage 23 Target)
   - Hold **Ctrl** and click each "Target" column header
   - **Do NOT select the "Complete" columns yet**

2. **Transform Tab** → Click **Unpivot Columns**

3. You should now see three columns:
   - `Attribute` (contains "Stage 01 Target", "Stage 02 Target", etc.)
   - `Value` (contains the target dates)
   - Plus all the "Complete" columns still there

4. **Rename columns**:
   - Right-click `Attribute` → Rename to: `StageTargetName`
   - Right-click `Value` → Rename to: `StageTargetDate`

#### Step 3.5: Extract Stage Number

1. Select **StageTargetName** column
2. **Add Column Tab** → **Extract** → **Text Before Delimiter**
3. Delimiter: ` Target`
4. Click **OK**
5. Rename new column to: `StageName`

6. **Add another Custom Column**:
   - Name: `StageNumber`
   - Formula:
```M
= Number.From(Text.Middle([StageName], 6, 2))
```
   This extracts "01" from "Stage 01" and converts to number 1

#### Step 3.6: Add Completion Status Column

Now we need to match each stage's target date with its Yes/No completion status.

1. **Add Custom Column**
2. **Name**: `StageComplete`
3. **Formula**:
```M
= Table.Column(#"Previous Step", [StageName] & " Complete"){0}
```

**Alternative Manual Approach**:
If the formula above doesn't work, we need a different strategy:

1. **Duplicate the StageProgress table** → Name it `StageProgress_Temp`
2. In `StageProgress_Temp`:
   - Select ONLY the "Complete" columns (Stage 01 Complete, Stage 02 Complete, etc.)
   - **Unpivot** these columns
   - Rename to `StageCompleteName` and `StageComplete`
   - Extract `StageNumber` same way as before

3. **Merge Tables**:
   - Go back to main `StageProgress` table
   - **Home Tab** → **Merge Queries**
   - Match on: `StageNumber` and `PartNumber`
   - Expand the `StageComplete` column from the merged table
   - Delete the temp table

#### Step 3.7: Clean Up and Set Data Types

1. **Remove unnecessary columns**:
   - Keep: `PartNumber`, `StageNumber`, `StageName`, `StageTargetDate`, `StageComplete`
   - Remove: `StageTargetName`, any other intermediate columns

2. **Set Data Types**:
   - `PartNumber`: Text
   - `StageNumber`: Whole Number
   - `StageName`: Text
   - `StageTargetDate`: Date
   - `StageComplete`: Text (Yes/No)

3. Click **Close & Apply**

---

### PHASE 4: CREATE RELATIONSHIPS

Back in the **Model View** (left sidebar icon):

#### Step 4.1: Link StageProgress to StageDefinitions

1. **Drag** `StageNumber` from **StageProgress** table
2. **Drop** onto `StageNumber` in **StageDefinitions** table
3. **Relationship Settings**:
   - Cardinality: Many to One (*:1)
   - Cross-filter direction: Single
   - Make this relationship active: ✓

#### Step 4.2: Link StageProgress to MasterStatus

1. **Drag** `PartNumber` from **StageProgress** table
2. **Drop** onto `PartNumber` in **MasterStatus** table
3. **Relationship Settings**:
   - Cardinality: Many to One (*:1)
   - Cross-filter direction: Both
   - Make this relationship active: ✓

---

### PHASE 5: CREATE DAX MEASURES FOR STAGE STATUS

Click on **Data View** (table icon) or **Report View**, then:

#### Step 5.1: Create Status Detection Measure

**Home Tab** → **New Measure**

```DAX
StageStatus = 
VAR CurrentDate = TODAY()
VAR IsComplete = SELECTEDVALUE(StageProgress[StageComplete])
VAR TargetDate = SELECTEDVALUE(StageProgress[StageTargetDate])
VAR DaysUntilDue = TargetDate - CurrentDate

RETURN
    SWITCH(
        TRUE(),
        IsComplete = "Yes", "Complete",
        DaysUntilDue < 0, "Late",
        DaysUntilDue <= 7, "At Risk",
        DaysUntilDue > 7, "On Track",
        "Unknown"
    )
```

#### Step 5.2: Create Status Color Measure

```DAX
StatusColor = 
VAR Status = [StageStatus]
RETURN
    SWITCH(
        Status,
        "Complete", "#28A745",    // Green
        "On Track", "#4A90E2",    // Blue
        "At Risk", "#FFC107",     // Yellow/Amber
        "Late", "#DC3545",        // Red
        "#6C757D"                 // Gray (Unknown)
    )
```

#### Step 5.3: Create Days Remaining Measure

```DAX
DaysRemaining = 
VAR CurrentDate = TODAY()
VAR TargetDate = SELECTEDVALUE(StageProgress[StageTargetDate])
VAR IsComplete = SELECTEDVALUE(StageProgress[StageComplete])

RETURN
    IF(
        IsComplete = "Yes",
        0,
        TargetDate - CurrentDate
    )
```

#### Step 5.4: Create Stage Completion Percentage

```DAX
StageCompletionPct = 
VAR TotalStages = COUNTROWS(StageProgress)
VAR CompletedStages = 
    CALCULATE(
        COUNTROWS(StageProgress),
        StageProgress[StageComplete] = "Yes"
    )

RETURN
    DIVIDE(CompletedStages, TotalStages, 0)
```

#### Step 5.5: Create Part-Level Status (Aggregated from Stages)

```DAX
PartOverallStatus = 
VAR PartNumber = SELECTEDVALUE(MasterStatus[PartNumber])
VAR PartStages = 
    FILTER(
        StageProgress,
        StageProgress[PartNumber] = PartNumber
    )
VAR LateStages = 
    COUNTROWS(
        FILTER(
            PartStages,
            [StageStatus] = "Late"
        )
    )
VAR AtRiskStages = 
    COUNTROWS(
        FILTER(
            PartStages,
            [StageStatus] = "At Risk"
        )
    )
VAR AllComplete = 
    COUNTROWS(
        FILTER(
            PartStages,
            StageProgress[StageComplete] = "Yes"
        )
    ) = COUNTROWS(PartStages)

RETURN
    SWITCH(
        TRUE(),
        AllComplete, "Complete",
        LateStages > 0, "Delayed",
        AtRiskStages > 0, "At Risk",
        "On Track"
    )
```

---

### PHASE 6: UPDATE DASHBOARD VISUALS

#### Page 1: Overview Dashboard - Updates

**KPI Cards** (Add New):

1. **Insert** → **Card**
2. **Field**: Create new measure:
```DAX
TotalStagesLate = 
CALCULATE(
    COUNTROWS(StageProgress),
    [StageStatus] = "Late"
)
```
3. **Title**: "Stages Late"
4. **Format**: Conditional color - Red if > 0

5. **Insert** → **Card**
6. **Field**: `[StageCompletionPct]`
7. **Title**: "Overall Stage Completion %"
8. **Format**: Percentage, 1 decimal

**Status Distribution Chart** - Update:

1. Select existing **Status Distribution Donut Chart**
2. **Change Legend** from `MasterStatus[StatusFlag]` to: `[PartOverallStatus]` (new measure)
3. Colors will now auto-apply based on aggregated stage status

**Parts Table** - Add Stage Details:

1. Select the **Parts Table** visual
2. **Add Columns**:
   - `[TotalStagesLate]` (shows how many stages are late for each part)
   - `[StageCompletionPct]` (shows % complete per part)
3. **Conditional Formatting**:
   - Right-click `StageCompletionPct` → Conditional Formatting → Data Bars
   - Color: Green gradient

---

#### Page 2: NEW - Stage Timeline View

**Create New Page**:

1. Click **+** at bottom to add new page
2. Rename: "Stage Timeline"

**Gantt Chart Alternative - Matrix Visual**:

1. **Insert** → **Matrix**
2. **Rows**: `MasterStatus[PartNumber]`
3. **Columns**: `StageProgress[StageName]`
4. **Values**: `StageProgress[StageComplete]`
5. **Conditional Formatting**:
   - Right-click the Values field
   - Background Color → Rules
   - If `StageComplete` = "Yes" → Green (#28A745)
   - If `StageComplete` = "No" → Check [StageStatus]:
     - "Late" → Red (#DC3545)
     - "At Risk" → Yellow (#FFC107)
     - "On Track" → Blue (#4A90E2)

**Better Alternative - Custom Visual**:

If Matrix doesn't show colors properly:

1. **Insert** → **Table**
2. **Columns**:
   - `PartNumber`
   - `StageName`
   - `StageTargetDate`
   - `StageComplete`
   - `[DaysRemaining]`
   - `[StageStatus]`
3. **Conditional Formatting** on `StageStatus` column:
   - Background color based on status

**Timeline Chart** (Show all parts' stage progress):

1. **Insert** → **Clustered Column Chart**
2. **X-Axis**: `StageProgress[StageName]`
3. **Y-Axis**: `COUNTROWS(StageProgress)` (count of parts at each stage)
4. **Legend**: `[StageStatus]`
5. **Colors**: Use status colors

---

#### Page 3: Stage Heatmap - Update

**Existing Heatmap Enhancement**:

1. Select the **Matrix** visual
2. **Current Setup**:
   - Rows: `PartNumber`
   - Columns: `StageName`
   - Values: Previously used `CurrentStage` comparison

3. **Update Values** to use new measure:
```DAX
HeatmapStatus = 
VAR PartNum = SELECTEDVALUE(MasterStatus[PartNumber])
VAR StageNum = SELECTEDVALUE(StageDefinitions[StageNumber])
VAR StageData = 
    FILTER(
        StageProgress,
        StageProgress[PartNumber] = PartNum &&
        StageProgress[StageNumber] = StageNum
    )
VAR IsComplete = MAXX(StageData, StageProgress[StageComplete])

RETURN
    IF(
        IsComplete = "Yes",
        "✓",
        BLANK()
    )
```

4. **Conditional Formatting** - Update colors:
   - Use `[StageStatus]` measure for background color
   - Green: Complete
   - Red: Late
   - Yellow: At Risk
   - Blue: On Track
   - Gray: Not Started

---

### PHASE 7: ADD SLICERS FOR FILTERING

**On Stage Timeline Page**:

1. **Insert** → **Slicer**
2. **Field**: `[StageStatus]`
3. **Position**: Top right
4. **Settings**: Multi-select enabled

5. **Insert** → **Slicer**
6. **Field**: `StageDefinitions[Phase]`
7. **Position**: Top right (below status slicer)

8. **Insert** → **Slicer**
9. **Field**: `MasterStatus[Customer]`
10. **Position**: Top right

**Sync Slicers Across Pages**:

1. **View Tab** → **Sync Slicers**
2. Select each slicer
3. Check which pages should respond to it
4. Sync Customer and Priority across all pages

---

### PHASE 8: CREATE DRILL-THROUGH PAGE

**Create Part Detail Drill-Through**:

1. **Add new page**: "Part Detail Drill-Through"
2. **In Visualizations pane** → **Drill through** section
3. **Add drill-through field**: `MasterStatus[PartNumber]`

**Add Visuals**:

1. **Card**: Display selected `PartNumber`
2. **Card**: Display `PartDescription`
3. **Card**: Display `Customer`

4. **Table**: Show all stages for selected part:
   - Columns:
     - `StageName`
     - `StageTargetDate`
     - `StageComplete`
     - `[DaysRemaining]`
     - `[StageStatus]`
   - **Conditional Formatting** on `StageStatus`

5. **Waterfall Chart**:
   - Category: `StageName`
   - Y-Axis: `[DaysRemaining]`
   - Shows timeline deviation for each stage

**Enable Drill-Through**:

1. Go back to **Overview** page
2. Right-click on any part in the Parts Table
3. Should see "Drill through" → "Part Detail Drill-Through"
4. Test it - should show detailed stage info for selected part

---

### PHASE 9: UPDATE EXISTING MEASURES (COMPATIBILITY)

**Update Old Measures to Use New Data**:

Some existing measures might reference the old single `TargetCompletionDate`. Update them:

**Old**:
```DAX
CompleteCount = 
CALCULATE(
    COUNT(MasterStatus[PartNumber]), 
    MasterStatus[CurrentStage] = 23
)
```

**New (Alternative using StageProgress)**:
```DAX
CompleteCount = 
VAR AllPartsComplete = 
    SUMMARIZE(
        StageProgress,
        StageProgress[PartNumber],
        "AllStagesComplete", 
        COUNTROWS(FILTER(StageProgress, StageProgress[StageComplete] = "Yes")) = 23
    )
RETURN
    COUNTROWS(FILTER(AllPartsComplete, [AllStagesComplete] = TRUE()))
```

**Or Keep Simple** (if you still maintain `CurrentStage` column):
```DAX
CompleteCount = 
CALCULATE(
    COUNT(MasterStatus[PartNumber]), 
    MasterStatus[CurrentStage] = 23
)
```
(No change needed if Excel still updates this column)

---

### PHASE 10: TESTING & VALIDATION

#### Test 10.1: Verify Stage Status Detection

1. **Create test data** in Excel:
   - Part A: Stage 5 target = Yesterday, Complete = No → Should show "Late"
   - Part B: Stage 5 target = Tomorrow, Complete = No → Should show "At Risk" (if < 7 days) or "On Track"
   - Part C: Stage 5 target = Any date, Complete = Yes → Should show "Complete"

2. **Save Excel** file
3. **Refresh Power BI** (Home → Refresh)
4. **Check Stage Timeline page**:
   - Verify colors match expectations
   - Late stages = Red
   - At Risk = Yellow
   - On Track = Blue
   - Complete = Green

#### Test 10.2: Verify Part-Level Aggregation

1. **Overview Page** → Check Status Distribution chart
2. If ANY stage of a part is "Late", the part should show as "Delayed"
3. If no stages late but some "At Risk", part should show "At Risk"

#### Test 10.3: Verify Drill-Through

1. Right-click a part in Overview table
2. Drill through to Part Detail
3. Should see all 23 stages for that part with individual statuses

#### Test 10.4: Cross-Filter Behavior

1. Click a stage in Timeline chart
2. Parts table should filter to show only parts at that stage
3. Click a status in Status Distribution
4. All visuals should filter to that status

---

## 📊 SAMPLE DAX MEASURES LIBRARY

Copy these to a text file for easy reference:

### Stage-Level Measures

```DAX
// Stage Status (Late, At Risk, On Track, Complete)
StageStatus = 
VAR CurrentDate = TODAY()
VAR IsComplete = SELECTEDVALUE(StageProgress[StageComplete])
VAR TargetDate = SELECTEDVALUE(StageProgress[StageTargetDate])
VAR DaysUntilDue = TargetDate - CurrentDate
RETURN
    SWITCH(TRUE(),
        IsComplete = "Yes", "Complete",
        DaysUntilDue < 0, "Late",
        DaysUntilDue <= 7, "At Risk",
        DaysUntilDue > 7, "On Track",
        "Unknown"
    )

// Days Remaining for Stage
DaysRemaining = 
VAR CurrentDate = TODAY()
VAR TargetDate = SELECTEDVALUE(StageProgress[StageTargetDate])
VAR IsComplete = SELECTEDVALUE(StageProgress[StageComplete])
RETURN
    IF(IsComplete = "Yes", 0, TargetDate - CurrentDate)

// Count Late Stages
TotalStagesLate = 
CALCULATE(
    COUNTROWS(StageProgress),
    [StageStatus] = "Late"
)

// Count At Risk Stages
TotalStagesAtRisk = 
CALCULATE(
    COUNTROWS(StageProgress),
    [StageStatus] = "At Risk"
)

// Stage Completion Percentage (All Parts)
StageCompletionPct = 
VAR TotalStages = COUNTROWS(StageProgress)
VAR CompletedStages = 
    CALCULATE(
        COUNTROWS(StageProgress),
        StageProgress[StageComplete] = "Yes"
    )
RETURN
    DIVIDE(CompletedStages, TotalStages, 0)
```

### Part-Level Aggregated Measures

```DAX
// Part Overall Status (Aggregated from Stage Status)
PartOverallStatus = 
VAR PartNumber = SELECTEDVALUE(MasterStatus[PartNumber])
VAR PartStages = FILTER(StageProgress, StageProgress[PartNumber] = PartNumber)
VAR LateStages = COUNTROWS(FILTER(PartStages, [StageStatus] = "Late"))
VAR AtRiskStages = COUNTROWS(FILTER(PartStages, [StageStatus] = "At Risk"))
VAR AllComplete = 
    COUNTROWS(FILTER(PartStages, StageProgress[StageComplete] = "Yes")) = 23
RETURN
    SWITCH(TRUE(),
        AllComplete, "Complete",
        LateStages > 0, "Delayed",
        AtRiskStages > 0, "At Risk",
        "On Track"
    )

// Part Completion Percentage
PartCompletionPct = 
VAR PartNumber = SELECTEDVALUE(MasterStatus[PartNumber])
VAR TotalStages = 23
VAR CompletedStages = 
    CALCULATE(
        COUNTROWS(StageProgress),
        StageProgress[PartNumber] = PartNumber,
        StageProgress[StageComplete] = "Yes"
    )
RETURN
    DIVIDE(CompletedStages, TotalStages, 0)

// Count Parts Delayed (Any Late Stage)
PartsDelayed = 
CALCULATE(
    DISTINCTCOUNT(StageProgress[PartNumber]),
    [StageStatus] = "Late"
)

// Count Parts At Risk (No Late, But Some At Risk)
PartsAtRisk = 
VAR PartsWithLate = CALCULATE(DISTINCTCOUNT(StageProgress[PartNumber]), [StageStatus] = "Late")
VAR PartsWithAtRisk = CALCULATE(DISTINCTCOUNT(StageProgress[PartNumber]), [StageStatus] = "At Risk")
RETURN
    PartsWithAtRisk - PartsWithLate
```

### Color Measures

```DAX
// Status Color
StatusColor = 
VAR Status = [StageStatus]
RETURN
    SWITCH(Status,
        "Complete", "#28A745",
        "On Track", "#4A90E2",
        "At Risk", "#FFC107",
        "Late", "#DC3545",
        "#6C757D"
    )

// Part Status Color
PartStatusColor = 
VAR Status = [PartOverallStatus]
RETURN
    SWITCH(Status,
        "Complete", "#28A745",
        "On Track", "#4A90E2",
        "At Risk", "#FFC107",
        "Delayed", "#DC3545",
        "#6C757D"
    )
```

---

## 🔧 TROUBLESHOOTING

### Issue: New Columns Not Appearing

**Solution**:
1. Power Query Editor → Right-click **MasterStatus** → **Refresh Preview**
2. Check Excel file path is still valid
3. Verify Excel file isn't open (can block refresh)

### Issue: Unpivot Creates Wrong Structure

**Solution**:
1. Verify you selected ONLY the Target columns (not Complete columns) for first unpivot
2. If needed, delete StageProgress table and start over from Step 3.1
3. Check column names match exactly ("Stage 01 Target" vs "Stage01Target")

### Issue: StageComplete Always Shows Blank

**Solution**:
1. The merge approach in Step 3.6 might need adjustment
2. Alternative: Use Excel formula to add StageComplete to original unpivot
3. Or manually map stage numbers to completion status using SWITCH in DAX

### Issue: Relationship Errors

**Solution**:
1. Model View → Delete broken relationships
2. Verify data types match (StageNumber must be Whole Number in both tables)
3. Check for blank values in key columns

### Issue: Measures Show "#Error"

**Solution**:
1. Check for typos in measure formulas
2. Verify table and column names match your data model exactly
3. Use `SELECTEDVALUE()` instead of `VALUES()` for single-row context
4. Add `HASONEVALUE()` checks before `SELECTEDVALUE()`

### Issue: Colors Not Showing in Matrix

**Solution**:
1. Matrix may not support all conditional formatting types
2. Use Table visual instead of Matrix
3. Or create separate measure that returns color code, apply to background

### Issue: Performance Slow After Update

**Solution**:
1. Reduce number of measures calculated in large tables
2. Use variables (VAR) to cache intermediate calculations
3. Consider creating calculated columns instead of measures for static data
4. Close & Apply in Power Query, don't leave it open

---

## 📈 RECOMMENDED VISUAL ENHANCEMENTS

### 1. Stage Progress Bar Chart

**Visual**: Clustered Bar Chart  
**X-Axis**: `StageProgress[StageName]`  
**Y-Axis**: `DISTINCTCOUNT(StageProgress[PartNumber])`  
**Legend**: `[StageStatus]`  
**Purpose**: See how many parts are at each stage and their status distribution

### 2. Timeline Waterfall

**Visual**: Waterfall Chart  
**Category**: `StageProgress[StageName]`  
**Y-Axis**: `[DaysRemaining]`  
**Purpose**: Visualize schedule buffer/overrun across stages

### 3. Critical Path View

**Visual**: Table with Custom Sort  
**Columns**:
- `PartNumber`
- `StageName`
- `StageTargetDate`
- `[DaysRemaining]`
- `[StageStatus]`

**Filter**: `[StageStatus]` IN ("Late", "At Risk")  
**Sort**: By `[DaysRemaining]` (ascending)  
**Purpose**: Show most urgent stages requiring attention

### 4. Completion Heatmap

**Visual**: Matrix  
**Rows**: `MasterStatus[PartNumber]`  
**Columns**: `StageDefinitions[Phase]`  
**Values**: `[StageCompletionPct]`  
**Conditional Formatting**: Data bars (Green = 100%, Red = 0%)  
**Purpose**: High-level view of part progress by phase

---

## 📝 FINAL CHECKLIST

- [ ] **Backup created** (original .pbix file copied)
- [ ] **Excel columns verified** (I to BC exist with correct names)
- [ ] **Power BI refreshed** (new columns loaded)
- [ ] **StageProgress table created** (unpivot successful)
- [ ] **Relationships established** (StageProgress ↔ StageDefinitions, MasterStatus)
- [ ] **DAX measures created** (StageStatus, PartOverallStatus, etc.)
- [ ] **Overview page updated** (uses new aggregated status)
- [ ] **Stage Timeline page created** (shows individual stage status)
- [ ] **Heatmap updated** (uses stage-level completion)
- [ ] **Slicers added** (StageStatus, Phase filters)
- [ ] **Drill-through working** (Part Detail page)
- [ ] **Testing complete** (Late/At Risk/On Track display correctly)
- [ ] **Published to Power BI Service** (if applicable)
- [ ] **Scheduled refresh configured** (if applicable)

---

## 🎯 EXPECTED OUTCOMES

After completing this update:

1. **Stage-Level Visibility**: See which specific stages are late/at risk for each part
2. **Proactive Management**: Identify at-risk stages 7 days before they become late
3. **Accurate Reporting**: Part status reflects reality of stage delays, not just overall target
4. **Timeline Analysis**: Understand which stages are bottlenecks across all parts
5. **Prioritization**: Focus attention on the most critical late/at-risk stages

**Example Insights You Can Now Answer**:
- "Which parts have late FAI stages?" → Filter StageTimeline by Stage = "First Article Inspection" AND Status = "Late"
- "How many stages are at risk this week?" → `[TotalStagesAtRisk]` KPI card
- "What's the completion rate for Validation phase?" → Filter by Phase = "VALIDATION", show `[StageCompletionPct]`

---

## 📚 ADDITIONAL RESOURCES

### Power Query M Formula Reference
- [Unpivot Columns](https://learn.microsoft.com/en-us/powerquery-m/table-unpivotothercolumns)
- [Custom Columns](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-add-custom-column)

### DAX Function Reference
- [CALCULATE](https://dax.guide/calculate/)
- [FILTER](https://dax.guide/filter/)
- [SWITCH](https://dax.guide/switch/)
- [SELECTEDVALUE](https://dax.guide/selectedvalue/)

### Power BI Community
- [Power BI Community Forum](https://community.powerbi.com/)
- [DAX Patterns](https://www.daxpatterns.com/)

---

## 💡 NEXT STEPS

After completing this update:

1. **Train stakeholders** on new visuals and filters
2. **Update documentation** for users
3. **Establish data entry standards** for the Yes/No completion flags in Excel
4. **Consider automation** for updating "Complete" flags based on evidence file detection
5. **Monitor performance** - add more measures as needed
6. **Gather feedback** on new insights available

---

**Questions or Issues?**  
Document issues encountered and solutions found for future reference.

**Last Updated**: October 30, 2025  
**Version**: 1.0  
**Status**: Ready for Implementation
