"""
app.py
------
PharmaGuard AI — Streamlit Dashboard
AI-Assisted Drug Safety Signal Detection & Regulatory Submission Readiness

IBM BoB AI Innovation Hackathon 2026
Problem: P2 – Drug Safety Signal Detector & Regulatory Submission Readiness Checker

DISCLAIMER:
This is a prototype screening tool using synthetic/demo data.
It does NOT make clinical, causal, or regulatory decisions.
"""

import io
import os
import sys

import pandas as pd
import streamlit as st

# Ensure src/ is on path when running directly
sys.path.insert(0, os.path.dirname(__file__))

from safety_signal import AdverseEventRecord, compute_prr
from ctd_checker import check_dossier
from bob_adapter import explain_signal, summarize_gaps, is_configured

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="PharmaGuard AI",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg",
    width=80,
)
st.sidebar.title("PharmaGuard AI")
st.sidebar.caption("IBM BoB AI Hackathon 2026")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "🔬 Safety Signal Detection", "📋 Submission Readiness Checker"],
    index=0,
)

st.sidebar.divider()
st.sidebar.markdown("**IBM Bob Status**")
if is_configured():
    st.sidebar.success("✅ Bob AI Connected")
else:
    st.sidebar.warning("⚠️ Bob AI not configured\n\nSet BOB_API_URL and BOB_API_KEY in .env")

st.sidebar.divider()
st.sidebar.markdown(
    "⚠️ **Disclaimer:** This prototype uses synthetic demo data and does "
    "not make clinical, causal, or regulatory decisions.",
    help="For research and demonstration purposes only.",
)

# ============================================================================
# HOME PAGE
# ============================================================================
if page == "🏠 Home":
    st.title("💊 PharmaGuard AI")
    st.subheader("AI-Assisted Drug Safety Signal Detection & Regulatory Submission Readiness")
    st.markdown("---")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            """
            <div style='background:#f0f4ff;padding:24px;border-radius:12px;border:1px solid #c5d3f0'>
            <h3>🔬 Safety Signal Detection</h3>
            <p>Upload adverse event data and automatically calculate the
            <strong>Proportional Reporting Ratio (PRR)</strong> for every drug–event pair.</p>
            <ul>
            <li>2×2 contingency table calculation</li>
            <li>Automatic PRR computation</li>
            <li>Signal ranking (highest PRR first)</li>
            <li>Potential signal flagging (PRR ≥ 2.0)</li>
            <li>Downloadable results CSV</li>
            <li>Optional IBM Bob AI explanation</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div style='background:#f0fff4;padding:24px;border-radius:12px;border:1px solid #b0d8c0'>
            <h3>📋 Submission Readiness Checker</h3>
            <p>Paste or upload your dossier text and evaluate it against a
            <strong>CTD-inspired checklist</strong> covering Modules 1–5.</p>
            <ul>
            <li>Module-wise completeness scores</li>
            <li>Overall submission readiness score</li>
            <li>Missing requirement detection</li>
            <li>Gap report generation</li>
            <li>Downloadable gap report</li>
            <li>Optional IBM Bob AI gap summary</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    st.subheader("📖 How It Works")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("**Step 1 — Upload Data**")
        st.markdown(
            "Upload a CSV file with `drug`, `event`, `count` columns "
            "or use the provided synthetic sample data."
        )
    with col_b:
        st.markdown("**Step 2 — Analyse**")
        st.markdown(
            "The engine calculates PRR for every drug–event pair and "
            "flags potential signals above your chosen threshold."
        )
    with col_c:
        st.markdown("**Step 3 — Review & Export**")
        st.markdown(
            "Review ranked signals and module scores, then download "
            "results. Optionally request an IBM Bob AI explanation."
        )

    st.markdown("---")

    st.subheader("⚠️ Important Limitations")
    st.warning(
        "**This is a prototype AI-assisted screening tool for demonstration purposes.**\n\n"
        "- All data used is **synthetic** and does not represent real patients or products.\n"
        "- PRR is a **disproportionality screening statistic** — it does **not** prove causality.\n"
        "- The CTD checklist is **configurable and simplified** — not a legal regulatory standard.\n"
        "- IBM Bob assistance depends on valid configuration in the `.env` file.\n"
        "- This system does **not** make clinical, causal, or regulatory decisions.\n"
        "- Always consult qualified pharmacovigilance and regulatory professionals."
    )


# ============================================================================
# SAFETY SIGNAL DETECTION PAGE
# ============================================================================
elif page == "🔬 Safety Signal Detection":
    st.title("🔬 Safety Signal Detection")
    st.markdown(
        "Upload adverse event reporting data to compute the **Proportional Reporting Ratio (PRR)** "
        "for every drug–event pair and identify potential safety signals."
    )

    # ---- Input section -----
    st.subheader("1. Load Data")
    input_method = st.radio(
        "Data source",
        ["📂 Upload CSV file", "📋 Use sample data"],
        horizontal=True,
    )

    df_raw = None

    if input_method == "📂 Upload CSV file":
        uploaded_csv = st.file_uploader(
            "Upload CSV (required columns: drug, event, count)",
            type=["csv"],
            key="csv_upload",
        )
        if uploaded_csv is not None:
            try:
                df_raw = pd.read_csv(uploaded_csv)
            except Exception as e:
                st.error(
                    f"**Could not parse CSV:** {e}\n\n"
                    "Ensure the file is a valid UTF-8 CSV with columns: drug, event, count."
                )
    else:
        sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_adverse_events.csv")
        try:
            df_raw = pd.read_csv(sample_path)
            st.success("✅ Sample data loaded: `data/sample_adverse_events.csv`")
            st.info(
                "This is synthetic demonstration data with realistic-looking but entirely "
                "fictional drug–adverse event records."
            )
        except FileNotFoundError:
            st.error(
                "Sample file not found at `src/data/sample_adverse_events.csv`. "
                "Please upload a CSV instead."
            )

    # ---- Validate data ----
    if df_raw is not None:
        # Show raw data
        with st.expander("📊 View raw data", expanded=False):
            st.dataframe(df_raw, use_container_width=True)
            st.caption(f"Rows: {len(df_raw)} | Columns: {list(df_raw.columns)}")

        # Validate columns
        df_raw.columns = df_raw.columns.str.lower().str.strip()
        required_cols = {"drug", "event"}
        missing_cols = required_cols - set(df_raw.columns)
        if missing_cols:
            st.error(
                f"**Missing required column(s): `{'`, `'.join(sorted(missing_cols))}`**\n\n"
                "Your CSV must have at least a `drug` column and an `event` column. "
                "Column names are case-insensitive."
            )
            st.stop()

        if "count" not in df_raw.columns:
            df_raw["count"] = 1
            st.info("ℹ️ No `count` column found — each row treated as 1 report.")

        # Validate count values
        try:
            df_raw["count"] = pd.to_numeric(df_raw["count"], errors="coerce")
        except Exception:
            pass

        invalid_counts = df_raw["count"].isna().sum()
        if invalid_counts > 0:
            st.warning(
                f"⚠️ {invalid_counts} row(s) have non-numeric `count` values — "
                "these rows will be skipped."
            )
            df_raw = df_raw.dropna(subset=["count"])

        df_raw["count"] = df_raw["count"].astype(int)
        df_raw = df_raw[df_raw["count"] > 0]  # skip zero-count rows
        df_raw = df_raw.dropna(subset=["drug", "event"])

        if df_raw.empty:
            st.warning("⚠️ No usable data rows after validation. Please check your CSV.")
            st.stop()

        # ---- Threshold configuration ----
        st.subheader("2. Configure Signal Threshold")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            prr_threshold = st.slider(
                "PRR Threshold",
                min_value=1.0,
                max_value=10.0,
                value=2.0,
                step=0.5,
                help="Drug–event pairs with PRR ≥ this value AND ≥ min_count reports are flagged.",
            )
        with col_t2:
            min_count = st.number_input(
                "Minimum co-reports (cell a)",
                min_value=1,
                max_value=20,
                value=3,
                help="Minimum number of co-reports required to flag a signal.",
            )

        # ---- Calculate PRR ----
        st.subheader("3. Calculate Safety Signals")
        if st.button("▶️ Calculate PRR & Detect Signals", type="primary"):
            records = [
                AdverseEventRecord(
                    drug=str(row["drug"]),
                    event=str(row["event"]),
                    count=int(row["count"]),
                )
                for _, row in df_raw.iterrows()
            ]

            try:
                results = compute_prr(records, prr_threshold=prr_threshold, min_count=int(min_count))
            except ValueError as e:
                st.error(f"**Computation error:** {e}")
                st.stop()

            signals = [r for r in results if r.is_signal]

            # ---- Summary metrics ----
            st.subheader("4. Results Summary")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Drug–Event Pairs", len(results))
            m2.metric("Potential Signals", len(signals))
            m3.metric(
                "Signal Rate",
                f"{100*len(signals)/len(results):.1f}%" if results else "—",
            )
            m4.metric("PRR Threshold", f"≥ {prr_threshold}")

            st.divider()

            if not signals:
                st.success(
                    f"✅ No potential safety signals detected at PRR ≥ {prr_threshold} "
                    f"with ≥ {int(min_count)} co-reports."
                )
            else:
                st.warning(
                    f"⚠️ **{len(signals)} potential safety signal(s) detected** "
                    f"(PRR ≥ {prr_threshold}, ≥ {int(min_count)} co-reports)"
                )

            # ---- Full results table ----
            st.subheader("5. Ranked Results Table")
            st.caption(
                "All drug–event pairs ranked highest PRR first. "
                "Shows full 2×2 contingency table values."
            )

            import math
            result_rows = []
            for r in results:
                prr_display = f"{r.prr:.4f}" if not math.isinf(r.prr) else "∞"
                result_rows.append(
                    {
                        "Drug": r.drug,
                        "Adverse Event": r.event,
                        "a (drug+event)": r.a,
                        "b (drug+other)": r.b,
                        "c (other+event)": r.c,
                        "d (other+other)": r.d,
                        "PRR": prr_display,
                        "Potential Signal": "⚠️ YES" if r.is_signal else "No",
                    }
                )

            result_df = pd.DataFrame(result_rows)

            # Highlight signal rows
            def highlight_signals(row):
                if row["Potential Signal"] == "⚠️ YES":
                    return ["background-color: #fff3cd"] * len(row)
                return [""] * len(row)

            st.dataframe(
                result_df.style.apply(highlight_signals, axis=1),
                use_container_width=True,
                height=400,
            )

            # ---- Flagged signals detail ----
            if signals:
                st.subheader("6. Flagged Potential Signals (Detail)")
                for i, r in enumerate(signals, 1):
                    prr_str = f"{r.prr:.4f}" if not math.isinf(r.prr) else "∞"
                    with st.expander(
                        f"#{i} · {r.drug} + {r.event} · PRR = {prr_str}", expanded=(i == 1)
                    ):
                        sig_c1, sig_c2 = st.columns(2)
                        with sig_c1:
                            st.markdown("**2×2 Contingency Table**")
                            table_df = pd.DataFrame(
                                {
                                    "": ["Drug: " + r.drug, "Other Drugs"],
                                    r.event: [r.a, r.c],
                                    "Other Events": [r.b, r.d],
                                }
                            ).set_index("")
                            st.dataframe(table_df, use_container_width=True)

                        with sig_c2:
                            st.markdown("**PRR Calculation**")
                            st.code(
                                f"a = {r.a}   (drug + event)\n"
                                f"b = {r.b}   (drug + other events)\n"
                                f"c = {r.c}   (other drugs + event)\n"
                                f"d = {r.d}   (other drugs + other events)\n\n"
                                f"PRR = (a/(a+b)) / (c/(c+d))\n"
                                f"    = ({r.a}/{r.a+r.b}) / ({r.c}/{r.c+r.d})\n"
                                f"    = {prr_str}"
                            )

                        st.markdown("---")
                        st.markdown("**🤖 IBM Bob AI Explanation**")
                        st.caption(
                            "Optional: request an AI-generated plain-language explanation "
                            "of this potential signal."
                        )
                        if st.button(
                            f"Explain Signal #{i} with IBM Bob",
                            key=f"explain_{i}",
                        ):
                            with st.spinner("Requesting IBM Bob AI explanation…"):
                                explanation = explain_signal(
                                    drug=r.drug,
                                    event=r.event,
                                    prr=r.prr,
                                    a=r.a,
                                    b=r.b,
                                    c=r.c,
                                    d=r.d,
                                )
                            st.info(explanation)

                        st.caption(
                            "⚠️ PRR is a disproportionality screening statistic. "
                            "It does NOT prove causality. All signals require "
                            "further clinical and epidemiological investigation."
                        )

            # ---- Download ----
            st.subheader("7. Download Results")
            csv_buffer = io.StringIO()
            result_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="⬇️ Download Results CSV",
                data=csv_buffer.getvalue(),
                file_name="pharmaguard_prr_results.csv",
                mime="text/csv",
            )

            st.caption(
                "⚠️ **Disclaimer:** These results are from a prototype AI-assisted "
                "screening tool using synthetic demonstration data. PRR is a screening "
                "statistic only and does NOT prove causality. Not for clinical use."
            )


# ============================================================================
# SUBMISSION READINESS CHECKER PAGE
# ============================================================================
elif page == "📋 Submission Readiness Checker":
    st.title("📋 Regulatory Submission Readiness Checker")
    st.markdown(
        "Evaluate a dossier against a **CTD-inspired checklist** covering "
        "**Modules 1–5**. Paste text or upload a file, then view completeness "
        "scores, missing requirements, and a downloadable gap report."
    )

    # ---- Input section ----
    st.subheader("1. Load Dossier")
    input_method2 = st.radio(
        "Dossier source",
        ["📂 Upload text file", "✏️ Paste dossier text", "📋 Use sample dossier"],
        horizontal=True,
    )

    dossier_text = ""

    if input_method2 == "📂 Upload text file":
        uploaded_txt = st.file_uploader(
            "Upload dossier (.txt or .md)",
            type=["txt", "md"],
            key="txt_upload",
        )
        if uploaded_txt is not None:
            try:
                dossier_text = uploaded_txt.read().decode("utf-8")
                st.success(f"✅ File loaded: {uploaded_txt.name} ({len(dossier_text):,} characters)")
            except Exception as e:
                st.error(f"**Could not read file:** {e}")

    elif input_method2 == "✏️ Paste dossier text":
        dossier_text = st.text_area(
            "Paste your dossier text here",
            height=300,
            placeholder=(
                "Paste the text content of your regulatory dossier here.\n\n"
                "The checker will scan for keywords related to each CTD module requirement.\n\n"
                "Example: Include text about 'Cover Letter', 'Quality Overall Summary', "
                "'Drug Substance', 'Clinical Overview', etc."
            ),
        )

    else:  # sample dossier
        sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_dossier.txt")
        try:
            with open(sample_path, "r", encoding="utf-8") as f:
                dossier_text = f.read()
            st.success("✅ Sample dossier loaded: `data/sample_dossier.txt`")
            st.info(
                "This is a synthetic demonstration dossier for NovaCept-200 "
                "(a fictional compound). It does not represent a real product."
            )
        except FileNotFoundError:
            st.error(
                "Sample dossier not found at `src/data/sample_dossier.txt`. "
                "Please upload a file or paste text instead."
            )

    if dossier_text:
        with st.expander("📄 Preview dossier text", expanded=False):
            st.text_area(
                "Dossier content (preview)",
                value=dossier_text[:3000] + ("…[truncated for preview]" if len(dossier_text) > 3000 else ""),
                height=200,
                disabled=True,
            )
            st.caption(f"Total characters: {len(dossier_text):,}")

    # ---- Check readiness ----
    st.subheader("2. Check Submission Readiness")
    if st.button("▶️ Check Submission Readiness", type="primary"):
        if not dossier_text.strip():
            st.error(
                "**No dossier content provided.** "
                "Please upload a file, paste text, or use the sample dossier."
            )
            st.stop()

        if len(dossier_text.strip()) < 50:
            st.warning(
                "⚠️ The dossier text is very short. For meaningful results, "
                "provide a more complete dossier."
            )

        try:
            report = check_dossier(dossier_text)
        except (TypeError, ValueError) as e:
            st.error(f"**Validation error:** {e}")
            st.stop()

        # ---- Overall metrics ----
        st.subheader("3. Overall Completeness")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Requirements", report.total_requirements)
        m2.metric("Requirements Found", report.found_count)
        m3.metric("Requirements Missing", report.missing_count)
        m4.metric("Completeness Score", f"{report.completeness_pct}%")

        if report.is_submission_ready:
            st.success(
                "✅ All checklist items detected in the dossier. "
                "Review carefully with a qualified regulatory professional before submission."
            )
        else:
            st.warning(
                f"⚠️ **{report.missing_count} requirement(s) not detected.** "
                "Address gaps before submission."
            )

        # ---- Module-wise scores ----
        st.subheader("4. Module-Wise Scores")
        module_scores = report.module_scores
        mod_cols = st.columns(len(module_scores))

        for i, ms in enumerate(module_scores):
            pct = ms.score_pct
            colour = "🟢" if pct == 100 else ("🟡" if pct >= 60 else "🔴")
            mod_cols[i].metric(
                label=f"{colour} {ms.module_id}",
                value=f"{pct}%",
                delta=f"{ms.found}/{ms.total} found",
                delta_color="normal",
                help=ms.module_name,
            )

        # Bar chart of module scores
        module_chart_data = pd.DataFrame(
            {
                "Module": [ms.module_id for ms in module_scores],
                "Score (%)": [ms.score_pct for ms in module_scores],
                "Module Name": [ms.module_name for ms in module_scores],
            }
        )
        st.bar_chart(module_chart_data.set_index("Module")["Score (%)"], use_container_width=True)

        # ---- Detailed requirements table ----
        st.subheader("5. Detailed Requirements")
        req_rows = []
        for req in report.requirements:
            req_rows.append(
                {
                    "Module": req.module_id,
                    "Requirement": req.requirement,
                    "Status": "✅ Found" if req.found else "❌ Not Detected",
                    "Matched Keywords": ", ".join(req.matched_keywords[:3]) if req.matched_keywords else "—",
                }
            )
        req_df = pd.DataFrame(req_rows)

        def highlight_missing(row):
            if "Not Detected" in row["Status"]:
                return ["background-color: #ffeaea"] * len(row)
            return ["background-color: #f0fff4"] * len(row)

        st.dataframe(
            req_df.style.apply(highlight_missing, axis=1),
            use_container_width=True,
            height=450,
        )

        # ---- Missing requirements detail ----
        if report.missing_requirements:
            st.subheader("6. Missing / Not-Detected Requirements")
            st.caption(
                "These items were not detected via keyword matching. "
                "They may be present in your dossier under different terminology."
            )
            for req in report.missing_requirements:
                st.markdown(f"- **[{req.module_id}]** {req.requirement}")

        # ---- IBM Bob gap summary ----
        st.subheader("7. IBM Bob AI Gap Summary")
        st.caption("Optional: request an AI-generated gap summary and recommendations.")
        if st.button("🤖 Generate IBM Bob Gap Summary"):
            ms_dicts = [
                {
                    "module_id": ms.module_id,
                    "module_name": ms.module_name,
                    "found": ms.found,
                    "total": ms.total,
                    "score_pct": ms.score_pct,
                }
                for ms in module_scores
            ]
            mr_dicts = [
                {"module_id": r.module_id, "requirement": r.requirement}
                for r in report.missing_requirements
            ]
            with st.spinner("Requesting IBM Bob AI gap summary…"):
                gap_summary = summarize_gaps(ms_dicts, mr_dicts)
            st.info(gap_summary)

        # ---- Gap report for download ----
        st.subheader("8. Download Gap Report")

        gap_lines = [
            "PharmaGuard AI — Submission Readiness Gap Report",
            "=" * 60,
            f"Overall Completeness: {report.completeness_pct}% "
            f"({report.found_count}/{report.total_requirements} requirements detected)",
            "",
            "MODULE SCORES",
            "-" * 40,
        ]
        for ms in module_scores:
            gap_lines.append(
                f"  {ms.module_id} ({ms.module_name}): "
                f"{ms.found}/{ms.total} ({ms.score_pct}%)"
            )
        gap_lines += [
            "",
            "MISSING / NOT-DETECTED REQUIREMENTS",
            "-" * 40,
        ]
        if report.missing_requirements:
            for req in report.missing_requirements:
                gap_lines.append(f"  [{req.module_id}] {req.requirement}")
        else:
            gap_lines.append("  None — all requirements detected.")

        gap_lines += [
            "",
            "FOUND REQUIREMENTS",
            "-" * 40,
        ]
        for req in report.found_requirements:
            gap_lines.append(
                f"  [{req.module_id}] {req.requirement} "
                f"(matched: {', '.join(req.matched_keywords[:3])})"
            )

        gap_lines += [
            "",
            "=" * 60,
            "DISCLAIMER: This gap report is generated by a prototype AI-assisted",
            "screening tool. It does NOT constitute a legal or regulatory",
            "certification. Always consult a qualified regulatory professional.",
            "Synthetic/demo data only — not for clinical or regulatory use.",
        ]

        gap_report_text = "\n".join(gap_lines)

        st.download_button(
            label="⬇️ Download Gap Report (TXT)",
            data=gap_report_text,
            file_name="pharmaguard_gap_report.txt",
            mime="text/plain",
        )

        # Also offer CSV of requirements
        req_csv = io.StringIO()
        req_df.to_csv(req_csv, index=False)
        st.download_button(
            label="⬇️ Download Requirements CSV",
            data=req_csv.getvalue(),
            file_name="pharmaguard_requirements.csv",
            mime="text/csv",
        )

        st.caption(
            "⚠️ **Disclaimer:** This prototype uses keyword matching and simplified "
            "CTD-inspired rules. It does NOT constitute a legal or regulatory certification. "
            "Always work with qualified regulatory professionals for actual submissions."
        )
