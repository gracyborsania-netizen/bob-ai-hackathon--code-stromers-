# PharmaGuard AI — Source Module Reference

## Overview

This directory contains the complete Python source code for PharmaGuard AI.

## Files

### `app.py`
The main Streamlit dashboard application.

- **Home page** — project overview, feature cards, and limitations disclaimer
- **Safety Signal Detection** — CSV upload, PRR calculation, signal ranking, flagging, download
- **Submission Readiness Checker** — dossier text input, CTD checklist evaluation, gap report, download

Run with:
```bash
streamlit run app.py
```

---

### `safety_signal.py`
PRR (Proportional Reporting Ratio) calculation engine.

**Key classes:**
- `AdverseEventRecord` — represents one row of adverse event data (drug, event, count)
- `PRRResult` — holds PRR results for one drug–event pair (a, b, c, d, PRR, is_signal)

**Key function:**
- `compute_prr(records, prr_threshold=2.0, min_count=3)` — computes PRR for every unique drug–event pair, sorted by PRR descending

**PRR Formula:**
```
PRR = (a / (a+b)) / (c / (c+d))

Where:
  a = reports of Drug X WITH Event E
  b = reports of Drug X WITHOUT Event E
  c = reports of OTHER drugs WITH Event E
  d = reports of OTHER drugs WITHOUT Event E
```

A PRR ≥ 2.0 with ≥ 3 co-reports is flagged as a potential safety signal.

**Disclaimer:** PRR is a disproportionality screening statistic. It does NOT prove causality.

---

### `ctd_checker.py`
CTD-inspired submission readiness checker using text keyword matching.

**Checklist:** `CTD_CHECKLIST` — covers ICH CTD Modules 1–5 with configurable keywords.

**Key classes:**
- `RequirementStatus` — status of a single checklist requirement (found/not found, matched keywords)
- `ModuleScore` — aggregate score per module
- `DossierReport` — full report with completeness %, module scores, missing requirements list

**Key function:**
- `check_dossier(dossier_text, checklist=None)` — evaluates plain text against the checklist

The checklist uses case-insensitive keyword matching. To customise, modify `CTD_CHECKLIST` in `ctd_checker.py` or pass a custom checklist dict to `check_dossier()`.

**Disclaimer:** This is a prototype screening tool. It does NOT constitute legal or regulatory certification.

---

### `bob_adapter.py`
IBM Bob AI integration adapter.

**Configuration** (via `.env` file):
```
BOB_API_URL=    # IBM Bob / watsonx API endpoint
BOB_API_KEY=    # API key
BOB_MODEL=      # Model name (default: ibm/granite-13b-instruct-v2)
```

**Public functions:**
- `is_configured()` — returns True when credentials are present
- `explain_signal(drug, event, prr, a, b, c, d)` — returns AI explanation for a safety signal
- `summarize_gaps(module_scores, missing_requirements)` — returns AI gap summary

When Bob is not configured, both functions return useful fallback messages.
The application works fully without Bob credentials.

---

### `requirements.txt`
Python dependencies. Install with:
```bash
pip install -r requirements.txt
```

---

### `.env.example`
Template for environment variables. Copy to `.env` and fill in your credentials:
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

---

## `data/` Folder

### `data/sample_adverse_events.csv`
Synthetic adverse event data for demonstration purposes.

Format: `drug, event, count`

Contains realistic-looking but entirely fictional records for 10 synthetic drugs
across ~90 rows. Used for the Safety Signal Detection demo.

### `data/sample_dossier.txt`
Synthetic regulatory submission dossier for demonstration purposes.

Represents a fictional product "NovaCept-200" from "PharmaDemo Laboratories Inc."
Covers all CTD Modules 1–5 with appropriate terminology.
Used for the Submission Readiness Checker demo.

**None of this data represents real patients, products, or companies.**
