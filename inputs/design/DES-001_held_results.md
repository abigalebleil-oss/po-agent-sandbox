# DES-001: Held-results handling — software design notes

Source: synthetic design doc for the fictional LabBridge middleware.
Code names below refer to `sandbox_codebase/labbridge/`.

## Current behavior
1. `astm_parser.parse_message` turns instrument output into result dictionaries.
2. `qc_rules.qc_status` summarizes the most recent QC run per test as `pass`, `warning` or `reject`.
3. `result_validator.validate_result` returns `(decision, reasons)`. Any QC warning, QC reject
   or non-final status produces `hold`. Reasons are free text only.
4. Released results go to `hl7_export.build_oru_r01`. Held results never leave LabBridge,
   so the LIS sees nothing.
5. `audit_log.AuditLog` provides a hash-chained, append-only log. Nothing writes to it for holds today.

## Proposed changes
- **D1 Hold category.** `validate_result` also returns a machine-readable hold category
  (`qc_warning`, `qc_reject`, `not_final`) and the QC rule and severity when QC caused the hold.
- **D2 Worklist hold panel (new UI).** Shows category, QC rule and severity per held result.
- **D3 Hold notification (new).** Event raised when a result is held; delivered to the
  logged-in technologist's worklist banner. Delivery target not yet set by product.
- **D4 Supervised override (new).** Allowed only for `qc_warning`. Requires Supervisor role,
  user ID and a non-empty reason. Writes an `override` entry with `AuditLog.record` before release.
- **D5 Held-status message to LIS.** New builder producing an HL7 v2.5 ORU with
  OBX-11 result status `P` (preliminary) and the hold reason in an NTE segment.
  Reuses `build_msh` and `build_pid`.

## Known constraints
- LabBridge has no user or role management. Role and identity come from the host system.
- The LIS interface engine accepts standard v2.5 segments only. NTE is supported; Z-segments are not.
