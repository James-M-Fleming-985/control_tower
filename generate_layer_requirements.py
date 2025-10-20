#!/usr/bin/env python3
"""
Generate Layer Requirements for PROJECT-003
Creates properly structured YAML requirement files with full traceability chain
"""

from pathlib import Path
from datetime import datetime
import yaml

# Define the layer specifications with traceability
LAYER_SPECS = {
    "FEATURE-003-001": {
        "feature_id": "FEATURE-003-001",
        "feature_name": "Data Reader Parser",
        "feature_description": "Reads and parses YAML/XML configuration files",
        "system_id": "SYSTEM-003",
        "prj_reqs": ["PRJ-REQ-001: Configuration-driven reporting system"],
        "sys_reqs": ["SYS-REQ-001: File-based data persistence", "SYS-REQ-008: YAML and XML parsing support"],
        "sys_comps": ["COMP-001: Data Reader", "COMP-002: Data Model Validator"],
        "layers": [
            {
                "layer_id": "LAYER-003-001-002",
                "req_id": "REQ-003-001-002",
                "layer_name": "Data_Model_Validator",
                "title": "Data Model Validator",
                "description": "Validate parsed data against Pydantic models to ensure consistency, completeness, and correctness. Apply validation rules, handle errors gracefully, return validated model instances.",
                "rationale": "Data integrity is critical before processing. Pydantic ensures type safety and business rule enforcement at the data entry point.",
                "classes": [
                    {
                        "name": "DataValidator",
                        "purpose": "Validate data against schema",
                        "methods": [
                            "validate_yaml_data(data: dict) -> ConfigModel",
                            "validate_xml_data(data: dict) -> ConfigModel"
                        ]
                    }
                ],
                "inputs": ["Parsed dictionaries from LAYER-003-001-001"],
                "outputs": ["Validated Pydantic model instances"],
                "depends_on": ["LAYER-003-001-001"],
                "consumed_by": ["LAYER-003-002-001"],
                "libraries": ["pydantic>=2.0"],
                "duration": "1.5 hours"
            },
            {
                "layer_id": "LAYER-003-001-003",
                "req_id": "REQ-003-001-003",
                "layer_name": "Schema_Compliance_Checker",
                "title": "Schema Compliance Checker",
                "description": "Validate configuration files against JSON schema definitions. Ensure all required fields are present, data types match specifications, value constraints are satisfied.",
                "rationale": "Schema validation catches configuration errors early. Prevents runtime failures caused by malformed config files.",
                "classes": [
                    {
                        "name": "SchemaValidator",
                        "purpose": "Validate against JSON schemas",
                        "methods": [
                            "load_schema(schema_path: Path) -> dict",
                            "validate_config(config: dict, schema: dict) -> bool",
                            "get_validation_errors() -> List[str]"
                        ]
                    }
                ],
                "inputs": ["Configuration dictionaries, JSON schema files"],
                "outputs": ["Validation results, error messages"],
                "depends_on": ["LAYER-003-001-001"],
                "consumed_by": ["LAYER-003-001-002"],
                "libraries": ["jsonschema>=4.0"],
                "duration": "1.5 hours"
            }
        ]
    },
    "FEATURE-003-002": {
        "feature_name": "Risk Aggregator",
        "prj_reqs": ["PRJ-REQ-002: Three-section report structure"],
        "sys_reqs": ["SYS-REQ-001: File-based data persistence", "SYS-REQ-004: Business Logic Layer"],
        "sys_comps": ["COMP-004: Risk Aggregator"],
        "layers": [
            {
                "layer_id": "LAYER-003-002-001",
                "req_id": "REQ-003-002-001",
                "layer_name": "Risk_File_Reader",
                "title": "Risk File Reader",
                "description": "Read risks.yaml files from all project folders using FileReaderFactory. Scan professional_excellence/projects/ directory, identify risk files, parse content, return list of Risk models.",
                "rationale": "Centralized risk file discovery and reading. Reuses LAYER-003-001-001 file reading infrastructure for consistency.",
                "classes": [
                    {
                        "name": "RiskFileScanner",
                        "purpose": "Scan project folders for risk files",
                        "methods": [
                            "scan_all_projects() -> List[Path]",
                            "read_risk_file(path: Path) -> List[Risk]"
                        ]
                    }
                ],
                "inputs": ["Project folder paths"],
                "outputs": ["List of Risk objects from all projects"],
                "depends_on": ["LAYER-003-001-001"],
                "consumed_by": ["LAYER-003-002-002"],
                "libraries": ["pyyaml>=6.0"],
                "duration": "1.5 hours"
            },
            {
                "layer_id": "LAYER-003-002-002",
                "req_id": "REQ-003-002-002",
                "layer_name": "Risk_Filter_Logic",
                "title": "Risk Filter Logic",
                "description": "Filter risks by status (active/open), group by section (Critical Documentation, Critical Maintenance, Post-Stabilization), calculate risk severity score (probability × impact), sort by severity.",
                "rationale": "Business logic for risk prioritization. Ensures only relevant active risks appear in report, grouped appropriately for each section's slide.",
                "classes": [
                    {
                        "name": "RiskFilter",
                        "purpose": "Filter and categorize risks",
                        "methods": [
                            "filter_active(risks: List[Risk]) -> List[Risk]",
                            "group_by_section(risks: List[Risk]) -> Dict[str, List[Risk]]",
                            "calculate_severity(risk: Risk) -> int"
                        ]
                    }
                ],
                "inputs": ["List of Risk objects from LAYER-003-002-001"],
                "outputs": ["Filtered and grouped risks by section"],
                "depends_on": ["LAYER-003-002-001"],
                "consumed_by": ["LAYER-003-002-003"],
                "libraries": [],
                "duration": "2 hours"
            },
            {
                "layer_id": "LAYER-003-002-003",
                "req_id": "REQ-003-002-003",
                "layer_name": "Risk_Table_Formatter",
                "title": "Risk Table Formatter",
                "description": "Format risks as tables for PowerPoint insertion. Create data structure with columns (Risk ID, Description, Probability, Impact, Mitigation, Owner), apply color coding (High=Red, Medium=Yellow, Low=Green).",
                "rationale": "Transforms risk data into PowerPoint-ready format. Separates data logic from presentation, making it easy to change table styling without affecting filtering logic.",
                "classes": [
                    {
                        "name": "RiskTableFormatter",
                        "purpose": "Format risks for PowerPoint tables",
                        "methods": [
                            "format_table(risks: List[Risk]) -> TableData",
                            "apply_color_coding(risk: Risk) -> ColorScheme",
                            "generate_summary_stats(risks: List[Risk]) -> Dict[str, int]"
                        ]
                    }
                ],
                "inputs": ["Filtered risks from LAYER-003-002-002"],
                "outputs": ["TableData structure ready for PowerPoint insertion"],
                "depends_on": ["LAYER-003-002-002"],
                "consumed_by": ["FEATURE-003-006"],
                "libraries": [],
                "duration": "1.5 hours"
            }
        ]
    },
    
    "FEATURE-003-003": {
        "feature_name": "Gantt Chart Generator",
        "prj_reqs": ["PRJ-REQ-002: Three-section report structure", "PRJ-REQ-005: Professional presentation with org branding"],
        "sys_reqs": ["SYS-REQ-004: Presentation Layer", "SYS-REQ-007: Report generation < 10 seconds"],
        "sys_comps": ["COMP-005: Gantt Chart Generator"],
        "layers": [
            {
                "layer_id": "LAYER-003-003-001",
                "req_id": "REQ-003-003-001",
                "layer_name": "Chart_Data_Preparation",
                "title": "Chart Data Preparation",
                "description": "Transform ProjectPlan objects into chart-ready data structures. Calculate bar positions, durations, grouping by section, handle project dependencies, compute critical path.",
                "rationale": "Separates data transformation from visualization. Makes it easy to switch chart libraries (matplotlib → plotly) without changing data logic.",
                "classes": [
                    {
                        "name": "GanttDataPrep",
                        "purpose": "Prepare project data for Gantt visualization",
                        "methods": [
                            "calculate_bar_positions(projects: List[ProjectPlan]) -> List[BarData]",
                            "group_by_section(projects: List[ProjectPlan]) -> Dict[str, List[ProjectPlan]]",
                            "calculate_duration(project: ProjectPlan) -> int"
                        ]
                    }
                ],
                "inputs": ["List of ProjectPlan objects"],
                "outputs": ["Chart-ready data structures (bar positions, durations, labels)"],
                "depends_on": ["LAYER-003-001-003"],
                "consumed_by": ["LAYER-003-003-002"],
                "libraries": ["pandas>=1.5.0"],
                "duration": "2 hours"
            },
            {
                "layer_id": "LAYER-003-003-002",
                "req_id": "REQ-003-003-002",
                "layer_name": "Matplotlib_Chart_Builder",
                "title": "Matplotlib Chart Builder",
                "description": "Generate Gantt chart images using matplotlib. Create horizontal bar chart (one bar per project), apply color scheme, add gridlines and labels, ensure readability at 1920x1080 projection.",
                "rationale": "Matplotlib provides fine-grained control over chart appearance. Generates static PNG images suitable for PowerPoint insertion.",
                "classes": [
                    {
                        "name": "MatplotlibGanttBuilder",
                        "purpose": "Build Gantt charts with matplotlib",
                        "methods": [
                            "create_chart(chart_data: ChartData) -> Figure",
                            "apply_styling(fig: Figure) -> Figure",
                            "add_gridlines(ax: Axes) -> None"
                        ]
                    }
                ],
                "inputs": ["Chart-ready data from LAYER-003-003-001"],
                "outputs": ["matplotlib Figure object"],
                "depends_on": ["LAYER-003-003-001"],
                "consumed_by": ["LAYER-003-003-003"],
                "libraries": ["matplotlib>=3.5.0"],
                "duration": "2.5 hours"
            },
            {
                "layer_id": "LAYER-003-003-003",
                "req_id": "REQ-003-003-003",
                "layer_name": "Image_Export",
                "title": "Image Export",
                "description": "Export matplotlib Figure to PNG image file with high DPI (300), optimal dimensions for PowerPoint (10x6 inches), save to temp directory, return Path for PowerPoint insertion.",
                "rationale": "Standardizes image export parameters. Ensures consistent image quality across all generated charts.",
                "classes": [
                    {
                        "name": "GanttImageExporter",
                        "purpose": "Export Gantt charts as PNG images",
                        "methods": [
                            "export_to_png(fig: Figure, output_path: Path) -> Path",
                            "optimize_for_powerpoint(fig: Figure) -> Figure",
                            "set_dpi(dpi: int) -> None"
                        ]
                    }
                ],
                "inputs": ["matplotlib Figure from LAYER-003-003-002"],
                "outputs": ["Path to PNG image file"],
                "depends_on": ["LAYER-003-003-002"],
                "consumed_by": ["FEATURE-003-006"],
                "libraries": ["matplotlib>=3.5.0", "Pillow>=9.0.0"],
                "duration": "1 hour"
            }
        ]
    },
    
    "FEATURE-003-004": {
        "feature_name": "Milestone Tracker",
        "prj_reqs": ["PRJ-REQ-002: Three-section report structure"],
        "sys_reqs": ["SYS-REQ-004: Business Logic Layer", "SYS-REQ-007: Report generation < 10 seconds"],
        "sys_comps": ["COMP-003: Milestone Calculator"],
        "layers": [
            {
                "layer_id": "LAYER-003-004-001",
                "req_id": "REQ-003-004-001",
                "layer_name": "Date_Calculator",
                "title": "Date Calculator",
                "description": "Calculate date ranges for milestone categorization. Determine 'this month' (current month start to end), 'next month', 'last month' date ranges. Handle edge cases (year boundaries, leap years).",
                "rationale": "Centralized date logic prevents inconsistencies. Using Python datetime ensures correct handling of complex date scenarios.",
                "classes": [
                    {
                        "name": "DateCalculator",
                        "purpose": "Calculate date ranges for milestone filtering",
                        "methods": [
                            "get_this_month_range() -> Tuple[date, date]",
                            "get_next_month_range() -> Tuple[date, date]",
                            "get_last_month_range() -> Tuple[date, date]",
                            "is_date_in_range(target: date, start: date, end: date) -> bool"
                        ]
                    }
                ],
                "inputs": ["Current date (datetime.now())"],
                "outputs": ["Date ranges for milestone filtering"],
                "depends_on": [],
                "consumed_by": ["LAYER-003-004-002"],
                "libraries": [],
                "duration": "1.5 hours"
            },
            {
                "layer_id": "LAYER-003-004-002",
                "req_id": "REQ-003-004-002",
                "layer_name": "Milestone_Categorizer",
                "title": "Milestone Categorizer",
                "description": "Categorize milestones into four quadrants: due this month, due next month, completed last month, active risks (delayed milestones). Use date ranges from LAYER-003-004-001, filter milestones from all projects.",
                "rationale": "Implements four-quadrant milestone view business logic. Clear separation allows easy modification of categorization rules.",
                "classes": [
                    {
                        "name": "MilestoneCategorizer",
                        "purpose": "Categorize milestones by date and status",
                        "methods": [
                            "categorize_milestones(projects: List[ProjectPlan]) -> MilestoneQuadrants",
                            "get_due_this_month(milestones: List[Milestone]) -> List[Milestone]",
                            "get_delayed_milestones(milestones: List[Milestone]) -> List[Milestone]"
                        ]
                    }
                ],
                "inputs": ["List of ProjectPlan objects, date ranges from LAYER-003-004-001"],
                "outputs": ["MilestoneQuadrants object with categorized milestones"],
                "depends_on": ["LAYER-003-004-001", "LAYER-003-001-003"],
                "consumed_by": ["LAYER-003-004-003"],
                "libraries": [],
                "duration": "2 hours"
            },
            {
                "layer_id": "LAYER-003-004-003",
                "req_id": "REQ-003-004-003",
                "layer_name": "Quadrant_Formatter",
                "title": "Quadrant Formatter",
                "description": "Format categorized milestones for PowerPoint four-quadrant layout. Create data structure for each quadrant (top-left, top-right, bottom-left, bottom-right), include milestone name, project, date, status indicator.",
                "rationale": "Prepares milestone data in PowerPoint-ready format. Separates data preparation from PowerPoint API calls.",
                "classes": [
                    {
                        "name": "QuadrantFormatter",
                        "purpose": "Format milestones for four-quadrant slide layout",
                        "methods": [
                            "format_quadrants(quadrants: MilestoneQuadrants) -> QuadrantData",
                            "format_milestone_row(milestone: Milestone) -> Dict[str, str]",
                            "apply_status_icons(milestone: Milestone) -> str"
                        ]
                    }
                ],
                "inputs": ["MilestoneQuadrants from LAYER-003-004-002"],
                "outputs": ["QuadrantData ready for PowerPoint insertion"],
                "depends_on": ["LAYER-003-004-002"],
                "consumed_by": ["FEATURE-003-006"],
                "libraries": [],
                "duration": "1.5 hours"
            }
        ]
    },
    
    "FEATURE-003-005": {
        "feature_name": "Change Management Logger",
        "prj_reqs": ["PRJ-REQ-001: Automated PowerPoint report generation"],
        "sys_reqs": ["SYS-REQ-001: File-based data persistence", "SYS-REQ-003: On-demand execution", "SYS-REQ-004: Presentation Layer"],
        "sys_comps": ["COMP-007: Change Management UI"],
        "layers": [
            {
                "layer_id": "LAYER-003-005-001",
                "req_id": "REQ-003-005-001",
                "layer_name": "Terminal_UI",
                "title": "Terminal UI",
                "description": "Interactive terminal UI using Rich library. Display project and milestone lists in tables, prompt for milestone selection, collect new dates with validation, prompt for reason and contingency, confirm changes before saving.",
                "rationale": "Rich library provides professional terminal UI with tables, colors, and prompts. User-friendly interface for non-technical users.",
                "classes": [
                    {
                        "name": "ChangeManagementUI",
                        "purpose": "Interactive terminal interface for schedule changes",
                        "methods": [
                            "display_projects(projects: List[ProjectPlan]) -> None",
                            "select_milestone(project: ProjectPlan) -> Milestone",
                            "prompt_for_new_date() -> date",
                            "prompt_for_reason() -> str",
                            "confirm_change(change: ChangeEntry) -> bool"
                        ]
                    }
                ],
                "inputs": ["User keyboard input"],
                "outputs": ["ChangeEntry object with user inputs"],
                "depends_on": ["LAYER-003-001-003"],
                "consumed_by": ["LAYER-003-005-002"],
                "libraries": ["rich>=13.0.0"],
                "duration": "2.5 hours"
            },
            {
                "layer_id": "LAYER-003-005-002",
                "req_id": "REQ-003-005-002",
                "layer_name": "Change_Data_Collector",
                "title": "Change Data Collector",
                "description": "Collect and structure change data from UI inputs. Create ChangeEntry object with timestamp, old/new values, reason, contingency. Validate data completeness and business rules (new date > current date).",
                "rationale": "Separates UI layer from data logic. Ensures change data structure is consistent regardless of UI implementation (terminal, web, API).",
                "classes": [
                    {
                        "name": "ChangeDataCollector",
                        "purpose": "Structure and validate change data",
                        "methods": [
                            "create_change_entry(milestone: Milestone, new_date: date, reason: str, contingency: str) -> ChangeEntry",
                            "validate_change_data(entry: ChangeEntry) -> ValidationResult",
                            "generate_change_id() -> str"
                        ]
                    }
                ],
                "inputs": ["User inputs from LAYER-003-005-001"],
                "outputs": ["Validated ChangeEntry object"],
                "depends_on": ["LAYER-003-005-001"],
                "consumed_by": ["LAYER-003-005-003"],
                "libraries": [],
                "duration": "1.5 hours"
            },
            {
                "layer_id": "LAYER-003-005-003",
                "req_id": "REQ-003-005-003",
                "layer_name": "Log_File_Writer",
                "title": "Log File Writer",
                "description": "Write change entries to change_log.yaml files. Append new entries to existing log, update project_plan.yaml with new milestone date, create backup before modification, handle file locking for concurrent access.",
                "rationale": "Centralized file writing logic with safety features. Backups prevent data loss, file locking prevents corruption from concurrent updates.",
                "classes": [
                    {
                        "name": "ChangeLogWriter",
                        "purpose": "Persist changes to YAML files",
                        "methods": [
                            "append_to_log(entry: ChangeEntry, log_path: Path) -> None",
                            "update_project_plan(project_id: str, milestone_id: str, new_date: date) -> None",
                            "create_backup(file_path: Path) -> Path"
                        ]
                    }
                ],
                "inputs": ["ChangeEntry from LAYER-003-005-002"],
                "outputs": ["Updated change_log.yaml and project_plan.yaml files"],
                "depends_on": ["LAYER-003-005-002", "LAYER-003-001-001"],
                "consumed_by": [],
                "libraries": ["pyyaml>=6.0"],
                "duration": "2 hours"
            }
        ]
    },
    
    "FEATURE-003-006": {
        "feature_name": "PowerPoint Generator",
        "prj_reqs": ["PRJ-REQ-001: Automated PowerPoint report generation", "PRJ-REQ-002: Three-section report structure", "PRJ-REQ-005: Professional presentation with org branding"],
        "sys_reqs": ["SYS-REQ-004: Presentation Layer", "SYS-REQ-006: Factory Pattern for slide generation", "SYS-REQ-007: Report generation < 10 seconds"],
        "sys_comps": ["COMP-006: PowerPoint Builder", "COMP-008: Report Orchestrator"],
        "layers": [
            {
                "layer_id": "LAYER-003-006-001",
                "req_id": "REQ-003-006-001",
                "layer_name": "Slide_Factory",
                "title": "Slide Factory",
                "description": "Factory to create different slide types (title, Gantt, status, change management). Implement Factory Pattern, return appropriate SlideBuilder based on slide type, encapsulate slide creation logic.",
                "rationale": "Factory Pattern allows easy addition of new slide types. Centralizes slide creation, making it easy to maintain consistent styling.",
                "classes": [
                    {
                        "name": "SlideFactory",
                        "purpose": "Create different types of slides",
                        "methods": [
                            "create_title_slide(prs: Presentation, title: str) -> Slide",
                            "create_gantt_slide(prs: Presentation, section: str, chart_path: Path) -> Slide",
                            "create_status_slide(prs: Presentation, section: str, quadrants: QuadrantData, risks: TableData) -> Slide",
                            "create_change_slide(prs: Presentation, section: str, changes: List[ChangeEntry]) -> Slide"
                        ]
                    }
                ],
                "inputs": ["Presentation object, slide-specific data"],
                "outputs": ["Slide object with content"],
                "depends_on": [],
                "consumed_by": ["LAYER-003-006-003"],
                "libraries": ["python-pptx>=0.6.21"],
                "duration": "3 hours"
            },
            {
                "layer_id": "LAYER-003-006-002",
                "req_id": "REQ-003-006-002",
                "layer_name": "Theme_Applier",
                "title": "Theme Applier",
                "description": "Load and apply organization PowerPoint theme template. Copy master slides, apply color scheme, fonts, logos. Ensure consistency across all generated slides.",
                "rationale": "Separates branding logic from content generation. Easy to swap themes without changing content code.",
                "classes": [
                    {
                        "name": "ThemeApplier",
                        "purpose": "Apply organization theme to presentation",
                        "methods": [
                            "load_template(template_path: Path) -> Presentation",
                            "apply_color_scheme(prs: Presentation, scheme: ColorScheme) -> None",
                            "apply_fonts(prs: Presentation, font_config: FontConfig) -> None",
                            "copy_master_slides(source: Presentation, target: Presentation) -> None"
                        ]
                    }
                ],
                "inputs": ["Template PowerPoint file path"],
                "outputs": ["Presentation object with theme applied"],
                "depends_on": [],
                "consumed_by": ["LAYER-003-006-004"],
                "libraries": ["python-pptx>=0.6.21"],
                "duration": "2.5 hours"
            },
            {
                "layer_id": "LAYER-003-006-003",
                "req_id": "REQ-003-006-003",
                "layer_name": "Content_Inserter",
                "title": "Content Inserter",
                "description": "Insert content into slide placeholders. Add Gantt chart images, populate milestone tables, insert risk tables, format change management entries. Handle text sizing, alignment, and overflow.",
                "rationale": "Abstracts python-pptx API complexity. Provides simple methods for common content insertion operations.",
                "classes": [
                    {
                        "name": "ContentInserter",
                        "purpose": "Insert various content types into slides",
                        "methods": [
                            "insert_image(slide: Slide, image_path: Path, position: Position) -> None",
                            "insert_table(slide: Slide, table_data: TableData, position: Position) -> None",
                            "insert_text(slide: Slide, text: str, placeholder_id: int) -> None",
                            "format_table_cell(cell: Cell, color: str, bold: bool) -> None"
                        ]
                    }
                ],
                "inputs": ["Slide objects, content data (images, tables, text)"],
                "outputs": ["Slides with content inserted"],
                "depends_on": ["LAYER-003-006-001"],
                "consumed_by": ["LAYER-003-006-004"],
                "libraries": ["python-pptx>=0.6.21"],
                "duration": "3.5 hours"
            },
            {
                "layer_id": "LAYER-003-006-004",
                "req_id": "REQ-003-006-004",
                "layer_name": "Report_Assembler",
                "title": "Report Assembler",
                "description": "Orchestrate complete report generation. Coordinate all previous layers (data reading, chart generation, milestone tracking, risk aggregation). Generate all 9 slides (3 per section), apply theme, save final PowerPoint file.",
                "rationale": "Top-level orchestration layer. Implements workflow from PROJECT_REQUIREMENTS.yaml, coordinates all features into cohesive report.",
                "classes": [
                    {
                        "name": "ReportAssembler",
                        "purpose": "Orchestrate complete report generation",
                        "methods": [
                            "generate_report(output_path: Path) -> None",
                            "generate_section(section_name: str, projects: List[ProjectPlan]) -> List[Slide]",
                            "validate_all_data() -> ValidationResult",
                            "save_report(prs: Presentation, output_path: Path) -> Path"
                        ]
                    }
                ],
                "inputs": ["All feature outputs (charts, milestones, risks, changes)"],
                "outputs": ["Complete PowerPoint file at specified path"],
                "depends_on": ["LAYER-003-006-002", "LAYER-003-006-003", "FEATURE-003-001", "FEATURE-003-002", "FEATURE-003-003", "FEATURE-003-004"],
                "consumed_by": [],
                "libraries": ["python-pptx>=0.6.21"],
                "duration": "4 hours"
            }
        ]
    }
}


def generate_layer_requirement(feature_id: str, feature_data: dict, layer_spec: dict) -> str:
    """Generate a complete layer requirement YAML document."""
    
    req_template = f"""# ================================================================================
# LAYER REQUIREMENT: {layer_spec['title']}
# ================================================================================
# REQUIREMENT ID: {layer_spec['req_id']}
# FEATURE: {feature_id} ({feature_data['feature_name']})
# LAYER: {layer_spec['layer_id']} ({layer_spec['layer_name']})
# VERSION: 1.0.0
# STATUS: Active
# ================================================================================

metadata:
  requirement_id: "{layer_spec['req_id']}"
  requirement_title: "{layer_spec['title']}"
  layer: "{layer_spec['layer_id'].replace('LAYER-', 'LAYER-').split('-', 3)[3]}_{layer_spec['layer_name']}"
  feature: "{feature_id}_{feature_data['feature_name'].replace(' ', '_')}"
  version: "1.0.0"
  status: "Active"
  priority: "MUST HAVE"
  created_date: "{datetime.now().strftime('%Y-%m-%d')}"
  updated_date: "{datetime.now().strftime('%Y-%m-%d')}"
  owner: "James Fleming"
  target_date: "2025-10-31"
  change_log:
    - version: "1.0.0"
      date: "{datetime.now().strftime('%Y-%m-%d')}"
      changes: "Initial version - {layer_spec['title']}"

# ================================================================================
# REQUIREMENT DEFINITION
# ================================================================================

requirement:
  title: "{layer_spec['title']}"
  
  description: |
    {layer_spec['description']}
  
  rationale: |
    {layer_spec['rationale']}

# ================================================================================
# SPECIFICATION
# ================================================================================

specification:
  structure:
    entry_point: "src/{layer_spec['layer_name'].lower()}/{layer_spec['layer_name'].lower()}.py"
    modules:
      - "{layer_spec['layer_name'].lower()}.py"
      - "models.py"
      - "exceptions.py"
  
  classes:"""
    
    # Add classes
    for cls in layer_spec['classes']:
        req_template += f"""
    - name: "{cls['name']}"
      purpose: "{cls['purpose']}"
      methods:"""
        for method in cls['methods']:
            req_template += f"""
        - name: "{method.split('(')[0]}"
          signature: "{method}"
          purpose: "Implement {method.split('(')[0]} logic" """
    
    req_template += f"""

  implementation_details:
    libraries: {layer_spec['libraries']}
    patterns: ["Repository Pattern", "Factory Pattern"]
    error_handling:
      - error_type: "ValidationError"
        handling: "Raise with clear error message"
      - error_type: "DataError"
        handling: "Log and raise custom exception"
  
  inputs:"""
    
    for inp in layer_spec['inputs']:
        req_template += f"""
    - name: "input_data"
      type: "Various"
      description: "{inp}" """
    
    req_template += f"""

  outputs:"""
    
    for out in layer_spec['outputs']:
        req_template += f"""
    - name: "output_data"
      type: "Various"
      description: "{out}" """
    
    req_template += f"""

# ================================================================================
# ACCEPTANCE CRITERIA
# ================================================================================

acceptance_criteria:
  - criterion: "Processes valid input data without errors"
    test: "pytest tests/unit/test_{layer_spec['layer_name'].lower()}.py -v"
  
  - criterion: "Handles invalid input with appropriate error messages"
    test: "Pass invalid data, verify exception with clear message"
  
  - criterion: "Integrates correctly with dependent layers"
    test: "pytest tests/integration/test_{layer_spec['layer_name'].lower()}_integration.py -v"
  
  - criterion: "Performance meets requirements"
    test: "Benchmark test with realistic data volume"

# ================================================================================
# TDD IMPLEMENTATION PLAN
# ================================================================================

week_1_task:
  title: "Build {layer_spec['title']} (TDD Approach)"
  
  steps:
    - step: 1
      action: "Write failing unit tests (RED phase)"
      file: "tests/unit/test_{layer_spec['layer_name'].lower()}.py"
      tests:"""
    
    for cls in layer_spec['classes']:
        for method in cls['methods']:
            method_name = method.split('(')[0]
            req_template += f"""
        - "test_{method_name}_success"
        - "test_{method_name}_failure" """
    
    req_template += f"""
      duration: "30 min"
    
    - step: 2
      action: "Run pytest to confirm RED phase"
      command: "pytest tests/unit/test_{layer_spec['layer_name'].lower()}.py -v"
      expected: "All tests FAIL (as expected)"
      duration: "2 min"
    
    - step: 3
      action: "Implement {layer_spec['classes'][0]['name']} class (GREEN phase)"
      file: "src/{layer_spec['layer_name'].lower()}/{layer_spec['layer_name'].lower()}.py"
      methods:"""
    
    for method in layer_spec['classes'][0]['methods']:
        req_template += f"""
        - "{method}" """
    
    req_template += f"""
      duration: "45 min"
    
    - step: 4
      action: "Run pytest to confirm GREEN phase"
      command: "pytest tests/unit/test_{layer_spec['layer_name'].lower()}.py -v"
      expected: "All tests PASS"
      duration: "5 min"
    
    - step: 5
      action: "Refactor for code quality (REFACTOR phase)"
      improvements:
        - "Add comprehensive docstrings"
        - "Extract common logic to helper methods"
        - "Add type hints to all methods"
      duration: "20 min"
    
    - step: 6
      action: "Integration test with dependent layers"
      file: "tests/integration/test_{layer_spec['layer_name'].lower()}_integration.py"
      duration: "15 min"
  
  total_time: "{layer_spec['duration']}"
  
  deliverable: |
    {layer_spec['title']} implementation ready for integration with 
    {', '.join(layer_spec['consumed_by']) if layer_spec['consumed_by'] else 'downstream layers'}.

# ================================================================================
# TRACEABILITY
# ================================================================================

traceability:
  implements_project_requirements:"""
    
    for prj_req in feature_data['prj_reqs']:
        req_template += f"""
    - "{prj_req}" """
    
    req_template += f"""
  
  implements_system_requirements:"""
    
    for sys_req in feature_data['sys_reqs']:
        req_template += f"""
    - "{sys_req}" """
    
    req_template += f"""
  
  implements_system_components:"""
    
    for comp in feature_data['sys_comps']:
        req_template += f"""
    - "{comp}" """
    
    req_template += f"""
  
  maps_to_feature:
    - "{feature_id}: {feature_data['feature_name']}"
  
  depends_on_layers:"""
    
    if layer_spec['depends_on']:
        for dep in layer_spec['depends_on']:
            req_template += f"""
    - "{dep}" """
    else:
        req_template += f"""
    []  # Foundation layer or independent """
    
    req_template += f"""
  
  consumed_by_layers:"""
    
    if layer_spec['consumed_by']:
        for consumer in layer_spec['consumed_by']:
            req_template += f"""
    - "{consumer}" """
    else:
        req_template += f"""
    []  # Terminal layer """
    
    req_template += f"""

# ================================================================================
# INTEGRATION POINTS
# ================================================================================

integration:
  input_from:"""
    
    if layer_spec['depends_on']:
        for dep in layer_spec['depends_on']:
            req_template += f"""
    - layer: "{dep}"
      data_type: "Various"
      interface: "Method calls" """
    else:
        req_template += f"""
    []  # Foundation layer, reads from filesystem """
    
    req_template += f"""
  
  output_to:"""
    
    if layer_spec['consumed_by']:
        for consumer in layer_spec['consumed_by']:
            req_template += f"""
    - layer: "{consumer}"
      data_type: "Various"
      interface: "Method calls" """
    else:
        req_template += f"""
    []  # Terminal layer, produces final output """
    
    req_template += f"""
  
  shared_dependencies:
    - "src/models/ - Shared data models"
    - "src/exceptions/ - Shared exceptions"

# ================================================================================
# TESTING STRATEGY
# ================================================================================

testing_strategy:
  unit_tests:
    location: "tests/unit/test_{layer_spec['layer_name'].lower()}.py"
    coverage_target: "90%"
    key_scenarios:
      - "Valid input processing"
      - "Invalid input error handling"
      - "Edge cases and boundary conditions"
  
  integration_tests:
    location: "tests/integration/test_{layer_spec['layer_name'].lower()}_integration.py"
    scenarios:
      - "Integration with dependent layers"
      - "End-to-end data flow"
  
  fixtures:
    location: "tests/fixtures/{layer_spec['layer_name'].lower()}/"
    files:
      - "sample_valid_data.yaml"
      - "sample_invalid_data.yaml"
      - "edge_case_data.yaml"

# ================================================================================
# DEPLOYMENT NOTES
# ================================================================================

deployment:
  dependencies:"""
    
    for lib in layer_spec['libraries']:
        req_template += f"""
    - package: "{lib.split('>=')[0] if '>=' in lib else lib}"
      version: "{lib.split('>=')[1] if '>=' in lib else 'latest'}"
      purpose: "{layer_spec['title']} implementation" """
    
    req_template += f"""
  
  configuration:
    - setting: "config_key"
      value: "default_value"
      location: "config/settings.yaml"
  
  usage_example: |
    # Example of how to use this layer
    from src.{layer_spec['layer_name'].lower()} import {layer_spec['classes'][0]['name']}
    
    instance = {layer_spec['classes'][0]['name']}()
    result = instance.{layer_spec['classes'][0]['methods'][0].split('(')[0]}(data)
    print(result)

# ================================================================================
# NOTES
# ================================================================================

notes: |
  IMPORTANT CONSIDERATIONS:
  - This layer is part of {feature_id}: {feature_data['feature_name']}
  - Proper error handling is critical for downstream layers
  - Performance should be monitored with realistic data volumes
  
  DESIGN DECISIONS:
  - Chosen architecture supports extensibility
  - Error messages include actionable context
  - Separates data transformation from business logic
  
  FUTURE ENHANCEMENTS:
  - Consider async processing for performance
  - Add caching for frequently accessed data
  - Implement monitoring and metrics

# ================================================================================
# END OF LAYER REQUIREMENT
# ================================================================================
"""
    
    return req_template


def main():
    """Generate all layer requirements."""
    base_path = Path("/workspaces/professional_excellence/projects/PROJECT-003 REPORT GENERATOR")
    
    total_created = 0
    skipped = 0
    
    print("=" * 80)
    print("  PROJECT-003 Layer Requirements Generator")
    print("=" * 80)
    print()
    
    for feature_id, feature_data in LAYER_SPECS.items():
        print(f"\n📁 {feature_id}: {feature_data['feature_name']}")
        print(f"   Layers to generate: {len(feature_data['layers'])}")
        
        for layer_spec in feature_data['layers']:
            # Skip LAYER-003-001-001 (already created manually)
            if layer_spec['layer_id'] == "LAYER-003-001-001":
                print(f"   ⏭️  Skipping {layer_spec['layer_id']} (already exists)")
                skipped += 1
                continue
            
            # Construct paths - match existing directory structure
            feature_dir = base_path / f"{feature_id}_{feature_data['feature_name'].replace(' ', '_')}"
            # Extract layer number parts: LAYER-003-001-002 -> 001, 002 -> LAYER-001, LAYER-002
            layer_parts = layer_spec['layer_id'].split('-')
            layer_num = f"LAYER-{layer_parts[-1]}"
            layer_dir = feature_dir / f"{layer_num}_{layer_spec['layer_name']}"
            req_file = layer_dir / f"{layer_spec['req_id']}.yaml"
            
            # Check if already exists
            if req_file.exists():
                print(f"   ⏭️  Skipping {layer_spec['layer_id']} (file exists)")
                skipped += 1
                continue
            
            # Generate requirement
            print(f"   ✨ Generating {layer_spec['layer_id']}: {layer_spec['title']}")
            
            content = generate_layer_requirement(feature_id, feature_data, layer_spec)
            
            # Write file
            req_file.write_text(content)
            
            file_size = req_file.stat().st_size / 1024  # KB
            print(f"      ✅ Created {req_file.name} ({file_size:.1f}KB)")
            total_created += 1
    
    print("\n" + "=" * 80)
    print(f"  Summary:")
    print(f"  - Created: {total_created} layer requirements")
    print(f"  - Skipped: {skipped} (already exist)")
    print(f"  - Total: {total_created + skipped} layers")
    print("=" * 80)
    print("\n✅ All layer requirements generated successfully!")
    print("\n📍 Location: /workspaces/professional_excellence/projects/PROJECT-003 REPORT GENERATOR/")
    print("\n🚀 Next step: Run build_feature.py to generate code")
    print()


if __name__ == "__main__":
    main()
