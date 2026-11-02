<!-- DELIBERATELY FLAWED example for the demo. It reads plausibly, but cites code that does not
     exist. verify_citations.py must fail it before any human spends time reviewing it. -->

# Impact analysis: REQ-002

## Impacted code
- `sandbox_codebase/labbridge/result_validator.py::override_hold` — extend the existing override function to require a reason.
- `sandbox_codebase/labbridge/auth.py::check_role` — reuse the existing role check for Supervisor.
- `sandbox_codebase/labbridge/audit_log.py::AuditLog.record` — write the override entry.

## Not impacted (checked)
- `sandbox_codebase/labbridge/qc_rules.py::check_qc_run` — unchanged.

## Acceptance criteria
- AC-1: Given a held result, when a Supervisor overrides with a reason, then it is released and audited.

## Risks introduced
- Unauthorized release — links to RISK-004

## ASSUMPTIONS
- None.
