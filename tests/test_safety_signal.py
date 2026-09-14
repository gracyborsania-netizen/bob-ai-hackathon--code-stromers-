"""
test_safety_signal.py
---------------------
Unit tests for src/safety_signal.py.

Coverage targets
----------------
- Normal signal detection (PRR >= 2, count >= 3)
- No signals when PRR < threshold
- Empty input raises ValueError
- Single-record input (edge case — only one drug/event)
- count field is respected (aggregated correctly)
- Infinite PRR when the event is exclusive to one drug
- Drug with zero co-reports produces PRR == 0
"""

import math
import sys
import os

import pytest

# Allow imports from src/ without an installed package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from safety_signal import AdverseEventRecord, PRRResult, compute_prr


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_records(*tuples):
    """Create a list of AdverseEventRecord from (drug, event[, count]) tuples."""
    records = []
    for t in tuples:
        if len(t) == 3:
            records.append(AdverseEventRecord(drug=t[0], event=t[1], count=t[2]))
        else:
            records.append(AdverseEventRecord(drug=t[0], event=t[1]))
    return records


# ---------------------------------------------------------------------------
# Empty / invalid input
# ---------------------------------------------------------------------------

def test_empty_records_raises():
    """compute_prr must raise ValueError for an empty list."""
    with pytest.raises(ValueError, match="empty"):
        compute_prr([])


# ---------------------------------------------------------------------------
# No flagged signals
# ---------------------------------------------------------------------------

def test_no_signals_when_prr_below_threshold():
    """When PRR < 2 for every pair, is_signal is False for all results."""
    # Uniform distribution — every drug has the same event frequency,
    # so PRR == 1.0 for every pair.
    records = make_records(
        ("DrugA", "Headache", 5),
        ("DrugA", "Nausea",   5),
        ("DrugB", "Headache", 5),
        ("DrugB", "Nausea",   5),
    )
    results = compute_prr(records)
    assert results, "Should return results even when no signals."
    assert all(not r.is_signal for r in results), "No pair should be flagged when PRR == 1."


# ---------------------------------------------------------------------------
# Normal signal detection
# ---------------------------------------------------------------------------

def test_signal_detected_above_threshold():
    """A drug–event pair with PRR >= 2 and a >= 3 is flagged as a signal."""
    # DrugA + Rash appears 10 times; DrugA without Rash = 2.
    # DrugB + Rash = 1 (rare); DrugB without Rash = 20.
    records = make_records(
        ("DrugA", "Rash",  10),
        ("DrugA", "Other",  2),
        ("DrugB", "Rash",   1),
        ("DrugB", "Other", 20),
    )
    results = compute_prr(records)
    signal_pairs = {(r.drug, r.event) for r in results if r.is_signal}
    assert ("DrugA", "Rash") in signal_pairs, "DrugA/Rash should be flagged as a signal."


def test_signal_not_flagged_when_count_below_min():
    """PRR >= 2 but a < 3 should NOT be flagged (insufficient evidence)."""
    # Only 2 co-reports for DrugA+Rash, even though PRR is high.
    records = make_records(
        ("DrugA", "Rash",  2),
        ("DrugA", "Other", 1),
        ("DrugB", "Rash",  0),   # count 0 is a no-op (no row added)
        ("DrugB", "Other", 20),
    )
    # Filter out zero-count records manually (compute_prr doesn't skip them,
    # but a count of 0 simply adds 0 to the aggregation).
    records = [r for r in records if r.count > 0]
    results = compute_prr(records)
    drugA_rash = next((r for r in results if r.drug == "DrugA" and r.event == "Rash"), None)
    assert drugA_rash is not None
    assert not drugA_rash.is_signal, "Should NOT flag when a < min_count (3)."


# ---------------------------------------------------------------------------
# count field aggregation
# ---------------------------------------------------------------------------

def test_count_field_is_aggregated():
    """Two rows for the same (drug, event) pair must be summed."""
    records = [
        AdverseEventRecord("DrugA", "Headache", 3),
        AdverseEventRecord("DrugA", "Headache", 4),  # same pair, different row
        AdverseEventRecord("DrugB", "Headache", 1),
        AdverseEventRecord("DrugB", "Nausea",   10),
    ]
    results = compute_prr(records)
    drugA_headache = next(r for r in results if r.drug == "DrugA" and r.event == "Headache")
    assert drugA_headache.a == 7, "Counts for the same pair must be summed (3+4=7)."


# ---------------------------------------------------------------------------
# Infinite PRR (event exclusive to one drug)
# ---------------------------------------------------------------------------

def test_infinite_prr_when_event_exclusive_to_one_drug():
    """When no other drug reports the event, PRR should be infinite."""
    records = make_records(
        ("DrugA", "UniqueEvent", 5),
        ("DrugA", "Common",      2),
        ("DrugB", "Common",      8),
    )
    results = compute_prr(records)
    unique_result = next(r for r in results if r.drug == "DrugA" and r.event == "UniqueEvent")
    assert math.isinf(unique_result.prr), "PRR should be infinite when c == 0."
    assert unique_result.is_signal, "An infinite PRR with a >= 3 should still be flagged."


# ---------------------------------------------------------------------------
# Single-record edge case
# ---------------------------------------------------------------------------

def test_single_record():
    """A dataset with a single record should not raise and should return one result."""
    records = [AdverseEventRecord("DrugX", "EventY", 1)]
    results = compute_prr(records)
    assert len(results) == 1
    # With only one record there are no other drugs/events, so PRR is infinite
    # but a=1 < min_count=3, so is_signal must be False.
    assert not results[0].is_signal


# ---------------------------------------------------------------------------
# Custom threshold
# ---------------------------------------------------------------------------

def test_custom_prr_threshold():
    """Lowering the threshold to 1.0 should flag more pairs."""
    records = make_records(
        ("DrugA", "Rash",  4),
        ("DrugA", "Other", 2),
        ("DrugB", "Rash",  3),
        ("DrugB", "Other", 10),
    )
    results_default = compute_prr(records, prr_threshold=2.0)
    results_low     = compute_prr(records, prr_threshold=1.0)
    signals_default = [r for r in results_default if r.is_signal]
    signals_low     = [r for r in results_low     if r.is_signal]
    assert len(signals_low) >= len(signals_default), (
        "Lowering the threshold should flag at least as many signals."
    )


# ---------------------------------------------------------------------------
# NEW: results are sorted by PRR descending
# ---------------------------------------------------------------------------

def test_results_sorted_by_prr_descending():
    """compute_prr must return results sorted highest PRR first."""
    records = make_records(
        ("DrugA", "Rash",    10),
        ("DrugA", "Nausea",   1),
        ("DrugB", "Rash",     1),
        ("DrugB", "Nausea",  10),
    )
    results = compute_prr(records)
    prr_values = [r.prr for r in results if not math.isinf(r.prr)]
    assert prr_values == sorted(prr_values, reverse=True), (
        "Results must be ordered by PRR descending."
    )
