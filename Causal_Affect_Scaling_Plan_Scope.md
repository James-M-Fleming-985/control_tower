**Causal Affect\
Scaling Plan**

Baseline → 10TB / 90% Accuracy / Full Automation Revenue Engine

12-Month Programme Scope Document\
March 2026 -- March 2027\
\
Prepared: 10 March 2026

Table of Contents
=================

1\. Problem Statement & Objectives

2\. Current Baselines (March 2026)

3\. Programme Milestones

M0: Instrument & Measure (Weeks 1--3)

M1: Foundation Scaling (Weeks 4--9)

M2: Intelligence Layer (Weeks 10--15)

M3: Self-Learning Foundation (Weeks 16--21)

M4: Scale & Optimize (Weeks 22--27)

M5: Autonomous Operations (Weeks 28--33)

M6: Intelligence Engine (Weeks 34--39)

M7: Market Leadership (Weeks 40--48)

4\. Architecture Evolution Path

5\. Key Deliverables & Files

1. Problem Statement & Objectives
=================================

Current state: approximately 14,000 data points across 55 variables,
unmeasured model accuracy, manual multi-hour builds, no cross-app
revenue tracking, and no self-improvement loop.

Target state: 10TB data ingestion, 90% model accuracy, 2-hour automated
deployments, less than 5% build errors, region-aware pricing,
centralised revenue dashboard --- all feeding a self-learning engine.

Key Decisions
-------------

-   **Timeline:** 12 months (balanced), \~8 milestones at approximately
    6 weeks each

-   **App Scope:** 4--10 apps (per AMP plan)

-   **Data Sources:** All --- social/financial feeds, news/search
    trends, IoT/sensor

-   **Storage Evolution:** PostgreSQL → TimescaleDB → S3 cold storage +
    hot cache

Foundational Architecture: The Autonomous Business Loop
-------------------------------------------------------

Every capability in this programme exists to serve a single self-correcting loop. The system MUST operate this loop without human intervention; user input is restricted to read-only audit and program-level configuration.

**The six stages:**

1.  **Discovery** --- The system identifies opportunities from external signals (causal models, trends, market data). Recommendations originate ONLY here.
2.  **Adapt** --- For each Discovery-sourced opportunity, the system generates a specification, acceptance criteria, and an implementation plan. No human approval gate.
3.  **Exploit** --- The system builds, verifies, and deploys an MVP from the spec. Verification artifacts (REQ traceability, AC pass/fail) are produced as internal evidence.
4.  **Monitor** --- The deployed MVP emits a beacon identifying its `build_id`. Engagement is collected via GA4 (system of record) and revenue via Stripe, joined back to the build.
5.  **Learn** --- The system correlates verification status, telemetry outcomes, prompt versions, and spec attributes to identify what predicts engagement and revenue.
6.  **Optimize** --- Findings feed back into prompt selection, discovery signal weighting, and resource allocation, closing the loop. Initially this surfaces recommendations; in M3+ it auto-rotates.

**Operating principle:** when build quality is poor, the fix is to improve the loop's learning, never to insert a human gate.

Out-of-Scope Guardrails (Anti-Drift)
------------------------------------

To preserve the autonomous loop, the following are explicitly out of scope for the entire programme:

**The system MUST NOT:**

-   Accept manually-entered ideas or recommendations from the user (Discovery is the only source)
-   Require user approval of specifications, acceptance criteria, or generated code before building
-   Allow editing of specs, ACs, or code via the UI
-   Treat verification artifacts as a user-facing approval gate
-   Interrupt the Discovery → Adapt → Exploit → Monitor → Learn → Optimize loop with synchronous user steps
-   Use mock, synthetic, or placeholder data anywhere in production

**The system MUST:**

-   Originate every build from a Discovery-sourced recommendation
-   Verify every build against its acceptance criteria with PROJECT-004-style traceability artifacts
-   Bind every build to telemetry (engagement via GA4, revenue via Stripe) keyed by `build_id`
-   Use telemetry plus verification status to learn and improve future builds
-   Expose all evidence (specs, ACs, verification reports, telemetry) as a read-only audit trail

When a feature request would violate any MUST NOT above, the request must be re-framed as either (a) a system-learning improvement, or (b) a read-only audit improvement.

2. Current Baselines (March 2026)
=================================

  **Dimension**                **Current**                                   **Target**                         **Gap**
  ---------------------------- --------------------------------------------- ---------------------------------- ------------------------
  Data Volume                  \~14K records, \~55 vars, single PostgreSQL   10TB across distributed storage    \~99.999% gap
  Model Accuracy (direction)   Unmeasured (\~50% theoretical)                90%                                \~40% improvement
  Exploitation Accuracy        Viability scoring just implemented            90%                                \~40% improvement
  Deployment Time              30--45 min build + manual = several hours     2 hours fully automated            Automation gap
  Build Error Rate             Unmeasured, no tracking                       \<5%                               Tracking + improvement
  Pricing Intelligence         Fixed tiers (\$0--\$199.99)                   Region/economy-specific dynamic    Not started
  Revenue Dashboard            Stripe in systems3 only                       Central dashboard, all apps        Not started
  Self-Improvement             Legacy retrain code (non-operational)         Continuous learning, auto-tuning   Not started
  Deployed Apps                1 (Causal Affect) + 1 (systems3)              4--10 apps (per AMP)               2--8 more apps

3. Programme Milestones
=======================

Milestone Progression Summary
-----------------------------

  **ID**   **Weeks**   **Name**                   **Data**   **Model Acc**   **Exploit Acc**   **Build Err**   **Deploy Time**
  -------- ----------- -------------------------- ---------- --------------- ----------------- --------------- -----------------
  M0       Wk 1--3     Instrument & Measure       Baseline   Baseline        Baseline          \~30%           \~5+ hrs
  M1       Wk 4--9     Foundation Scaling         \~100GB    60%             55%               25%             ---
  M2       Wk 10--15   Intelligence Layer         \~500GB    65%             60%               20%             4 hrs
  M3       Wk 16--21   Self-Learning Foundation   \~1TB      70%             65%               15%             3 hrs
  M4       Wk 22--27   Scale & Optimize           \~3TB      75%             70%               10%             2.5 hrs
  M5       Wk 28--33   Autonomous Operations      \~7TB      80%             75%               5%              2 hrs
  M6       Wk 34--39   Intelligence Engine        \~10TB     85%             80%               Self-opt        Self-opt
  M7       Wk 40--48   Market Leadership          10TB       90%             90%               \<5%            \<2 hrs

Milestone 0: Instrument & Measure (Weeks 1--3)
----------------------------------------------

*\"You can\'t improve what you can\'t measure\"*

### Track A: Model Accuracy Baseline

1.  Run prediction validation on all matured predictions: POST
    /predictions/validate

2.  Record baseline direction\_accuracy, avg\_error\_pct,
    avg\_change\_error\_pct

3.  Add automated weekly validation cron (APScheduler or Railway cron)

4.  Add accuracy trend chart to Prediction Accuracy tab

5.  Deliverable: Documented baseline accuracy number (expected
    \~50--55%)

### Track B: Build Error Baseline

6.  Add BuildMetrics tracking to build\_feature.py --- log: syntax
    errors, test failures, frontend build failures, production wiring
    failures per build

7.  Store results in JSON artifact uploaded with GitHub Actions

8.  Parse artifact in a /builds/metrics endpoint

9.  Deliverable: Error rate measurement framework, initial baseline
    (expected \~20--30%)

### Track C: Exploitation Metrics Baseline

10. Tag all 103 existing BUILD recommendations with viability scores
    (run /exploitation/generate)

11. Manually validate 10--20 BUILD recommendations against real-world
    outcomes

12. Create exploitation\_validation table to track: recommended vs
    actual opportunity success

13. Deliverable: Documented baseline viability prediction accuracy
    (expected \~45--50%)

### Track D: Revenue Baseline

14. Audit Stripe dashboard for current subscriber count and MRR

15. Document current revenue per app (Causal Affect,
    systems3-project-reporter)

16. Deliverable: Revenue baseline document

### Verification Criteria

-   All 4 baselines documented with numbers

-   Automated weekly validation running

-   Build error tracking live in CI/CD

Milestone 1: Foundation Scaling (Weeks 4--9)
--------------------------------------------

*Target: +5% accuracy (55→60%), data to \~100GB, build errors measured*

### Track A: Model Accuracy → 60%

17. Add daily Wikipedia pageview ingestion (currently only monthly) ---
    55 variables × 365 days = 20K new daily records/year

18. Add daily Reddit activity ingestion for top 30 subreddits mapped in
    SIGNAL\_CROSS\_VALIDATION

19. Implement walk-forward validation (train on N months, predict month
    N+1, slide forward)

20. Add multi-lag Granger testing (currently single optimal lag → test
    1--12 month lags)

21. Method: More granular data + proper validation methodology → reduces
    overfitting noise

### Track B: Build Errors → 25% (from \~30%)

22. Add pre-build template validation (lint templates before generation)

23. Add automated import resolution (detect missing imports, auto-add)

24. Add structured error reporting to GitHub Actions artifacts

25. Method: Catch common failures before they happen

### Track C: Exploitation Accuracy → 55%

26. Backtest viability scores against 6-month historical data (which
    BUILD targets actually grew?)

27. Calibrate viability scoring weights based on backtest results

28. Add target\_growth\_actual field to ExploitationRecommendation for
    outcome tracking

29. Method: Empirical calibration of scoring model

### Track D: Data Infrastructure

30. Enable TimescaleDB extension on Railway PostgreSQL

31. Convert time\_series\_data to hypertable with time-based
    partitioning

32. Add automated data retention policy (raw daily data: 2 years,
    aggregated: forever)

33. Set up S3 bucket for cold storage archive

34. Add connection pool tuning: pool\_size=20, max\_overflow=10

35. Data target: \~100GB (55 vars × daily × 5 years + 30 Reddit subs ×
    daily)

### Track E: Revenue Dashboard v1

36. Create RevenueEvent model (tracks: app\_id, event\_type, amount,
    currency, region, timestamp)

37. Create /revenue/dashboard endpoint aggregating across all Stripe
    accounts

38. Wire Stripe webhook events for all deployed apps to central tracker

39. Build basic Revenue tab in dashboard (MRR chart, subscriber count,
    per-app breakdown)

40. Method: Central webhook receiver that all deployed apps POST to

### Verification Criteria

-   Walk-forward validation shows 60%+ direction accuracy

-   Build error rate measured and baseline established

-   TimescaleDB partitioning active, daily ingestion running

-   Revenue dashboard shows real MRR data

Milestone 2: Intelligence Layer (Weeks 10--15)
----------------------------------------------

*Target: 65% accuracy, 60% exploitation, build time → 4hrs, errors →
20%*

### Track A: Model Accuracy → 65%

41. Add ensemble model: combine Granger causality + simple linear
    regression + ARIMA

42. Implement confidence-weighted ensemble (weight by historical
    accuracy per model)

43. Add feature engineering: rolling averages (7d, 30d, 90d), rate of
    change, volatility

44. Add cross-validation signal confidence (Wikipedia + Reddit agreement
    score as feature)

45. Method: Ensemble reduces individual model bias

### Track B: Build Errors → 20%

46. Add AI-powered code review step (LLM validates generated code before
    commit)

47. Add integration test templates for common patterns (CRUD, auth,
    Stripe)

48. Fix top 5 most common build failure patterns from M1 data

49. Method: Systematic failure pattern elimination

### Track C: Exploitation Accuracy → 60%

50. Add Google Trends integration (use pytrends with proxy rotation to
    avoid blocks)

51. Cross-reference viability scores with Google Trends search volume

52. Add competition scoring from real arxiv citation counts (not just
    paper count)

53. Method: Richer data inputs → more accurate viability assessment

### Track D: Build Automation → 4 hours

54. Automate GitHub repo creation in build trigger endpoint (via GitHub
    API)

55. Auto-generate Railway project via Railway API

56. Auto-wire Stripe subscription (create product + price via Stripe
    API)

57. Auto-inject GA4 measurement ID from analytics template

58. Deliverable: One-click \"Build & Deploy\" from Exploitation Board →
    live app in 4 hours

### Track E: Data Scale → 500GB

59. Add FRED economic indicators (50+ variables: GDP, CPI, unemployment,
    etc.)

60. Add Alpha Vantage intraday data for top 10 stocks (5-min intervals)

61. Add news sentiment from GDELT API (daily event counts by theme)

62. Set up ETL pipeline with batch scheduling (APScheduler)

63. Method: More diverse, higher-frequency data sources

### Track I: Autonomous Loop Closure (M2)

I-1. Remove all manual idea-injection paths from the dashboard (button, modal, endpoint). Existing `source='manual'` rows hard-deleted. Discovery becomes the sole origin of recommendations.

I-2. Port the PROJECT-004 verification engine into the build pipeline. Inject `# REQ-AC-NNN` tags into spec, test, and implementation prompts. Generate the 5-file `Requirements Verification/` artifact bundle per build (traceability_matrix, requirements_verification, execution_evidence, quality_gates_report, README_VERIFICATION).

I-3. Persist `verification_status` and `verification_artifacts_url` on each MVPBuild. Display a read-only "X/N verified" badge and a "View Build Evidence" link (GitHub folder) on the build card. No approval gate.

I-4. Auto-REFACTOR loop: when any AC is FAILED, the system automatically re-runs REFACTOR (max 2 retries) targeting the failed ACs. If verification still fails, the build is BLOCKED from deployment, the build row shows "—" instead of a URL, and the failure is recorded for telemetry/learning.

I-5. Beacon binding (Monitor stage): every AI-generated `main.py` includes a GA4 snippet with `build_id` as a custom dimension; Stripe metadata includes `build_id`. A `BuildTelemetry` table joins GA4 engagement + Stripe revenue + verification status per build (on-demand fetch initially).

I-6. Program Baseline panel additions (Learn stage, read-only): build quality × engagement × revenue scatter and correlation summary, displayed within the existing Program Baseline tab.

I-7. Verification criteria: zero manual-entry paths in the UI; every new build pushes a verification artifact bundle; build cards show verification status; Program Baseline shows the quality↔outcome correlation.

### Verification Criteria

-   Ensemble model shows 65%+ direction accuracy on walk-forward test

-   Build → deploy → live app achievable in 4 hours with automation

-   Revenue dashboard tracking first deployed app(s)

-   Track I: autonomous loop fully closed end-to-end (Discovery → Adapt → Exploit → Monitor → Learn) with no manual user gates

Milestone 3: Self-Learning Foundation (Weeks 16--21)
----------------------------------------------------

*Target: 70% accuracy, 65% exploitation, build time → 3hrs, errors →
15%*

### Track A: Model Accuracy → 70%

64. Implement automatic model retraining when accuracy drops below
    threshold

65. Add prediction feedback loop: validated predictions → retrain
    features

66. Add anomaly detection (Z-score) to flag unusual signals before
    prediction

67. Implement adaptive lag selection (dynamically adjust lag based on
    recent accuracy)

68. Method: System learns from its own prediction outcomes

### Track B: Build Errors → 15%

69. Build error pattern classifier (categorize failures: import, syntax,
    config, runtime)

70. Auto-fix common patterns (missing \_\_init\_\_.py, wrong import
    paths, missing env vars)

71. Add scaffold regression tests (test each template produces working
    code)

72. Method: Error taxonomy → targeted fixes → prevent recurrence

### Track C: Exploitation Accuracy → 65%

73. Track actual outcomes of PURSUING recommendations (did the BUILD
    succeed?)

74. Add time-to-market analysis (how long from recommendation to live
    product?)

75. Calibrate opportunity\_duration\_months against actual opportunity
    windows

76. Method: Closed-loop validation against real deployment outcomes

### Track D: Build Automation → 3 hours

77. Add automated domain configuration (subdomain allocation)

78. Add automated SSL certificate provisioning

79. Add automated database setup for deployed apps

80. Add post-deploy health check + smoke test

81. Method: Remove remaining manual steps

### Track E: Data Scale → 1TB

82. Add social media feeds (Twitter/X academic API for trend data)

83. Add IoT starter: OpenWeather API for 100 cities (hourly)

84. Add Pushshift/Pullpush for full Reddit historical data

85. Implement data compression in TimescaleDB (compress chunks \>7 days
    old)

86. Method: Breadth of sources + compression for storage efficiency

### Track F: Pricing Intelligence v1

87. Add IP geolocation to dashboard (MaxMind GeoLite2 free database)

88. Map regions to PPP (Purchasing Power Parity) tiers from World Bank
    API

89. Create pricing\_recommendation table (region, suggested\_price,
    confidence)

90. Add traffic-based demand estimation per region

91. Method: Traffic patterns + economic data → region-aware pricing
    suggestions

### Track I: Loop Optimize Stage (M3)

I-8. Move all generation prompts (spec, test, implementation, wrapper) to versioned files under `prompts/*.md`. Record `prompt_path` + git SHA used per build on the MVPBuild record.

I-9. Background analysis job: every N builds, correlate {prompt_version, verification_status, telemetry_outcomes, spec_attributes} and surface findings in the Program Baseline panel (e.g. "impl_prompt_v3.2 reduced facade endpoints from 40% → 12%").

I-10. Optimize stage at M3 = surface findings only (read-only). Auto-rotation of prompts is deferred to M5+ once enough baseline data exists.

### Verification Criteria

-   Self-retraining loop running automatically on weekly schedule

-   Accuracy at 70%+ with feedback loop active

-   Pricing intelligence generating region-specific suggestions

-   1TB data threshold reached

-   Track I: prompt versions tracked per build; Program Baseline shows
    prompt-version performance correlations

Milestone 4: Scale & Optimize (Weeks 22--27)
--------------------------------------------

*Target: 75% accuracy, 70% exploitation, build time → 2.5hrs, errors →
10%*

### Track A: Model Accuracy → 75%

92. Add LSTM/transformer-based time series model (PyTorch) as ensemble
    member

93. Implement feature importance ranking (SHAP values) for
    interpretability

94. Add regime detection (market regimes: bull/bear/sideways affect
    model choice)

95. Implement online learning (update model incrementally with new data)

96. Method: Deep learning for non-linear patterns + regime-awareness

### Track B: Build Errors → 10%

97. Implement AI-powered scaffold improvement (analyse failed builds →
    update templates)

98. Add end-to-end integration test suite for full build pipeline

99. Add canary deployment (deploy to staging first, promote if healthy)

100. Method: Self-improving templates based on failure analysis

### Track C: Exploitation Accuracy → 70%

101. Add competitive landscape analysis (how many similar apps exist?)

102. Cross-reference with Product Hunt / Indie Hackers for market
     validation

103. Add user engagement prediction model (predict DAU/MAU from topic +
     competition)

104. Method: Market intelligence beyond statistical signals

### Track D: Build Automation → 2.5 hours

105. Add automated testing pipeline for deployed apps

106. Add automated monitoring setup (uptime, error rate, performance)

107. Add automated changelog and release notes generation

108. Method: Reduce post-deployment manual work

### Track E: Data Scale → 3TB

109. Add Bloomberg/Reuters alternative data feeds (if budget allows)

110. Add satellite imagery analysis for economic indicators (nighttime
     lights → GDP proxy)

111. Implement data lakehouse pattern (S3 + DuckDB for analytics,
     PostgreSQL for hot data)

112. Method: Alternative data + hybrid storage architecture

### Track F: Revenue Dashboard v2

113. Add Google AdSense integration for ad-supported apps

114. Add per-app P&L tracking (revenue − infrastructure cost)

115. Add subscriber cohort analysis (retention by signup month)

116. Add revenue forecasting from growth trends

117. Method: Full financial visibility across portfolio

### Verification Criteria

-   Deep learning ensemble at 75%+ accuracy

-   Build → deploy pipeline consistently under 2.5 hours

-   Revenue dashboard showing all revenue streams (subscriptions + ads)

-   3TB data with hybrid hot/cold storage

Milestone 5: Autonomous Operations (Weeks 28--33)
-------------------------------------------------

*Target: 80% accuracy, 75% exploitation, build time → 2hrs, errors → 5%*

### Track A: Model Accuracy → 80%

118. Implement multi-horizon forecasting (1 week, 1 month, 3 month
     predictions)

119. Add cross-market contagion detection (detect when one market shock
     propagates)

120. Implement model selection autopilot (automatically pick best model
     per signal-target pair)

121. Add uncertainty quantification (prediction intervals, not just
     point estimates)

122. Method: Multi-horizon + automatic model selection + uncertainty

### Track B: Build Errors → 5%

123. Implement self-healing builds (detect error → auto-apply fix →
     retry)

124. Add template versioning with A/B testing (test new vs old
     templates)

125. Implement build quality gate (block deploy if quality score \<
     threshold)

126. Method: Self-healing + quality gates

### Track C: Exploitation Accuracy → 75%

127. Add market timing model (when to launch, not just what to build)

128. Add user acquisition cost prediction from similar product data

129. Add churn prediction for deployed products

130. Method: Full lifecycle prediction (build + launch + grow + retain)

### Track D: Build Automation → 2 hours

131. Full zero-touch pipeline: recommendation → build → deploy → monitor
     → scale

132. Add automated A/B testing for deployed apps

133. Add automated pricing optimisation based on conversion data

134. Method: Complete automation of all manual steps

### Track E: Data Scale → 7TB

135. Add real-time streaming (Kafka/Redis Streams for sub-minute data)

136. Add sensor/IoT data ingestion (via MQTT broker)

137. Implement federated querying across PostgreSQL + S3 + streaming

138. Method: Real-time data foundation for time-critical signals

### Track F: Pricing Intelligence v2

139. Implement dynamic pricing engine (A/B test prices per region)

140. Add currency conversion + PPP-adjusted pricing per country

141. Add price elasticity estimation from traffic → conversion data

142. Revenue-optimal pricing recommendations per app per region

143. Method: Data-driven pricing optimisation

### Verification Criteria

-   80%+ accuracy with uncertainty intervals

-   Zero-touch build-to-deploy in 2 hours

-   Self-healing builds at \<5% error rate

-   Revenue dashboard with dynamic pricing active

Milestone 6: Intelligence Engine (Weeks 34--39)
-----------------------------------------------

*Target: 85% accuracy, 80% exploitation, self-optimising*

### Track A: Model Accuracy → 85%

144. Add reinforcement learning for trading strategy optimisation

145. Implement model distillation (compress ensemble into fast inference
     model)

146. Add causal discovery (go beyond Granger to structural causal
     models)

147. Method: Advanced ML + causal inference

### Track B: Self-Optimising Builds

148. AI generates feature requirements from opportunity analysis (no
     YAML needed)

149. Auto-select best scaffold and tech stack per opportunity

150. Builds generate their own tests and validation suites

151. Method: AI writes its own specifications

### Track C: Exploitation Accuracy → 80%

152. Portfolio optimisation across all deployed apps

153. Resource re-allocation recommendations (scale winners, sunset
     losers)

154. Auto-sunset underperforming products

155. Method: Portfolio management approach

### Track D: Data Scale → 10TB

156. Full multi-source streaming ingestion operational

157. Automated data quality monitoring and anomaly detection

158. Data lineage tracking (know provenance of every prediction)

159. Method: Enterprise-grade data platform

### Track E: Revenue Engine

160. Central dashboard showing portfolio MRR, CAC, LTV, churn by app

161. Automated financial reporting (monthly P&L per product)

162. Revenue alerts and anomaly detection

163. Investment-ready metrics dashboard

164. Method: Full financial operating system

### Verification Criteria

-   85%+ accuracy on 3-month forward predictions

-   Self-generating build specifications

-   Portfolio-level revenue optimisation active

-   10TB data platform operational

Milestone 7: Market Leadership (Weeks 40--48)
---------------------------------------------

*Target: 90% accuracy, 90% exploitation, market-ready*

### Track A: Model Accuracy → 90%

165. Continuous learning pipeline (models retrain and auto-promote)

166. Model marketplace (share/sell prediction models to other users)

167. Multi-asset class prediction (stocks, crypto, commodities, real
     estate)

168. Method: Continuous improvement + market breadth

### Track B: Full Automation

169. End-to-end: signal detected → app built → deployed → monetised →
     optimised

170. Average deployment time consistently under 2 hours

171. Build error rate sustained below 5%

172. Method: Mature, battle-tested automation

### Track C: Exploitation Accuracy → 90%

173. Multi-factor opportunity scoring validated against 12+ months of
     outcomes

174. Automated opportunity discovery (system finds BUILD opportunities
     without prompting)

175. Cross-opportunity synergy detection (products that complement each
     other)

176. Method: Validated scoring + autonomous discovery

### Track D: Revenue Targets

177. 4--10 deployed apps generating subscription revenue

178. Region-specific pricing active in 10+ markets

179. Central revenue dashboard with real-time MRR tracking

180. Target: \$20K+ MRR across portfolio

181. Method: Portfolio scale + pricing optimisation

### Verification Criteria

-   90% direction accuracy on walk-forward validation (6-month window)

-   90% exploitation recommendation viability (validated against
    outcomes)

-   \<5% build errors sustained over 3-month period

-   2-hour average deployment time sustained

-   Revenue dashboard live with all apps reporting

-   Dynamic pricing active in multiple regions

4. Architecture Evolution Path
==============================

Storage Evolution
-----------------

  **Milestone**   **Architecture**
  --------------- -----------------------------------------------------------------------
  M0              PostgreSQL (14K records, \~50MB)
  M1              \+ TimescaleDB extension + daily ingestion → 100GB
  M2              \+ Connection pool tuning + query optimisation → 500GB
  M3              \+ Data compression + S3 cold storage → 1TB
  M4              \+ DuckDB analytics layer + data lakehouse → 3TB
  M5              \+ Kafka streaming + federated queries → 7TB
  M6--7           Full hybrid: TimescaleDB (hot) + S3 (cold) + Kafka (streaming) → 10TB

Model Pipeline Evolution
------------------------

  **Milestone**   **Architecture**
  --------------- --------------------------------------------------------------
  M0              Granger causality only (granger\_v1)
  M1              \+ Walk-forward validation + multi-lag testing
  M2              \+ Ensemble (Granger + linear + ARIMA) + feature engineering
  M3              \+ Feedback loop + auto-retrain + anomaly detection
  M4              \+ LSTM/transformer + regime detection + online learning
  M5              \+ Multi-horizon + uncertainty quantification + autopilot
  M6              \+ Causal discovery + reinforcement learning
  M7              \+ Continuous learning + multi-asset + model marketplace

Build Pipeline Evolution
------------------------

  **Milestone**   **Architecture**
  --------------- -------------------------------------------------------------------------
  M0              Manual build\_feature.py + manual GitHub + manual Stripe (\~5+ hours)
  M1              \+ Error tracking + pre-build validation
  M2              \+ Auto GitHub repo + auto Railway + auto Stripe + auto GA4 (\~4 hours)
  M3              \+ Auto domain + auto SSL + auto DB + smoke tests (\~3 hours)
  M4              \+ Staging/canary + auto monitoring (\~2.5 hours)
  M5              \+ Self-healing + quality gates (\~2 hours)
  M6              \+ AI-generated specs + auto stack selection
  M7              \+ Zero-touch end-to-end pipeline

Revenue System Evolution
------------------------

  **Milestone**   **Architecture**
  --------------- -----------------------------------------------------------
  M0              Manual Stripe dashboard checks
  M1              \+ Central RevenueEvent model + webhook aggregation
  M2              \+ Per-app MRR chart + subscriber counts
  M3              \+ Geo-pricing intelligence v1
  M4              \+ Google Ads integration + per-app P&L + cohort analysis
  M5              \+ Dynamic pricing engine + A/B pricing
  M6              \+ Portfolio optimisation + auto-sunset
  M7              \+ Full financial OS + investment-ready dashboard

5. Key Deliverables & Files
===========================

New Files to Create
-------------------

  **File**                    **Purpose**
  --------------------------- ----------------------------------------------------------------
  revenue\_models.py          RevenueEvent, SubscriptionMetric, PricingRecommendation models
  revenue\_router.py          Revenue dashboard endpoints
  revenue\_webhook.py         Central Stripe webhook receiver for all apps
  pricing\_engine.py          Region-aware pricing intelligence
  model\_ensemble.py          Ensemble prediction service
  auto\_retrain.py            Self-learning feedback loop
  streaming\_ingestion.py     Kafka/Redis Streams ingestion
  build\_error\_tracker.py    Systematic build error classification
  self\_healing\_builder.py   Auto-fix build failures
  verification\_engine.py     PROJECT-004 port: REQ traceability + AC pass/fail artifacts (Track I)
  build\_telemetry.py         BuildTelemetry model + GA4/Stripe joiners keyed by build\_id (Track I)
  prompts/                    Versioned generation prompts (spec, test, impl, wrapper) tracked per build (Track I)

Existing Files to Evolve
------------------------

  **File**                      **Changes Required**
  ----------------------------- -------------------------------------------------------
  models.py                     Add RevenueEvent, BuildProject, PricingRecommendation
  database.py                   Connection pool tuning, TimescaleDB support
  data\_fetcher.py              Add GDELT, Twitter/X, OpenWeather, Bloomberg feeds
  data\_ingestion\_service.py   Daily ingestion, streaming support
  build\_feature.py             Error tracking, self-healing, quality gates
  build\_system.py              Auto GitHub/Railway/Stripe/GA4 wiring
  dashboard\_real.py            Revenue tab, pricing intelligence, model comparison
  dashboard.html                Revenue dashboard tab, pricing display
  ai-feature-builder.yml        Error artifact upload, staging deploy step

*--- End of Scope Document ---*
