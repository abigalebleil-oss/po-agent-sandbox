"""Deterministic traceability coverage check. No AI involved.

Rules:
  - Every requirement links to at least one risk, and every linked risk ID exists.
  - Every requirement is verified by at least one test.
  - Every test links only to requirement IDs that exist.

Exit code 0 = full coverage. Exit code 1 = gaps found.
"""

import csv
import sys
from pathlib import Path

TRACE_DIR = Path(__file__).resolve().parents[1] / "traceability"


def load(name):
    with open(TRACE_DIR / name, newline="") as f:
        return list(csv.DictReader(f))


def split_ids(value):
    return [v.strip() for v in (value or "").split(";") if v.strip()]


def check():
    reqs, risks, tests = load("requirements.csv"), load("risks.csv"), load("tests.csv")
    risk_ids = {r["id"] for r in risks}
    req_ids = {r["id"] for r in reqs}

    tested = {}
    gaps = []
    for t in tests:
        for rid in split_ids(t["requirement_ids"]):
            if rid not in req_ids:
                gaps.append(f"{t['id']}: links to unknown requirement {rid}")
            tested.setdefault(rid, []).append(t["id"])

    rows = []
    for r in reqs:
        linked_risks = split_ids(r["risk_ids"])
        missing = [x for x in linked_risks if x not in risk_ids]
        if not linked_risks:
            gaps.append(f"{r['id']}: no linked risk")
        for x in missing:
            gaps.append(f"{r['id']}: links to unknown risk {x}")
        if r["id"] not in tested:
            gaps.append(f"{r['id']}: no verifying test")
        rows.append((r["id"], ";".join(linked_risks) or "-", ";".join(tested.get(r["id"], [])) or "-"))
    return rows, gaps


def main():
    rows, gaps = check()
    print(f"{'Requirement':<12} {'Risks':<20} Tests")
    for req, risks, tests in rows:
        print(f"{req:<12} {risks:<20} {tests}")
    covered = sum(1 for _, _, t in rows if t != "-")
    print(f"\nTest coverage: {covered}/{len(rows)} requirements")
    if gaps:
        print(f"GAPS ({len(gaps)}):")
        for g in gaps:
            print(f"  - {g}")
        sys.exit(1)
    print("No gaps. Full coverage.")


if __name__ == "__main__":
    main()
