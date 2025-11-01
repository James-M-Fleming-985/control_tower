"""
CA-001 ↔ CA-002 Integration Layer Plan
=====================================

This integration layer will bridge CA-001 data ingestion with CA-002 correlation features.

ARCHITECTURE:
============

1. SYSTEM-CA-002/src/system_integration.py
   - Main orchestrator that connects CA-001 data to CA-002 features
   - Handles data fetching, formatting, and feature coordination

2. SYSTEM-CA-002/src/data_connector.py  
   - Client for CA-001 TimescaleDB API
   - Data format conversion (TimescaleDB → pandas DataFrame)
   - Handles multiple data sources and time ranges

3. SYSTEM-CA-002/src/correlation_api.py
   - FastAPI endpoints for correlation requests
   - Coordinates Feature CA-002-01 (calculator) + CA-002-04 (dashboard)
   - Provides REST API for external access

DATA FLOW:
==========

Step 1: External Request
------------------------
GET /api/correlations?symbols=SPY,VIX,GOLD&timeframe=30d

Step 2: Data Retrieval
---------------------
data_connector.py → CA-001 API → TimescaleDB → Raw time series

Step 3: Data Processing  
----------------------
system_integration.py → Format conversion → pandas DataFrame

Step 4: Correlation Calculation
------------------------------
Feature CA-002-01 → Statistical correlations (Pearson, Spearman, etc.)

Step 5: Visualization
-------------------
Feature CA-002-04 → Interactive dashboard (heatmap, charts, etc.)

INTEGRATION POINTS:
==================

CA-001 Side:
- Add endpoint: GET /api/timeseries-data
- Returns: JSON time series for specified symbols/dates

CA-002 Side:  
- Create system_integration.py (NEW)
- Create data_connector.py (NEW)
- Create correlation_api.py (NEW)
- Use existing feature_integration.py files

FILES TO CREATE:
===============

1. /SYSTEM-CA-002/src/system_integration.py
2. /SYSTEM-CA-002/src/data_connector.py
3. /SYSTEM-CA-002/src/correlation_api.py
4. /SYSTEM-CA-001/src/backend/app/routes/timeseries.py (NEW endpoint)

This approach:
- ✅ Keeps systems decoupled
- ✅ Uses existing feature implementations
- ✅ Scales for disparate correlations
- ✅ Provides clean API interface
"""