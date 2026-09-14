# PharmaGuard AI — Demo Guide

## 3–5 Minute Demo Script

This guide explains how to demonstrate PharmaGuard AI in a hackathon setting.
The demo requires the application to be running locally at http://localhost:8501.

## Setup

1. Make sure the application is running: `cd src && streamlit run app.py`
2. Have a browser open at http://localhost:8501
3. No internet connection required for core features

## Demo Flow

### 0:00 – 0:30 | Introduction (30 seconds)
- "PharmaGuard AI is an AI-assisted screening prototype addressing two challenges in pharmaceutical development"
- Show the Home page — point to the two feature cards
- "First: safety signal detection. Second: regulatory submission readiness checking"

### 0:30 – 1:30 | Safety Signal Detection — Load & Calculate (60 seconds)
- Navigate to 🔬 Safety Signal Detection
- Select "Use sample data" — show it loads immediately
- Briefly show the raw data (drug, event, count format)
- Set threshold to PRR ≥ 2.0 (default)
- Click "Calculate PRR & Detect Signals"
- Show the 4 metric cards: total pairs, signals, rate, threshold

### 1:30 – 2:00 | PRR Results (30 seconds)
- Scroll through the ranked results table
- "Highlighted rows are potential signals — highest PRR first"
- Point to the columns: drug, adverse event, a/b/c/d values, PRR, signal flag

### 2:00 – 2:30 | Signal Detail & IBM Bob (30 seconds)
- Open the top flagged signal expander
- Show the 2×2 contingency table and PRR calculation formula
- Click "Explain Signal #1 with IBM Bob"
- Show the explanation (AI or fallback)

### 2:30 – 3:30 | Submission Readiness (60 seconds)
- Navigate to 📋 Submission Readiness Checker
- Select "Use sample dossier"
- Click "Check Submission Readiness"
- Show overall score, module-wise metrics, and bar chart
- Scroll to the requirements table — show green (found) vs red (not detected)

### 3:30 – 4:00 | Gap Report (30 seconds)
- Show the missing requirements section
- Click "Download Gap Report"
- "Regulatory teams can use this to prioritise what to fix before submission"

### 4:00 – 4:30 | IBM Bob Summary (30 seconds)
- Click "Generate IBM Bob Gap Summary"
- Show the gap summary response

### 4:30 – 5:00 | Wrap-up (30 seconds)
- "PharmaGuard AI combines quantitative signal screening and structured readiness checking in one transparent, explainable dashboard"
- "All core features work without any external services — IBM Bob adds AI explainability on top"

## Screenshots

Replace the placeholder files in screenshots/ with actual application screenshots before submission:

- `screenshot-1.png` — Home page showing feature cards
- `screenshot-2.png` — Safety Signal Detection results with flagged signals
- `screenshot-3.png` — Submission Readiness module scores and requirements table

## Notes

- If IBM Bob is not configured, the AI features will show useful fallback messages — this is expected and acceptable in demo mode
- The sample data is entirely synthetic — clearly state this during the demo
- All disclaimers are built into the UI — point to them during the demo to show responsible AI design
