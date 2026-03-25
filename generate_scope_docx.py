#!/usr/bin/env python3
"""Generate Word document for the Causal Affect Scaling Plan scope."""

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
import datetime

def set_cell_shading(cell, color_hex):
    """Set background color on a table cell."""
    shading = cell._element.get_or_add_tcPr()
    shd = shading.makeelement(qn('w:shd'), {
        qn('w:val'): 'clear',
        qn('w:color'): 'auto',
        qn('w:fill'): color_hex,
    })
    shading.append(shd)

def add_styled_table(doc, headers, rows, header_color='1F4E79'):
    """Add a formatted table with header styling."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'

    # Header row
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.bold = True
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                run.font.size = Pt(9)
        set_cell_shading(cell, header_color)

    # Data rows
    for r, row_data in enumerate(rows):
        for c, val in enumerate(row_data):
            cell = table.rows[r + 1].cells[c]
            cell.text = str(val)
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(9)
            if r % 2 == 1:
                set_cell_shading(cell, 'F2F2F2')

    return table


def build_document():
    doc = Document()

    # -- Page margins --
    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)

    # -- Styles --
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(10)

    for level in range(1, 4):
        h = doc.styles[f'Heading {level}']
        h.font.name = 'Calibri'
        h.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    # ===================== TITLE PAGE =====================
    for _ in range(6):
        doc.add_paragraph()

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run('Causal Affect\nScaling Plan')
    run.font.size = Pt(36)
    run.bold = True
    run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run('Baseline → 10TB / 90% Accuracy / Full Automation Revenue Engine')
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x4A, 0x4A, 0x4A)

    doc.add_paragraph()

    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = meta.add_run(f'12-Month Programme Scope Document\nMarch 2026 – March 2027\n\nPrepared: {datetime.date.today().strftime("%d %B %Y")}')
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    doc.add_page_break()

    # ===================== TABLE OF CONTENTS placeholder =====================
    doc.add_heading('Table of Contents', level=1)
    toc_items = [
        '1. Problem Statement & Objectives',
        '2. Current Baselines (March 2026)',
        '3. Programme Milestones',
        '    M0: Instrument & Measure (Weeks 1–3)',
        '    M1: Foundation Scaling (Weeks 4–9)',
        '    M2: Intelligence Layer (Weeks 10–15)',
        '    M3: Self-Learning Foundation (Weeks 16–21)',
        '    M4: Scale & Optimize (Weeks 22–27)',
        '    M5: Autonomous Operations (Weeks 28–33)',
        '    M6: Intelligence Engine (Weeks 34–39)',
        '    M7: Market Leadership (Weeks 40–48)',
        '4. Architecture Evolution Path',
        '5. Key Deliverables & Files',
    ]
    for item in toc_items:
        p = doc.add_paragraph(item)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(2)
        for run in p.runs:
            run.font.size = Pt(10)

    doc.add_page_break()

    # ===================== 1. PROBLEM STATEMENT =====================
    doc.add_heading('1. Problem Statement & Objectives', level=1)

    doc.add_paragraph(
        'Current state: approximately 14,000 data points across 55 variables, '
        'unmeasured model accuracy, manual multi-hour builds, no cross-app revenue '
        'tracking, and no self-improvement loop.'
    )
    doc.add_paragraph(
        'Target state: 10TB data ingestion, 90% model accuracy, 2-hour automated '
        'deployments, less than 5% build errors, region-aware pricing, centralised '
        'revenue dashboard — all feeding a self-learning engine.'
    )

    doc.add_heading('Key Decisions', level=2)
    decisions = [
        ('Timeline', '12 months (balanced), ~8 milestones at approximately 6 weeks each'),
        ('App Scope', '4–10 apps (per AMP plan)'),
        ('Data Sources', 'All — social/financial feeds, news/search trends, IoT/sensor'),
        ('Storage Evolution', 'PostgreSQL → TimescaleDB → S3 cold storage + hot cache'),
    ]
    for label, desc in decisions:
        p = doc.add_paragraph(style='List Bullet')
        run = p.add_run(f'{label}: ')
        run.bold = True
        p.add_run(desc)

    doc.add_page_break()

    # ===================== 2. BASELINES =====================
    doc.add_heading('2. Current Baselines (March 2026)', level=1)

    baselines = [
        ('Data Volume', '~14K records, ~55 vars, single PostgreSQL', '10TB across distributed storage', '~99.999% gap'),
        ('Model Accuracy (direction)', 'Unmeasured (~50% theoretical)', '90%', '~40% improvement'),
        ('Exploitation Accuracy', 'Viability scoring just implemented', '90%', '~40% improvement'),
        ('Deployment Time', '30–45 min build + manual = several hours', '2 hours fully automated', 'Automation gap'),
        ('Build Error Rate', 'Unmeasured, no tracking', '<5%', 'Tracking + improvement'),
        ('Pricing Intelligence', 'Fixed tiers ($0–$199.99)', 'Region/economy-specific dynamic', 'Not started'),
        ('Revenue Dashboard', 'Stripe in systems3 only', 'Central dashboard, all apps', 'Not started'),
        ('Self-Improvement', 'Legacy retrain code (non-operational)', 'Continuous learning, auto-tuning', 'Not started'),
        ('Deployed Apps', '1 (Causal Affect) + 1 (systems3)', '4–10 apps (per AMP)', '2–8 more apps'),
    ]
    add_styled_table(doc, ['Dimension', 'Current', 'Target', 'Gap'], baselines)

    doc.add_page_break()

    # ===================== 3. MILESTONES =====================
    doc.add_heading('3. Programme Milestones', level=1)

    # Progression summary table
    doc.add_heading('Milestone Progression Summary', level=2)
    progression = [
        ('M0', 'Wk 1–3',   'Instrument & Measure',    'Baseline', 'Baseline', 'Baseline', '~30%',   '~5+ hrs'),
        ('M1', 'Wk 4–9',   'Foundation Scaling',       '~100GB',   '60%',     '55%',      '25%',    '—'),
        ('M2', 'Wk 10–15', 'Intelligence Layer',       '~500GB',   '65%',     '60%',      '20%',    '4 hrs'),
        ('M3', 'Wk 16–21', 'Self-Learning Foundation', '~1TB',     '70%',     '65%',      '15%',    '3 hrs'),
        ('M4', 'Wk 22–27', 'Scale & Optimize',         '~3TB',     '75%',     '70%',      '10%',    '2.5 hrs'),
        ('M5', 'Wk 28–33', 'Autonomous Operations',    '~7TB',     '80%',     '75%',      '5%',     '2 hrs'),
        ('M6', 'Wk 34–39', 'Intelligence Engine',      '~10TB',    '85%',     '80%',      'Self-opt', 'Self-opt'),
        ('M7', 'Wk 40–48', 'Market Leadership',        '10TB',     '90%',     '90%',      '<5%',    '<2 hrs'),
    ]
    add_styled_table(doc,
        ['ID', 'Weeks', 'Name', 'Data', 'Model Acc', 'Exploit Acc', 'Build Err', 'Deploy Time'],
        progression)

    doc.add_page_break()

    # ---------- M0 ----------
    doc.add_heading('Milestone 0: Instrument & Measure (Weeks 1–3)', level=2)
    p = doc.add_paragraph()
    run = p.add_run('"You can\'t improve what you can\'t measure"')
    run.italic = True

    doc.add_heading('Track A: Model Accuracy Baseline', level=3)
    tasks_m0a = [
        'Run prediction validation on all matured predictions: POST /predictions/validate',
        'Record baseline direction_accuracy, avg_error_pct, avg_change_error_pct',
        'Add automated weekly validation cron (APScheduler or Railway cron)',
        'Add accuracy trend chart to Prediction Accuracy tab',
        'Deliverable: Documented baseline accuracy number (expected ~50–55%)',
    ]
    for t in tasks_m0a:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track B: Build Error Baseline', level=3)
    tasks_m0b = [
        'Add BuildMetrics tracking to build_feature.py — log: syntax errors, test failures, frontend build failures, production wiring failures per build',
        'Store results in JSON artifact uploaded with GitHub Actions',
        'Parse artifact in a /builds/metrics endpoint',
        'Deliverable: Error rate measurement framework, initial baseline (expected ~20–30%)',
    ]
    for t in tasks_m0b:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track C: Exploitation Metrics Baseline', level=3)
    tasks_m0c = [
        'Tag all 103 existing BUILD recommendations with viability scores (run /exploitation/generate)',
        'Manually validate 10–20 BUILD recommendations against real-world outcomes',
        'Create exploitation_validation table to track: recommended vs actual opportunity success',
        'Deliverable: Documented baseline viability prediction accuracy (expected ~45–50%)',
    ]
    for t in tasks_m0c:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track D: Revenue Baseline', level=3)
    tasks_m0d = [
        'Audit Stripe dashboard for current subscriber count and MRR',
        'Document current revenue per app (Causal Affect, systems3-project-reporter)',
        'Deliverable: Revenue baseline document',
    ]
    for t in tasks_m0d:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Verification Criteria', level=3)
    for v in ['All 4 baselines documented with numbers', 'Automated weekly validation running', 'Build error tracking live in CI/CD']:
        doc.add_paragraph(v, style='List Bullet')

    doc.add_page_break()

    # ---------- M1 ----------
    doc.add_heading('Milestone 1: Foundation Scaling (Weeks 4–9)', level=2)
    p = doc.add_paragraph()
    run = p.add_run('Target: +5% accuracy (55→60%), data to ~100GB, build errors measured')
    run.italic = True

    doc.add_heading('Track A: Model Accuracy → 60%', level=3)
    for t in [
        'Add daily Wikipedia pageview ingestion (currently only monthly) — 55 variables × 365 days = 20K new daily records/year',
        'Add daily Reddit activity ingestion for top 30 subreddits mapped in SIGNAL_CROSS_VALIDATION',
        'Implement walk-forward validation (train on N months, predict month N+1, slide forward)',
        'Add multi-lag Granger testing (currently single optimal lag → test 1–12 month lags)',
        'Method: More granular data + proper validation methodology → reduces overfitting noise',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track B: Build Errors → 25% (from ~30%)', level=3)
    for t in [
        'Add pre-build template validation (lint templates before generation)',
        'Add automated import resolution (detect missing imports, auto-add)',
        'Add structured error reporting to GitHub Actions artifacts',
        'Method: Catch common failures before they happen',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track C: Exploitation Accuracy → 55%', level=3)
    for t in [
        'Backtest viability scores against 6-month historical data (which BUILD targets actually grew?)',
        'Calibrate viability scoring weights based on backtest results',
        'Add target_growth_actual field to ExploitationRecommendation for outcome tracking',
        'Method: Empirical calibration of scoring model',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track D: Data Infrastructure', level=3)
    for t in [
        'Enable TimescaleDB extension on Railway PostgreSQL',
        'Convert time_series_data to hypertable with time-based partitioning',
        'Add automated data retention policy (raw daily data: 2 years, aggregated: forever)',
        'Set up S3 bucket for cold storage archive',
        'Add connection pool tuning: pool_size=20, max_overflow=10',
        'Data target: ~100GB (55 vars × daily × 5 years + 30 Reddit subs × daily)',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track E: Revenue Dashboard v1', level=3)
    for t in [
        'Create RevenueEvent model (tracks: app_id, event_type, amount, currency, region, timestamp)',
        'Create /revenue/dashboard endpoint aggregating across all Stripe accounts',
        'Wire Stripe webhook events for all deployed apps to central tracker',
        'Build basic Revenue tab in dashboard (MRR chart, subscriber count, per-app breakdown)',
        'Method: Central webhook receiver that all deployed apps POST to',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Verification Criteria', level=3)
    for v in [
        'Walk-forward validation shows 60%+ direction accuracy',
        'Build error rate measured and baseline established',
        'TimescaleDB partitioning active, daily ingestion running',
        'Revenue dashboard shows real MRR data',
    ]:
        doc.add_paragraph(v, style='List Bullet')

    doc.add_page_break()

    # ---------- M2 ----------
    doc.add_heading('Milestone 2: Intelligence Layer (Weeks 10–15)', level=2)
    p = doc.add_paragraph()
    run = p.add_run('Target: 65% accuracy, 60% exploitation, build time → 4hrs, errors → 20%')
    run.italic = True

    doc.add_heading('Track A: Model Accuracy → 65%', level=3)
    for t in [
        'Add ensemble model: combine Granger causality + simple linear regression + ARIMA',
        'Implement confidence-weighted ensemble (weight by historical accuracy per model)',
        'Add feature engineering: rolling averages (7d, 30d, 90d), rate of change, volatility',
        'Add cross-validation signal confidence (Wikipedia + Reddit agreement score as feature)',
        'Method: Ensemble reduces individual model bias',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track B: Build Errors → 20%', level=3)
    for t in [
        'Add AI-powered code review step (LLM validates generated code before commit)',
        'Add integration test templates for common patterns (CRUD, auth, Stripe)',
        'Fix top 5 most common build failure patterns from M1 data',
        'Method: Systematic failure pattern elimination',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track C: Exploitation Accuracy → 60%', level=3)
    for t in [
        'Add Google Trends integration (use pytrends with proxy rotation to avoid blocks)',
        'Cross-reference viability scores with Google Trends search volume',
        'Add competition scoring from real arxiv citation counts (not just paper count)',
        'Method: Richer data inputs → more accurate viability assessment',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track D: Build Automation → 4 hours', level=3)
    for t in [
        'Automate GitHub repo creation in build trigger endpoint (via GitHub API)',
        'Auto-generate Railway project via Railway API',
        'Auto-wire Stripe subscription (create product + price via Stripe API)',
        'Auto-inject GA4 measurement ID from analytics template',
        'Deliverable: One-click "Build & Deploy" from Exploitation Board → live app in 4 hours',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track E: Data Scale → 500GB', level=3)
    for t in [
        'Add FRED economic indicators (50+ variables: GDP, CPI, unemployment, etc.)',
        'Add Alpha Vantage intraday data for top 10 stocks (5-min intervals)',
        'Add news sentiment from GDELT API (daily event counts by theme)',
        'Set up ETL pipeline with batch scheduling (APScheduler)',
        'Method: More diverse, higher-frequency data sources',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Verification Criteria', level=3)
    for v in [
        'Ensemble model shows 65%+ direction accuracy on walk-forward test',
        'Build → deploy → live app achievable in 4 hours with automation',
        'Revenue dashboard tracking first deployed app(s)',
    ]:
        doc.add_paragraph(v, style='List Bullet')

    doc.add_page_break()

    # ---------- M3 ----------
    doc.add_heading('Milestone 3: Self-Learning Foundation (Weeks 16–21)', level=2)
    p = doc.add_paragraph()
    run = p.add_run('Target: 70% accuracy, 65% exploitation, build time → 3hrs, errors → 15%')
    run.italic = True

    doc.add_heading('Track A: Model Accuracy → 70%', level=3)
    for t in [
        'Implement automatic model retraining when accuracy drops below threshold',
        'Add prediction feedback loop: validated predictions → retrain features',
        'Add anomaly detection (Z-score) to flag unusual signals before prediction',
        'Implement adaptive lag selection (dynamically adjust lag based on recent accuracy)',
        'Method: System learns from its own prediction outcomes',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track B: Build Errors → 15%', level=3)
    for t in [
        'Build error pattern classifier (categorize failures: import, syntax, config, runtime)',
        'Auto-fix common patterns (missing __init__.py, wrong import paths, missing env vars)',
        'Add scaffold regression tests (test each template produces working code)',
        'Method: Error taxonomy → targeted fixes → prevent recurrence',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track C: Exploitation Accuracy → 65%', level=3)
    for t in [
        'Track actual outcomes of PURSUING recommendations (did the BUILD succeed?)',
        'Add time-to-market analysis (how long from recommendation to live product?)',
        'Calibrate opportunity_duration_months against actual opportunity windows',
        'Method: Closed-loop validation against real deployment outcomes',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track D: Build Automation → 3 hours', level=3)
    for t in [
        'Add automated domain configuration (subdomain allocation)',
        'Add automated SSL certificate provisioning',
        'Add automated database setup for deployed apps',
        'Add post-deploy health check + smoke test',
        'Method: Remove remaining manual steps',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track E: Data Scale → 1TB', level=3)
    for t in [
        'Add social media feeds (Twitter/X academic API for trend data)',
        'Add IoT starter: OpenWeather API for 100 cities (hourly)',
        'Add Pushshift/Pullpush for full Reddit historical data',
        'Implement data compression in TimescaleDB (compress chunks >7 days old)',
        'Method: Breadth of sources + compression for storage efficiency',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track F: Pricing Intelligence v1', level=3)
    for t in [
        'Add IP geolocation to dashboard (MaxMind GeoLite2 free database)',
        'Map regions to PPP (Purchasing Power Parity) tiers from World Bank API',
        'Create pricing_recommendation table (region, suggested_price, confidence)',
        'Add traffic-based demand estimation per region',
        'Method: Traffic patterns + economic data → region-aware pricing suggestions',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Verification Criteria', level=3)
    for v in [
        'Self-retraining loop running automatically on weekly schedule',
        'Accuracy at 70%+ with feedback loop active',
        'Pricing intelligence generating region-specific suggestions',
        '1TB data threshold reached',
    ]:
        doc.add_paragraph(v, style='List Bullet')

    doc.add_page_break()

    # ---------- M4 ----------
    doc.add_heading('Milestone 4: Scale & Optimize (Weeks 22–27)', level=2)
    p = doc.add_paragraph()
    run = p.add_run('Target: 75% accuracy, 70% exploitation, build time → 2.5hrs, errors → 10%')
    run.italic = True

    doc.add_heading('Track A: Model Accuracy → 75%', level=3)
    for t in [
        'Add LSTM/transformer-based time series model (PyTorch) as ensemble member',
        'Implement feature importance ranking (SHAP values) for interpretability',
        'Add regime detection (market regimes: bull/bear/sideways affect model choice)',
        'Implement online learning (update model incrementally with new data)',
        'Method: Deep learning for non-linear patterns + regime-awareness',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track B: Build Errors → 10%', level=3)
    for t in [
        'Implement AI-powered scaffold improvement (analyse failed builds → update templates)',
        'Add end-to-end integration test suite for full build pipeline',
        'Add canary deployment (deploy to staging first, promote if healthy)',
        'Method: Self-improving templates based on failure analysis',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track C: Exploitation Accuracy → 70%', level=3)
    for t in [
        'Add competitive landscape analysis (how many similar apps exist?)',
        'Cross-reference with Product Hunt / Indie Hackers for market validation',
        'Add user engagement prediction model (predict DAU/MAU from topic + competition)',
        'Method: Market intelligence beyond statistical signals',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track D: Build Automation → 2.5 hours', level=3)
    for t in [
        'Add automated testing pipeline for deployed apps',
        'Add automated monitoring setup (uptime, error rate, performance)',
        'Add automated changelog and release notes generation',
        'Method: Reduce post-deployment manual work',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track E: Data Scale → 3TB', level=3)
    for t in [
        'Add Bloomberg/Reuters alternative data feeds (if budget allows)',
        'Add satellite imagery analysis for economic indicators (nighttime lights → GDP proxy)',
        'Implement data lakehouse pattern (S3 + DuckDB for analytics, PostgreSQL for hot data)',
        'Method: Alternative data + hybrid storage architecture',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track F: Revenue Dashboard v2', level=3)
    for t in [
        'Add Google AdSense integration for ad-supported apps',
        'Add per-app P&L tracking (revenue − infrastructure cost)',
        'Add subscriber cohort analysis (retention by signup month)',
        'Add revenue forecasting from growth trends',
        'Method: Full financial visibility across portfolio',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Verification Criteria', level=3)
    for v in [
        'Deep learning ensemble at 75%+ accuracy',
        'Build → deploy pipeline consistently under 2.5 hours',
        'Revenue dashboard showing all revenue streams (subscriptions + ads)',
        '3TB data with hybrid hot/cold storage',
    ]:
        doc.add_paragraph(v, style='List Bullet')

    doc.add_page_break()

    # ---------- M5 ----------
    doc.add_heading('Milestone 5: Autonomous Operations (Weeks 28–33)', level=2)
    p = doc.add_paragraph()
    run = p.add_run('Target: 80% accuracy, 75% exploitation, build time → 2hrs, errors → 5%')
    run.italic = True

    doc.add_heading('Track A: Model Accuracy → 80%', level=3)
    for t in [
        'Implement multi-horizon forecasting (1 week, 1 month, 3 month predictions)',
        'Add cross-market contagion detection (detect when one market shock propagates)',
        'Implement model selection autopilot (automatically pick best model per signal-target pair)',
        'Add uncertainty quantification (prediction intervals, not just point estimates)',
        'Method: Multi-horizon + automatic model selection + uncertainty',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track B: Build Errors → 5%', level=3)
    for t in [
        'Implement self-healing builds (detect error → auto-apply fix → retry)',
        'Add template versioning with A/B testing (test new vs old templates)',
        'Implement build quality gate (block deploy if quality score < threshold)',
        'Method: Self-healing + quality gates',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track C: Exploitation Accuracy → 75%', level=3)
    for t in [
        'Add market timing model (when to launch, not just what to build)',
        'Add user acquisition cost prediction from similar product data',
        'Add churn prediction for deployed products',
        'Method: Full lifecycle prediction (build + launch + grow + retain)',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track D: Build Automation → 2 hours', level=3)
    for t in [
        'Full zero-touch pipeline: recommendation → build → deploy → monitor → scale',
        'Add automated A/B testing for deployed apps',
        'Add automated pricing optimisation based on conversion data',
        'Method: Complete automation of all manual steps',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track E: Data Scale → 7TB', level=3)
    for t in [
        'Add real-time streaming (Kafka/Redis Streams for sub-minute data)',
        'Add sensor/IoT data ingestion (via MQTT broker)',
        'Implement federated querying across PostgreSQL + S3 + streaming',
        'Method: Real-time data foundation for time-critical signals',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track F: Pricing Intelligence v2', level=3)
    for t in [
        'Implement dynamic pricing engine (A/B test prices per region)',
        'Add currency conversion + PPP-adjusted pricing per country',
        'Add price elasticity estimation from traffic → conversion data',
        'Revenue-optimal pricing recommendations per app per region',
        'Method: Data-driven pricing optimisation',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Verification Criteria', level=3)
    for v in [
        '80%+ accuracy with uncertainty intervals',
        'Zero-touch build-to-deploy in 2 hours',
        'Self-healing builds at <5% error rate',
        'Revenue dashboard with dynamic pricing active',
    ]:
        doc.add_paragraph(v, style='List Bullet')

    doc.add_page_break()

    # ---------- M6 ----------
    doc.add_heading('Milestone 6: Intelligence Engine (Weeks 34–39)', level=2)
    p = doc.add_paragraph()
    run = p.add_run('Target: 85% accuracy, 80% exploitation, self-optimising')
    run.italic = True

    doc.add_heading('Track A: Model Accuracy → 85%', level=3)
    for t in [
        'Add reinforcement learning for trading strategy optimisation',
        'Implement model distillation (compress ensemble into fast inference model)',
        'Add causal discovery (go beyond Granger to structural causal models)',
        'Method: Advanced ML + causal inference',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track B: Self-Optimising Builds', level=3)
    for t in [
        'AI generates feature requirements from opportunity analysis (no YAML needed)',
        'Auto-select best scaffold and tech stack per opportunity',
        'Builds generate their own tests and validation suites',
        'Method: AI writes its own specifications',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track C: Exploitation Accuracy → 80%', level=3)
    for t in [
        'Portfolio optimisation across all deployed apps',
        'Resource re-allocation recommendations (scale winners, sunset losers)',
        'Auto-sunset underperforming products',
        'Method: Portfolio management approach',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track D: Data Scale → 10TB', level=3)
    for t in [
        'Full multi-source streaming ingestion operational',
        'Automated data quality monitoring and anomaly detection',
        'Data lineage tracking (know provenance of every prediction)',
        'Method: Enterprise-grade data platform',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track E: Revenue Engine', level=3)
    for t in [
        'Central dashboard showing portfolio MRR, CAC, LTV, churn by app',
        'Automated financial reporting (monthly P&L per product)',
        'Revenue alerts and anomaly detection',
        'Investment-ready metrics dashboard',
        'Method: Full financial operating system',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Verification Criteria', level=3)
    for v in [
        '85%+ accuracy on 3-month forward predictions',
        'Self-generating build specifications',
        'Portfolio-level revenue optimisation active',
        '10TB data platform operational',
    ]:
        doc.add_paragraph(v, style='List Bullet')

    doc.add_page_break()

    # ---------- M7 ----------
    doc.add_heading('Milestone 7: Market Leadership (Weeks 40–48)', level=2)
    p = doc.add_paragraph()
    run = p.add_run('Target: 90% accuracy, 90% exploitation, market-ready')
    run.italic = True

    doc.add_heading('Track A: Model Accuracy → 90%', level=3)
    for t in [
        'Continuous learning pipeline (models retrain and auto-promote)',
        'Model marketplace (share/sell prediction models to other users)',
        'Multi-asset class prediction (stocks, crypto, commodities, real estate)',
        'Method: Continuous improvement + market breadth',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track B: Full Automation', level=3)
    for t in [
        'End-to-end: signal detected → app built → deployed → monetised → optimised',
        'Average deployment time consistently under 2 hours',
        'Build error rate sustained below 5%',
        'Method: Mature, battle-tested automation',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track C: Exploitation Accuracy → 90%', level=3)
    for t in [
        'Multi-factor opportunity scoring validated against 12+ months of outcomes',
        'Automated opportunity discovery (system finds BUILD opportunities without prompting)',
        'Cross-opportunity synergy detection (products that complement each other)',
        'Method: Validated scoring + autonomous discovery',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Track D: Revenue Targets', level=3)
    for t in [
        '4–10 deployed apps generating subscription revenue',
        'Region-specific pricing active in 10+ markets',
        'Central revenue dashboard with real-time MRR tracking',
        'Target: $20K+ MRR across portfolio',
        'Method: Portfolio scale + pricing optimisation',
    ]:
        doc.add_paragraph(t, style='List Number')

    doc.add_heading('Verification Criteria', level=3)
    for v in [
        '90% direction accuracy on walk-forward validation (6-month window)',
        '90% exploitation recommendation viability (validated against outcomes)',
        '<5% build errors sustained over 3-month period',
        '2-hour average deployment time sustained',
        'Revenue dashboard live with all apps reporting',
        'Dynamic pricing active in multiple regions',
    ]:
        doc.add_paragraph(v, style='List Bullet')

    doc.add_page_break()

    # ===================== 4. ARCHITECTURE EVOLUTION =====================
    doc.add_heading('4. Architecture Evolution Path', level=1)

    doc.add_heading('Storage Evolution', level=2)
    storage_evol = [
        ('M0',   'PostgreSQL (14K records, ~50MB)'),
        ('M1',   '+ TimescaleDB extension + daily ingestion → 100GB'),
        ('M2',   '+ Connection pool tuning + query optimisation → 500GB'),
        ('M3',   '+ Data compression + S3 cold storage → 1TB'),
        ('M4',   '+ DuckDB analytics layer + data lakehouse → 3TB'),
        ('M5',   '+ Kafka streaming + federated queries → 7TB'),
        ('M6–7', 'Full hybrid: TimescaleDB (hot) + S3 (cold) + Kafka (streaming) → 10TB'),
    ]
    add_styled_table(doc, ['Milestone', 'Architecture'], storage_evol, header_color='2E75B6')

    doc.add_paragraph()

    doc.add_heading('Model Pipeline Evolution', level=2)
    model_evol = [
        ('M0',   'Granger causality only (granger_v1)'),
        ('M1',   '+ Walk-forward validation + multi-lag testing'),
        ('M2',   '+ Ensemble (Granger + linear + ARIMA) + feature engineering'),
        ('M3',   '+ Feedback loop + auto-retrain + anomaly detection'),
        ('M4',   '+ LSTM/transformer + regime detection + online learning'),
        ('M5',   '+ Multi-horizon + uncertainty quantification + autopilot'),
        ('M6',   '+ Causal discovery + reinforcement learning'),
        ('M7',   '+ Continuous learning + multi-asset + model marketplace'),
    ]
    add_styled_table(doc, ['Milestone', 'Architecture'], model_evol, header_color='2E75B6')

    doc.add_paragraph()

    doc.add_heading('Build Pipeline Evolution', level=2)
    build_evol = [
        ('M0',   'Manual build_feature.py + manual GitHub + manual Stripe (~5+ hours)'),
        ('M1',   '+ Error tracking + pre-build validation'),
        ('M2',   '+ Auto GitHub repo + auto Railway + auto Stripe + auto GA4 (~4 hours)'),
        ('M3',   '+ Auto domain + auto SSL + auto DB + smoke tests (~3 hours)'),
        ('M4',   '+ Staging/canary + auto monitoring (~2.5 hours)'),
        ('M5',   '+ Self-healing + quality gates (~2 hours)'),
        ('M6',   '+ AI-generated specs + auto stack selection'),
        ('M7',   '+ Zero-touch end-to-end pipeline'),
    ]
    add_styled_table(doc, ['Milestone', 'Architecture'], build_evol, header_color='2E75B6')

    doc.add_paragraph()

    doc.add_heading('Revenue System Evolution', level=2)
    rev_evol = [
        ('M0',   'Manual Stripe dashboard checks'),
        ('M1',   '+ Central RevenueEvent model + webhook aggregation'),
        ('M2',   '+ Per-app MRR chart + subscriber counts'),
        ('M3',   '+ Geo-pricing intelligence v1'),
        ('M4',   '+ Google Ads integration + per-app P&L + cohort analysis'),
        ('M5',   '+ Dynamic pricing engine + A/B pricing'),
        ('M6',   '+ Portfolio optimisation + auto-sunset'),
        ('M7',   '+ Full financial OS + investment-ready dashboard'),
    ]
    add_styled_table(doc, ['Milestone', 'Architecture'], rev_evol, header_color='2E75B6')

    doc.add_page_break()

    # ===================== 5. KEY FILES =====================
    doc.add_heading('5. Key Deliverables & Files', level=1)

    doc.add_heading('New Files to Create', level=2)
    new_files = [
        ('revenue_models.py', 'RevenueEvent, SubscriptionMetric, PricingRecommendation models'),
        ('revenue_router.py', 'Revenue dashboard endpoints'),
        ('revenue_webhook.py', 'Central Stripe webhook receiver for all apps'),
        ('pricing_engine.py', 'Region-aware pricing intelligence'),
        ('model_ensemble.py', 'Ensemble prediction service'),
        ('auto_retrain.py', 'Self-learning feedback loop'),
        ('streaming_ingestion.py', 'Kafka/Redis Streams ingestion'),
        ('build_error_tracker.py', 'Systematic build error classification'),
        ('self_healing_builder.py', 'Auto-fix build failures'),
    ]
    add_styled_table(doc, ['File', 'Purpose'], new_files, header_color='548235')

    doc.add_paragraph()

    doc.add_heading('Existing Files to Evolve', level=2)
    existing_files = [
        ('models.py', 'Add RevenueEvent, BuildProject, PricingRecommendation'),
        ('database.py', 'Connection pool tuning, TimescaleDB support'),
        ('data_fetcher.py', 'Add GDELT, Twitter/X, OpenWeather, Bloomberg feeds'),
        ('data_ingestion_service.py', 'Daily ingestion, streaming support'),
        ('build_feature.py', 'Error tracking, self-healing, quality gates'),
        ('build_system.py', 'Auto GitHub/Railway/Stripe/GA4 wiring'),
        ('dashboard_real.py', 'Revenue tab, pricing intelligence, model comparison'),
        ('dashboard.html', 'Revenue dashboard tab, pricing display'),
        ('ai-feature-builder.yml', 'Error artifact upload, staging deploy step'),
    ]
    add_styled_table(doc, ['File', 'Changes Required'], existing_files, header_color='548235')

    # ===================== FOOTER =====================
    doc.add_paragraph()
    doc.add_paragraph()
    footer = doc.add_paragraph()
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run('— End of Scope Document —')
    run.italic = True
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    return doc


if __name__ == '__main__':
    doc = build_document()
    output_path = '/workspaces/control_tower/Causal_Affect_Scaling_Plan_Scope.docx'
    doc.save(output_path)
    print(f'Saved to {output_path}')
