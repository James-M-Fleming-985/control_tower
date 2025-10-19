#!/bin/bash

# CA-002 Setup Script
# Creates complete directory structure and requirements YAMLs for CA-002

set -e

REPO_ROOT="/workspaces/business_ventures/Causal_affect"
SYSTEM_DIR="$REPO_ROOT/SYSTEM-CA-002_correlation_analysis"

echo "=== CA-002 Setup ==="
echo "Target: $SYSTEM_DIR"
echo ""

# Check if repository exists
if [ ! -d "$REPO_ROOT" ]; then
    echo "ERROR: Repository $REPO_ROOT does not exist"
    echo "Please clone the Causal_affect repository first"
    exit 1
fi

# Create system directory
echo "Creating system directory..."
mkdir -p "$SYSTEM_DIR"

# Copy SYSTEM requirements YAML
echo "Copying SYSTEM-CA-002.yaml..."
cp /workspaces/control_tower/CA-002_setup/SYSTEM-CA-002.yaml "$SYSTEM_DIR/"

# Create feature directories
echo "Creating feature directories..."
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-01_statistical_correlation"
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-02_causality_testing"
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-03_correlation_scorer"
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-04_correlation_dashboard"

# Create layer directories for Feature 01
echo "Creating layer directories for Feature 01..."
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-01_statistical_correlation/LAYER-CA-002-01-01_pearson_calculator"
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-01_statistical_correlation/LAYER-CA-002-01-02_spearman_calculator"
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-01_statistical_correlation/LAYER-CA-002-01-03_kendall_calculator"
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-01_statistical_correlation/LAYER-CA-002-01-04_partial_correlation"
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-01_statistical_correlation/LAYER-CA-002-01-05_lagged_correlation"

# Create layer directories for Feature 02
echo "Creating layer directories for Feature 02..."
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-02_causality_testing/LAYER-CA-002-02-01_granger_test"
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-02_causality_testing/LAYER-CA-002-02-02_var_model"
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-02_causality_testing/LAYER-CA-002-02-03_irf_calculator"
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-02_causality_testing/LAYER-CA-002-02-04_transfer_entropy"
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-02_causality_testing/LAYER-CA-002-02-05_dag_inference"

# Create layer directories for Feature 03
echo "Creating layer directories for Feature 03..."
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-03_correlation_scorer/LAYER-CA-002-03-01_significance_calculator"
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-03_correlation_scorer/LAYER-CA-002-03-02_effect_size_analyzer"
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-03_correlation_scorer/LAYER-CA-002-03-03_stability_tracker"
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-03_correlation_scorer/LAYER-CA-002-03-04_actionability_classifier"
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-03_correlation_scorer/LAYER-CA-002-03-05_market_estimator"

# Create layer directories for Feature 04
echo "Creating layer directories for Feature 04..."
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-04_correlation_dashboard/LAYER-CA-002-04-01_heatmap_generator"
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-04_correlation_dashboard/LAYER-CA-002-04-02_timeseries_plotter"
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-04_correlation_dashboard/LAYER-CA-002-04-03_network_graph"
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-04_correlation_dashboard/LAYER-CA-002-04-04_leaderboard"

# Create src directories
echo "Creating src directories..."
mkdir -p "$SYSTEM_DIR/src/backend/app"
mkdir -p "$SYSTEM_DIR/src/frontend"
mkdir -p "$SYSTEM_DIR/docs"
mkdir -p "$SYSTEM_DIR/tests"

echo ""
echo "✅ Directory structure created successfully"
echo ""
echo "Next: Run generate_requirements.py to create all FEATURE and LAYER YAML files"

