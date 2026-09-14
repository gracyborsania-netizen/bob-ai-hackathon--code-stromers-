"""
bob_adapter.py
--------------
IBM Bob integration adapter for PharmaGuard AI.

This adapter provides two AI-assistance functions:
  1. explain_signal()    — plain-language explanation for a PRR safety signal
  2. summarize_gaps()    — concise gap summary for submission readiness results

Configuration (via environment variables or .env file):
  BOB_API_URL   — IBM Bob / watsonx API endpoint URL
  BOB_API_KEY   — IBM Bob / watsonx API key
  BOB_MODEL     — Model identifier (e.g. "ibm/granite-13b-instruct-v2")

The adapter degrades gracefully when credentials are not configured —
it returns a useful fallback message and does NOT crash the application.

IMPORTANT
---------
This adapter does NOT invent undocumented IBM Bob API endpoints, authentication
formats, or SDK methods. The HTTP integration pattern used here follows the
standard REST completion API pattern. If the actual IBM Bob API differs from
the endpoint structure below, update BOB_API_URL accordingly.

No real credentials are stored in this file. All secrets are read from
environment variables. See .env.example for required variable names.
"""

import os
from typing import Optional

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed — rely on system environment variables

# Optional HTTP client for making API calls
try:
    import urllib.request
    import urllib.error
    import json as _json
    _HTTP_AVAILABLE = True
except ImportError:
    _HTTP_AVAILABLE = False


# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------

def _get_config() -> dict:
    """Read Bob configuration from environment variables.

    Returns a dict with keys: api_url, api_key, model.
    Values are empty strings when not configured.
    """
    return {
        "api_url": os.getenv("BOB_API_URL", "").strip(),
        "api_key": os.getenv("BOB_API_KEY", "").strip(),
        "model": os.getenv("BOB_MODEL", "ibm/granite-13b-instruct-v2").strip(),
    }


def is_configured() -> bool:
    """Return True when the required Bob credentials are present."""
    cfg = _get_config()
    return bool(cfg["api_url"] and cfg["api_key"])


# ---------------------------------------------------------------------------
# Internal API call
# ---------------------------------------------------------------------------

def _call_bob(prompt: str) -> Optional[str]:
    """Send *prompt* to the configured Bob API and return the response text.

    Uses a standard REST completion request.  Returns None on any error
    so that callers can fall back gracefully.

    The expected request format is:
        POST {BOB_API_URL}
        Authorization: Bearer {BOB_API_KEY}
        Content-Type: application/json
        Body: {"model": "{BOB_MODEL}", "prompt": "...", "max_tokens": 512}

    The expected response format is:
        {"results": [{"generated_text": "..."}]}
    or:
        {"choices": [{"text": "..."}]}

    Update this function if the actual IBM Bob API uses a different schema.
    """
    if not _HTTP_AVAILABLE:
        return None

    cfg = _get_config()
    if not cfg["api_url"] or not cfg["api_key"]:
        return None

    payload = _json.dumps({
        "model": cfg["model"],
        "prompt": prompt,
        "max_tokens": 512,
        "temperature": 0.2,
    }).encode("utf-8")

    req = urllib.request.Request(
        url=cfg["api_url"],
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {cfg['api_key']}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            body = _json.loads(response.read().decode("utf-8"))

        # Try watsonx-style response first
        if "results" in body and body["results"]:
            return body["results"][0].get("generated_text", "").strip()

        # Try OpenAI-compatible style
        if "choices" in body and body["choices"]:
            choice = body["choices"][0]
            if "text" in choice:
                return choice["text"].strip()
            if "message" in choice:
                return choice["message"].get("content", "").strip()

        # Try simple text field
        if "generated_text" in body:
            return body["generated_text"].strip()

    except urllib.error.HTTPError as e:
        # Log the error code but do not crash
        _ = f"Bob API HTTP error: {e.code} {e.reason}"
    except urllib.error.URLError:
        pass
    except Exception:
        pass

    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def explain_signal(drug: str, event: str, prr: float, a: int, b: int, c: int, d: int) -> str:
    """Return a plain-language explanation for a detected PRR safety signal.

    Sends the signal details to the configured Bob API and requests a
    concise clinical explanation. Falls back to a well-formed static
    message when Bob is not configured or the call fails.

    Parameters
    ----------
    drug:   Drug name involved in the signal.
    event:  Adverse event name.
    prr:    Computed PRR value.
    a:      Cell a — reports of drug + event.
    b:      Cell b — reports of drug + other events.
    c:      Cell c — other drugs + event.
    d:      Cell d — other drugs + other events.

    Returns
    -------
    str
        2–3 sentence plain-language explanation suitable for display in the UI.
    """
    prr_display = f"{prr:.2f}" if not (prr == float("inf")) else "∞ (event exclusive to this drug)"

    prompt = (
        f"A pharmacovigilance safety signal screening was performed using the "
        f"Proportional Reporting Ratio (PRR) method on spontaneous adverse event data.\n\n"
        f"Signal details:\n"
        f"- Drug: {drug}\n"
        f"- Adverse event: {event}\n"
        f"- PRR: {prr_display}\n"
        f"- Contingency table: a={a}, b={b}, c={c}, d={d}\n\n"
        f"In 2–3 plain sentences, explain what this PRR value might indicate clinically "
        f"and what next steps a pharmacovigilance team should consider. "
        f"Emphasise that this is a disproportionality screening statistic and does NOT "
        f"prove causality."
    )

    response = _call_bob(prompt)
    if response:
        return response

    # Fallback message — useful even without Bob
    prr_str = f"{prr:.2f}" if prr != float("inf") else "∞"
    return (
        f"**PRR Screening Result:** A potential safety signal was identified for "
        f"**{drug}** associated with **{event}** (PRR = {prr_str}). "
        f"This indicates that {drug} is reported with {event} more frequently than "
        f"other drugs in the dataset (a={a} co-reports). "
        f"PRR is a disproportionality screening statistic and does **not** prove causality. "
        f"This result warrants further clinical review, case-series analysis, and causality "
        f"assessment by a qualified pharmacovigilance professional.\n\n"
        f"*(IBM Bob assistance not configured — showing automated fallback explanation.)*"
    )


def summarize_gaps(module_scores: list, missing_requirements: list) -> str:
    """Return a concise gap summary for submission readiness results.

    Sends module scores and missing requirements to the configured Bob API
    and requests actionable guidance. Falls back gracefully when Bob is
    not configured.

    Parameters
    ----------
    module_scores:
        List of dicts with keys: module_id, module_name, found, total, score_pct.
    missing_requirements:
        List of dicts with keys: module_id, requirement.

    Returns
    -------
    str
        Concise gap summary suitable for display in the UI.
    """
    if not module_scores:
        return "No module scores available to summarise."

    # Build a concise summary string for the prompt
    score_lines = "\n".join(
        f"  - {ms['module_id']} ({ms['module_name']}): {ms['found']}/{ms['total']} "
        f"requirements found ({ms['score_pct']}%)"
        for ms in module_scores
    )

    missing_lines = "\n".join(
        f"  - [{mr['module_id']}] {mr['requirement']}"
        for mr in missing_requirements[:15]  # cap at 15 to keep prompt manageable
    )
    if len(missing_requirements) > 15:
        missing_lines += f"\n  ... and {len(missing_requirements) - 15} more"

    prompt = (
        f"A CTD-inspired regulatory submission readiness check was performed on a "
        f"pharmaceutical dossier. Results:\n\n"
        f"Module Scores:\n{score_lines}\n\n"
        f"Missing / Incomplete Requirements:\n{missing_lines}\n\n"
        f"Provide a concise 3–5 bullet-point gap summary explaining the most critical "
        f"missing items and recommended next steps for the regulatory affairs team. "
        f"Note that this is a prototype screening tool and not a legal certification."
    )

    response = _call_bob(prompt)
    if response:
        return response

    # Fallback — build a structured gap summary without Bob
    total_missing = len(missing_requirements)
    overall_pct = (
        sum(ms["found"] for ms in module_scores)
        / max(sum(ms["total"] for ms in module_scores), 1)
        * 100
    )

    lines = [
        f"**Submission Gap Summary** (automated — IBM Bob not configured)\n",
        f"Overall completeness: **{overall_pct:.1f}%** "
        f"({total_missing} requirement(s) not detected in the dossier text)\n",
    ]

    if total_missing == 0:
        lines.append(
            "All checklist items were detected. Review the full dossier carefully "
            "before formal submission."
        )
    else:
        lines.append("**Key gaps identified:**")
        # Group by module
        by_module: dict = {}
        for mr in missing_requirements:
            by_module.setdefault(mr["module_id"], []).append(mr["requirement"])
        for mod_id, reqs in by_module.items():
            lines.append(f"- **{mod_id}:** {', '.join(reqs)}")
        lines.append(
            "\n**Recommended next steps:** Address the missing requirements above, "
            "ensure all sections contain substantive content, and consult a qualified "
            "regulatory professional before submission."
        )

    return "\n".join(lines)
