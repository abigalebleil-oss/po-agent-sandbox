# PO Agent Sandbox

A working, shareable reconstruction of how I use AI and agentic tools as a Product Owner
to move from messy user input to reviewed, traceable, codebase-aware requirements.

> **Why a sandbox?** The original workflow was built inside my current employer's environment,
> on proprietary code and real customer feedback. Nothing from that environment is in this repo.
> Everything here — the codebase, the users, the feedback — is fictional and synthetic, built
> to demonstrate the same workflow and the same guardrails without exposing employer IP.

## The workflow in one picture

```
 messy user feedback ──► [Skill 1] problem framing ──► HUMAN REVIEW (PO)
                                                          │
                                                          ▼
 requirement ──► [Skill 2] impact analysis + acceptance criteria
                      │   (grounded in a deterministic code index)
                      ▼
            [Guardrail] verify_citations.py  ── fails if the AI cites code that doesn't exist
                      │
                      ▼
                 HUMAN REVIEW (PO + dev)
                      │
                      ▼
 requirements + risks + tests ──► [Skill 3] traceability review
                      │
                      ▼
            [Guardrail] trace_check.py  ── fails on any requirement missing a risk or test link
                      │
                      ▼
                 HUMAN APPROVAL → backlog
```

**Principle:** AI drafts. Deterministic code checks what can be checked. Humans approve.

## What's in here

| Folder | What it is |
|---|---|
| `sandbox_codebase/` | "LabBridge" — a tiny fictional instrument-to-LIS middleware (ASTM in → QC check → HL7 out, with an audit log). Has passing unit tests. |
| `inputs/feedback/` | Synthetic feedback from fictional lab users. The starting ambiguity. |
| `skills/` | Reusable instructions run in an LLM (I use Claude). Each defines inputs, output format, and rules that make output checkable. |
| `workflow/` | Deterministic Python scripts — no AI. Code indexer, citation verifier, traceability checker. |
| `traceability/` | Requirements, risks and tests as CSVs, linked by ID. |
| `examples/` | Saved AI outputs, including one with a planted hallucination that the verifier catches. |
| `evals/` | Rubric and review checklist used to judge AI output quality. |
| `docs/BUILD_LOG.md` | Step-by-step record of how and why this was built. |

## Run it

Requires Python 3.10+ and `pytest`.

```bash
# 1. The fictional codebase and the guardrails both have passing
