#!/bin/bash

# CA-002 Complete Setup & Deployment Script
# Creates directory structure and copies all requirements YAMLs to correct locations

set -e

REPO_ROOT="/workspaces/business_ventures/Causal_affect"
SYSTEM_DIR="$REPO_ROOT/SYSTEM-CA-002_correlation_analysis"
SETUP_DIR="/workspaces/control_tower/CA-002_setup"

echo "========================================"
echo "  CA-002 Complete Setup & Deployment"
echo "========================================"
echo ""
echo "Source: $SETUP_DIR"
echo "Target: $SYSTEM_DIR"
echo ""

# Check if repository exists
if [ ! -d "$REPO_ROOT" ]; then
    echo "❌ ERROR: Repository $REPO_ROOT does not exist"
    echo ""
    echo "Please clone the Causal_affect repository first:"
    echo "  mkdir -p /workspaces/business_ventures"
    echo "  cd /workspaces/business_ventures"
    echo "  git clone <causal_affect_repo_url>"
    exit 1
fi

echo "✓ Repository found"
echo ""

# Create system directory
echo "Step 1: Creating system directory structure..."
mkdir -p "$SYSTEM_DIR"
mkdir -p "$SYSTEM_DIR/src/backend/app"
mkdir -p "$SYSTEM_DIR/src/frontend"
mkdir -p "$SYSTEM_DIR/docs"
mkdir -p "$SYSTEM_DIR/tests"

# Copy SYSTEM requirements YAML
echo "Step 2: Copying SYSTEM-CA-002.yaml..."
cp "$SETUP_DIR/SYSTEM-CA-002.yaml" "$SYSTEM_DIR/"

# Feature 01: Statistical Correlation Calculator
echo "Step 3: Setting up Feature 01..."
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-01_statistical_correlation"
cp "$SETUP_DIR/FEATURE-CA-002-01_statistical_correlation_calculator.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-01_statistical_correlation/FEATURE-CA-002-01_statistical_correlation.yaml"

# Layer 01-01: Pearson
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-01_statistical_correlation/LAYER-CA-002-01-01_pearson_calculator"
cp "$SETUP_DIR/LAYER-CA-002-01-01_pearson_calculator.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-01_statistical_correlation/LAYER-CA-002-01-01_pearson_calculator/"

# Layer 01-02: Spearman
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-01_statistical_correlation/LAYER-CA-002-01-02_spearman_calculator"
cp "$SETUP_DIR/LAYER-CA-002-01-02_spearman_calculator.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-01_statistical_correlation/LAYER-CA-002-01-02_spearman_calculator/"

# Layer 01-03: Kendall
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-01_statistical_correlation/LAYER-CA-002-01-03_kendall_calculator"
cp "$SETUP_DIR/LAYER-CA-002-01-03_kendall_calculator.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-01_statistical_correlation/LAYER-CA-002-01-03_kendall_calculator/"

# Layer 01-04: Partial Correlation
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-01_statistical_correlation/LAYER-CA-002-01-04_partial_correlation"
cp "$SETUP_DIR/LAYER-CA-002-01-04_partial_correlation.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-01_statistical_correlation/LAYER-CA-002-01-04_partial_correlation/"

# Layer 01-05: Lagged Correlation
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-01_statistical_correlation/LAYER-CA-002-01-05_lagged_correlation"
cp "$SETUP_DIR/LAYER-CA-002-01-05_lagged_correlation.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-01_statistical_correlation/LAYER-CA-002-01-05_lagged_correlation/"

# Feature 02: Causality Testing Engine
echo "Step 4: Setting up Feature 02..."
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-02_causality_testing"
cp "$SETUP_DIR/FEATURE-CA-002-02_causality_testing_engine.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-02_causality_testing/FEATURE-CA-002-02_causality_testing.yaml"

# Layer 02-01: Granger Test
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-02_causality_testing/LAYER-CA-002-02-01_granger_test"
cp "$SETUP_DIR/LAYER-CA-002-02-01_granger_test.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-02_causality_testing/LAYER-CA-002-02-01_granger_test/"

# Layer 02-02: VAR Model
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-02_causality_testing/LAYER-CA-002-02-02_var_model"
cp "$SETUP_DIR/LAYER-CA-002-02-02_var_model.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-02_causality_testing/LAYER-CA-002-02-02_var_model/"

# Layer 02-03: IRF Calculator
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-02_causality_testing/LAYER-CA-002-02-03_irf_calculator"
cp "$SETUP_DIR/LAYER-CA-002-02-03_irf_calculator.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-02_causality_testing/LAYER-CA-002-02-03_irf_calculator/"

# Layer 02-04: Transfer Entropy
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-02_causality_testing/LAYER-CA-002-02-04_transfer_entropy"
cp "$SETUP_DIR/LAYER-CA-002-02-04_transfer_entropy.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-02_causality_testing/LAYER-CA-002-02-04_transfer_entropy/"

# Layer 02-05: DAG Inference
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-02_causality_testing/LAYER-CA-002-02-05_dag_inference"
cp "$SETUP_DIR/LAYER-CA-002-02-05_dag_inference.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-02_causality_testing/LAYER-CA-002-02-05_dag_inference/"

# Feature 03: Correlation Exploitation Scorer
echo "Step 5: Setting up Feature 03..."
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-03_correlation_scorer"
cp "$SETUP_DIR/FEATURE-CA-002-03_correlation_exploitation_scorer.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-03_correlation_scorer/FEATURE-CA-002-03_correlation_scorer.yaml"

# Layer 03-01: Significance Calculator
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-03_correlation_scorer/LAYER-CA-002-03-01_significance_calculator"
cp "$SETUP_DIR/LAYER-CA-002-03-01_significance_calculator.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-03_correlation_scorer/LAYER-CA-002-03-01_significance_calculator/"

# Layer 03-02: Effect Size Analyzer
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-03_correlation_scorer/LAYER-CA-002-03-02_effect_size_analyzer"
cp "$SETUP_DIR/LAYER-CA-002-03-02_effect_size_analyzer.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-03_correlation_scorer/LAYER-CA-002-03-02_effect_size_analyzer/"

# Layer 03-03: Stability Tracker
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-03_correlation_scorer/LAYER-CA-002-03-03_stability_tracker"
cp "$SETUP_DIR/LAYER-CA-002-03-03_stability_tracker.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-03_correlation_scorer/LAYER-CA-002-03-03_stability_tracker/"

# Layer 03-04: Actionability Classifier
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-03_correlation_scorer/LAYER-CA-002-03-04_actionability_classifier"
cp "$SETUP_DIR/LAYER-CA-002-03-04_actionability_classifier.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-03_correlation_scorer/LAYER-CA-002-03-04_actionability_classifier/"

# Layer 03-05: Market Estimator
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-03_correlation_scorer/LAYER-CA-002-03-05_market_estimator"
cp "$SETUP_DIR/LAYER-CA-002-03-05_market_estimator.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-03_correlation_scorer/LAYER-CA-002-03-05_market_estimator/"

# Feature 04: Correlation Dashboard & Visualization
echo "Step 6: Setting up Feature 04..."
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-04_correlation_dashboard"
cp "$SETUP_DIR/FEATURE-CA-002-04_correlation_dashboard_and_visualization.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-04_correlation_dashboard/FEATURE-CA-002-04_correlation_dashboard.yaml"

# Layer 04-01: Heatmap Generator
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-04_correlation_dashboard/LAYER-CA-002-04-01_heatmap_generator"
cp "$SETUP_DIR/LAYER-CA-002-04-01_heatmap_generator.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-04_correlation_dashboard/LAYER-CA-002-04-01_heatmap_generator/"

# Layer 04-02: Time Series Plotter
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-04_correlation_dashboard/LAYER-CA-002-04-02_time_series_plotter"
cp "$SETUP_DIR/LAYER-CA-002-04-02_time_series_plotter.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-04_correlation_dashboard/LAYER-CA-002-04-02_time_series_plotter/"

# Layer 04-03: Network Graph
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-04_correlation_dashboard/LAYER-CA-002-04-03_network_graph"
cp "$SETUP_DIR/LAYER-CA-002-04-03_network_graph.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-04_correlation_dashboard/LAYER-CA-002-04-03_network_graph/"

# Layer 04-04: Leaderboard
mkdir -p "$SYSTEM_DIR/FEATURE-CA-002-04_correlation_dashboard/LAYER-CA-002-04-04_leaderboard"
cp "$SETUP_DIR/LAYER-CA-002-04-04_leaderboard.yaml" \
   "$SYSTEM_DIR/FEATURE-CA-002-04_correlation_dashboard/LAYER-CA-002-04-04_leaderboard/"

echo ""
echo "========================================"
echo "  ✅ CA-002 Setup Complete!"
echo "========================================"
echo ""
echo "Structure created at: $SYSTEM_DIR"
echo ""
echo "Directory tree:"
tree -L 3 "$SYSTEM_DIR" || find "$SYSTEM_DIR" -type d | head -20

echo ""
echo "Next Steps:"
echo "  1. Review the structure: cd $SYSTEM_DIR"
echo "  2. Verify YAML files are in place"
echo "  3. Run build_system.py from control_tower to generate code"
echo ""
