# ZnNi Industrialization Dashboard — User Guide

> **Report Name:** ZnNi Industrialization Tracker  
> **Purpose:** Track the progress of ZnNi (Zinc-Nickel) coating industrialization across all parts — from initial planning through to completion.  
> **Tool:** Microsoft Power BI  
> **Last Updated:** March 2026

---

## Table of Contents

1. [What This Dashboard Shows](#1-what-this-dashboard-shows)
2. [How to Open the Dashboard](#2-how-to-open-the-dashboard)
3. [Navigating the Dashboard](#3-navigating-the-dashboard)
4. [Page 1 — Overview](#4-page-1--overview)
5. [Page 2 — Bulk Action Planning](#5-page-2--bulk-action-planning)
6. [Working with Filters](#6-working-with-filters)
7. [Source Spreadsheets — Where the Data Comes From](#7-source-spreadsheets--where-the-data-comes-from)
8. [How to Update the Data](#8-how-to-update-the-data)
9. [Exporting and Sharing](#9-exporting-and-sharing)
10. [Troubleshooting](#10-troubleshooting)
11. [Glossary](#11-glossary)

---

## 1. What This Dashboard Shows

This Power BI dashboard provides a single view of the ZnNi industrialization programme. It answers these key questions:

- **How many parts** are in scope for ZnNi conversion?
- **How many are complete**, how many are still in progress, and what percentage is done?
- **What is the status breakdown** of all parts? (Bar chart and donut chart views)
- **Who owns which parts**, and what stage is each part at?
- **What does each part need?** (Tooling requirements, parent part relationships)

The dashboard is fed by **four Excel spreadsheets stored on SharePoint (Safran MyShare)**. When those spreadsheets are updated and the dataset is refreshed, the dashboard updates automatically.

---

## 2. How to Open the Dashboard

### Option A — Power BI Service (Web Browser)
1. Go to [Power BI Service](https://app.powerbi.com)
2. Sign in with your Safran / organisational account
3. Navigate to the workspace where the report is published
4. Click on **"ZnNi Industrialization Dashboard"** to open it

### Option B — Power BI Desktop (Local Application)
1. Open **Power BI Desktop** on your computer
2. Click **File → Open report → Browse reports**
3. Select the `.pbix` file (`ZnNi Industrialization Dashboard-Instruction.pbix`)
4. The report will open with the most recent data snapshot

> **Tip:** The Power BI Service version (Option A) will always show the most up-to-date data if scheduled refresh is configured. The Desktop version shows data from the last time it was refreshed or saved.

---

## 3. Navigating the Dashboard

The dashboard has **two pages**:

| Page | Name | Purpose |
|------|------|---------|
| 1 | **Overview** | High-level summary: KPIs, status charts, and part details |
| 2 | **Bulk Action Planning** | Operational view: who owns what, at which stage |

### How to Switch Between Pages

- **Page tabs** are at the bottom of the screen — click the tab name to switch
- Each page also has a **Back button** (◄) in the top-left corner to return to the previous page
- You can also click on chart elements (e.g., a status bar) to drillthrough to the Bulk Action page filtered for that status

---

## 4. Page 1 — Overview

This is the main landing page. It gives you a snapshot of the entire ZnNi industrialization programme.

### Layout (top to bottom):

```
┌──────────────────────────────────────────────────────────────┐
│ [◄ Back]     ZnNi Industrialization Tracker                  │
├──────────────┬──────────────┬──────────────┬─────────────────┤
│ Total Parts  │ % Complete   │ Completed    │ In Progress     │
│   (card)     │   (card)     │   (card)     │   (card)        │
├──────────────┴──────────────┼──────────────┴─────────────────┤
│                             │                                │
│  Parts by Status            │  Status Distribution           │
│  (Bar Chart)                │  (Donut Chart)                 │
│                             │                                │
├─────────────────────────────┴────────────────────────────────┤
│                                                              │
│  Part Details Table                                          │
│  (PartNumber, Description, Parent Part, Tooling Required)    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Visual-by-Visual Explanation

#### KPI Cards (top row — 4 cards)

| Card | What It Shows | How to Read It |
|------|--------------|----------------|
| **Total Parts** | The total count of unique part numbers in the programme | A single number. If this changes, new parts have been added or removed from scope. |
| **% Complete** | Percentage of parts that have completed all stages | Shown as a percentage. Target is 100%. |
| **Completed Parts** | The count of parts with a "Complete" status | A single number — how many parts are fully done. |
| **In Progress** | The count of parts currently in progress | A single number — parts that are active but not yet finished. |

> **Reading the cards:** These four cards give you the headline numbers at a glance. Together they tell you: "Out of X total parts, Y are done (Z%), and W are still being worked on."

#### Parts by Status (Bar Chart — left, middle row)

- **What it shows:** A horizontal or vertical bar chart with one bar per status category (e.g., Complete, In Progress, Not Started)
- **X-axis / Categories:** `StatusFlag` — the status label for each part
- **Y-axis / Values:** Count of parts in that status
- **How to read it:** Taller/longer bars mean more parts in that status. You want the "Complete" bar to grow over time.
- **Interaction:** Click on any bar to filter the rest of the page to show only parts with that status.

#### Status Distribution (Donut Chart — right, middle row)

- **What it shows:** The same status data as the bar chart, but as proportions of the whole
- **Segments:** Each coloured segment = one status category
- **How to read it:** The larger the segment, the more parts are in that status. Hover over a segment to see the exact count and percentage.
- **Interaction:** Click a segment to filter the page.

#### Part Details Table (bottom)

This table shows one row per part with the following columns:

| Column | Description |
|--------|-------------|
| **PartNumber** | The unique identifier for each part |
| **PartDescription** | A text description of what the part is |
| **Parent Part Number** | The parent/assembly part number this part belongs to (if applicable) |
| **Passivate Tooling Required** | Whether passivation tooling is needed for this part (Yes/No) |
| **Touch-Up Tooling Required** | Whether touch-up tooling is needed for this part (Yes/No) |

> **Tip:** You can sort by any column by clicking the column header. Click once for ascending, again for descending. You can also scroll down if there are more rows than fit on screen.

---

## 5. Page 2 — Bulk Action Planning

This page focuses on **who is doing what** and **where each part sits in the process pipeline**. Use this page to coordinate workload and identify bottlenecks.

### Layout (top to bottom):

```
┌──────────────────────────────────────────────────────────────┐
│ [◄ Back]              [Dynamic Page Title]                   │
├─────────────────────────────┬────────────────────────────────┤
│                             │                                │
│  Parts by Owner             │  Owner Distribution            │
│  (Bar Chart)                │  (Donut Chart)                 │
│                             │                                │
├─────────────────────────────┴────────────────────────────────┤
│                                                              │
│  No. of Part Numbers at Current Stage                        │
│  (Column Chart)                                              │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Action Details Table                                        │
│  (PartNumber, Description, Owner, Stage, StageName)          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Visual-by-Visual Explanation

#### Dynamic Page Title (top-right card)

- This card displays a **dynamic title** that changes based on the currently active filters
- For example, if you drillthrough from the Overview page filtering on "In Progress" status, the title may reflect that context

#### Parts by Owner (Bar Chart — top-left)

- **What it shows:** How many parts each owner/team is responsible for
- **X-axis / Categories:** `Owner` — the person or team assigned
- **Y-axis / Values:** Count of part numbers
- **How to read it:** Identifies workload distribution. Uneven bars may indicate someone is overloaded.

#### Owner Distribution (Donut Chart — top-right)

- **What it shows:** Same owner data as the bar chart, shown as proportions
- **How to read it:** Quickly see who holds the largest share of parts

#### No. of Part Numbers at Current Stage (Column Chart — middle)

- **What it shows:** How many parts are at each stage of the industrialization process
- **X-axis:** `CurrentStage` — the stage identifier (e.g., Stage 1, Stage 2, etc.)
- **Y-axis:** Count of part numbers at that stage
- **How to read it:** Shows where parts are accumulating. A large bar at an early stage means many parts haven't progressed. A large bar at a late stage means parts are nearing completion.
- **Tip:** Cross-reference this with the Stage Definitions table to understand what each stage means.

#### Action Details Table (bottom)

| Column | Description |
|--------|-------------|
| **PartNumber** | The unique part identifier |
| **PartDescription** | Description of the part |
| **Owner** | The person or team responsible for this part |
| **CurrentStage** | The stage number this part is currently at |
| **StageName** | The human-readable name of that stage (looked up from Stage Definitions) |

> **Tip:** Sort by `Owner` to see all parts for a specific person. Sort by `CurrentStage` to see which parts are earliest or furthest along.

---

## 6. Working with Filters

### Page-Level Filter: Parts Overall Status

Both pages are filtered by **PartsOverallStatus** from the Master Status table. This filter controls which parts are displayed across all visuals on the page.

### How to Use the Filter Pane

1. Look for the **filter icon** (funnel symbol) on the right side of the report
2. Click it to expand the **Filters pane**
3. You will see filters for the current page — you can select/deselect status values to focus on specific groups of parts
4. To clear a filter, click the **eraser icon** next to the filter name

### Cross-Filtering (Clicking on Visuals)

- **Click** on any bar, donut segment, or table row to filter the rest of the page
- This is called **cross-filtering** — when you click an element in one visual, all other visuals on the same page update to show only related data
- **To clear a cross-filter:** click the same element again, or click on an empty area of the chart

### Example: Finding All Parts Owned by a Specific Person

1. Go to Page 2 (Bulk Action Planning)
2. Click on the person's name in the **Parts by Owner** bar chart
3. The table, column chart, and donut chart will all update to show only that person's parts
4. Click the same bar again to clear the filter

---

## 7. Source Spreadsheets — Where the Data Comes From

The dashboard is powered by **four Excel spreadsheets** stored on **Safran MyShare (SharePoint)**. Each spreadsheet feeds a specific table in the data model.

### File Location

All files are stored in the same SharePoint folder:

> **Path:** `Safran MyShare → GLO REACh → Shared Documents → SLS Internal → ZnNi Industrialization → ZnNi Industrialization Data`

### Spreadsheet-to-Table Mapping

| # | Spreadsheet File | Dashboard Table | What It Contains |
|---|-----------------|-----------------|------------------|
| 1 | **ZnNi_Master_Status.xlsx** | Master Status | The main tracking sheet — each row is a part with its current status, stage, and overall progress flag. This is the primary data source. |
| 2 | **ZnNi_Part_Master_List.xlsx** | Part Master List | Part details — part numbers, descriptions, parent parts, and tooling requirements (passivate and touch-up). |
| 3 | **ZnNi_Stage_Definitions.xlsx** | Stage Definitions | Defines what each stage means — maps stage numbers to stage names and assigns an owner/team to each stage. |
| 4 | **Stakeholder_Distribution.xlsx** | StageProgress / StageTargets | Stakeholder and progress tracking — defines targets per stage and tracks actual progress against those targets. |

### How the Tables Connect

```
                    ┌───────────────────┐
                    │  Master Status    │
                    │  (main tracker)   │
                    └─────────┬─────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
    ┌─────────▼─────┐  ┌─────▼──────────┐  ┌─▼──────────────┐
    │ Part Master   │  │ Stage          │  │ StageProgress  │
    │ List          │  │ Definitions    │  │ & StageTargets │
    │ (part info)   │  │ (stage names)  │  │ (targets)      │
    └───────────────┘  └────────────────┘  └────────────────┘
```

- **Master Status** links to **Part Master List** via `PartNumber` — to pull in part descriptions and tooling info
- **Master Status** links to **Stage Definitions** via `CurrentStage` — to get the stage name and owner
- **StageProgress** and **StageTargets** provide progress metrics against defined milestones

---

## 8. How to Update the Data

### Step 1 — Update the Source Spreadsheets

1. Open the relevant spreadsheet on **Safran MyShare** using the links below:
   - [ZnNi_Master_Status.xlsx](https://myshare.grp.collab.group.safran/personal/mg020923/GLO%20REACh/Shared%20Documents/SLS%20Internal/ZnNi%20Industrialization/ZnNi%20Industrialization%20Data/ZnNi_Master_Status.xlsx)
   - [ZnNi_Part_Master_List.xlsx](https://myshare.grp.collab.group.safran/personal/mg020923/GLO%20REACh/Shared%20Documents/SLS%20Internal/ZnNi%20Industrialization/ZnNi%20Industrialization%20Data/ZnNi_Part_Master_List.xlsx)
   - [ZnNi_Stage_Definitions.xlsx](https://myshare.grp.collab.group.safran/personal/mg020923/GLO%20REACh/Shared%20Documents/SLS%20Internal/ZnNi%20Industrialization/ZnNi%20Industrialization%20Data/ZnNi_Stage_Definitions.xlsx)
   - [Stakeholder_Distribution.xlsx](https://myshare.grp.collab.group.safran/personal/mg020923/GLO%20REACh/Shared%20Documents/SLS%20Internal/ZnNi%20Industrialization/ZnNi%20Industrialization%20Data/Stakeholder_Distribution.xlsx)

2. Make your changes (add rows, update statuses, modify stage assignments, etc.)

3. **Save the file** — make sure the file is saved back to the SharePoint location (not your local Downloads folder)

> **Important:** Do not rename the files, change the sheet names, or alter the column headers — the Power BI dataset expects a specific structure.

### Step 2 — Refresh the Power BI Dataset

#### If Using Power BI Service (Recommended)

1. Go to [Power BI Service](https://app.powerbi.com)
2. Navigate to the **workspace** containing the dataset
3. Find the **dataset** (not the report) — it will have a database icon
4. Click the **three dots (⋯)** next to the dataset name
5. Click **Refresh now**
6. Wait for the refresh to complete (you may see a spinning icon)
7. Open the report — it will now show the updated data

> **Tip:** If a scheduled refresh is configured, the dataset will refresh automatically (e.g., daily at a set time). Ask your Power BI administrator if this is set up.

#### If Using Power BI Desktop

1. Open the `.pbix` file in Power BI Desktop
2. Click **Home → Refresh** in the ribbon (or press `Ctrl+F5`)
3. Power BI will connect to the SharePoint files and pull the latest data
4. Once the refresh completes, click **File → Save** to save the updated data into the file

### What to Update and When

| Scenario | Spreadsheet to Update | What to Change |
|----------|----------------------|----------------|
| A part moves to the next stage | ZnNi_Master_Status.xlsx | Update `CurrentStage` and `StatusFlag` for that part |
| A part is completed | ZnNi_Master_Status.xlsx | Set `StatusFlag` to Complete, update `PartsOverallStatus` |
| A new part is added to scope | ZnNi_Part_Master_List.xlsx **and** ZnNi_Master_Status.xlsx | Add the part to both spreadsheets |
| Ownership changes for a stage | ZnNi_Stage_Definitions.xlsx | Update the `Owner` column for the relevant stage |
| A part is removed from scope | ZnNi_Master_Status.xlsx | Remove the row or mark as out of scope |

---

## 9. Exporting and Sharing

### Export Data from a Visual

1. Hover over the visual (chart or table) you want to export
2. Click the **three dots (⋯)** that appear in the top-right corner of the visual
3. Select **Export data**
4. Choose the format (Excel is recommended)
5. Click **Export** — the file will download to your computer

### Export the Whole Page as PDF or PowerPoint

1. Click **File → Export** in the Power BI toolbar
2. Select **PDF** or **PowerPoint**
3. Choose which pages to include
4. Click **Export**

### Share the Report with Others

1. In Power BI Service, click the **Share** button in the toolbar
2. Enter the email addresses of the people you want to share with
3. Choose whether they can re-share or only view
4. Click **Send**

> **Note:** Recipients must have a Power BI Pro or Premium Per User licence to view shared reports.

---

## 10. Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Dashboard shows old data | Dataset hasn't been refreshed | Follow the refresh steps in Section 8 |
| A visual is blank or shows "No data" | A filter is active that excludes all data | Clear the filters (see Section 6) |
| "Can't connect to data source" error on refresh | SharePoint credentials have expired, or the file has been moved/renamed | Re-enter SharePoint credentials in dataset settings; verify files haven't been moved |
| Numbers don't match my spreadsheet | You may have unsaved changes in the spreadsheet, or the refresh hasn't completed yet | Save the spreadsheet, refresh the dataset, and wait for it to finish |
| I can't see the report | You don't have access to the Power BI workspace | Ask your Power BI administrator to grant you access |
| The page title on Page 2 shows the wrong text | A drillthrough filter is still active | Click the Back button or clear the page filter |
| Column chart shows unfamiliar stage numbers | A new stage was added to Master Status but not to Stage Definitions | Add the new stage to ZnNi_Stage_Definitions.xlsx and refresh |

---

## 11. Glossary

| Term | Definition |
|------|-----------|
| **ZnNi** | Zinc-Nickel — an electroplated coating used for corrosion protection on aircraft parts |
| **Industrialization** | The process of transitioning parts from the current coating process to ZnNi |
| **StatusFlag** | The current status of a part (e.g., Complete, In Progress, Not Started) |
| **PartsOverallStatus** | An overall status flag used to filter the entire dashboard |
| **CurrentStage** | A numeric identifier indicating which stage of the process a part is at |
| **StageName** | The human-readable name for a stage (from Stage Definitions) |
| **Owner** | The person or team responsible for a given stage or part |
| **Parent Part Number** | The assembly or higher-level part that a component belongs to |
| **Passivate Tooling** | Specialised tooling required for the passivation step of the ZnNi process |
| **Touch-Up Tooling** | Specialised tooling required for touch-up work on ZnNi-coated parts |
| **Cross-Filter** | When clicking on one visual causes other visuals on the same page to update |
| **Drillthrough** | Navigating from one page to another while carrying a filter context |
| **Dataset** | The Power BI data model that connects to the source spreadsheets |
| **Scheduled Refresh** | An automatic refresh configured in Power BI Service to update data on a set schedule |

---

*End of User Guide*
