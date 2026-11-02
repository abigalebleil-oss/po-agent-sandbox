# Review Checklist and Quality Rubric

AI output is checked in two layers. The layers do different jobs on purpose.

## Layer 1 — Deterministic (scripts, run first, pass/fail)
| Check | Script | Catches |
|---|---|---|
| Code citations exist | `verify_citations.py` | Hallucinated files, functions, classes |
| Trace IDs exist | `verify_citations.py` | Invented REQ/RISK/TEST IDs |
| Coverage complete | `trace_check.py` | Requirements with no risk or no test |
| Delivery plan structure | `check_stories.py` | Uncovered PRI requirements, empty milestones, stories with no trace, user need or Given/when/then ACs, vague AC wording |

Output that fails Layer 1 is fixed or regenerated before any human reviews it. This saves
reviewer time and means humans never "trust" a citation.

## Layer 2 — Human review (PO, plus developer for impact analysis)
Scripts cannot judge these. Score each 0–2 (0 = wrong, 1 = partly, 2 = right).

| Criterion | Question for the reviewer |
|---|---|
| Faithful to source | Are quotes verbatim? Is anything important from users missing? |
| Correct reasoning | Is the impacted code actually the code that changes, for the right reason? |
| Safety preserved | Does anything weaken a safety behavior (e.g., release on QC reject)? Any weakening = automatic fail. |
| Testable ACs | Could QA write a test from each AC without asking the PO? |
| Honest uncertainty | Are guesses labeled ASSUMPTION rather than stated as fact? |

**Pass bar:** Layer 1 passes, no safety fail, and Layer 2 total ≥ 8 of 10.

## Known limit, stated plainly
`verify_citations.py` proves a cited function *exists*, not that it is the *right* function.
Example: `examples/impact_analysis_hallucinated.md` also has a vague AC-1 that does not exclude
QC-reject holds. No script catches that; the human safety check does. That is why both layers exist.

## Data sensitivity rules for real (non-sandbox) use
- No patient identifiers or real customer data in prompts. Synthetic or de-identified only.
- Use only the company-approved AI tool and tenant.
- The AI drafts; it never writes to the backlog, CSVs or repo directly. A human commits changes,
  so version control is the review and approval record.
