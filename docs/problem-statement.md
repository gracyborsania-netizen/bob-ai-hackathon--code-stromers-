# Problem Statement

## Background

Drug safety monitoring (pharmacovigilance) is a critical pillar of the modern pharmaceutical regulatory framework. Once a drug reaches the market, regulatory agencies such as the FDA, EMA, and national authorities require pharmaceutical companies to continuously monitor spontaneous adverse event reports, identify potential safety signals, and take appropriate action — including label updates, risk communication, or market withdrawal.

Simultaneously, bringing a new drug to market requires assembling a complex regulatory submission dossier in a standardised format. The International Council for Harmonisation (ICH) developed the Common Technical Document (CTD) format — a globally accepted structure covering quality (Module 3), nonclinical (Module 4), and clinical (Module 5) data, plus administrative and summary modules.

Both processes — pharmacovigilance signal detection and submission dossier readiness — are data-intensive, time-consuming, and prone to human error when performed manually at scale.

---

## The Problem

### Part 1: Drug Safety Signal Detection

Spontaneous adverse event reporting databases (such as FDA FAERS, WHO VigiBase, EudraVigilance) contain millions of drug–event reports. Pharmacovigilance professionals must screen these databases to identify **disproportionate reporting patterns** — drug–event combinations that appear more often than would be expected by chance, which may indicate a potential safety signal requiring further investigation.

The challenge: manually reviewing every possible drug–event combination is infeasible. Standard statistical methods like the **Proportional Reporting Ratio (PRR)** provide a transparent, reproducible screening approach — but applying them correctly to large datasets, ranking the results, and communicating findings clearly still requires significant time and expertise.

There is a need for:
- Automated PRR calculation across all drug–event pairs
- Clear, ranked presentation of potential signals
- Transparent display of the underlying contingency table values
- Plain-language explanations accessible to non-statisticians
- Fast iteration with configurable thresholds

### Part 2: Regulatory Submission Readiness

Before a New Drug Application (NDA) or Marketing Authorisation Application (MAA) can be submitted, a regulatory affairs team must verify that the CTD dossier is complete. The ICH CTD format requires specific content in each of five modules:

- **Module 1** — Administrative and regional information
- **Module 2** — CTD summaries (quality, nonclinical, clinical overviews and summaries)
- **Module 3** — Quality (drug substance, drug product, manufacturing, stability)
- **Module 4** — Nonclinical study reports (pharmacology, pharmacokinetics, toxicology)
- **Module 5** — Clinical study reports (BA/BE, PK, efficacy, safety)

Verifying completeness manually across all modules is time-consuming and error-prone. Gaps discovered late — for example, a missing stability section or an incomplete clinical summary — can delay submissions by months and incur significant costs.

There is a need for:
- Automated checklist-based completeness evaluation
- Module-wise scoring to identify weak areas
- Clear identification of missing requirements
- Actionable gap reports that guide the team toward resolution

---

## Who Is Affected

- **Pharmacovigilance teams** — responsible for ongoing drug safety monitoring post-marketing
- **Regulatory affairs professionals** — responsible for preparing and submitting dossiers
- **Small and mid-size pharmaceutical companies** — may lack large teams to perform these checks manually
- **Contract research organisations (CROs)** — providing regulatory and pharmacovigilance services
- **Regulatory agencies** — who benefit when submissions are better prepared and complete

---

## Why It Matters

- Delayed signal detection can mean continued patient exposure to preventable risks
- Incomplete dossiers lead to regulatory queries, deficiency letters, and submission rejections
- Both outcomes have direct patient safety implications and significant financial consequences
- AI-assisted tools that are transparent, configurable, and explainable can meaningfully reduce the burden on expert teams

---

## Why Existing Solutions Fall Short

Existing pharmacovigilance and regulatory tools are often:

- **Expensive and complex** — enterprise software requiring extensive configuration and licensing
- **Opaque** — statistical scores without clear explanations of how they were computed
- **Not accessible** — require specialised expertise to operate
- **Siloed** — separate tools for signal detection and submission readiness with no integration

PharmaGuard AI addresses these gaps with a lightweight, transparent, prototype AI-assisted tool that combines both functions in a single, beginner-friendly web dashboard — with optional IBM Bob AI assistance for plain-language explainability.
