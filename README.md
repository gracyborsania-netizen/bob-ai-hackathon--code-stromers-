# 💊 PharmaGuard AI

> **AI-Assisted Drug Safety Signal Detection & Regulatory Submission Readiness**
> IBM BoB AI Innovation Hackathon 2026 — Problem P2

---

## 👥 Team

| Field | Details |
|---|---|
| **Team Name** | *code stromers* |
| **Member 1** | *Gracy* |
| **Member 2** | *Siya* |
| **Member 3** | *Vishva* |
| **Member 4** | *Prushti* |

---

## 🎯 Problem Statement

**P2 — Drug Safety Signal Detector & Regulatory Submission Readiness Checker**

The pharmaceutical industry faces two critical and time-consuming challenges:

1. **Drug Safety Signal Detection** — Spontaneous adverse event reporting systems generate enormous volumes of drug–event pairs. Pharmacovigilance teams must identify potential safety signals — combinations of drugs and adverse events that occur more frequently than expected by chance — from hundreds of thousands of reports. Manual review is slow, error-prone, and does not scale.

2. **Regulatory Submission Readiness** — Before a new drug application can be submitted to a regulatory authority, the dossier must meet complex standards (such as the ICH Common Technical Document format). Checking completeness manually across Modules 1–5 is labour-intensive, and gaps discovered late in the process cause costly delays.

Both problems benefit from AI-assisted automation, transparency, and explainability.

---

## 💡 Solution

**PharmaGuard AI** is an AI-assisted screening prototype that addresses both challenges in a single unified web dashboard:

- **Safety Signal Detection** — Upload adverse event data (CSV) and automatically compute the Proportional Reporting Ratio (PRR) for every drug–event pair. Signals above the configurable threshold (default PRR ≥ 2.0) are ranked and flagged. Full 2×2 contingency tables are shown for transparency.

- **Submission Readiness Checker** — Paste or upload a dossier text and evaluate it against a CTD-inspired checklist covering ICH CTD Modules 1–5. View module-wise scores, detected and missing requirements, and download a gap report.

- **IBM Bob AI Assistance** — When configured, IBM Bob provides plain-language explanations for safety signals and concise gap summaries for submission readiness results.

---

## ✨ Key Features

- ✅ PRR-based safety signal screening with configurable threshold
- ✅ Automatic signal ranking (highest PRR first)
- ✅ Potential signal flagging with full 2×2 contingency table display
- ✅ CTD-inspired readiness checking across Modules 1–5
- ✅ Module-wise completeness scores with visual bar chart
- ✅ Missing requirement detection with keyword matching
- ✅ Gap report generation and download (TXT + CSV)
- ✅ Optional IBM Bob-assisted plain-language signal explanations
- ✅ Optional IBM Bob-assisted submission gap summaries
- ✅ Synthetic demo data (sample CSV + sample dossier)
- ✅ Works fully offline without IBM Bob credentials
- ✅ Friendly validation messages and error handling
- ✅ Download buttons for all results

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python 3.9+ |
| **Frameworks** | Streamlit, Pandas, NumPy |
| **IBM Technologies** | IBM Bob / IBM Bob integration adapter (configurable) |
| **AI Integration** | REST-based adapter for IBM Bob / watsonx (BOB_API_URL, BOB_API_KEY, BOB_MODEL) |
| **Databases** | CSV-based storage — no database required |
| **Other** | Git, GitHub Actions, YAML, python-dotenv |

---

## ⚡ How to Run

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Navigate to the `src` directory

```bash
cd src
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and fill in your IBM Bob credentials (optional — the app works without them):

```
BOB_API_URL=https://your-bob-api-endpoint
BOB_API_KEY=your-api-key-here
BOB_MODEL=ibm/granite-13b-instruct-v2
```

### 5. Run the application

```bash
streamlit run app.py
```

The application will open at **http://localhost:8501**

---

## 🎬 Demo

| Resource | Location |
|---|---|
| Demo Video | See [`demo/demo-video-link.txt`](demo/demo-video-link.txt) |
| Live Demo URL | See [`demo/live-demo-url.txt`](demo/live-demo-url.txt) |
| Screenshots | See [`demo/screenshots/`](demo/screenshots/) |

---

## 🧪 Running Tests

From the repository root:

```bash
pytest tests/ -v
```

Tests cover:
- PRR calculation correctness
- CSV validation
- CTD checklist scoring
- Missing requirement detection
- Edge cases (zero division, empty input, custom thresholds)

---

## ⚠️ Known Limitations

- All data used is **synthetic** and does not represent real patients, products, or companies
- PRR is a **disproportionality screening statistic** — it does **NOT** prove causality
- The CTD checklist uses **keyword matching** — it is a configurable prototype, not a legal standard
- IBM Bob AI assistance depends on valid configuration in the `.env` file
- This prototype does **not** make clinical, causal, or regulatory decisions
- Always consult qualified pharmacovigilance and regulatory professionals for real decisions

---

## 🏆 What We're Most Proud Of

PharmaGuard AI combines two distinct but complementary pharmaceutical challenges — **quantitative drug safety screening** and **structured regulatory readiness assessment** — into a single, transparent, and explainable AI-assisted dashboard.

The PRR calculation is fully transparent: every 2×2 contingency table value (a, b, c, d) is shown alongside the computed ratio, making the screening logic auditable rather than a black box. The CTD checklist uses keyword matching that is easy to configure and extend for different jurisdictions.

By integrating IBM Bob AI explanations as an optional layer on top of quantitative results, PharmaGuard AI demonstrates how large language models can add value in regulated domains — not by replacing expert judgment, but by making outputs more accessible and actionable for pharmacovigilance and regulatory affairs teams.

---

## 📁 Project Structure

```
PharmaGuard-AI/
├── src/
│   ├── app.py                    # Main Streamlit dashboard
│   ├── safety_signal.py          # PRR calculation engine
│   ├── ctd_checker.py            # CTD-inspired readiness checker
│   ├── bob_adapter.py            # IBM Bob integration adapter
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Environment variable template
│   ├── README.md                 # Source code documentation
│   └── data/
│       ├── sample_adverse_events.csv   # Synthetic AE data
│       └── sample_dossier.txt          # Synthetic CTD dossier
├── tests/
│   ├── test_safety_signal.py     # PRR calculation tests
│   └── test_ctd_checker.py       # CTD checker tests
├── docs/
│   ├── problem-statement.md      # Problem P2 analysis
│   ├── solution-overview.md      # Solution description
│   ├── architecture.md           # Technical architecture
│   └── setup-guide.md            # Installation & demo guide
├── demo/
│   ├── README.md                 # Demo instructions
│   ├── demo-video-link.txt       # Video link (to be filled)
│   ├── live-demo-url.txt         # Live URL (to be filled)
│   └── screenshots/              # Application screenshots
├── presentation/
│   └── slides.pptx               # Hackathon presentation
├── README.md                     # This file
├── CONTRIBUTING.md               # Contribution guidelines
├── .gitignore                    # Git ignore rules
└── submission.yaml               # Official submission metadata
```

---

## 📄 License

This project was created for the IBM BoB AI Innovation Hackathon 2026.
