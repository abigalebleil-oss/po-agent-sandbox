<!-- PLANTED FLAWED OUTPUT, for the demo. Looks plausible at a glance. check_stories.py should
     reject it. Planted problems:
       1. REQ-003 is linked in PRI-001 but no story covers it; M3 has no stories.
       2. STORY-01 AC-2 uses "promptly" (untestable).
       3. STORY-02 cites hl7_export.py::send_alert, which does not exist.
       4. STORY-02 user need is not "As a ..., I need ... so that ...".
       5. STORY-03 traces to no requirement, and its "quote" is a paraphrase, not verbatim.
       6. STORY-04 points at milestone M4, which is not defined.
     Planted problem the SCRIPT CANNOT catch (only the human safety review does):
       7. STORY-03 AC-1 lets a Supervisor release ANY held result, including a QC reject.
          It is valid Given/when/then, so it passes structure checks. It breaks a PRI non-negotiable. -->

# Delivery plan: PRI-001

## Milestones

### M1 — Technologists know a result is held, and why
- Window: Release 2027.1, sprints 1–2
- Goal: technologists see hold reasons and are notified.
- Requirements: REQ-001, REQ-004

### M2 — Supervisors can release held results
- Window: Release 2027.1, sprints 3–4
- Goal: supervisors can release held results with a reason.
- Requirements: REQ-002

### M3 — The LIS sees held results
- Window: Release 2027.1, sprints 4–5
- Goal: the LIS gets a held status.
- Requirements: REQ-003

## User stories

### STORY-01 · M1 · Worklist shows why a result is held
- Traces to: REQ-001
- User need: As a night-shift technologist, I need the hold reason on the worklist so that I can act faster.
- Code: `sandbox_codebase/labbridge/result_validator.py::validate_result` — return a hold category.
- Acceptance criteria:
  - AC-1: Given a result held for a QC warning, when the worklist opens, then the row shows the QC rule and severity.
  - AC-2: Given a held result, when the worklist loads, then the reason is shown promptly.
- Verified by: TEST-001

### STORY-02 · M1 · Notify on hold
- Traces to: REQ-004
- User need: Technologists get notified of holds.
- Code: `sandbox_codebase/labbridge/hl7_export.py::send_alert` — send the notification.
- Acceptance criteria:
  - AC-1: Given a result is held, when the hold is saved, then a banner appears on the worklist within 60 seconds.
- Verified by: none yet

### STORY-03 · M2 · Supervisor override
- User need: As a core lab supervisor, I need to release held results with a reason so that turnaround time improves.
- Evidence: "I need an override with a reason and a name." [source: 02_lab_supervisor.md]
- Code: `sandbox_codebase/labbridge/audit_log.py::AuditLog.record` — write the override entry.
- Acceptance criteria:
  - AC-1: Given a held result, when a Supervisor enters a reason and confirms, then the result is released and an audit entry is written.
- Verified by: TEST-002

### STORY-04 · M4 · Override report for inspectors
- Traces to: REQ-002
- User need: As a core lab supervisor, I need a list of overrides so that I can answer inspectors.
- Code: NEW: override report.
- Acceptance criteria:
  - AC-1: Given overrides exist this month, when the supervisor opens the report, then each override shows user ID, reason and time.
- Verified by: none yet
