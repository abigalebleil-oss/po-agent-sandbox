---
name: impact-analysis
description: Given a requirement and the deterministic code index, draft an impact analysis and testable acceptance criteria, citing only code that exists in the index.
---

# Requirement → Impact Analysis + Acceptance Criteria

## Inputs
1. One requirement (ID + text) from `traceability/requirements.csv`.
2. `workflow/code_index.json`, produced by `workflow/build_code_index.py`. This is the ONLY
   source of truth for what code exists. Do not rely on memory or guesses about the codebase.

## Output (exact format)
```
# Impact analysis: <REQ-ID>

## Impacted code
- `<file path>::<function or class>` — <what changes and why>

## Not impacted (checked)
- `<file path>::<function or class>` — <why it is unaffected>

## Acceptance criteria
- AC-1: Given <context>, when <action>, then <observable result>.

## Risks introduced
- <risk> — suggested link to an existing RISK-ID, or `NEW RISK` if none fits

## ASSUMPTIONS
- <anything not provable from the code index or requirement>
```

## Rules
1. Every code reference must use the form `path::name`, and the path and name must exist in
   `code_index.json`. Code that would need to be NEW is written as `NEW: <description>`, never
   as a made-up path.
2. Acceptance criteria must be testable by a QA engineer without asking the PO a question.
3. Never weaken a safety behavior (for example, auto-releasing on a QC reject) unless the
   requirement explicitly says so. If it seems implied, list it under ASSUMPTIONS instead.
4. If the requirement is ambiguous, list the ambiguity under ASSUMPTIONS rather than choosing.

## Guardrail (deterministic, runs after this skill)
`python workflow/verify_citations.py <output file>` fails if any `path::name` is not in the
index. A failing output is not reviewed by humans until it is fixed. Humans review what
deterministic checks cannot judge: correctness of reasoning, completeness, and risk.

## Human checkpoint
PO and a developer review together. The developer confirms impacted code; the PO confirms
the acceptance criteria express the user need.
