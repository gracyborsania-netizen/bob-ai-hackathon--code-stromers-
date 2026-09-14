# Setup Guide

A beginner-friendly guide to installing and running PharmaGuard AI locally.

---

## Prerequisites

Before you begin, make sure you have the following installed:

| Tool | Version | Install |
|---|---|---|
| **Python** | 3.9 or later | https://python.org/downloads |
| **Git** | Any recent version | https://git-scm.com |
| **GitHub account** | — | https://github.com |
| **pip** | Included with Python | — |

Verify your Python installation:
```bash
python --version
# Expected: Python 3.9.x or later

pip --version
# Expected: pip 21.x or later
```

---

## Installation

### Step 1 — Clone the Repository

```bash
git clone <repository-url>
cd <repository-name>
```

Replace `<repository-url>` with the actual GitHub URL of the repository.

### Step 2 — Navigate to the Source Directory

```bash
cd src
```

### Step 3 — (Recommended) Create a Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `streamlit` — web dashboard framework
- `pandas` — data processing
- `numpy` — numerical computing
- `python-dotenv` — environment variable loading
- `pytest` — test runner

---

## Environment Variables

### Step 5 — Create Your `.env` File

```bash
# Windows Command Prompt
copy .env.example .env

# Windows PowerShell
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

### Step 6 — Configure IBM Bob (Optional)

Open `.env` in a text editor and fill in your IBM Bob credentials:

```
BOB_API_URL=https://your-ibm-bob-api-endpoint
BOB_API_KEY=your-actual-api-key
BOB_MODEL=ibm/granite-13b-instruct-v2
```

**If you do not have IBM Bob credentials**, leave all three values empty. The application will run in fallback mode — all core features work, and AI explanations will show automated fallback messages.

**Important:** Never commit your `.env` file to GitHub. It is already listed in `.gitignore`.

---

## Run Application

### Step 7 — Start PharmaGuard AI

```bash
streamlit run app.py
```

The terminal will display:

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Open your browser and navigate to **http://localhost:8501**

---

## Verification

When the application starts correctly, you should see:

1. **Sidebar** — "PharmaGuard AI" title, navigation radio buttons, IBM Bob status indicator
2. **Home page** — Two feature cards (Safety Signal Detection, Submission Readiness Checker), How It Works section, Limitations disclaimer
3. **IBM Bob Status** — Either "✅ Bob AI Connected" (if credentials configured) or "⚠️ Bob AI not configured" (fallback mode)

---

## Running Tests

From the **repository root** (not the `src/` directory):

```bash
pytest tests/ -v
```

Expected output: all tests pass with `PASSED` status.

```
tests/test_safety_signal.py::test_empty_records_raises PASSED
tests/test_safety_signal.py::test_no_signals_when_prr_below_threshold PASSED
...
tests/test_ctd_checker.py::test_full_ich_checklist_with_sample_dossier PASSED
```

---

## Demo Walkthrough

Follow this 3–5 minute demo script to showcase all features:

### 0:00 – 0:30 | Introduction
- Open browser at http://localhost:8501
- Show the Home page
- Explain the two features (Safety Signal Detection, Submission Readiness)
- Point out the IBM Bob status in the sidebar

### 0:30 – 1:30 | Safety Signal Detection — Load Data
1. Click **🔬 Safety Signal Detection** in the sidebar
2. Select **"📋 Use sample data"**
3. The sample CSV loads automatically — a green success message appears
4. Click the "📊 View raw data" expander to show the data (10 drugs, ~15 events, count column)

### 1:30 – 2:00 | Calculate PRR
1. Leave threshold at default (PRR ≥ 2.0, min 3 co-reports)
2. Click **"▶️ Calculate PRR & Detect Signals"**
3. Show the metrics: total pairs, signals detected, signal rate
4. Show the ranked results table (highest PRR first, ⚠️ YES for signals)

### 2:00 – 2:30 | Signal Detail & PRR Explanation
1. Scroll to **"6. Flagged Potential Signals (Detail)"**
2. The top signal is already expanded — show the 2×2 contingency table and the PRR calculation formula
3. Click **"Explain Signal #1 with IBM Bob"** (shows AI explanation or fallback message)

### 2:30 – 3:00 | Download
1. Scroll to **"7. Download Results"**
2. Click **"⬇️ Download Results CSV"** — file downloads

### 3:00 – 4:00 | Submission Readiness — Load Dossier
1. Click **📋 Submission Readiness Checker** in the sidebar
2. Select **"📋 Use sample dossier"**
3. Sample dossier loads — show success message
4. Click the "📄 Preview dossier text" expander to show the text

### 4:00 – 4:30 | Check Readiness
1. Click **"▶️ Check Submission Readiness"**
2. Show overall completeness score (should be ≥ 90%)
3. Show module-wise scores metrics and bar chart
4. Show the detailed requirements table (green = found, red = not detected)

### 4:30 – 5:00 | Gap Report & IBM Bob Summary
1. Show missing requirements section
2. Click **"🤖 Generate IBM Bob Gap Summary"** (shows AI summary or fallback)
3. Click **"⬇️ Download Gap Report (TXT)"**
4. Summarise: "PharmaGuard AI helps pharmacovigilance and regulatory teams screen faster and more consistently"

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'streamlit'`

You have not installed the dependencies, or your virtual environment is not activated.

```bash
# Make sure you are in the src/ directory
pip install -r requirements.txt
```

### `streamlit: command not found`

Python's Scripts directory is not on your PATH. Try:

```bash
python -m streamlit run app.py
```

### Sample data not found

Make sure you run `streamlit run app.py` from the `src/` directory, not the repository root.

### IBM Bob shows "not configured"

This is normal. Create `.env` from `.env.example` and fill in your credentials. The app works without credentials.

### Port 8501 already in use

Stop any other Streamlit instances, or use:

```bash
streamlit run app.py --server.port 8502
```

### Tests fail with import errors

Make sure you run `pytest` from the repository root directory, not from `src/`:

```bash
cd ..          # go to repository root
pytest tests/ -v
```

### `FileNotFoundError` for sample data in tests

The test `test_full_ich_checklist_with_sample_dossier` automatically skips if the sample file is not found. If you want to run it, ensure `src/data/sample_dossier.txt` exists.
