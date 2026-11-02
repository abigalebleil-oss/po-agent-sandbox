<!-- Example output of skills/02-impact-analysis for REQ-002, grounded on workflow/code_index.json.
     Passes verify_citations.py. Still requires PO + developer review. -->

# Impact analysis: REQ-002

## Impacted code
- `sandbox_codebase/labbridge/result_validator.py::validate_result` — currently returns only HOLD plus free-text reasons. It must also return a machine-readable hold category (QC warning vs QC reject vs not final) so override eligibility can be decided without parsing text.
- `sandbox_codebase/labbridge/audit_log.py::AuditLog.record` — used as-is to write an override entry (event, user ID, reason, timestamp). No change to the method; new call site only.
- NEW: an override function that checks the hold category is QC warning, requires a non-empty user ID and reason, writes the audit entry, then releases the result.
- NEW: a role check for Supervisor. No role or user management exists in the code index.

## Not impacted (checked)
- `sandbox_codebase/labbridge/qc_rules.py::check_qc_run` — QC rule evaluation is unchanged; override acts after QC, never alters QC status.
- `sandbox_codebase/labbridge/hl7_export.py::build_oru_r01` — an overridden result is a released result and flows through unchanged.
- `sandbox_codebase/labbridge/astm_parser.py::parse_message` — input parsing is unaffected.

## Acceptance criteria
- AC-1: Given a result held for a QC warning, when a Supervisor enters a user ID and a non-empty reason and confirms, then the result is released and one audit entry exists with event "override", that user ID and that reason.
- AC-2: Given a result held for a QC warning, when the reason is empty, then the release is refused and no audit entry is written.
- AC-3: Given a result held for a QC reject, when any user attempts an override, then the option is unavailable and the result stays held.
- AC-4: Given a non-Supervisor user, when they attempt an override, then it is refused.
- AC-5: Given an override was recorded, when the audit chain is verified, then verification passes.

## Risks introduced
- Override used to release results that should be re-run — links to RISK-001
- Override recorded without enough context for inspectors — links to RISK-002

## ASSUMPTIONS
- Supervisor role and user identity are provided by the host system; LabBridge has no user management today.
- "Free-text reason" has no minimum length. PO to confirm.
