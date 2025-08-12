# 🔄 CONTROL TOWER WORKFLOWS
**Project Management & Task Orchestration Platform**

---

## 📋 WORKFLOW DOCUMENTATION

**Purpose**: Document all Control Tower workflows for project management, XML synchronization, and PowerPoint generation processes.

**Maintained By**: James Fleming  
**Last Updated**: August 8, 2025  
**Document Version**: 2.0

---

## 🚀 PRIMARY WORKFLOWS

### **Workflow #1: Friday PowerPoint Generation & Change Management Workflow** ✅ **ACTIVE**
**Purpose**: Weekly PowerPoint update with automated change detection and change management forms  
**Frequency**: Every Friday for weekly stakeholder presentations  
**Duration**: 10-20 minutes depending on number of changes detected  
**Command**: **Single command executes complete workflow**

#### **Complete Friday Workflow Overview:**
```bash
# Single Command - Complete Friday Workflow
python friday_workflow.py --compare-xml --previous-week /path/to/last_friday_xml.xml --generate-powerpoint --change-management
```

**User Experience**:
1. **Pre-Command**: User manually exports latest XML from MS Project and uploads to xml_workspace
2. **Single Command**: Executes complete automated change detection and presentation generation
3. **Interactive Change Management**: Terminal forms open for each detected milestone change
4. **Result**: Updated PowerPoint presentation with change management slides populated

#### **Workflow Steps:**
1. **XML Comparison**: Compare last Friday's XML vs current XML
2. **Change Detection**: Identify milestone date changes, new milestones, completed milestones
3. **Change Management Forms**: Interactive terminal forms for each change (4-impact assessment)
4. **PowerPoint Generation**: Update presentation with change management data
5. **Slide Mapping**: Changes mapped to correct slides based on Level 3 projects

#### **Level 3 Project → Slide Mapping:**
```
1_ZnNi_Line_Stabilization_Critical_Documentation_and_Training → Slide 4
2_ZnNi_Line_Stabilization_Critical_Maintenance → Slide 8  
3_ZnNi_Line_Post_Stabilization_Optimization → Slide 12
```

#### **Change Management Impact Assessment:**
- **Schedule Impact**: Date changes, project end date impact
- **Cost Impact**: Additional costs, budget implications
- **Quality Impact**: Quality measures, mitigation plans
- **Scope Impact**: Scope additions/reductions, approval requirements
- **Reason**: Root cause of change
- **Contingency**: Recovery/mitigation plan
- **Risk**: Forward-looking concerns

#### **PowerPoint Change Management Format:**
```
Change Management Summary - [Project Name]

Milestone: [Milestone Name]
Date Change: [Old Date] → [New Date]

IMPACTS: 🕒 Schedule: +X days | 💰 Cost: +£X,XXX | 🎯 Quality: [Description] | 📋 Scope: [Description]
REASON: [Root cause description]
CONTINGENCY: [Recovery plan description]
RISK: [Risk assessment]
```

**Smart Display Logic**: Only show impacts that are not N/A to save slide space

---

## 🚫 DEPRECATED WORKFLOWS

### **~~Workflow #1: MS Project Update & Integration Workflow~~** ❌ **DEPRECATED**
**Status**: ❌ **DEPRECATED - Cross-platform limitations**  
**Reason for Deprecation**: Cannot reliably sync between Linux containerized Control Tower and Windows MS Project

#### **Technical Limitations Identified:**
1. **Cross-Platform File Access**: 
   - Control Tower runs in Linux container
   - MS Project runs on Windows  
   - Direct file path access (`D:\Downloads\ZnNi Line Development Plan-08.mpp`) not available from container
   
2. **COM Interface Limitations**:
   - PowerShell COM interface requires same machine execution
   - Cannot execute MS Project COM commands from Linux environment
   - Network share access unreliable and complex to configure

3. **Authentication & Permissions**:
   - Cross-platform authentication complexities
   - Network drive mounting issues between container and Windows
   - Security restrictions on containerized environment

4. **Real-time Sync Challenges**:
   - No reliable way to detect when MS Project file is updated
   - Manual intervention still required for XML export
   - Automated sync creates more complexity than manual export

#### **Original Workflow (For Reference Only)**:
```bash
# DEPRECATED - Does not work in current environment
python push_project_update.py --description "Update SF Investment Strategy Data Integration"
```

**Why This Approach Failed**:
- Required direct access to Windows MS Project file from Linux
- Attempted automated COM interface execution across platforms
- Complex network share configuration with limited reliability
- Manual XML export is simpler and more reliable than cross-platform automation

---

## 🔧 CURRENT IMPLEMENTATION APPROACH

### **Manual XML Export + Automated Processing** ✅ **RECOMMENDED**

**Philosophy**: Leverage the strengths of each platform rather than fighting cross-platform limitations

#### **Step 1: Manual XML Export (Windows)**
1. **User Action**: Open MS Project on Windows machine
2. **Export**: File → Export → Save as XML Format (.xml)
3. **Upload**: Place XML file in Control Tower xml_workspace via VS Code

#### **Step 2: Automated Processing (Linux)**
1. **Change Detection**: Compare current XML vs previous week's XML
2. **PowerPoint Generation**: Generate updated presentation
3. **Change Management**: Interactive terminal forms for changes
4. **Slide Updates**: Automatically populate change management slides

#### **Benefits of This Approach**:
- ✅ **Reliable**: No cross-platform sync issues
- ✅ **Simple**: Clear manual step + automated processing
- ✅ **Fast**: 2-3 minutes manual export + 5-10 minutes automated processing
- ✅ **Flexible**: Works with any XML updates, not dependent on network connectivity
- ✅ **Audit Trail**: Clear XML snapshots for each Friday update

---

## 📋 IMPLEMENTATION STATUS

### **Ready to Implement:**
- [x] Friday workflow concept defined
- [x] Change management impact assessment structure
- [x] PowerPoint slide formatting rules
- [x] Level 3 project to slide mapping
- [x] Deprecated old workflow with clear technical reasons

### **Next Implementation Steps:**
1. **Create friday_workflow.py** with XML comparison engine
2. **Enhance change management terminal forms** with 4-impact assessment
3. **Update PowerPoint generator** with change management slide population
4. **Test with sample XML files** to validate change detection
5. **Document user guide** for Friday workflow execution

### **File Structure for Implementation:**
```
/workspaces/control_tower/
├── friday_workflow.py                 # Main Friday workflow script
├── modules/
│   ├── xml_comparison/
│   │   ├── __init__.py
│   │   ├── xml_comparator.py         # XML comparison engine
│   │   └── change_detector.py        # Milestone change detection
│   ├── change_management/
│   │   ├── __init__.py
│   │   ├── impact_assessment.py      # 4-impact assessment forms
│   │   └── change_formatter.py       # PowerPoint change formatting
│   └── powerpoint_generation/
│       ├── __init__.py
│       └── change_slide_updater.py   # Change management slide updates
└── xml_workspace/
    ├── current/
    │   └── ZnNi Line Development Plan-08.xml
    └── snapshots/
        ├── friday_20250801.xml
        ├── friday_20250808.xml
        └── friday_20250815.xml
```

---

## 🎯 WORKFLOW EXECUTION EXAMPLES

### **Typical Friday Execution:**
```bash
# 1. User uploads fresh XML to xml_workspace/current/
# 2. Execute Friday workflow
python friday_workflow.py --compare-xml --previous-week snapshots/friday_20250801.xml --generate-powerpoint --change-management

# Example Output:
� MILESTONE CHANGE DETECTION REPORT
=====================================
🔍 Comparing: friday_20250801.xml vs current XML
� CHANGES DETECTED: 3 changes requiring change management forms

📝 CHANGE MANAGEMENT FORMS REQUIRED: 3
1. Training Module 3 Complete (Date slip: +6 days)
2. Equipment Inspection (Date slip: +15 days)  
3. NEW: Safety Documentation Review (New milestone)

✅ PowerPoint generated: contract_projects/powerpoint_reports/REACh_ZnNi_Line_Flash_Report_20250808.pptx
✅ Change management slides updated: Slides 4, 8, 12
✅ Snapshot saved: snapshots/friday_20250808.xml
```

**Total Time**: ~15 minutes (3 min XML export + 12 min change management forms + automated processing)
- **Business Sets**: Levels 1-3 are defined by business requirements (fixed structure)

---

## 🔧 AGREED IMPLEMENTATION APPROACH

### **OPTION 1: STANDALONE XML DIRECT IMPORT** ✅ **CHOSEN APPROACH**

**Decision Date**: August 5, 2025  
**Status**: ✅ **IMPLEMENTED AND ACTIVE**

**Approach**:
- **Direct Import**: Standalone XML files imported directly into MS Project
- **No Integration Step**: Skip merging with main 17MB XML file
- **Simplified Workflow**: Standalone files → MS Project → PowerPoint generation
- **Auto-Launch**: System automatically opens MS Project with standalone XML

**Rationale**:
- ✅ **Simplicity**: Avoids complex XML merging and parsing issues
- ✅ **Performance**: No need to process 17MB main XML file
- ✅ **Reliability**: Direct import eliminates integration failure points
- ✅ **User Experience**: One-click launch with auto-opening MS Project

**Implementation Files**:
- **Main Script**: `/workspaces/control_tower/auto_launch_msproject.py`
- **Remote Execution**: `/workspaces/control_tower/remote_ms_project_launcher.py`
- **Configuration**: `/workspaces/control_tower/config/windows_target.conf`
- **Standalone XML**: `SF_Investment_Strategy_OEE_OLE_Application_Schedule.xml`

**Cross-Platform Execution**:
- **Local Windows**: `python auto_launch_msproject.py --description "Update description"`
- **Linux → Windows**: `python remote_ms_project_launcher.py --description "Update description"`
- **Any Codespaces → Windows**: Uses configured target machine from `config/windows_target.conf`

**User Workflow**:
```bash
# Local execution (when on Windows machine)
python auto_launch_msproject.py --description "Updated Level 4 SF Investment tasks and children"

# Remote execution (from Linux/Codespaces to Windows)
python remote_ms_project_launcher.py --description "Updated Level 4 SF Investment tasks and children"
# Local execution (when on Windows machine)
python auto_launch_msproject.py --description "Updated Level 4 SF Investment tasks and children"

# Remote execution (from Linux/Codespaces to Windows)
python remote_ms_project_launcher.py --description "Updated Level 4 SF Investment tasks and children"

# Result: MS Project opens with standalone XML file directly
# Updates Level 4 project AND its children (Level 5-6 tasks)
# No integration step, no parsing of main XML file
```

### **OPTION 2: INTEGRATED XML APPROACH** ❌ **REJECTED**

**Status**: ❌ **NOT IMPLEMENTED** (Dynamic project identification attempted but abandoned)

**Reason for Rejection**:
- Complex XML parsing of 17MB file
- Dynamic project identification challenges
- Multiple failure points in integration chain
- Performance and reliability concerns

---
- **Implementation Freedom**: Levels 4-6 are how you achieve the business goals
- **Timeline Display**: PowerPoint timeline **always shows Level 4** tasks
- **Milestone Tracking**: PowerPoint milestone pages track **Level 5** milestones
- **Change Management**: Only triggered for **Level 5 milestone impacts** (date changes, scope changes)
- **Granular Updates**: Level 6 task updates are invisible to reporting (too granular for audience)

**Example Structure**:
- **Level 1**: SF Investment Strategy (Business requirement)
- **Level 2**: Data Integration Phase (Business requirement)
- **Level 3**: OEE Reporting Package (Business requirement)
- **Level 4**: 📊 **Timeline Item** - SF Investment Strategy OEE & OLE Application (Your project)
- **Level 5**: 🎯 **Milestone** - Data Architecture Implementation (Key deliverable)
- **Level 6**: Database setup, API configs (Granular work - not reported)

#### **Phase 1: Continuous Sync (MS Project ↔️ Main XML)**
**Status**: 🔍 **VERIFICATION NEEDED**  
**Purpose**: Ensure the main XML file continuously reflects the latest MS Project state

```mermaid
MS Project File ↔️ Main ZnNi XML File
     ↕️                    ↕️
Auto-sync Process    Always Up-to-Date
```

**Requirements**:
- ✅ **Bi-directional sync**: Changes in MS Project automatically update main XML
- ✅ **Real-time updates**: XML file always represents current MS Project state
- ❓ **Current Status**: Needs verification if this sync is working properly

**Files Involved**:
- MS Project: `ZnNi Line Development Plan-08.mpp` (or equivalent)
- Main XML: `/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml`

---

#### **Phase 2: User Agreement (Manual - Pre-Command)**
**Status**: ✅ **PROCESS DEFINED**  
**Purpose**: User reviews and approves implementation work (Levels 4-6) before execution

**Process**:
1. **User Specification**: User identifies implementation work needed
   - Example: "Update Level 5 milestone: SF Investment Strategy Data Pipeline Complete"
   - Example: "Update Level 6 tasks: Database configuration and API setup"
2. **Impact Assessment**: System identifies if changes affect milestones (Level 5)
3. **Approval**: User approves proceeding with the single-command execution

**Output**: User approval to proceed with `push_project_update.py` command

---

#### **Phase 3: Single-Command Complete Workflow (Automated)**
**Status**: ✅ **IMPLEMENTED** - Single command executes everything  
**Purpose**: Complete end-to-end update: MS Project + PowerPoint + Change Management

```bash
# THE COMPLETE WORKFLOW - ONE COMMAND
python push_project_update.py --description "Update SF Investment Strategy Data Integration"
```

**What This Single Command Does**:
```
┌─ MS Project Updates ──────────────────────┐
│ 1. Read implementation updates (L4-6)     │
│ 2. Integrate into main XML                │
│ 3. Sync updated XML → MS Project app      │
│ 4. 🎯 MILESTONE CHECK: Level 5 impacted?  │
│ 5. If YES: Change management form         │
│ 6. If NO: Silent update (too granular)    │
└────────────────────────────────────────────┘
                         ↓
┌─ PowerPoint Updates (If Milestones Change)┐
│ 7. Timeline slide (Level 4 overview)     │
│ 8. Milestone slide (Level 5 tracking)    │
│ 9. Change mgmt slide (milestone impacts) │
└────────────────────────────────────────────┘
```

**Complete Workflow Steps (All in Single Command)**:

1. **Implementation XML Integration** ✅ **WORKING**
   - Script: `update_znni_project.py`
   - Process: Read implementation updates (L4-6) → Integrate into main XML
   - Recent Fix: Reads from standalone files, preserves hierarchical structure

2. **Milestone Impact Detection** ❓ **NEEDS IMPLEMENTATION**
   - Detect if Level 5 milestones are affected by the update
   - Only proceed to change management if milestones impacted
   - Skip change management for granular Level 6 task updates

3. **Conditional Change Management Form** ✅ **WORKING** (needs milestone gating)
   - Opens in terminal **only if Level 5 milestones affected**
   - Captures milestone impact description and approval
   - Data flows to PowerPoint change management slides

4. **MS Project Synchronization** ✅ **FIXED** - Export functionality restored
   - **Solution**: Added missing `export_for_ms_project()` call to main workflow
   - **Functionality**: Exports updated XML for manual import into MS Project
   - **Process**: Creates timestamped XML file with import instructions
   - **Status**: XML → MS Project export now integrated into workflow

5. **PowerPoint Generation** ✅ **WORKING** (needs level-specific updates)
   - **Timeline slide**: Level 4 tasks for executive overview
   - **Milestone slide**: Level 5 milestones for delivery tracking
   - **Change management slide**: Only milestone-level impacts

**User Experience**: Run one command → (Conditional: Fill change management form if milestones impacted) → Get updated MS Project + PowerPoint

**Files Involved**:
- Integration: `/cloned_repos/contract_projects/xml_workspace/update_znni_project.py`
- Workflow: `/workspaces/control_tower/push_project_update.py`
- PowerPoint: `/modules/milestone_management/reporting/safran_powerpoint_generator.py`

---

## 🔧 WORKFLOW COMPONENTS

### **Component A: XML Integration Engine**
**File**: `update_znni_project.py`  
**Status**: ✅ **RECENTLY FIXED**

**Functionality**:
- ✅ **Dynamic Reading**: Reads from standalone XML files (not hardcoded)
- ✅ **Implementation Updates**: Handles Level 4-6 task integration
- ✅ **Section Replacement**: Overwrites existing project sections with updates
- ✅ **UID Management**: Handles task ID conflicts and dependencies

**Recent Improvements** (August 4, 2025):
```python
# NEW: Dynamic reading from standalone files
def read_standalone_sf_tasks():
    """Read tasks from the standalone SF Investment Strategy XML file"""
    # Reads actual file instead of hardcoded content
    # Handles implementation-level updates (L4-6)
    # Falls back to hardcoded content if file missing

# FIXED: Main integration function
def update_znni_project():
    new_tasks = read_standalone_sf_tasks()  # Was: generate_comprehensive_tasks()
```

### **Component B: Milestone Impact Detection System**
**File**: `modules/ms_project/contract_project_manager.py`  
**Status**: ❓ **NEEDS IMPLEMENTATION**

**Functionality**:
- ❓ **Milestone Detection**: Identify if Level 5 milestones are affected by updates
- ❓ **Impact Assessment**: Determine if changes warrant change management reporting
- ❓ **Conditional Triggering**: Only open change management form for milestone impacts
- ❓ **Granular Filtering**: Ignore Level 6 task updates (too granular for reporting)

### **Component C: Change Management System**
**File**: `modules/ms_project/contract_project_manager.py`  
**Status**: ✅ **WORKING** (needs milestone gating)

**Functionality**:
- ✅ **Terminal Interface**: Opens change management form in terminal
- ✅ **Data Capture**: Records milestone impact description and approval
- ✅ **Workflow Integration**: Feeds data to PowerPoint generation
- ❓ **Milestone Gating**: Only activate for Level 5 milestone impacts
- ❓ **Data Persistence**: Verify milestone change data appears in final presentations

### **Component D: PowerPoint Generation Engine**
**File**: `modules/milestone_management/reporting/safran_powerpoint_generator.py`  
**Status**: ✅ **WORKING** (needs level-specific updates)

**Functionality**:
- ✅ **Safran Branding**: Corporate colors, logos, formatting
- ✅ **4-Slide Pattern**: Title → Timeline → 4-Table → Change Management
- ❓ **Level 4 Timeline Display**: Timeline slides show Level 4 tasks for executive overview
- ❓ **Level 5 Milestone Tracking**: Milestone slides track Level 5 deliverables
- ✅ **3-Phase Structure**: Documentation & Training, Critical Maintenance, Post Stabilization

---

## 📊 WORKFLOW STATUS MATRIX

| Phase | Component | Status | Next Action |
|-------|-----------|--------|-------------|
| 1 | MS Project ↔️ XML Sync | ❓ Needs Verification | Test sync functionality |
| 2 | User Agreement Process | ✅ Process Defined | Document approval procedures |
| 3 | **Single-Command Workflow** | **🔧 Ready for Enhancement** | **Add milestone impact detection** |
| 3.1 | Implementation XML Integration | ✅ Fixed (reads standalone) | Test Level 4-6 integration |
| 3.2 | Milestone Impact Detection | ❓ **NEEDS IMPLEMENTATION** | **Detect Level 5 impacts** |
| 3.3 | Conditional Change Management | ✅ Working (needs gating) | Add milestone trigger logic |
| 3.4 | MS Project Sync | ❓ Needs Verification | Test XML → MS Project updates |
| 3.5 | PowerPoint Timeline (Level 4) | ✅ **WORKING** | **Level 4 filtering successful - 33 tasks detected** |
| 3.6 | PowerPoint Milestones (Level 5) | ✅ **WORKING** | **Level 5 milestone tracking active** |
| 3.7 | PowerPoint Change Mgmt | ❓ Needs Verification | Test milestone impact data |

**Key Priority**: 🎉 **LEVEL HIERARCHY RESOLVED** - PowerPoint workflow successfully generating presentations with L4 timeline and L5 milestones

---

## 🎯 WORKFLOW TESTING PROCEDURES

### **Test 1: End-to-End SF Investment Strategy Update** ✅ **LEVEL STRUCTURE FIXED**
**Purpose**: Verify complete workflow from implementation update to PowerPoint presentation

**Status**: 🚀 **READY FOR COMPLETE TESTING** - Level hierarchy restructured

**Completed Steps**:
1. ✅ **Level Hierarchy Analysis**: Identified SF Investment Strategy used L0,1,2 instead of required L1-3 (business) + L4-5 (implementation)
2. ✅ **Data Extraction**: Successfully extracted all task data from original XML structure
3. ✅ **Business Logic Restructuring**: Converted L2 tasks → L4 (timeline), L2 milestones → L5 (milestone tracking)
4. ✅ **XML Generation**: Created properly structured XML file with correct namespace and encoding
5. ✅ **Validation**: Confirmed restructured file has L4 tasks and L5 milestones as required

**Restructuring Results**:
- **Level 0**: 1 item (Project Summary) ✅
- **Level 1**: 2 items (Business Phases) ✅ 
- **Level 4**: 5 items (Implementation Tasks - for timeline display) ✅
- **Level 5**: 2 items (Milestones - for milestone tracking) ✅

**Next Testing Steps**:
1. ✅ **Verify Phase 1**: Main XML now has correct structure
2. ✅ **Ready for Phase 3**: Test `push_project_update.py` workflow with restructured file
3. ✅ **Verify Results**: **COMPLETE WORKFLOW SUCCESS!**
   - ✅ **Level 4 tasks appear in PowerPoint timeline** - 33 Level 4 tasks detected and included
   - ✅ **Level 5 milestones tracked in PowerPoint milestone pages** - Milestone tracking active
   - ✅ **PowerPoint generated successfully** - `REACh_ZnNi_Line_Flash_Report_04082025_ControlTower.pptx`

**Success Criteria**: ✅ **ALL CRITERIA MET**
- ✅ Main XML file has correct structure (Level 4/5 hierarchy)
- ✅ Standalone XML integrates without errors  
- ✅ Level 4 tasks appear on PowerPoint timeline slides (33 tasks included)
- ✅ Level 5 milestones tracked on PowerPoint milestone pages
- ✅ Adaptive filtering prefers Level 4 over Level 2 ("Level 4 (preferred)")
- ✅ PowerPoint generation complete with Safran branding (12 pages)

### **Test 2: Multiple Project Updates**
**Purpose**: Verify workflow handles multiple project updates without conflicts

**Steps**:
1. Update SF Investment Strategy project
2. Update different project (e.g., ZnNi Phase 2)
3. Verify both updates integrate correctly
4. Check for UID conflicts or dependency issues

---

## 🔄 WORKFLOW OPTIMIZATION OPPORTUNITIES

### **Short Term (Next 2 weeks)**
1. **Verify Phase 1 Sync**: Ensure MS Project ↔️ XML sync is working
2. **Test Integration Fix**: Confirm Level 4 tasks are preserved
3. **Validate PowerPoint Output**: Check SF Investment Strategy appears in timeline

### **Medium Term (Next month)**
1. **Implement Phase 2 Command**: Create `--project` selection interface
2. **Add Plan Generation**: Logic to extract and update specific projects
3. **Create Approval System**: Interactive approval gate before integration

### **Long Term (Next quarter)**
1. **Automated Sync Monitoring**: Alert if Phase 1 sync fails
2. **Web Interface**: Replace command-line with web-based workflow
3. **Multi-User Support**: Handle concurrent project updates

---

## 📚 RELATED DOCUMENTATION

- **Issue Tracking**: `CONTROL_TOWER_ISSUE_LOG.md` - Current problems and resolutions
- **Roadmap**: `CONTROL_TOWER_ROADMAP.md` - Development priorities and features
- **PowerPoint Details**: `/modules/milestone_management/reporting/` - Generator implementation
- **Commands**: `CONTROL_TOWER_COMMANDS.md` - Available command reference

---

## 🚨 KNOWN WORKFLOW ISSUES

Refer to `CONTROL_TOWER_ISSUE_LOG.md` for current active issues:
- **Issue #001**: SF Investment Strategy missing from PowerPoint timeline (Level 4 structure)
- **Issue #002**: MS Project XML updates sync verification needed
- **Issue #003**: Change management data persistence in presentations

---

## 📝 WORKFLOW CHANGE LOG

| Date | Change | Impact | Author |
|------|--------|--------|--------|
| Aug 4, 2025 | **BUSINESS LOGIC CLARIFIED: L1-3 business set, L4-6 implementation** | **Timeline=L4, Milestones=L5, Change Mgmt=L5 only** | **James Fleming** |
| Aug 4, 2025 | INSIGHT: Level-agnostic update system needed | Projects use different anchor levels (L2, L3, L4) | James Fleming |
| Aug 4, 2025 | Fixed XML integration to read standalone files | Level 4 preservation | James Fleming |
| Aug 4, 2025 | Created workflow documentation | Process clarity | James Fleming |
| Aug 1, 2025 | Implemented Safran PowerPoint generator | Professional presentations | James Fleming |

---

**Document Maintained By**: James Fleming  
**Next Review**: August 11, 2025  
**Workflow Version**: 1.0
