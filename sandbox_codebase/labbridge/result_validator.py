"""Decide whether a patient result can be auto-released to the LIS or must be held for review."""

RELEASE = "release"
HOLD = "hold"


def range_flag(value, reference_range):
    """Return 'L', 'H' or 'N' against a (low, high) reference range; None if no range."""
    if reference_range is None:
        return None
    low, high = reference_range
    if value < low:
        return "L"
    if value > high:
        return "H"
    return "N"


def validate_result(result, qc_status_for_test):
    """Return (decision, reasons).

    Rules:
      - QC 'reject' for the test -> HOLD (results cannot be trusted)
      - QC 'warning' -> HOLD for technologist review
      - result status other than final ('F') -> HOLD
      - out-of-range values are flagged but still released when QC passes
    """
    reasons = []
    if qc_status_for_test == "reject":
        reasons.append("QC rejected for this test")
    elif qc_status_for_test == "warning":
        reasons.append("QC warning requires technologist review")
    if result.get("status") != "F":
        reasons.append("Result is not final")
    decision = HOLD if reasons else RELEASE
    result["range_flag"] = range_flag(result["value"], result.get("reference_range"))
    return decision, reasons
