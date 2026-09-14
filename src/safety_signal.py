"""
safety_signal.py
----------------
Computes the Proportional Reporting Ratio (PRR) for drug–adverse-event
pairs from a spontaneous adverse-event reporting dataset.

PRR Formula
-----------
Given a 2×2 contingency table:

                   Event E     Other Events
Drug X               a              b
Other Drugs          c              d

  a = reports of Drug X WITH Event E
  b = reports of Drug X WITHOUT Event E
  c = reports of OTHER drugs WITH Event E
  d = reports of OTHER drugs WITHOUT Event E

  PRR = (a / (a + b)) / (c / (c + d))

A PRR >= 2 with a >= 3 co-reports is a common screening threshold for a
"potential safety signal" per Evans et al. (2001).

DISCLAIMER
----------
PRR is a disproportionality screening statistic. It does NOT prove causality.
All signals require further clinical and epidemiological investigation.
"""

import math
from collections import defaultdict
from dataclasses import dataclass
from typing import List


@dataclass
class AdverseEventRecord:
    """Represents one row of spontaneous adverse-event reporting data."""

    drug: str
    event: str
    count: int = 1  # number of reports this row represents


@dataclass
class PRRResult:
    """Holds the PRR calculation result for one drug–event pair."""

    drug: str
    event: str
    a: int           # drug X + event E
    b: int           # drug X + other events
    c: int           # other drugs + event E
    d: int           # other drugs + other events
    prr: float
    is_signal: bool  # True when PRR >= threshold AND a >= min_count


def compute_prr(
    records: List[AdverseEventRecord],
    prr_threshold: float = 2.0,
    min_count: int = 3,
) -> List[PRRResult]:
    """Compute PRR for every unique drug–event pair in *records*.

    Parameters
    ----------
    records:
        List of :class:`AdverseEventRecord` objects.
    prr_threshold:
        Minimum PRR value to flag a signal (default 2.0).
    min_count:
        Minimum number of co-reports (cell *a*) required to flag a
        signal (default 3). Prevents flagging on single isolated reports.

    Returns
    -------
    List[PRRResult]
        One result per unique (drug, event) pair, sorted by PRR descending.

    Raises
    ------
    ValueError
        If *records* is empty.
    """
    if not records:
        raise ValueError("records list must not be empty.")

    # ----------------------------------------------------------------
    # Aggregate counts by (drug, event) pair, drug total, event total
    # ----------------------------------------------------------------
    pair_counts: dict = defaultdict(int)
    drug_totals: dict = defaultdict(int)
    event_totals: dict = defaultdict(int)
    grand_total: int = 0

    for rec in records:
        pair_counts[(rec.drug, rec.event)] += rec.count
        drug_totals[rec.drug] += rec.count
        event_totals[rec.event] += rec.count
        grand_total += rec.count

    results: List[PRRResult] = []

    for (drug, event), a in pair_counts.items():
        # b = total reports for this drug minus those with this event
        b = drug_totals[drug] - a
        # c = total reports for this event across ALL drugs minus cell a
        c = event_totals[event] - a
        # d = everything else (other drugs, other events)
        d = grand_total - a - b - c

        # Guard against division by zero
        if c == 0 or (c + d) == 0:
            # Event is exclusive to this drug → infinite disproportionality
            prr_value = float("inf")
        elif (a + b) == 0:
            prr_value = 0.0
        else:
            prr_value = (a / (a + b)) / (c / (c + d))

        is_signal = prr_value >= prr_threshold and a >= min_count

        results.append(
            PRRResult(
                drug=drug,
                event=event,
                a=a,
                b=b,
                c=c,
                d=d,
                prr=round(prr_value, 4),
                is_signal=is_signal,
            )
        )

    # Sort highest PRR first; treat inf as a very large number for sorting
    results.sort(
        key=lambda r: r.prr if not math.isinf(r.prr) else 1e9,
        reverse=True,
    )
    return results
