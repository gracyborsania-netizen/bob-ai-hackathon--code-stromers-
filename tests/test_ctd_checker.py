"""
test_ctd_checker.py
-------------------
Unit tests for src/ctd_checker.py (text-based CTD checker).

Coverage targets
----------------
- Empty dossier text raises ValueError
- Non-string input raises TypeError
- Very short text produces mostly-missing results
- Full sample text produces high completeness
- Module score aggregation
- Missing requirements list
- is_submission_ready flag
- Custom checklist override
- Completeness percentage calculation
"""

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ctd_checker import check_dossier, DossierReport, CTD_CHECKLIST


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MINIMAL_CHECKLIST = {
    "Module 2": (
        "CTD Summaries",
        [
            ("Quality Overall Summary", ["quality overall summary", "qos"]),
            ("Clinical Overview", ["clinical overview"]),
        ],
    ),
    "Module 3": (
        "Quality",
        [
            ("Drug Substance", ["drug substance"]),
        ],
    ),
}

FULL_TEXT = (
    "Quality overall summary has been prepared. "
    "Clinical overview is provided. "
    "Drug substance section contains all required information."
)

EMPTY_TEXT_VARIANTS = ["", "   ", "\n\n\t"]


# ---------------------------------------------------------------------------
# Invalid input
# ---------------------------------------------------------------------------

def test_non_string_raises_type_error():
    """check_dossier must raise TypeError when given a non-string."""
    with pytest.raises(TypeError):
        check_dossier({"not": "a string"})


def test_none_raises_type_error():
    """None is not a valid dossier."""
    with pytest.raises(TypeError):
        check_dossier(None)


def test_empty_string_raises_value_error():
    """An empty string raises ValueError."""
    with pytest.raises(ValueError):
        check_dossier("")


def test_whitespace_only_raises_value_error():
    """Whitespace-only string raises ValueError."""
    with pytest.raises(ValueError):
        check_dossier("   \n\t  ")


# ---------------------------------------------------------------------------
# Full match
# ---------------------------------------------------------------------------

def test_full_text_all_found():
    """Text containing all keywords should mark all requirements found."""
    report = check_dossier(FULL_TEXT, checklist=MINIMAL_CHECKLIST)
    assert report.found_count == 3
    assert report.total_requirements == 3
    assert report.is_submission_ready
    assert report.completeness_pct == 100.0
    assert report.missing_requirements == []


# ---------------------------------------------------------------------------
# Partial match
# ---------------------------------------------------------------------------

def test_partial_text():
    """Text with only some keywords should reflect partial completeness."""
    text = "Quality overall summary is provided."  # no clinical overview, no drug substance
    report = check_dossier(text, checklist=MINIMAL_CHECKLIST)
    assert report.found_count == 1
    assert report.total_requirements == 3
    assert not report.is_submission_ready
    assert len(report.missing_requirements) == 2


# ---------------------------------------------------------------------------
# No match
# ---------------------------------------------------------------------------

def test_unrelated_text_all_missing():
    """Text with no relevant keywords should have zero found requirements."""
    text = "This document discusses general topics unrelated to pharmaceuticals."
    report = check_dossier(text, checklist=MINIMAL_CHECKLIST)
    assert report.found_count == 0
    assert report.missing_count == 3
    assert not report.is_submission_ready


# ---------------------------------------------------------------------------
# Case insensitivity
# ---------------------------------------------------------------------------

def test_case_insensitive_matching():
    """Keywords should match regardless of case."""
    text = "QUALITY OVERALL SUMMARY and CLINICAL OVERVIEW and DRUG SUBSTANCE"
    report = check_dossier(text, checklist=MINIMAL_CHECKLIST)
    assert report.found_count == 3


# ---------------------------------------------------------------------------
# Module scores
# ---------------------------------------------------------------------------

def test_module_scores_aggregated():
    """Module scores should aggregate per-module correctly."""
    # Only Module 2 requirements present, Module 3 missing
    text = "quality overall summary and clinical overview present"
    report = check_dossier(text, checklist=MINIMAL_CHECKLIST)
    scores = {ms.module_id: ms for ms in report.module_scores}
    assert scores["Module 2"].found == 2
    assert scores["Module 2"].total == 2
    assert scores["Module 3"].found == 0
    assert scores["Module 3"].total == 1


# ---------------------------------------------------------------------------
# Completeness percentage
# ---------------------------------------------------------------------------

def test_completeness_pct_one_third():
    """One out of three requirements should give ~33.3%."""
    text = "drug substance information"
    report = check_dossier(text, checklist=MINIMAL_CHECKLIST)
    assert abs(report.completeness_pct - 33.3) < 0.5


# ---------------------------------------------------------------------------
# Custom checklist override
# ---------------------------------------------------------------------------

def test_custom_checklist_override():
    """A caller can supply their own checklist."""
    custom = {
        "Module X": (
            "Custom Module",
            [
                ("Custom Item 1", ["custom keyword one"]),
                ("Custom Item 2", ["custom keyword two"]),
            ],
        )
    }
    text = "This text contains custom keyword one."
    report = check_dossier(text, checklist=custom)
    assert report.total_requirements == 2
    assert report.found_count == 1


# ---------------------------------------------------------------------------
# Full ICH checklist smoke test
# ---------------------------------------------------------------------------

def test_full_ich_checklist_with_sample_dossier():
    """The sample dossier text should achieve high completeness on the real checklist."""
    sample_path = os.path.join(
        os.path.dirname(__file__), "..", "src", "data", "sample_dossier.txt"
    )
    if not os.path.exists(sample_path):
        pytest.skip("Sample dossier not found — skipping smoke test.")

    with open(sample_path, "r", encoding="utf-8") as f:
        text = f.read()

    report = check_dossier(text)
    # The sample dossier is designed to cover all requirements — expect ≥ 90%
    assert report.completeness_pct >= 90.0, (
        f"Expected ≥90% completeness, got {report.completeness_pct}%\n"
        f"Missing: {[r.requirement for r in report.missing_requirements]}"
    )


# ---------------------------------------------------------------------------
# found_requirements property
# ---------------------------------------------------------------------------

def test_found_requirements_property():
    """found_requirements should contain only requirements that were found."""
    text = "quality overall summary is here"
    report = check_dossier(text, checklist=MINIMAL_CHECKLIST)
    found = report.found_requirements
    assert all(r.found for r in found)
    assert any(r.requirement == "Quality Overall Summary" for r in found)
