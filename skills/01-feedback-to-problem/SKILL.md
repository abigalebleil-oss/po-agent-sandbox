---
name: feedback-to-problem
description: Turn raw user feedback or interview notes into a framed problem statement with evidence, for PO review before any solutioning.
---

# Feedback → Problem Statement

## Input
One or more feedback files (interview notes, support tickets, observations).

## Output (exact format)
```
## Problem statement
<one or two sentences: who is blocked, doing what, and why it matters>

## Users affected
- <role>: <their specific pain> [source: <file name>]

## Evidence
- "<short verbatim quote>" [source: <file name>]
- <quantified signal if one exists, e.g. time lost, KPI impacted> [source: <file name>]

## Constraints stated by users
- <constraint> [source: <file name>]

## Open questions for the PO
- <what the feedback does NOT tell us>

## ASSUMPTIONS
- <anything inferred rather than stated; empty list if none>
```

## Rules
1. Every bullet must end with `[source: <file name>]`, except open questions and assumptions.
2. Quotes must be verbatim from the input. Never paraphrase inside quotation marks.
3. Do not propose solutions. Framing only.
4. If users disagree or constraints conflict, say so explicitly. Do not smooth it over.
5. If a number is not in the input, do not invent one. Put the gap under Open questions.

## Human checkpoint
The PO reviews and edits this before it is used as input to requirements. The PO checks:
quotes are verbatim, nothing important was dropped, and assumptions are labeled.
