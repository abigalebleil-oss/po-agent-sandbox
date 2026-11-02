# PO Agent Sandbox

A working, shareable reconstruction of how I use AI and agentic tools as a Product Owner
to move from messy user input to reviewed, traceable, codebase-aware requirements.

**The centerpiece** is the skill I built and use at work: it takes a roadmap item (PRI, a high-level
customer need) plus software design notes, breaks it into milestones the team can commit to, and drafts
user stories with user need statements and acceptance criteria. Teams see a realistic picture of what
will ship much earlier, so we can plan extra testing, resources or time before committing. Here it is
rebuilt as `skills/04-pri-to-stories`, with a deterministic checker and a readiness report.

> **Why a sandbox?** The original workflow was built inside my current employer's environment,
> on proprietary code and real customer feedback. Nothing from that environment is in this repo.
> Everything here — the codebase, the users, the feedback — is fictional and synthetic, built
> to demonstrate the same workflow and the same guardrails without exposing employer IP.

## The workflow in one picture

```
 roadmap item (PRI) + design notes ──► [Skill 4] milestones + user story drafts
                      │
                      ▼
            [Guardrail] check_stories.py  ── fails on fake citations, uncovered requirements,
                      │                       missing user needs, vague acceptance criteria;
                      │                       prints a readiness report per milestone
                      ▼
                 HUMAN REVIEW (PO + dev lead + QA) → backlog

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
| `inputs/roadmap/`, `inputs/design/` | A fictional roadmap item (PRI-001) and its software design notes (DES-001). Input to Skill 4. |
| `skills/` | Reusable instructions run in an LLM (I use Claude). Each defines inputs, output format, and rules that make output checkable. |
| `workflow/` | Deterministic Python scripts — no AI. Code indexer, citation verifier, traceability checker, story checker. |
| `traceability/` | Requirements, risks and tests as CSVs, linked by ID. |
| `examples/` | Saved AI outputs, including one with a planted hallucination that the verifier catches. |
| `evals/` | Rubric and review checklist used to judge AI output quality. |
| `docs/BUILD_LOG.md` | Step-by-step record of how and why this was built. |

## Run it

Requires Python 3.10+ and `pytest`.

```bash
# 1. The fictional codebase and the guardrails both have passing tests
python -m pytest -q

# 2. Build the code index the AI is grounded on
python workflow/build_code_index.py

# 3. Check AI outputs: the good one passes, the hallucinated one fails
python workflow/verify_citations.py examples/impact_analysis_good.md
python workflow/verify_citations.py examples/impact_analysis_hallucinated.md

# 4. Check traceability coverage
python workflow/trace_check.py

# 5. Check a PRI -> milestones -> stories plan: the good one passes, the flawed one fails
python workflow/check_stories.py examples/stories_PRI-001.md
python workflow/check_stories.py examples/stories_PRI-001_flawed.md
```

## Planted on purpose
- `examples/stories_PRI-001_flawed.md` leaves a requirement uncovered, uses "promptly" in an
  acceptance criterion, cites a function that doesn't exist, paraphrases a user quote, skips a
  user need statement and points a story at a milestone that doesn't exist. `check_stories.py`
  catches all of them. It also contains one override criterion that would release a QC-reject
  result. That one is well formed, so no script catches it; the human safety review does.
- `examples/impact_analysis_hallucinated.md` cites a function and a file that don't exist, plus
  an unknown risk ID. The verifier fails it.
- `REQ-004` has no verifying test and uses the untestable word "promptly". `trace_check.py`
  catches the missing test; the traceability-review skill catches the vague wording.
  Code catches what is checkable; AI and humans judge what isn't.

## What the verifier checks
1. Every `path::function` citation exists in the code index.
2. Every REQ/RISK/TEST ID exists in the traceability CSVs.
3. Every quote attributed to a user appears verbatim in the cited feedback file.
