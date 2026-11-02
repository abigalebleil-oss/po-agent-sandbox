# Build Log

How this sandbox was built, step by step, and why each choice was made. Written so every
piece can be reviewed for accuracy and explained to someone else.

Built with Claude as a pair: I directed scope and design choices; Claude drafted code and
content; every output was run and tested before being kept.

---

## Step 1 — Decide what to demonstrate
**Goal:** show an AI-assisted PO workflow on real-shaped work, without exposing employer IP.
**Decision:** rebuild the workflow on a fictional codebase and synthetic users, in the
clinical-lab domain so the audience is on familiar ground.
**Why not a personal project?** It would show building, but not stakeholders, regulated
traceability, or human review — the things the role actually needs.

## Step 2 — Build a small fake codebase ("LabBridge")
**What:** five Python modules mirroring real middleware concerns:
ASTM parsing → Westgard QC rules → release/hold decision → HL7 export → audit log.
**Why:** impact analysis needs real code to reason about. A tiny codebase keeps the demo
readable in 25 minutes.
**Verified by:** 7 unit tests in `sandbox_codebase/tests/` (all pass).
**Honest limits:** ASTM and HL7 are simplified — realistic structure, not spec-complete.
The QC rules cover 1-2s, 1-3s, 2-2s and R-4s only, within a single run.

## Step 3 — Write synthetic user feedback
**What:** three fictional interviews (night-shift tech, supervisor, LIS admin).
**Why:** a workflow is only interesting if it starts from ambiguity. The three users disagree
in useful ways: speed vs. safety vs. interface stability.

## Step 4 — Write three reusable skills
| Skill | Input → Output | Key rule |
|---|---|---|
| 01 feedback-to-problem | feedback → problem statement | Verbatim quotes with sources; no solutions |
| 02 impact-analysis | requirement + code index → impacted code + ACs | Cite only indexed code; new code marked `NEW:` |
| 03 traceability-review | CSVs + script report → quality findings | Script decides coverage; AI judges quality |

**Design principle:** every skill has a fixed output format and a citation rule, so its output
is machine-checkable. Each one names a human checkpoint.

## Step 5 — Write traceability data
4 requirements, 3 risks, 4 tests in CSVs, linked by ID. CSVs because they diff cleanly in
version control, so the commit history is the review record.
**Planted gap:** REQ-004 has no test and uses "promptly" (untestable).

## Step 6 — Build deterministic guardrails (no AI)
| Script | What it does |
|---|---|
| `build_code_index.py` | Uses Python's own parser to list every file, function, class and method. Same code in, same index out. |
| `verify_citations.py` | Fails any AI output that cites missing code, unknown IDs, missing source files, or quotes not verbatim in the source. |
| `trace_check.py` | Fails if any requirement lacks a risk or a test, or links to unknown IDs. |

**Why deterministic:** existence and coverage are yes/no facts. Asking an AI to check them
would just add another thing that can hallucinate.

## Step 7 — Create example outputs
- `problem_statement.md` and `impact_analysis_good.md`: pass the verifier.
- `impact_analysis_hallucinated.md`: plausible but cites `override_hold`, `auth.py` and
  `RISK-004`, none of which exist. The verifier catches all three.

**Transparency note:** these examples were drafted with Claude for this sandbox. In the live
demo, regenerate them by running the skills and compare.

## Step 8 — Test the guardrails themselves
6 tests in `workflow/tests/` prove the verifier passes good output, catches each fabrication,
catches a paraphrased quote, and that trace_check finds exactly the planted gap.
**Total: 13 tests, all passing.**

## Step 9 — Write the review checklist
`evals/review_checklist.md`: Layer 1 (scripts, pass/fail) before Layer 2 (human rubric).
States the known limit plainly: the verifier proves a function *exists*, not that it is the
*right* one. The hallucinated example's vague AC-1 is only caught by a human.

## Step 10 — Add the PRI → milestones → user stories skill
**What:** `skills/04-pri-to-stories`, rebuilt from the skill I use at work. Inputs: a roadmap item
(`inputs/roadmap/PRI-001.md`), design notes (`inputs/design/DES-001_held_results.md`), the
traceability CSVs, the code index and user feedback. Output: milestones, then user stories with
user need statements, Given/when/then acceptance criteria, code impact and test links.
**Why:** at work this is the skill with the clearest results. Teams get a realistic view of a
release earlier, so testing, resourcing and timing risks show up before the commitment, not after.
**Guardrail:** `workflow/check_stories.py` reuses the citation verifier, then checks structure:
every PRI requirement covered, every milestone has stories, every story has a milestone, trace,
user need and testable ACs with no vague words. It prints a **readiness report** per milestone
(stories, ACs, NEW code items, untested requirements). In the example, M1 is the riskiest: the
most stories, two pieces of new code and an untested requirement (REQ-004).
**Examples:** `stories_PRI-001.md` passes; `stories_PRI-001_flawed.md` fails on six planted problems
and contains a seventh (an unsafe override AC) that only the human review catches.
**Verified by:** 5 new tests in `workflow/tests/test_stories.py`. **Total: 18 tests, all passing.**
**Transparency note:** the example plans were drafted with Claude by running this skill's
instructions. Regenerate live in the demo and compare.

---

## Suggested live demo flow (~12 of the 25 minutes)
1. Show PRI-001 and the three feedback files (1 min): "this is the ambiguity."
2. Run Skill 4 live in Claude on PRI-001 + DES-001; run `check_stories.py` on the result.
   Walk the readiness report: "M1 is where we'd plan extra testing" (4 min).
3. Run `check_stories.py` on the flawed plan. Let the panel watch it fail (1 min).
   Then ask them to spot the one problem the script missed (the unsafe override AC).
4. Pick one story; run Skill 2 for its requirement to show code-level impact; verify (2 min).
5. Run `trace_check.py`; show the REQ-004 gap that the readiness report already flagged (1 min).
6. Open the review checklist: "this is what a human still owns" (2 min).

**Backup:** if live AI calls are slow, the saved examples show the same flow.
