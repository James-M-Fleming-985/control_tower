#!/usr/bin/env python3
"""
CA-002 Requirements Generator
Creates all FEATURE and LAYER YAML files for the Correlation Analysis Engine
"""

import os
from pathlib import Path
from datetime import datetime

# Feature definitions
FEATURES = {
    "01": {
        "name": "Statistical Correlation Calculator",
        "description": "Calculates multiple correlation coefficients between time-series variable pairs including Pearson, Spearman, Kendall Tau, partial correlation, and time-lagged correlation.",
        "business_value": [
            "Identifies linear, monotonic, and rank-based relationships in data",
            "Controls for confounding variables via partial correlation",
            "Detects delayed effects through time-lagged analysis",
            "Provides statistical foundation for causality testing"
        ],
        "user_story": "As a data analyst, I want to calculate multiple types of correlations between market variables, so that I can identify potential exploitable relationships for MVP opportunities.",
        "layers": {
            "01": {"name": "Pearson Calculator", "tech": "NumPy, SciPy", "responsibility": "Calculates Pearson correlation coefficient (r) and p-values for linear relationships"},
            "02": {"name": "Spearman Calculator", "tech": "SciPy", "responsibility": "Calculates Spearman rank correlation for monotonic relationships"},
            "03": {"name": "Kendall Calculator", "tech": "SciPy", "responsibility": "Calculates Kendall Tau correlation for ordinal data"},
            "04": {"name": "Partial Correlation", "tech": "Statsmodels, Pandas", "responsibility": "Calculates partial correlation controlling for confounding variables"},
            "05": {"name": "Lagged Correlation", "tech": "NumPy, Pandas", "responsibility": "Calculates time-lagged correlations to detect delayed effects"}
        }
    },
    "02": {
        "name": "Causality Testing Engine",
        "description": "Distinguishes correlation from causation using econometric and information-theoretic tests including Granger causality, VAR models, IRF, transfer entropy, and DAG inference.",
        "business_value": [
            "Identifies causal relationships vs spurious correlations",
            "Quantifies direction and strength of causal effects",
            "Provides foundation for predictive drift models",
            "Reduces false positives in MVP recommendations"
        ],
        "user_story": "As a data scientist, I want to test whether correlations are causal, so that I can focus on exploitable cause-effect relationships rather than spurious patterns.",
        "layers": {
            "01": {"name": "Granger Test", "tech": "Statsmodels", "responsibility": "Implements Granger causality tests with multiple lags"},
            "02": {"name": "VAR Model", "tech": "Statsmodels", "responsibility": "Builds Vector Autoregression models for multivariate analysis"},
            "03": {"name": "IRF Calculator", "tech": "Statsmodels", "responsibility": "Calculates Impulse Response Functions to quantify shock effects"},
            "04": {"name": "Transfer Entropy", "tech": "NumPy, SciPy", "responsibility": "Calculates transfer entropy for information flow quantification"},
            "05": {"name": "DAG Inference", "tech": "CausalNex, NetworkX", "responsibility": "Infers directed acyclic graphs of causal structure"}
        }
    },
    "03": {
        "name": "Correlation Exploitation Scorer",
        "description": "Ranks correlations by their potential for MVP exploitation based on statistical significance, effect size, temporal stability, actionability, and market size.",
        "business_value": [
            "Prioritizes correlations by MVP opportunity potential",
            "Balances statistical rigor with business practicality",
            "Identifies stable vs volatile correlations",
            "Estimates market opportunity size for recommendations"
        ],
        "user_story": "As a business strategist, I want correlations ranked by exploitability, so that I can focus resources on the highest-potential MVP opportunities.",
        "layers": {
            "01": {"name": "Significance Calculator", "tech": "SciPy, Statsmodels", "responsibility": "Calculates p-values, applies multiple testing corrections (Bonferroni, FDR)"},
            "02": {"name": "Effect Size Analyzer", "tech": "NumPy, SciPy", "responsibility": "Calculates Cohen's d and other effect size metrics"},
            "03": {"name": "Stability Tracker", "tech": "Pandas, NumPy", "responsibility": "Tracks correlation stability over rolling windows"},
            "04": {"name": "Actionability Classifier", "tech": "Scikit-learn", "responsibility": "Classifies correlations by MVP feasibility (high/medium/low)"},
            "05": {"name": "Market Estimator", "tech": "Pandas, NumPy", "responsibility": "Estimates market size from search volume and engagement data"}
        }
    },
    "04": {
        "name": "Correlation Dashboard & Visualization",
        "description": "Interactive web dashboard for exploring correlations with heatmaps, time-series plots, network graphs, leaderboards, and drill-down views.",
        "business_value": [
            "Enables visual exploration of correlation patterns",
            "Provides intuitive access to complex statistical results",
            "Supports data-driven decision making for MVP selection",
            "Facilitates communication of findings to stakeholders"
        ],
        "user_story": "As a product manager, I want an interactive dashboard to explore correlations visually, so that I can identify promising MVP opportunities and communicate findings to the team.",
        "layers": {
            "01": {"name": "Heatmap Generator", "tech": "D3.js, React", "responsibility": "Generates interactive correlation matrix heatmaps"},
            "02": {"name": "Time Series Plotter", "tech": "Recharts, React", "responsibility": "Plots time-series data with correlation overlays"},
            "03": {"name": "Network Graph", "tech": "D3.js, React, NetworkX", "responsibility": "Visualizes causal relationships as directed network graphs"},
            "04": {"name": "Leaderboard", "tech": "React, Tailwind CSS", "responsibility": "Displays top correlations ranked by exploitation score"}
        }
    }
}

def generate_feature_yaml(feature_num, feature_data, target_dir):
    """Generate FEATURE requirements YAML"""
    filename = f"FEATURE-CA-002-{feature_num}_{feature_data['name'].lower().replace(' ', '_').replace('&', 'and')}.yaml"
    filepath = target_dir / filename
    
    layers_yaml = ""
    for layer_num, layer_data in feature_data['layers'].items():
        layers_yaml += f"""  - layer_id: "LAYER-CA-002-{feature_num}-{layer_num}"
    name: "{layer_data['name']}"
    responsibility: "{layer_data['responsibility']}"
    technology: "{layer_data['tech']}"
    requirement_file: "LAYER-CA-002-{feature_num}-{layer_num}_{layer_data['name'].lower().replace(' ', '_')}.yaml"
    requirements:
      - "LAYER-CA-002-{feature_num}-{layer_num}"
  
"""
    
    business_value_yaml = "\n    ".join([f'- "{bv}"' for bv in feature_data['business_value']])
    
    content = f"""# ====================================================================================
# FEATURE REQUIREMENTS: {feature_data['name']}
# ====================================================================================
# FEATURE ID: FEATURE-CA-002-{feature_num}
# VERSION: 1.0.0
# LAST UPDATED: {datetime.now().strftime('%Y-%m-%d')}
# SYSTEM: CA-002 Correlation Analysis Engine
# ====================================================================================

metadata:
  requirement_id: "FEATURE-CA-002-{feature_num}"
  requirement_name: "{feature_data['name']}"
  feature_code: "CA-002-{feature_num}"
  version: "1.0.0"
  status: "Active"
  created_date: "{datetime.now().strftime('%Y-%m-%d')}"
  last_modified: "{datetime.now().strftime('%Y-%m-%d')}"
  owner: "Causal Affect Team"
  priority: "MUST HAVE"
  target_date: "2025-01-30"

# ====================================================================================
# FEATURE OVERVIEW
# ====================================================================================

overview:
  description: |
    {feature_data['description']}
  
  business_value:
    {business_value_yaml}
  
  user_story: |
    {feature_data['user_story']}
  
  acceptance_criteria:
    - "All layer implementations complete and passing tests"
    - "API endpoints functional and returning correct data"
    - "Integration with CA-001 data source working"
    - "Performance meets system requirements"
    - "Documentation complete and accurate"

# ====================================================================================
# LAYER ARCHITECTURE
# ====================================================================================

layers:
{layers_yaml}
# ====================================================================================
# FEATURE REQUIREMENTS
# ====================================================================================

requirements:
  - id: "FEAT-CA-002-{feature_num}-REQ-001"
    title: "Core Implementation"
    description: "Implement all layers with correct statistical algorithms and data handling"
    priority: "MUST HAVE"
    status: "Active"
    traces_to:
      system_requirements: ["SYSTEM-CA-002"]
      layer_requirements: [{', '.join([f'"LAYER-CA-002-{feature_num}-{ln}"' for ln in feature_data['layers'].keys()])}]
  
  - id: "FEAT-CA-002-{feature_num}-REQ-002"
    title: "Integration"
    description: "Integrate with CA-001 TimescaleDB and system orchestrator"
    priority: "MUST HAVE"
    status: "Active"
    traces_to:
      system_requirements: ["SYSTEM-CA-002", "SYSTEM-CA-001"]
  
  - id: "FEAT-CA-002-{feature_num}-REQ-003"
    title: "Testing"
    description: "Unit, integration, and end-to-end tests with >85% coverage"
    priority: "MUST HAVE"
    status: "Active"
    traces_to:
      system_requirements: ["SYSTEM-CA-002"]
  
  - id: "FEAT-CA-002-{feature_num}-REQ-004"
    title: "Performance"
    description: "Meet performance requirements specified in SYSTEM-CA-002"
    priority: "MUST HAVE"
    status: "Active"
    traces_to:
      system_requirements: ["SYSTEM-CA-002"]
  
  - id: "FEAT-CA-002-{feature_num}-REQ-005"
    title: "Documentation"
    description: "API documentation, architectural decisions, usage examples"
    priority: "MUST HAVE"
    status: "Active"
    traces_to:
      system_requirements: ["SYSTEM-CA-002"]

# ====================================================================================
# TECHNICAL SPECIFICATIONS
# ====================================================================================

technical_specifications:
  architecture: "Feature-based architecture with service layer pattern"
  data_flow: "CA-001 → Data Retrieval → Calculation → Cache → API Response"
  error_handling: "Comprehensive error handling with graceful degradation"
  caching: "Redis caching for expensive calculations"
  testing: "Pytest with fixtures, mocks, and real data validation"

# ====================================================================================
# TRACEABILITY
# ====================================================================================

traceability:
  traces_from:
    system: "SYSTEM-CA-002"
  traces_to:
    layers: [{', '.join([f'"LAYER-CA-002-{feature_num}-{ln}"' for ln in feature_data['layers'].keys()])}]
"""
    
    filepath.write_text(content)
    print(f"✓ Created {filename}")

def generate_layer_yaml(feature_num, layer_num, layer_data, feature_name, target_dir):
    """Generate LAYER requirements YAML"""
    layer_name_clean = layer_data['name'].lower().replace(' ', '_')
    filename = f"LAYER-CA-002-{feature_num}-{layer_num}_{layer_name_clean}.yaml"
    filepath = target_dir / filename
    
    content = f"""# ================================================================================
# LAYER REQUIREMENT: {layer_data['name']}
# ================================================================================
# LAYER ID: LAYER-CA-002-{feature_num}-{layer_num}
# FEATURE: {feature_name}
# VERSION: 1.0.0
# LAST UPDATED: {datetime.now().strftime('%Y-%m-%d')}
# ================================================================================

# ================================================================================
# METADATA
# ================================================================================
metadata:
  requirement_id: "LAYER-CA-002-{feature_num}-{layer_num}"
  requirement_title: "{layer_data['name']}"
  layer: "LAYER-CA-002-{feature_num}-{layer_num}_{layer_name_clean}"
  feature: "FEATURE-CA-002-{feature_num}_{feature_name.lower().replace(' ', '_').replace('&', 'and')}"
  version: "1.0.0"
  status: "Active"
  priority: "MUST HAVE"
  created_date: "{datetime.now().strftime('%Y-%m-%d')}"
  updated_date: "{datetime.now().strftime('%Y-%m-%d')}"
  owner: "Causal Affect Team"
  target_date: "2025-01-30"
  change_log:
    - version: "1.0.0"
      date: "{datetime.now().strftime('%Y-%m-%d')}"
      changes: "Initial version"

# ================================================================================
# REQUIREMENT DEFINITION
# ================================================================================
requirement:
  title: "{layer_data['name']}"
  
  description: |
    {layer_data['responsibility']}
    
    Part of the {feature_name} feature in the CA-002 Correlation Analysis Engine.
    Integrates with CA-001 time-series data and provides results to system orchestrator.
  
  rationale: |
    This layer implements a critical component of the correlation analysis pipeline.
    It provides specialized functionality that contributes to the overall goal of
    identifying exploitable market correlations for MVP opportunities.

# ================================================================================
# SPECIFICATION
# ================================================================================
specification:
  # Implementation structure
  structure:
    entry_point: "src/backend/app/features/FEATURE-CA-002-{feature_num}_{feature_name.lower().replace(' ', '_').replace('&', 'and')}/services/{layer_name_clean}.py"
    modules:
      - "{layer_name_clean}.py - Main implementation"
      - "tests/test_{layer_name_clean}.py - Unit tests"
  
  # Key technologies
  implementation_details:
    libraries: {layer_data['tech'].split(', ')}
    patterns: ["Service Layer Pattern", "Repository Pattern"]
    error_handling:
      - error_type: "DataError"
        handling: "Validate input data, raise informative errors"
      - error_type: "CalculationError"
        handling: "Log error, return None or default value"
  
  # Input/output contract
  inputs:
    - name: "time_series_data"
      type: "pd.DataFrame"
      description: "Time-series data from CA-001"
      example: "DataFrame with datetime index and variable columns"
  
  outputs:
    - name: "result"
      type: "dict"
      description: "Calculation result with statistics"
      example: '{{"coefficient": 0.85, "p_value": 0.001, "confidence_interval": [0.75, 0.95]}}'

# ================================================================================
# ACCEPTANCE CRITERIA
# ================================================================================
acceptance_criteria:
  functional:
    - "Calculation produces statistically correct results"
    - "Handles missing data gracefully"
    - "Returns results in expected format"
    - "Integrates with feature orchestrator"
  
  performance:
    - "Completes calculation in <5 seconds for 10K data points"
    - "Supports concurrent execution"
  
  quality:
    - "Unit test coverage >90%"
    - "Passes integration tests"
    - "Code follows project style guide"
    - "Documentation complete"

# ================================================================================
# TRACEABILITY
# ================================================================================
traceability:
  traces_from:
    feature: "FEATURE-CA-002-{feature_num}"
    system: "SYSTEM-CA-002"
  traces_to:
    implementation: "src/backend/app/features/FEATURE-CA-002-{feature_num}_{feature_name.lower().replace(' ', '_').replace('&', 'and')}/services/{layer_name_clean}.py"
    tests: "src/backend/app/features/FEATURE-CA-002-{feature_num}_{feature_name.lower().replace(' ', '_').replace('&', 'and')}/tests/test_{layer_name_clean}.py"
"""
    
    filepath.write_text(content)
    print(f"  ✓ Created {filename}")

def main():
    """Generate all FEATURE and LAYER requirements YAMLs"""
    base_dir = Path("/workspaces/control_tower/CA-002_setup")
    
    print("=== CA-002 Requirements Generator ===\n")
    
    # Generate FEATURE YAMLs
    for feature_num, feature_data in FEATURES.items():
        print(f"Generating FEATURE-CA-002-{feature_num}...")
        feature_yaml_path = base_dir / f"FEATURE-CA-002-{feature_num}.yaml"
        generate_feature_yaml(feature_num, feature_data, base_dir)
        
        # Generate LAYER YAMLs for this feature
        for layer_num, layer_data in feature_data['layers'].items():
            generate_layer_yaml(feature_num, layer_num, layer_data, feature_data['name'], base_dir)
        print()
    
    print("✅ All requirements YAMLs generated successfully!")
    print(f"\nFiles created in: {base_dir}")
    print("\nNext steps:")
    print("1. Review generated YAML files")
    print("2. Run setup_ca002.sh to create directory structure in Causal_affect repo")
    print("3. Copy YAML files to appropriate directories")
    print("4. Run build_system.py to generate implementation")

if __name__ == "__main__":
    main()
