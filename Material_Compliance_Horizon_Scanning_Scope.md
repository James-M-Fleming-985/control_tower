# Material Compliance Horizon Scanning and Impact Assessment Application

**Project Code:** PROJECT-MCH-IA
**Reference MVP:** [mvp-32-mc-scanner-and-risk-identification](https://github.com/James-M-Fleming-985/mvp-32-mc-scanner-and-risk-identification)
**Duration:** 6 months (2026-04-21 to 2026-10-20)
**Status:** Scope baseline

---

## 1. Vision

A horizon-scanning and **impact assessment** platform that continuously monitors global material-compliance signals (regulatory bodies, NGO campaigns, scientific literature, social media) and quantifies their impact on a client's product portfolio by reading directly from the client's PLM (parts and products database). The application gives compliance, sustainability, and engineering teams an early-warning view of forthcoming restrictions and enables fact-based prioritisation of mitigation work.

> Terminology: the assessment performed by the application is referred to as **impact assessment** (the client's preferred term), not "risk assessment".

---

## 2. Features

### 2.1 Regulatory Change Ingestion
Continuous ingestion of new and amended regulations, restricted-substance lists, candidate lists, and consultation documents from UK REACH, EU REACH/ECHA, US EPA (TSCA), APAC regulators (China MEE, Japan METI, Korea ME), RoHS, PFAS-specific instruments, SCIP, EU Batteries Regulation, Packaging & Waste Directive, and aerospace/defence-specific regimes.

### 2.2 Normalisation & Classification
LLM-assisted normalisation of heterogeneous source documents into a common schema (substance, CAS, regulation, jurisdiction, status, effective date, scope, threshold). Classification of events by lifecycle stage (proposal, consultation, adopted, in-force, sunset).

### 2.3 Impact Scoring (Impact Assessment Engine)
Scoring of each regulatory event against the client's parts/products by joining ingested substance/scope data with the client's PLM bill-of-materials. Produces per-part, per-product, and per-business-unit impact scores with traceable evidence chains.

### 2.4 Dashboard
Interactive dashboard with:
- Live event feed (chronological, filterable)
- Regulatory heatmap (jurisdiction × substance class × time)
- Event detail drill-down (source document, normalised fields, affected parts)
- Filters (jurisdiction, substance, lifecycle stage, business unit, product family)
- Portfolio impact dashboard (top affected products, mitigation backlog)
- Module selector (toggle which regulatory modules are active per tenant)

### 2.5 Alerts
Configurable alerts (email, webhook, in-app) on new events, status changes, and threshold-crossing impact scores against the client's portfolio.

### 2.6 API
REST/JSON API for:
- Querying normalised events
- Submitting/refreshing PLM data
- Retrieving impact assessments
- Webhook subscription management

### 2.7 Modular Expansion
Pluggable module pattern enabling new regulatory regimes (e.g. additional jurisdictions, new substance instruments) to be added without core changes. Each module encapsulates its sources, parsers, and classification rules.

---

## 3. UI / UX

- **Event feed** — chronological stream with severity, jurisdiction, lifecycle stage badges
- **Heatmap** — substance × jurisdiction × time intensity view
- **Event detail** — source document viewer, normalised fields, affected parts list with PLM links
- **Filters** — persistent, shareable URL state
- **Portfolio impact dashboard** — KPIs, top-N affected products, trend
- **Module selector** — admin view to enable/disable regulatory modules per tenant
- **Dark mode** parity across all views

---

## 4. Integrations

### 4.1 Inbound (Sources)
- UK REACH / HSE
- EU REACH / ECHA (Candidate List, Authorisation List, Restriction List, SCIP)
- US EPA (TSCA Inventory, SNUR, Section 6 actions)
- APAC: China MEE, Japan METI/CSCL, Korea K-REACH
- RoHS amendments and exemption decisions
- PFAS-specific instruments (multi-jurisdiction)
- EU Batteries Regulation
- Packaging & Packaging Waste Directive
- Aerospace/Defence-specific lists (e.g. REACH Annex XIV impact on Defence exemptions)
- NGO campaign feeds (ChemSec, EEB, etc.)
- Social-media signal (curated handle list, scientific Twitter/X, LinkedIn)

### 4.2 Outbound / Bi-directional
- **PLM (Teamcenter reference adapter)** — read parts, BOMs, substance declarations from the client's Teamcenter instance via Active Workspace REST / TC Open Services. The integration is delivered as a generic PLM adapter interface plus a reference Teamcenter adapter so further PLMs (Windchill, Aras, 3DEXPERIENCE) can be added later.
- Email / SMTP for alerts
- Webhooks for downstream systems (ERP, EHS, ticketing)

---

## 5. PLM Integration — Capability Specification

The application must be **capable** of impact assessment by reading the client's PLM. The 6-month scope delivers the capability and a reference adapter, not a full production rollout into a specific client tenant.

Deliverables:
- PLM Adapter Interface (language-level contract: `list_parts`, `get_bom`, `get_substance_declarations`, `subscribe_changes`)
- Reference adapter: **Teamcenter** via Active Workspace REST API
- Authentication patterns documented (SSO, service account, OAuth)
- Data sync model: full-load + delta, with configurable cadence
- Mapping layer: PLM substance fields → application's normalised substance schema
- Sample/synthetic Teamcenter dataset for CI and demo
- Adapter SDK + documentation enabling addition of further PLMs

---

## 6. Target Users

- **Compliance Managers** — own regulatory posture across the portfolio
- **Sustainability Leads** — track substances of concern and mitigation
- **Materials & Design Engineers** — receive impact alerts on the parts they own
- **Programme / Product Managers** — see portfolio-level impact and prioritise mitigation
- **Executives** — KPI summary and trend reporting

---

## 7. Regulatory Rollout Order (6-month plan)

1. **UK REACH** (Phase 1, MVP-aligned)
2. **EU REACH** (Phase 3)
3. **US TSCA** + **APAC** (Phase 4)
4. **RoHS, PFAS, SCIP** (Phase 5)
5. **Batteries, Packaging & Waste, Aerospace/Defence** (Phase 6)

---

## 8. Constraints & Principles

- The plan extends the existing MVP (`mvp-32-mc-scanner-and-risk-identification`) in place rather than rebuilding.
- Every phase delivers a vertical slice (ingest → normalise → score → display → alert) for at least one regulatory module.
- LLM use is constrained to normalisation/classification with deterministic post-checks; scoring is rule-based and auditable.
- All impact assessments are evidence-linked back to the source regulatory event and the PLM record.
