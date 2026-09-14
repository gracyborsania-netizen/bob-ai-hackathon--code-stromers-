# Solution Overview

## What We Built

**PharmaGuard AI** is an AI-assisted screening prototype web application that addresses Problem P2 of the IBM BoB AI Innovation Hackathon 2026. It provides two core capabilities in a single Streamlit dashboard:

1. **Drug Safety Signal Detection** — computes the Proportional Reporting Ratio (PRR) for every drug–event pair in uploaded adverse event data, ranks potential signals, and optionally explains them using IBM Bob AI.

2. **Regulatory Submission Readiness Checker** — evaluates a dossier text against a CTD-inspired checklist covering ICH CTD Modules 1–5, produces module-wise completeness scores, and generates a downloadable gap report.

---

## How It Works

PharmaGuard AI is a pure Python + Streamlit application. It requires no database, no cloud infrastructure, and works fully offline. IBM Bob AI assistance is an optional enhancement layer.

### Safety Signal Detection Workflow

```
User uploads CSV
      ↓
Data validation (columns, types, empty rows)
      ↓
Aggregate reports by (drug, event) pair
      ↓
Build 2×2 contingency table for each pair
  a = drug + event reports
  b = drug + other event reports
  c = other drugs + event reports
  d = other drugs + other event reports
      ↓
Calculate PRR = (a/(a+b)) / (c/(c+d))
      ↓
Flag signals: PRR ≥ threshold AND a ≥ min_count
      ↓
Sort results highest PRR first
      ↓
Display ranked table + detailed contingency tables
      ↓
Optional: IBM Bob explains top signal in plain language
      ↓
User downloads results CSV
```

### Submission Readiness Workflow

```
User uploads or pastes dossier text
      ↓
Text validation (non-empty, minimum length)
      ↓
Keyword matching against CTD_CHECKLIST (Modules 1–5)
  Each requirement: check if any keyword found in text (case-insensitive)
      ↓
Aggregate scores per module (found / total)
      ↓
Calculate overall completeness percentage
      ↓
Generate full requirements table (found / not detected)
      ↓
List missing requirements by module
      ↓
Optional: IBM Bob generates concise gap summary
      ↓
User downloads gap report (TXT) and requirements (CSV)
```

---

## IBM Bob Assistance

IBM Bob is integrated as an optional AI layer via the `bob_adapter.py` module.

**When configured** (BOB_API_URL + BOB_API_KEY set in `.env`):
- `explain_signal()` — sends PRR signal details to IBM Bob and returns a plain-language clinical explanation
- `summarize_gaps()` — sends module scores and missing requirements to IBM Bob and returns actionable gap recommendations

**When not configured**:
- Both functions return well-structured fallback messages that are still useful
- The application continues to work fully — no errors or crashes

This design ensures PharmaGuard AI is a complete, functional application regardless of IBM Bob availability.

---

## Architecture Diagram

```
User (Browser)
      │
      ▼
Streamlit Dashboard (app.py)
      │
      ├──────────────────────────────┐
      │                              │
      ▼                              ▼
Safety Signal Engine         CTD Readiness Checker
(safety_signal.py)           (ctd_checker.py)
      │                              │
      │  PRR Calculation             │  Keyword Matching
      │  Contingency Table           │  Module Scoring
      │  Signal Ranking              │  Gap Detection
      │                              │
      └──────────────┬───────────────┘
                     │
                     ▼
              IBM Bob Adapter
              (bob_adapter.py)
                     │
                     ├── Configured? → POST to IBM Bob API
                     │                 ↓ AI Response
                     └── Not configured? → Fallback message
                     │
                     ▼
              Results & Reports
              (Displayed in UI + Download)
```

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| CSV-based input for safety data | No database required; easy to use with real FAERS exports |
| Text-based input for dossier | Flexible — works with .txt exports from Word, PDF text, etc. |
| Keyword matching for CTD check | Transparent, explainable, easy to configure for different jurisdictions |
| Configurable threshold via slider | Pharmacovigilance teams use different thresholds; flexibility is important |
| Fallback messages when Bob unavailable | Application must work in demo without live API credentials |
| Environment variables for credentials | Standard security practice; no secrets in source code |
| Pure Python + Streamlit | Minimal dependencies; easy to run locally and deploy to Streamlit Cloud |
| Module-level PRR aggregation | Matches standard FAERS analysis approach |

---

## IBM Technologies Used

| Technology | Purpose |
|---|---|
| IBM Bob AI (via `bob_adapter.py`) | Optional plain-language signal explanations and gap summaries |
| IBM Granite (default model) | Text generation for clinical and regulatory explanations |

The IBM Bob integration uses a standard REST API adapter that reads configuration from environment variables (`BOB_API_URL`, `BOB_API_KEY`, `BOB_MODEL`). The adapter supports both watsonx-style (`results[].generated_text`) and OpenAI-compatible (`choices[].text`) response formats.

---

## Limitations

- **PRR is a screening statistic** — it does not prove causality and requires clinical follow-up
- **Keyword matching is imperfect** — dossiers using non-standard terminology may have lower scores
- **Synthetic data only** — all demo data is fictional and does not represent real patients or products
- **Prototype, not production** — this application is a demonstration tool, not a validated regulatory system
- **IBM Bob availability** — AI features require valid credentials; all core features work without them
