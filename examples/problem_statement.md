<!-- Example output of skills/01-feedback-to-problem, run on inputs/feedback/*.md.
     Saved as a reference. In the live demo, regenerate it and compare. -->

## Problem statement
When QC raises a warning, LabBridge holds patient results without telling anyone why, so
technologists lose time diagnosing holds, the LIS shows results as simply missing, and manual
releases are hard to attribute — contributing to missed ED turnaround targets.

## Users affected
- Night-shift technologist: does not learn about holds quickly, and cannot see the hold reason without extra navigation [source: 01_night_shift_tech.md]
- Lab supervisor: cannot easily see who manually released a result or why [source: 02_lab_supervisor.md]
- LIS administrator: held results are invisible to the LIS until released [source: 03_lis_admin.md]

## Evidence
- "The screen says HELD but not why." [source: 01_night_shift_tech.md]
- Each warning-driven re-run and manual release takes about 10–15 minutes, a few times per night [source: 01_night_shift_tech.md]
- "Our turnaround-time KPI for ED potassium is 60 minutes." [source: 02_lab_supervisor.md]
- "From the LIS side, a held result just looks missing." [source: 03_lis_admin.md]

## Constraints stated by users
- Results must never auto-release on a real QC reject [source: 01_night_shift_tech.md]
- Any override must require a name and a reason, and appear in the audit trail [source: 02_lab_supervisor.md]
- Messages to the LIS must use HL7 the interface engine already understands [source: 03_lis_admin.md]

## Open questions for the PO
- How many QC-warning holds occur per week across all shifts, not just nights?
- What share of missed ED potassium turnaround targets is caused by QC-warning holds?
- Which roles, besides Supervisor, should be allowed to override?

## ASSUMPTIONS
- The three interviews are representative of other sites. Not yet validated.
