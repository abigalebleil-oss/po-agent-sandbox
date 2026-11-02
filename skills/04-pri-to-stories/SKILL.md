---
name: pri-to-stories
description: Turn a roadmap item (PRI) plus software design notes into milestones and draft user stories with user need statements and testable acceptance criteria, traced to requirements and grounded in the code index.
---

# PRI → Milestones → User Story Drafts

This is the sandbox version of the skill I use at work: it turns a high-level customer need into
a realistic, reviewable delivery plan early, so the team can see what will actually ship and
where extra testing, resources or time are needed **before** committing.

## Inputs
1. One PRI from `inputs/roadmap/` (customer need statement, users, linked requirements, non-negotiables).
2. The matching design notes from `inputs/design/`.
3. `traceability/requirements.csv` and `traceability/tests.csv`.
4. `workflow/code_index.json`. The ONLY source of truth for what code exists.
5. The feedback files in `inputs/feedback/`, for user evidence.

## Definitions
- **PRI:** a high-level customer need statement on the roadmap.
- **Milestone:** a slice of the PRI the team commits to deliver within a specific time window.
  Each milestone must deliver user-visible value on its own.
- **User story:** one unit of work a team can finish within a sprint, with a user need
  statement and acceptance criteria.

## Output (exact format)
```
# Delivery plan: <PRI-ID>

## Milestones

### M1 — <title>
- Window: <release / sprints>
- Goal: <user-visible outcome>
- Requirements: <REQ-IDs>
- Out of scope: <what is deliberately not in this milestone>

## User stories

### STORY-01 · M1 · <title>
- Traces to: <REQ-IDs>
- User need: As a <user>, I need <capability> so that <outcome>.
- Evidence: "<verbatim quote>" [source: <feedback file>]
- Code: `<path>::<name>` — <what changes>   (or)   NEW: <description>
- Acceptance criteria:
  - AC-1: Given <context>, when <action>, then <observable result>.
- Verified by: <TEST-IDs, or "none yet">

## ASSUMPTIONS
- <anything not provable from the inputs; every open product decision goes here>
```

## Rules
1. Every linked requirement in the PRI is covered by at least one story.
2. Every milestone has at least one story; every story names exactly one milestone.
3. Every user need is written "As a …, I need … so that …". The user must be a real user from the PRI.
4. Every acceptance criterion is Given / when / then and testable by QA without asking the PO.
   No vague words ("promptly", "quickly", "user-friendly", "as needed", "appropriate").
   If the requirement itself is vague, propose a measurable value **and** list it under ASSUMPTIONS for the PO to confirm.
5. Code references use `path::name` and must exist in `code_index.json`. Code that does not exist is `NEW:`.
6. Quotes are verbatim from the feedback files, with `[source: file]`.
7. Never weaken a PRI non-negotiable. If a story seems to need it, stop and list it under ASSUMPTIONS.
8. Do not invent requirement, risk or test IDs. A requirement with no test is written "Verified by: none yet".

## Guardrails (deterministic, run after this skill)
```bash
python workflow/check_stories.py <output file>
```
Runs `verify_citations.py` checks (code, IDs, quotes), then checks structure: every PRI requirement
covered, every milestone has stories, every story has a milestone, trace, user need and Given/when/then
ACs, and no vague words in ACs. It also prints a **readiness report**: per milestone, how many stories,
ACs and NEW code items, and which requirements have no test yet. That report is where the team
sees early where extra testing, resources or time are needed.

## Human checkpoint
PO reviews user needs and ACs against the customer need. Dev lead reviews the milestone split and
code impact. QA lead reviews the readiness report. Nothing enters the backlog until all three approve.
