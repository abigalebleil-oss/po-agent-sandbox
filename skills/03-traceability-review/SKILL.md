---
name: traceability-review
description: Review requirements, risks and tests for traceability gaps and quality issues after the deterministic coverage check has run.
---

# Traceability Review

## Inputs
1. `traceability/requirements.csv`, `traceability/risks.csv`, `traceability/tests.csv`
2. Output of `python workflow/trace_check.py` (deterministic coverage report)

## Division of labor
- **The script decides coverage.** Whether each requirement links to at least one risk and one
  test, and whether linked IDs exist, is a yes/no fact. The LLM never re-decides it.
- **The LLM judges quality.** Does a linked test actually verify the requirement? Is a risk
  mitigation plausible? Is requirement wording testable and unambiguous?

## Output (exact format)
```
## Coverage (copied from trace_check.py, not re-derived)
<paste script summary>

## Quality findings
- <REQ/RISK/TEST ID>: <issue> — severity: high | medium | low

## Suggested fixes (drafts for human approval)
- <ID>: <proposed change>

## ASSUMPTIONS
- <anything inferred>
```

## Rules
1. Only reference IDs that appear in the input CSVs.
2. Suggested fixes are drafts. The skill never edits the CSVs directly.
3. Flag any requirement wording such as "fast", "user-friendly" or "as needed" as untestable.

## Human checkpoint
PO approves or rejects each suggested fix. Approved changes are made in the CSVs by a human
and committed, so version history is the review record.
