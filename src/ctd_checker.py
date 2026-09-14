"""
ctd_checker.py
--------------
Evaluates a regulatory dossier (plain text or structured text) against a
CTD-inspired checklist covering ICH CTD Modules 1–5.

This module uses keyword/phrase matching to detect whether each required
section is present in the submitted dossier text. The checklist is fully
configurable and easy to extend.

DISCLAIMER
----------
This is a prototype screening tool. It does NOT constitute a legal or
regulatory certification. Always consult a qualified regulatory professional
for actual submission readiness assessment.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# CTD-Inspired Checklist — Modules 1–5
# ---------------------------------------------------------------------------
# Each entry is:
#   module_id  →  (module_name, list of (requirement_label, [keywords]))
#
# A requirement is considered PRESENT when at least one keyword is found
# (case-insensitive) in the dossier text.
# ---------------------------------------------------------------------------

CTD_CHECKLIST: Dict[str, Tuple[str, List[Tuple[str, List[str]]]]] = {
    "Module 1": (
        "Administrative and Regional Information",
        [
            (
                "Cover Letter",
                ["cover letter", "covering letter", "letter of application"],
            ),
            (
                "Application Form",
                ["application form", "application number", "new drug application", "nda", "maa"],
            ),
            (
                "Product Information / Labelling",
                ["product information", "smpc", "summary of product characteristics",
                 "patient information leaflet", "pil", "labelling", "label"],
            ),
            (
                "Qualified Expert Declarations",
                ["expert", "declaration", "qualified person", "cv"],
            ),
        ],
    ),
    "Module 2": (
        "Common Technical Document Summaries",
        [
            (
                "CTD Table of Contents",
                ["table of contents", "toc", "2.1"],
            ),
            (
                "Introduction",
                ["introduction", "2.2"],
            ),
            (
                "Quality Overall Summary (QOS)",
                ["quality overall summary", "qos", "2.3"],
            ),
            (
                "Nonclinical Overview",
                ["nonclinical overview", "non-clinical overview", "2.4"],
            ),
            (
                "Clinical Overview",
                ["clinical overview", "2.5"],
            ),
            (
                "Nonclinical Written and Tabulated Summaries",
                ["nonclinical written", "nonclinical summary", "non-clinical written",
                 "pharmacology written summary", "pharmacokinetics written summary",
                 "toxicology written summary", "tabulated summaries", "2.6"],
            ),
            (
                "Clinical Summary",
                ["clinical summary", "2.7"],
            ),
        ],
    ),
    "Module 3": (
        "Quality",
        [
            (
                "Drug Substance (3.2.S)",
                ["drug substance", "3.2.s", "active pharmaceutical ingredient", "api",
                 "drug substance manufacture", "drug substance specification",
                 "drug substance stability"],
            ),
            (
                "Drug Product (3.2.P)",
                ["drug product", "3.2.p", "finished product", "finished dosage form",
                 "drug product manufacture", "drug product specification",
                 "drug product stability"],
            ),
            (
                "Drug Substance Stability",
                ["drug substance stability", "stability data", "stability study",
                 "long-term stability", "accelerated stability", "re-test period"],
            ),
            (
                "Drug Product Stability",
                ["drug product stability", "shelf life", "shelf-life",
                 "stability of drug product", "stability specification"],
            ),
            (
                "Manufacturing Process & Controls",
                ["manufacturing process", "process validation", "critical process",
                 "gmp", "batch record", "in-process control"],
            ),
        ],
    ),
    "Module 4": (
        "Nonclinical Study Reports",
        [
            (
                "Primary Pharmacodynamics",
                ["primary pharmacodynamics", "primary pharmacodynamic",
                 "pharmacodynamic study", "pharmacology study", "4.2.1", "in vitro", "in vivo"],
            ),
            (
                "Safety Pharmacology",
                ["safety pharmacology", "herg", "cardiovascular telemetry",
                 "cns safety", "respiratory", "icn s7a", "s7a", "s7b"],
            ),
            (
                "Pharmacokinetics Studies",
                ["pharmacokinetics", "pharmacokinetic study", "absorption",
                 "distribution", "metabolism", "excretion", "adme",
                 "bioavailability", "4.2.2"],
            ),
            (
                "Toxicology Studies",
                ["toxicology", "repeat-dose toxicity", "toxicity study",
                 "noael", "single-dose toxicity", "genotoxicity", "4.2.3"],
            ),
            (
                "Reproductive Toxicology",
                ["reproductive", "embryo", "foetal", "fetal", "developmental toxicity",
                 "fertility", "pre- and postnatal", "teratogenicity"],
            ),
            (
                "Genotoxicity Studies",
                ["genotoxicity", "ames", "mutagenicity", "clastogenicity",
                 "micronucleus", "chromosomal aberration"],
            ),
        ],
    ),
    "Module 5": (
        "Clinical Study Reports",
        [
            (
                "Tabular Listing of Clinical Studies",
                ["tabular listing", "table of clinical studies", "clinical studies conducted",
                 "5.2"],
            ),
            (
                "Biopharmaceutic Studies (BA/BE)",
                ["bioavailability", "bioequivalence", "biopharmaceutic",
                 "food effect", "ba study", "be study", "5.3.1"],
            ),
            (
                "Human PK Studies",
                ["human pharmacokinetics", "human pk", "sad", "mad",
                 "single ascending dose", "multiple ascending dose",
                 "population pk", "poppk", "5.3.2"],
            ),
            (
                "Efficacy and Safety Studies",
                ["efficacy", "randomised controlled", "randomized controlled",
                 "placebo-controlled", "phase ii", "phase 2", "clinical trial",
                 "primary endpoint", "5.3.4", "5.3.5"],
            ),
            (
                "Clinical Summary of Safety",
                ["clinical summary", "adverse event", "treatment-emergent",
                 "teae", "serious adverse", "safety summary", "2.7.4"],
            ),
        ],
    ),
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class RequirementStatus:
    """Status of a single checklist requirement."""

    module_id: str
    module_name: str
    requirement: str
    found: bool
    matched_keywords: List[str] = field(default_factory=list)


@dataclass
class ModuleScore:
    """Summary score for one CTD module."""

    module_id: str
    module_name: str
    found: int
    total: int

    @property
    def score_pct(self) -> float:
        if self.total == 0:
            return 0.0
        return round(100.0 * self.found / self.total, 1)


@dataclass
class DossierReport:
    """Full readiness report for a submitted dossier text."""

    requirements: List[RequirementStatus] = field(default_factory=list)

    @property
    def total_requirements(self) -> int:
        return len(self.requirements)

    @property
    def found_count(self) -> int:
        return sum(1 for r in self.requirements if r.found)

    @property
    def missing_count(self) -> int:
        return self.total_requirements - self.found_count

    @property
    def completeness_pct(self) -> float:
        if self.total_requirements == 0:
            return 0.0
        return round(100.0 * self.found_count / self.total_requirements, 1)

    @property
    def missing_requirements(self) -> List[RequirementStatus]:
        return [r for r in self.requirements if not r.found]

    @property
    def found_requirements(self) -> List[RequirementStatus]:
        return [r for r in self.requirements if r.found]

    @property
    def module_scores(self) -> List[ModuleScore]:
        """Aggregate scores per module."""
        scores: Dict[str, ModuleScore] = {}
        for req in self.requirements:
            mid = req.module_id
            if mid not in scores:
                scores[mid] = ModuleScore(
                    module_id=mid,
                    module_name=req.module_name,
                    found=0,
                    total=0,
                )
            scores[mid].total += 1
            if req.found:
                scores[mid].found += 1
        return list(scores.values())

    @property
    def is_submission_ready(self) -> bool:
        """True only when every requirement is found."""
        return self.found_count == self.total_requirements


# ---------------------------------------------------------------------------
# Main checker function
# ---------------------------------------------------------------------------

def check_dossier(
    dossier_text: str,
    checklist: Optional[Dict] = None,
) -> DossierReport:
    """Evaluate *dossier_text* against the CTD-inspired checklist.

    Parameters
    ----------
    dossier_text:
        The plain-text content of the dossier to evaluate.
    checklist:
        Optional override of the default :data:`CTD_CHECKLIST`.
        Must follow the same structure: module_id → (module_name, requirements).

    Returns
    -------
    DossierReport
        Structured report with per-requirement and per-module results.

    Raises
    ------
    TypeError
        If *dossier_text* is not a string.
    ValueError
        If *dossier_text* is empty after stripping whitespace.
    """
    if not isinstance(dossier_text, str):
        raise TypeError(
            f"dossier_text must be a str, got {type(dossier_text).__name__}."
        )

    stripped = dossier_text.strip()
    if not stripped:
        raise ValueError("dossier_text must not be empty.")

    text_lower = stripped.lower()
    active_checklist = checklist if checklist is not None else CTD_CHECKLIST

    requirements: List[RequirementStatus] = []

    for module_id, (module_name, module_requirements) in active_checklist.items():
        for req_label, keywords in module_requirements:
            matched = [kw for kw in keywords if kw.lower() in text_lower]
            found = len(matched) > 0
            requirements.append(
                RequirementStatus(
                    module_id=module_id,
                    module_name=module_name,
                    requirement=req_label,
                    found=found,
                    matched_keywords=matched,
                )
            )

    return DossierReport(requirements=requirements)
