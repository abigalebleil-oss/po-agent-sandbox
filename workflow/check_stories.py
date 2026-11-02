"""Deterministic checks for a PRI -> milestones -> user stories delivery plan. No AI involved.

Layer 1: every citation is real (reuses verify_citations: code, REQ/RISK/TEST IDs, verbatim quotes).
Layer 2: structure
  - every requirement linked in the PRI is covered by at least one story
  - every milestone has at least one story; every story names a milestone that exists
  - every story traces to at least one REQ, has an "As a ..., I need ... so that ..." user need,
    and at least one Given / when / then acceptance criterion
  - no vague, untestable words in acceptance criteria
Then prints a readiness report: stories, ACs, NEW code items and untested requirements per milestone.

Exit code 0 = ready for human review. Exit code 1 = problems found.

Usage: python workflow/check_stories.py <delivery plan .md>
"""

import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_citations  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
ROADMAP_DIR = REPO_ROOT / "inputs" / "roadmap"
TRACE_DIR = REPO_ROOT / "traceability"

PLAN_HEADER = re.compile(r"^# Delivery plan:\s*(PRI-\d{3})", re.M)
MILESTONE = re.compile(r"^### (M\d+)\s+—\s+(.+)$")
STORY = re.compile(r"^### (STORY-\d+)\s+·\s+(M\d+)?\s*·?\s*(.*)$")
REQ_ID = re.compile(r"\bREQ-\d{3}\b")
USER_NEED = re.compile(r"As an? .+?, I need .+? so that .+", re.I)
AC_LINE = re.compile(r"^\s*-\s*AC-\d+:\s*(.*)$")
GWT = re.compile(r"\bGiven\b.+\bwhen\b.+\bthen\b", re.I)

VAGUE_TERMS = [
    "promptly", "quickly", "fast", "timely", "as soon as possible", "asap", "immediately",
    "user-friendly", "easy", "easily", "intuitive", "seamless", "appropriate", "appropriately",
    "as needed", "if necessary", "etc", "and/or", "efficient", "reasonable", "sufficient",
]
VAGUE = re.compile(r"\b(" + "|".join(re.escape(t) for t in VAGUE_TERMS) + r")\b", re.I)


def pri_requirements(pri_id):
    path = ROADMAP_DIR / f"{pri_id}.md"
    if not path.exists():
        return None
    text = path.read_text()
    m = re.search(r"## Linked requirements\s*\n(.+)", text)
    return REQ_ID.findall(m.group(1)) if m else []


def tested_requirements():
    with open(TRACE_DIR / "tests.csv", newline="") as f:
        ids = set()
        for row in csv.DictReader(f):
            ids.update(x.strip() for x in row["requirement_ids"].split(";") if x.strip())
    return ids


def parse(text):
    """Split the plan into milestones and stories. Returns (milestones, stories)."""
    milestones, stories = {}, []
    current = None
    for line in text.splitlines():
        m = MILESTONE.match(line)
        s = STORY.match(line)
        if m:
            current = {"kind": "milestone", "id": m.group(1), "title": m.group(2), "lines": []}
            milestones[m.group(1)] = current
        elif s:
            current = {"kind": "story", "id": s.group(1), "milestone": s.group(2),
                       "title": s.group(3), "lines": []}
            stories.append(current)
        elif line.startswith("## "):
            current = None
        elif current is not None:
            current["lines"].append(line)
    return milestones, stories


def field(item, name):
    for line in item["lines"]:
        if line.strip().lower().startswith(f"- {name.lower()}:"):
            return line.split(":", 1)[1].strip()
    return ""


def check(text):
    problems = []

    # Layer 1: citations are real
    index = json.loads(verify_citations.INDEX.read_text())
    _, citation_problems = verify_citations.verify(text, index, verify_citations.load_known_ids())
    for lineno, ref, reason in citation_problems:
        problems.append(f"line {lineno}: {ref} -> {reason}")

    # Layer 2: structure
    header = PLAN_HEADER.search(text)
    pri_id = header.group(1) if header else None
    pri_reqs = pri_requirements(pri_id) if pri_id else None
    if pri_id is None:
        problems.append("missing '# Delivery plan: PRI-xxx' header")
    elif pri_reqs is None:
        problems.append(f"{pri_id}: no matching file in inputs/roadmap/")

    milestones, stories = parse(text)
    if not milestones:
        problems.append("no milestones found")
    if not stories:
        problems.append("no user stories found")

    covered = set()
    for s in stories:
        sid = s["id"]
        if not s["milestone"]:
            problems.append(f"{sid}: no milestone")
        elif s["milestone"] not in milestones:
            problems.append(f"{sid}: milestone {s['milestone']} is not defined")
        traces = REQ_ID.findall(field(s, "Traces to"))
        if not traces:
            problems.append(f"{sid}: does not trace to any requirement")
        covered.update(traces)
        if not USER_NEED.search(field(s, "User need")):
            problems.append(f"{sid}: user need is not 'As a ..., I need ... so that ...'")
        acs = [AC_LINE.match(l).group(1) for l in s["lines"] if AC_LINE.match(l)]
        s["ac_count"] = len(acs)
        if not acs:
            problems.append(f"{sid}: no acceptance criteria")
        for i, ac in enumerate(acs, start=1):
            if not GWT.search(ac):
                problems.append(f"{sid} AC-{i}: not written as Given / when / then")
            for word in sorted({w.lower() for w in VAGUE.findall(ac)}):
                problems.append(f"{sid} AC-{i}: vague, untestable wording '{word}'")
        s["new_code"] = sum(1 for l in s["lines"] if re.search(r"\bNEW:", l))

    for mid in milestones:
        if not any(s["milestone"] == mid for s in stories):
            problems.append(f"{mid}: milestone has no stories")

    for req in pri_reqs or []:
        if req not in covered:
            problems.append(f"{req}: linked in {pri_id} but not covered by any story")

    return milestones, stories, problems


def readiness_report(milestones, stories):
    tested = tested_requirements()
    lines = [f"{'Milestone':<10} {'Stories':>7} {'ACs':>5} {'NEW code':>9}  Untested requirements"]
    for mid, m in milestones.items():
        ms = [s for s in stories if s["milestone"] == mid]
        reqs = sorted(set(REQ_ID.findall(field(m, "Requirements"))) |
                      {r for s in ms for r in REQ_ID.findall(field(s, "Traces to"))})
        untested = [r for r in reqs if r not in tested]
        lines.append(f"{mid:<10} {len(ms):>7} {sum(s['ac_count'] for s in ms):>5} "
                     f"{sum(s['new_code'] for s in ms):>9}  {', '.join(untested) or '-'}")
    return "\n".join(lines)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    if not verify_citations.INDEX.exists():
        print("code_index.json not found. Run: python workflow/build_code_index.py")
        sys.exit(2)
    target = Path(sys.argv[1])
    milestones, stories, problems = check(target.read_text())

    print(f"Checking {target}")
    print(f"  Milestones: {len(milestones)}   Stories: {len(stories)}")
    print("\nReadiness report (where to plan extra testing, resources or time):")
    print(readiness_report(milestones, stories))
    if problems:
        print(f"\nFAILED: {len(problems)} problem(s)")
        for p in problems:
            print(f"  - {p}")
        print("Result: NOT READY FOR HUMAN REVIEW. Fix or regenerate.")
        sys.exit(1)
    print("\nResult: PASS. Ready for PO, dev lead and QA review.")


if __name__ == "__main__":
    main()
