"""Westgard quality-control rules applied to a run of QC measurements.

Each QC value is converted to a z-score: (value - target_mean) / target_sd.

Rules implemented:
    1-2s  WARNING  one value beyond +/-2 SD
    1-3s  REJECT   one value beyond +/-3 SD
    2-2s  REJECT   two consecutive values beyond 2 SD on the same side of the mean
    R-4s  REJECT   two consecutive values more than 4 SD apart
"""

WARNING = "warning"
REJECT = "reject"


def z_scores(values, target_mean, target_sd):
    if target_sd <= 0:
        raise ValueError("target_sd must be positive")
    return [(v - target_mean) / target_sd for v in values]


def check_qc_run(values, target_mean, target_sd):
    """Return a list of violations like {'rule': '1-3s', 'severity': 'reject', 'index': 2}."""
    z = z_scores(values, target_mean, target_sd)
    violations = []
    for i, score in enumerate(z):
        if abs(score) > 3:
            violations.append({"rule": "1-3s", "severity": REJECT, "index": i})
        elif abs(score) > 2:
            violations.append({"rule": "1-2s", "severity": WARNING, "index": i})
        if i > 0:
            prev = z[i - 1]
            if (prev > 2 and score > 2) or (prev < -2 and score < -2):
                violations.append({"rule": "2-2s", "severity": REJECT, "index": i})
            if abs(score - prev) > 4:
                violations.append({"rule": "R-4s", "severity": REJECT, "index": i})
    return violations


def qc_status(values, target_mean, target_sd):
    """Summarize a QC run as 'pass', 'warning' or 'reject'."""
    severities = {v["severity"] for v in check_qc_run(values, target_mean, target_sd)}
    if REJECT in severities:
        return REJECT
    if WARNING in severities:
        return WARNING
    return "pass"
