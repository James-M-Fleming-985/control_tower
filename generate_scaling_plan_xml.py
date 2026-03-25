#!/usr/bin/env python3
"""Generate MS Project XML for the Causal Affect Scaling Plan.

Produces an XML file compatible with the systems3-project-reporter parser
(MSProjectXMLParser) using the http://schemas.microsoft.com/project namespace.

Hierarchy:
  Level 1: Program summary (Summary=1) — skipped by parser
  Level 2: M0-M7 milestone phases (Summary=1) — becomes parent_project
  Level 3: Individual tasks (Milestone=0) — related tasks on milestone cards
  Level 3: Completion milestones (Duration=PT0H0M0S, Milestone=1) — milestone tab + calendar
"""

import xml.etree.ElementTree as ET
from datetime import date, timedelta
import shutil

# ---------------------------------------------------------------------------
# Project metadata
# ---------------------------------------------------------------------------
PROJECT_NAME = "Causal Affect Scaling Plan"
PROJECT_TITLE = "CA-SCALE: Baseline to 10TB / 90% Accuracy / Full Automation"
AUTHOR = "James Fleming"
PROJECT_START = date(2026, 3, 9)
PROJECT_END = date(2027, 3, 8)
NS = "http://schemas.microsoft.com/project"

# ---------------------------------------------------------------------------
# Scaling plan data: 8 milestones, each with tracks containing tasks
# ---------------------------------------------------------------------------
MILESTONES = [
    {
        "name": "M0: Instrument & Measure",
        "weeks": (1, 3),
        "notes": "You can't improve what you can't measure. Establish baselines for model accuracy, build errors, exploitation metrics, and revenue.",
        "tracks": [
            {
                "name": "Track A: Model Accuracy Baseline",
                "notes": "Run prediction validation, record baseline accuracy, set up weekly automation",
                "tasks": [
                    "Run prediction validation on all matured predictions (POST /predictions/validate)",
                    "Record baseline direction_accuracy, avg_error_pct, avg_change_error_pct",
                    "Add automated weekly validation cron (APScheduler or Railway cron)",
                    "Add accuracy trend chart to Prediction Accuracy tab",
                    "Deliverable: Documented baseline accuracy number (expected ~50-55%)",
                ],
            },
            {
                "name": "Track B: Build Error Baseline",
                "notes": "Add build metrics tracking, store results as CI artifacts, create metrics endpoint",
                "tasks": [
                    "Add BuildMetrics tracking to build_feature.py (syntax errors, test failures, frontend build failures)",
                    "Store results in JSON artifact uploaded with GitHub Actions",
                    "Parse artifact in /builds/metrics endpoint",
                    "Deliverable: Error rate measurement framework, initial baseline (expected ~20-30%)",
                ],
            },
            {
                "name": "Track C: Exploitation Metrics Baseline",
                "notes": "Score existing BUILD recommendations, manually validate sample, create validation table",
                "tasks": [
                    "Tag all 103 existing BUILD recommendations with viability scores (run /exploitation/generate)",
                    "Manually validate 10-20 BUILD recommendations against real-world outcomes",
                    "Create exploitation_validation table to track recommended vs actual opportunity success",
                    "Deliverable: Documented baseline viability prediction accuracy (expected ~45-50%)",
                ],
            },
            {
                "name": "Track D: Revenue Baseline",
                "notes": "Audit Stripe dashboard, document current revenue per app",
                "tasks": [
                    "Audit Stripe dashboard for current subscriber count and MRR",
                    "Document current revenue per app (Causal Affect, systems3-project-reporter)",
                    "Deliverable: Revenue baseline document",
                ],
            },
        ],
    },
    {
        "name": "M1: Foundation Scaling",
        "weeks": (4, 9),
        "notes": "Target: +5% accuracy (55-60%), data to ~100GB, build errors measured. More granular data + proper validation methodology.",
        "tracks": [
            {
                "name": "Track A: Model Accuracy to 60%",
                "notes": "Add daily ingestion, walk-forward validation, multi-lag testing",
                "tasks": [
                    "Add daily Wikipedia pageview ingestion (55 variables x 365 days = 20K new daily records/year)",
                    "Add daily Reddit activity ingestion for top 30 subreddits mapped in SIGNAL_CROSS_VALIDATION",
                    "Implement walk-forward validation (train on N months, predict month N+1, slide forward)",
                    "Add multi-lag Granger testing (test 1-12 month lags instead of single optimal lag)",
                ],
            },
            {
                "name": "Track B: Build Errors to 25%",
                "notes": "Pre-build validation, automated import resolution, structured error reporting",
                "tasks": [
                    "Add pre-build template validation (lint templates before generation)",
                    "Add automated import resolution (detect missing imports, auto-add)",
                    "Add structured error reporting to GitHub Actions artifacts",
                ],
            },
            {
                "name": "Track C: Exploitation Accuracy to 55%",
                "notes": "Backtest viability scores, calibrate weights, add outcome tracking",
                "tasks": [
                    "Backtest viability scores against 6-month historical data",
                    "Calibrate viability scoring weights based on backtest results",
                    "Add target_growth_actual field to ExploitationRecommendation for outcome tracking",
                ],
            },
            {
                "name": "Track D: Data Infrastructure",
                "notes": "TimescaleDB, hypertables, retention policies, S3 cold storage, connection pooling",
                "tasks": [
                    "Enable TimescaleDB extension on Railway PostgreSQL",
                    "Convert time_series_data to hypertable with time-based partitioning",
                    "Add automated data retention policy (raw daily: 2 years, aggregated: forever)",
                    "Set up S3 bucket for cold storage archive",
                    "Add connection pool tuning: pool_size=20, max_overflow=10",
                ],
            },
            {
                "name": "Track E: Revenue Dashboard v1",
                "notes": "Central RevenueEvent model, webhook aggregation, basic MRR chart",
                "tasks": [
                    "Create RevenueEvent model (app_id, event_type, amount, currency, region, timestamp)",
                    "Create /revenue/dashboard endpoint aggregating across all Stripe accounts",
                    "Wire Stripe webhook events for all deployed apps to central tracker",
                    "Build basic Revenue tab in dashboard (MRR chart, subscriber count, per-app breakdown)",
                ],
            },
        ],
    },
    {
        "name": "M2: Intelligence Layer",
        "weeks": (10, 15),
        "notes": "Target: 65% accuracy, 60% exploitation, build time 4hrs, errors 20%. Ensemble reduces individual model bias.",
        "tracks": [
            {
                "name": "Track A: Model Accuracy to 65%",
                "notes": "Ensemble model, confidence-weighted, feature engineering, cross-validation",
                "tasks": [
                    "Add ensemble model: combine Granger causality + simple linear regression + ARIMA",
                    "Implement confidence-weighted ensemble (weight by historical accuracy per model)",
                    "Add feature engineering: rolling averages (7d, 30d, 90d), rate of change, volatility",
                    "Add cross-validation signal confidence (Wikipedia + Reddit agreement score as feature)",
                ],
            },
            {
                "name": "Track B: Build Errors to 20%",
                "notes": "AI-powered code review, integration test templates, fix top failure patterns",
                "tasks": [
                    "Add AI-powered code review step (LLM validates generated code before commit)",
                    "Add integration test templates for common patterns (CRUD, auth, Stripe)",
                    "Fix top 5 most common build failure patterns from M1 data",
                ],
            },
            {
                "name": "Track C: Exploitation Accuracy to 60%",
                "notes": "Google Trends integration, cross-reference viability, competition scoring",
                "tasks": [
                    "Add Google Trends integration (pytrends with proxy rotation)",
                    "Cross-reference viability scores with Google Trends search volume",
                    "Add competition scoring from real arxiv citation counts",
                ],
            },
            {
                "name": "Track D: Build Automation to 4 Hours",
                "notes": "Auto GitHub repo, auto Railway, auto Stripe, auto GA4",
                "tasks": [
                    "Automate GitHub repo creation in build trigger endpoint (GitHub API)",
                    "Auto-generate Railway project via Railway API",
                    "Auto-wire Stripe subscription (create product + price via Stripe API)",
                    "Auto-inject GA4 measurement ID from analytics template",
                    "Deliverable: One-click Build and Deploy from Exploitation Board",
                ],
            },
            {
                "name": "Track E: Data Scale to 500GB",
                "notes": "FRED economic indicators, Alpha Vantage, GDELT news sentiment, ETL pipeline",
                "tasks": [
                    "Add FRED economic indicators (50+ variables: GDP, CPI, unemployment)",
                    "Add Alpha Vantage intraday data for top 10 stocks (5-min intervals)",
                    "Add news sentiment from GDELT API (daily event counts by theme)",
                    "Set up ETL pipeline with batch scheduling (APScheduler)",
                ],
            },
        ],
    },
    {
        "name": "M3: Self-Learning Foundation",
        "weeks": (16, 21),
        "notes": "Target: 70% accuracy, 65% exploitation, build time 3hrs, errors 15%. System learns from its own prediction outcomes.",
        "tracks": [
            {
                "name": "Track A: Model Accuracy to 70%",
                "notes": "Auto-retraining, prediction feedback loop, anomaly detection, adaptive lag",
                "tasks": [
                    "Implement automatic model retraining when accuracy drops below threshold",
                    "Add prediction feedback loop: validated predictions retrain features",
                    "Add anomaly detection (Z-score) to flag unusual signals before prediction",
                    "Implement adaptive lag selection (dynamically adjust lag based on recent accuracy)",
                ],
            },
            {
                "name": "Track B: Build Errors to 15%",
                "notes": "Error pattern classifier, auto-fix common patterns, scaffold regression tests",
                "tasks": [
                    "Build error pattern classifier (categorize: import, syntax, config, runtime)",
                    "Auto-fix common patterns (missing __init__.py, wrong import paths, missing env vars)",
                    "Add scaffold regression tests (test each template produces working code)",
                ],
            },
            {
                "name": "Track C: Exploitation Accuracy to 65%",
                "notes": "Track actual outcomes, time-to-market analysis, calibrate opportunity duration",
                "tasks": [
                    "Track actual outcomes of PURSUING recommendations (did the BUILD succeed?)",
                    "Add time-to-market analysis (how long from recommendation to live product?)",
                    "Calibrate opportunity_duration_months against actual opportunity windows",
                ],
            },
            {
                "name": "Track D: Build Automation to 3 Hours",
                "notes": "Auto domain, auto SSL, auto database, post-deploy smoke tests",
                "tasks": [
                    "Add automated domain configuration (subdomain allocation)",
                    "Add automated SSL certificate provisioning",
                    "Add automated database setup for deployed apps",
                    "Add post-deploy health check + smoke test",
                ],
            },
            {
                "name": "Track E: Data Scale to 1TB",
                "notes": "Twitter/X API, IoT starter (OpenWeather), Reddit historical, TimescaleDB compression",
                "tasks": [
                    "Add social media feeds (Twitter/X academic API for trend data)",
                    "Add IoT starter: OpenWeather API for 100 cities (hourly)",
                    "Add Pushshift/Pullpush for full Reddit historical data",
                    "Implement data compression in TimescaleDB (compress chunks older than 7 days)",
                ],
            },
            {
                "name": "Track F: Pricing Intelligence v1",
                "notes": "IP geolocation, PPP tiers, pricing recommendation table, demand estimation",
                "tasks": [
                    "Add IP geolocation to dashboard (MaxMind GeoLite2 free database)",
                    "Map regions to PPP (Purchasing Power Parity) tiers from World Bank API",
                    "Create pricing_recommendation table (region, suggested_price, confidence)",
                    "Add traffic-based demand estimation per region",
                ],
            },
        ],
    },
    {
        "name": "M4: Scale & Optimize",
        "weeks": (22, 27),
        "notes": "Target: 75% accuracy, 70% exploitation, build time 2.5hrs, errors 10%. Deep learning for non-linear patterns.",
        "tracks": [
            {
                "name": "Track A: Model Accuracy to 75%",
                "notes": "LSTM/transformer, SHAP feature importance, regime detection, online learning",
                "tasks": [
                    "Add LSTM/transformer-based time series model (PyTorch) as ensemble member",
                    "Implement feature importance ranking (SHAP values) for interpretability",
                    "Add regime detection (bull/bear/sideways affect model choice)",
                    "Implement online learning (update model incrementally with new data)",
                ],
            },
            {
                "name": "Track B: Build Errors to 10%",
                "notes": "AI-powered scaffold improvement, end-to-end test suite, canary deployment",
                "tasks": [
                    "Implement AI-powered scaffold improvement (analyze failed builds, update templates)",
                    "Add end-to-end integration test suite for full build pipeline",
                    "Add canary deployment (deploy to staging first, promote if healthy)",
                ],
            },
            {
                "name": "Track C: Exploitation Accuracy to 70%",
                "notes": "Competitive landscape, Product Hunt/Indie Hackers validation, engagement prediction",
                "tasks": [
                    "Add competitive landscape analysis (how many similar apps exist?)",
                    "Cross-reference with Product Hunt / Indie Hackers for market validation",
                    "Add user engagement prediction model (predict DAU/MAU from topic + competition)",
                ],
            },
            {
                "name": "Track D: Build Automation to 2.5 Hours",
                "notes": "Automated testing, monitoring setup, changelog generation",
                "tasks": [
                    "Add automated testing pipeline for deployed apps",
                    "Add automated monitoring setup (uptime, error rate, performance)",
                    "Add automated changelog and release notes generation",
                ],
            },
            {
                "name": "Track E: Data Scale to 3TB",
                "notes": "Alternative data feeds, satellite imagery, data lakehouse pattern",
                "tasks": [
                    "Add Bloomberg/Reuters alternative data feeds (if budget allows)",
                    "Add satellite imagery analysis for economic indicators (nighttime lights)",
                    "Implement data lakehouse pattern (S3 + DuckDB for analytics, PostgreSQL for hot data)",
                ],
            },
            {
                "name": "Track F: Revenue Dashboard v2",
                "notes": "AdSense integration, per-app P&L, cohort analysis, revenue forecasting",
                "tasks": [
                    "Add Google AdSense integration for ad-supported apps",
                    "Add per-app P&L tracking (revenue minus infrastructure cost)",
                    "Add subscriber cohort analysis (retention by signup month)",
                    "Add revenue forecasting from growth trends",
                ],
            },
        ],
    },
    {
        "name": "M5: Autonomous Operations",
        "weeks": (28, 33),
        "notes": "Target: 80% accuracy, 75% exploitation, build time 2hrs, errors 5%. Multi-horizon + automatic model selection + uncertainty.",
        "tracks": [
            {
                "name": "Track A: Model Accuracy to 80%",
                "notes": "Multi-horizon forecasting, cross-market contagion, model selection autopilot, uncertainty quantification",
                "tasks": [
                    "Implement multi-horizon forecasting (1 week, 1 month, 3 month predictions)",
                    "Add cross-market contagion detection (detect when one market shock propagates)",
                    "Implement model selection autopilot (auto pick best model per signal-target pair)",
                    "Add uncertainty quantification (prediction intervals, not just point estimates)",
                ],
            },
            {
                "name": "Track B: Build Errors to 5%",
                "notes": "Self-healing builds, template A/B testing, build quality gate",
                "tasks": [
                    "Implement self-healing builds (detect error, auto-apply fix, retry)",
                    "Add template versioning with A/B testing (test new vs old templates)",
                    "Implement build quality gate (block deploy if quality score below threshold)",
                ],
            },
            {
                "name": "Track C: Exploitation Accuracy to 75%",
                "notes": "Market timing model, user acquisition cost prediction, churn prediction",
                "tasks": [
                    "Add market timing model (when to launch, not just what to build)",
                    "Add user acquisition cost prediction from similar product data",
                    "Add churn prediction for deployed products",
                ],
            },
            {
                "name": "Track D: Build Automation to 2 Hours",
                "notes": "Zero-touch pipeline, automated A/B testing, automated pricing optimization",
                "tasks": [
                    "Full zero-touch pipeline: recommendation to build to deploy to monitor to scale",
                    "Add automated A/B testing for deployed apps",
                    "Add automated pricing optimization based on conversion data",
                ],
            },
            {
                "name": "Track E: Data Scale to 7TB",
                "notes": "Real-time streaming (Kafka/Redis), IoT/MQTT ingestion, federated querying",
                "tasks": [
                    "Add real-time streaming (Kafka/Redis Streams for sub-minute data)",
                    "Add sensor/IoT data ingestion (via MQTT broker)",
                    "Implement federated querying across PostgreSQL + S3 + streaming",
                ],
            },
            {
                "name": "Track F: Pricing Intelligence v2",
                "notes": "Dynamic pricing engine, currency conversion + PPP, price elasticity, revenue-optimal pricing",
                "tasks": [
                    "Implement dynamic pricing engine (A/B test prices per region)",
                    "Add currency conversion + PPP-adjusted pricing per country",
                    "Add price elasticity estimation from traffic to conversion data",
                    "Revenue-optimal pricing recommendations per app per region",
                ],
            },
        ],
    },
    {
        "name": "M6: Intelligence Engine",
        "weeks": (34, 39),
        "notes": "Target: 85% accuracy, 80% exploitation, self-optimizing. Advanced ML + causal inference.",
        "tracks": [
            {
                "name": "Track A: Model Accuracy to 85%",
                "notes": "Reinforcement learning, model distillation, causal discovery",
                "tasks": [
                    "Add reinforcement learning for trading strategy optimization",
                    "Implement model distillation (compress ensemble into fast inference model)",
                    "Add causal discovery (go beyond Granger to structural causal models)",
                ],
            },
            {
                "name": "Track B: Self-Optimizing Builds",
                "notes": "AI generates feature requirements, auto-select scaffold and tech stack, auto-generate tests",
                "tasks": [
                    "AI generates feature requirements from opportunity analysis (no YAML needed)",
                    "Auto-select best scaffold and tech stack per opportunity",
                    "Builds generate their own tests and validation suites",
                ],
            },
            {
                "name": "Track C: Exploitation Accuracy to 80%",
                "notes": "Portfolio optimization, resource re-allocation, auto-sunset underperformers",
                "tasks": [
                    "Portfolio optimization across all deployed apps",
                    "Resource re-allocation recommendations (scale winners, sunset losers)",
                    "Auto-sunset underperforming products",
                ],
            },
            {
                "name": "Track D: Data Scale to 10TB",
                "notes": "Full multi-source streaming, automated data quality monitoring, data lineage tracking",
                "tasks": [
                    "Full multi-source streaming ingestion operational",
                    "Automated data quality monitoring and anomaly detection",
                    "Data lineage tracking (know provenance of every prediction)",
                ],
            },
            {
                "name": "Track E: Revenue Engine",
                "notes": "Central portfolio dashboard (MRR, CAC, LTV, churn), automated P&L, revenue alerts, investment-ready metrics",
                "tasks": [
                    "Central dashboard showing portfolio MRR, CAC, LTV, churn by app",
                    "Automated financial reporting (monthly P&L per product)",
                    "Revenue alerts and anomaly detection",
                    "Investment-ready metrics dashboard",
                ],
            },
        ],
    },
    {
        "name": "M7: Market Leadership",
        "weeks": (40, 48),
        "notes": "Target: 90% accuracy, 90% exploitation, market-ready. Continuous improvement + market breadth.",
        "tracks": [
            {
                "name": "Track A: Model Accuracy to 90%",
                "notes": "Continuous learning pipeline, model marketplace, multi-asset class prediction",
                "tasks": [
                    "Continuous learning pipeline (models retrain and auto-promote)",
                    "Model marketplace (share/sell prediction models to other users)",
                    "Multi-asset class prediction (stocks, crypto, commodities, real estate)",
                ],
            },
            {
                "name": "Track B: Full Automation",
                "notes": "End-to-end signal-to-monetization, average deployment under 2 hours, build errors sustained below 5%",
                "tasks": [
                    "End-to-end: signal detected to app built to deployed to monetized to optimized",
                    "Average deployment time consistently under 2 hours",
                    "Build error rate sustained below 5%",
                ],
            },
            {
                "name": "Track C: Exploitation Accuracy to 90%",
                "notes": "Multi-factor scoring validated against 12+ months, automated opportunity discovery, cross-opportunity synergy",
                "tasks": [
                    "Multi-factor opportunity scoring validated against 12+ months of outcomes",
                    "Automated opportunity discovery (system finds BUILD opportunities without prompting)",
                    "Cross-opportunity synergy detection (products that complement each other)",
                ],
            },
            {
                "name": "Track D: Revenue Targets",
                "notes": "4-10 deployed apps generating revenue, region-specific pricing in 10+ markets, real-time MRR tracking, target $20K+ MRR",
                "tasks": [
                    "4-10 deployed apps generating subscription revenue",
                    "Region-specific pricing active in 10+ markets",
                    "Central revenue dashboard with real-time MRR tracking",
                    "Target: $20K+ MRR across portfolio",
                ],
            },
        ],
    },
]


def week_to_date(week_num: int) -> date:
    """Convert week number (1-based) to a date starting from PROJECT_START."""
    return PROJECT_START + timedelta(weeks=week_num - 1)


def hours_between(start: date, end: date) -> int:
    """Business hours between two dates (8hr days, 5 days/week)."""
    days = (end - start).days
    weeks = days // 7
    remaining = days % 7
    biz_days = weeks * 5 + min(remaining, 5)
    return max(biz_days * 8, 8)  # at least 1 day


def fmt_date(d: date) -> str:
    """Format date as ISO 8601 for MS Project XML."""
    return f"{d.isoformat()}T00:00:00"


def fmt_duration(hours: int) -> str:
    """Format duration as PT{n}H for MS Project XML."""
    return f"PT{hours}H0M0S"


def add_element(parent: ET.Element, tag: str, text: str) -> ET.Element:
    """Add a child element with text content."""
    elem = ET.SubElement(parent, tag)
    elem.text = str(text)
    return elem


def build_xml() -> ET.ElementTree:
    """Build the full MS Project XML document.

    3-level hierarchy matching the Project Reporter's expected structure:
      Level 1: Program title (Summary=1) — skipped by parser
      Level 2: M0-M7 phases (Summary=1) — becomes parent_project
      Level 3: Individual tasks (Milestone=0) — related tasks on milestone cards
      Level 3: Completion milestones (Duration=PT0H0M0S, Milestone=1) — milestone tab + calendar
    """
    ET.register_namespace("", NS)

    root = ET.Element("Project", xmlns=NS)
    add_element(root, "Name", PROJECT_NAME)
    add_element(root, "Title", PROJECT_TITLE)
    add_element(root, "Author", AUTHOR)
    add_element(root, "CreationDate", fmt_date(PROJECT_START))
    add_element(root, "StartDate", fmt_date(PROJECT_START))
    add_element(root, "FinishDate", fmt_date(PROJECT_END))
    add_element(root, "CurrencySymbol", "$")

    tasks_elem = ET.SubElement(root, "Tasks")

    uid = 1
    task_id = 1

    # -----------------------------------------------------------------------
    # Level 1: Program title
    # -----------------------------------------------------------------------
    task = ET.SubElement(tasks_elem, "Task")
    add_element(task, "UID", uid)
    add_element(task, "ID", task_id)
    add_element(task, "Name", f"Causal Affect Scaling: Baseline to 10TB / 90% Accuracy ({PROJECT_START.year}-{PROJECT_END.year})")
    add_element(task, "Notes", "12-month scaling plan: 10TB data ingestion, 90% model accuracy, full build automation, revenue dashboard, region-aware pricing, self-learning engine.")
    add_element(task, "OutlineLevel", 1)
    add_element(task, "Start", fmt_date(PROJECT_START))
    add_element(task, "Finish", fmt_date(PROJECT_END))
    add_element(task, "PercentComplete", 0)
    add_element(task, "Summary", 1)

    uid += 1
    task_id += 1

    prev_completion_uid = None

    for milestone in MILESTONES:
        week_start, week_end = milestone["weeks"]
        m_start = week_to_date(week_start)
        m_end = week_to_date(week_end + 1) - timedelta(days=1)

        # -------------------------------------------------------------------
        # Level 2: Project / parent task (Summary=1)
        # -------------------------------------------------------------------
        task = ET.SubElement(tasks_elem, "Task")
        add_element(task, "UID", uid)
        add_element(task, "ID", task_id)
        add_element(task, "Name", f"{milestone['name']} (Weeks {week_start}-{week_end})")
        add_element(task, "Notes", milestone["notes"])
        add_element(task, "OutlineLevel", 2)
        add_element(task, "Start", fmt_date(m_start))
        add_element(task, "Finish", fmt_date(m_end))
        add_element(task, "PercentComplete", 0)
        add_element(task, "Summary", 1)

        if prev_completion_uid is not None:
            pred = ET.SubElement(task, "PredecessorLink")
            add_element(pred, "PredecessorUID", prev_completion_uid)
            add_element(pred, "Type", 1)

        uid += 1
        task_id += 1

        # -------------------------------------------------------------------
        # Level 3: Individual tasks (Milestone=0) — one per task item
        # -------------------------------------------------------------------
        num_tracks = len(milestone["tracks"])
        for track_idx, track in enumerate(milestone["tracks"]):
            for task_text in track["tasks"]:
                t_start = m_start
                t_end = m_end
                t_hours = hours_between(t_start, t_end)

                task = ET.SubElement(tasks_elem, "Task")
                add_element(task, "UID", uid)
                add_element(task, "ID", task_id)
                add_element(task, "Name", task_text)
                add_element(task, "Notes", f"{track['name']}: {track['notes']}")
                add_element(task, "OutlineLevel", 3)
                add_element(task, "Start", fmt_date(t_start))
                add_element(task, "Finish", fmt_date(t_end))
                add_element(task, "PercentComplete", 0)
                add_element(task, "Duration", fmt_duration(t_hours))
                add_element(task, "Milestone", 0)

                uid += 1
                task_id += 1

        # -------------------------------------------------------------------
        # Level 3: Zero-duration completion milestone
        # -------------------------------------------------------------------
        task = ET.SubElement(tasks_elem, "Task")
        add_element(task, "UID", uid)
        add_element(task, "ID", task_id)
        add_element(task, "Name", f"MILESTONE: {milestone['name']} Complete")
        add_element(task, "Notes", f"All tasks for {milestone['name']} verified and complete.")
        add_element(task, "OutlineLevel", 3)
        add_element(task, "Start", fmt_date(m_end))
        add_element(task, "Finish", fmt_date(m_end))
        add_element(task, "PercentComplete", 0)
        add_element(task, "Duration", "PT0H0M0S")
        add_element(task, "Milestone", 1)

        prev_completion_uid = uid
        uid += 1
        task_id += 1

    # -----------------------------------------------------------------------
    # Level 2: Final program milestone
    # -----------------------------------------------------------------------
    task = ET.SubElement(tasks_elem, "Task")
    add_element(task, "UID", uid)
    add_element(task, "ID", task_id)
    add_element(task, "Name", "PROGRAM SUCCESS: 10TB / 90% Accuracy / Full Automation Achieved")
    add_element(task, "Notes", "All 8 milestones complete. 10TB data platform, 90% model accuracy, sub-2hr automated deployments, revenue dashboard live.")
    add_element(task, "OutlineLevel", 2)
    add_element(task, "Start", fmt_date(PROJECT_END))
    add_element(task, "Finish", fmt_date(PROJECT_END))
    add_element(task, "PercentComplete", 0)
    add_element(task, "Duration", "PT0H0M0S")
    add_element(task, "Milestone", 1)

    if prev_completion_uid is not None:
        pred = ET.SubElement(task, "PredecessorLink")
        add_element(pred, "PredecessorUID", prev_completion_uid)
        add_element(pred, "Type", 1)

    return ET.ElementTree(root)


def main():
    tree = build_xml()

    # Write with XML declaration
    output_path = "/workspaces/control_tower/cloned_repos/business_ventures/Causal_Affect_Scaling_Plan.xml"
    ET.indent(tree, space="  ")
    tree.write(output_path, encoding="UTF-8", xml_declaration=True)

    print(f"Generated: {output_path}")

    # Count tasks
    root = tree.getroot()
    ns = {"p": NS}
    all_tasks = root.findall(".//p:Task", ns)
    level_counts = {}
    for t in all_tasks:
        level = t.find("p:OutlineLevel", ns)
        if level is not None:
            lvl = level.text
            level_counts[lvl] = level_counts.get(lvl, 0) + 1

    print(f"Total tasks: {len(all_tasks)}")
    for lvl in sorted(level_counts):
        print(f"  Level {lvl}: {level_counts[lvl]}")

    # Copy to workspace root for easy download
    root_copy = "/workspaces/control_tower/Causal_Affect_Scaling_Plan.xml"
    shutil.copy2(output_path, root_copy)
    print(f"Copied to: {root_copy}")


if __name__ == "__main__":
    main()
