<!-- Example output of skills/04-pri-to-stories for PRI-001, using DES-001, the traceability CSVs,
     the code index and the feedback files. Passes check_stories.py. Still requires PO, dev lead
     and QA review before anything enters the backlog. -->

# Delivery plan: PRI-001

## Milestones

### M1 — Technologists know a result is held, and why
- Window: Release 2027.1, sprints 1–2
- Goal: a held result shows its QC rule and severity, and the technologist on shift is told about it without waiting for the ED to call.
- Requirements: REQ-001, REQ-004
- Out of scope: releasing held results; anything sent to the LIS.

### M2 — Supervisors can release QC-warning holds, on the record
- Window: Release 2027.1, sprints 3–4
- Goal: a QC-warning hold can be released by a Supervisor with a name and reason in the audit trail. QC-reject holds can never be overridden.
- Requirements: REQ-002
- Out of scope: role and user management (provided by the host system).

### M3 — The LIS sees held results instead of missing ones
- Window: Release 2027.1, sprints 4–5
- Goal: the LIS receives a standard HL7 v2.5 "not final" status with the hold reason, so the ED can see it.
- Requirements: REQ-003
- Out of scope: changes to the LIS itself; any custom (Z) segments.

## User stories

### STORY-01 · M1 · Hold decisions carry a machine-readable category
- Traces to: REQ-001
- User need: As a night-shift technologist, I need each hold to state whether it is a QC warning, a QC reject or a non-final result so that I can tell at a glance whether a re-run is likely to clear it.
- Evidence: "I have to go dig through the QC screen to figure out if it was a 1-2s warning or a real reject." [source: 01_night_shift_tech.md]
- Code: `sandbox_codebase/labbridge/result_validator.py::validate_result` — also return a hold category plus the QC rule and severity when QC caused the hold.
- Code: `sandbox_codebase/labbridge/qc_rules.py::check_qc_run` — read only; already returns rule and severity per violation.
- Acceptance criteria:
  - AC-1: Given QC status "warning" from a 1-2s violation, when a result is validated, then the decision is "hold", the category is "qc_warning", and the rule is "1-2s".
  - AC-2: Given QC status "reject" from a 1-3s violation, when a result is validated, then the decision is "hold" and the category is "qc_reject".
  - AC-3: Given QC status "pass" and a final result, when it is validated, then the decision is "release" and no category is set.
- Verified by: TEST-001

### STORY-02 · M1 · Worklist shows why a result is held
- Traces to: REQ-001
- User need: As a night-shift technologist, I need the worklist to show the hold reason next to each held result so that I don't have to search the QC screen to decide what to do.
- Evidence: "The screen says HELD but not why." [source: 01_night_shift_tech.md]
- Code: NEW: worklist hold panel showing category, QC rule and severity (DES-001 D2).
- Acceptance criteria:
  - AC-1: Given a result held for a 1-2s QC warning, when the technologist opens the worklist, then the row shows "QC warning", rule "1-2s" and severity "warning".
  - AC-2: Given a result held because it is not final, when the technologist opens the worklist, then the row shows "Not final" and no QC rule.
- Verified by: TEST-001

### STORY-03 · M1 · Technologist is notified when a result is held
- Traces to: REQ-004
- User need: As a night-shift technologist working alone, I need to be told as soon as one of my results is held so that I can act before the ED calls asking for it.
- Evidence: "I don't find out until the ED calls asking where their results are." [source: 01_night_shift_tech.md]
- Code: NEW: hold event raised after validation and shown as a worklist banner (DES-001 D3).
- Acceptance criteria:
  - AC-1: Given a technologist is logged in, when a result is held, then a banner naming the test and hold category appears on their worklist within 60 seconds.
  - AC-2: Given three results are held within one minute, when the banner appears, then it lists all three.
- Verified by: none yet

### STORY-04 · M2 · Supervisor override for QC-warning holds
- Traces to: REQ-002
- User need: As a core lab supervisor, I need to release a QC-warning hold only with my user ID and a reason so that every manual release can be explained to an inspector.
- Evidence: "I want an override, but it has to require a reason and a name, and it has to be in the audit trail." [source: 02_lab_supervisor.md]
- Code: `sandbox_codebase/labbridge/audit_log.py::AuditLog.record` — new call site writing an "override" entry; no change to the method.
- Code: NEW: override function allowed only for category "qc_warning" and the Supervisor role (DES-001 D4).
- Acceptance criteria:
  - AC-1: Given a result held for a QC warning, when a Supervisor enters a user ID and a non-empty reason and confirms, then the result is released and one audit entry exists with event "override", that user ID and that reason.
  - AC-2: Given a result held for a QC warning, when the reason is empty, then the release is refused and no audit entry is written.
  - AC-3: Given a result held for a QC reject, when any user opens the result, then no override option is shown and the result stays held.
  - AC-4: Given a user without the Supervisor role, when they attempt an override, then it is refused and an audit entry records the refused attempt.
- Verified by: TEST-002, TEST-003

### STORY-05 · M3 · Send held status to the LIS
- Traces to: REQ-003
- User need: As an LIS administrator, I need LabBridge to send a standard "not final" message for held results so that the ED sees the result is on hold instead of missing.
- Evidence: "From the LIS side, a held result just looks missing." [source: 03_lis_admin.md]
- Evidence: "Please don't invent custom segments without telling us." [source: 03_lis_admin.md]
- Code: `sandbox_codebase/labbridge/hl7_export.py::build_msh` — reused unchanged.
- Code: `sandbox_codebase/labbridge/hl7_export.py::build_pid` — reused unchanged.
- Code: NEW: held-status builder producing an ORU^R01 with OBX-11 = "P" and an NTE segment carrying the hold reason (DES-001 D5).
- Acceptance criteria:
  - AC-1: Given a result held for a QC warning, when the held-status message is built, then it contains MSH, PID, OBX with OBX-11 "P", and an NTE with the text "QC warning requires technologist review".
  - AC-2: Given any held-status message, when it is checked against the segment list agreed with the LIS admin, then it contains no Z-segments.
  - AC-3: Given the held result is later released, when the final message is sent, then OBX-11 is "F".
- Verified by: TEST-004

## ASSUMPTIONS
- REQ-004 says "promptly". STORY-03 proposes **within 60 seconds** as a measurable target. PO to confirm with the lab supervisor, then update REQ-004 so it is testable.
- REQ-004 has no verifying test. QA to add one before M1 can close.
- STORY-04 AC-4 (audit the refused attempt) goes beyond REQ-002. PO to confirm or drop.
- Supervisor role and user identity come from the host system (DES-001 constraint).
- STORY-05 AC-3 assumes the LIS accepts a final message replacing a preliminary one. Confirm with the LIS admin during interface validation (RISK-003).
