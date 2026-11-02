"""Check an AI-generated document against reality. No AI involved.

Checks:
  1. Every code citation written as `path::name` exists in workflow/code_index.json.
  2. Every REQ-/RISK-/TEST- ID mentioned exists in the traceability CSVs.
  3. Every [source: file] exists in inputs/feedback/, and every "quote" followed by a
     [source: file] appears verbatim (ignoring line breaks) in that file.

Lines starting with 'NEW:' (inside a bullet) describe code that does not exist yet and are
allowed by design. 'NEW RISK' is also allowed.

Exit code 0 = all citations verified. Exit code 1 = at least one citation is fabricated.

Usage: python workflow/verify_citations.py <file.md>
"""

import csv
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX = REPO_ROOT / "workflow" / "code_index.json"
TRACE_DIR = REPO_ROOT / "traceability"

FEEDBACK_DIR = REPO_ROOT / "inputs" / "feedback"

CODE_REF = re.compile(r"`([\w./-]+\.py)::([\w.]+)`")
TRACE_REF = re.compile(r"\b((?:REQ|RISK|TEST)-\d{3})\b")
SOURCE_REF = re.compile(r"\[source:\s*([\w.-]+)\]")
QUOTE_WITH_SOURCE = re.compile(r'"([^"]+)"\s*\[source:\s*([\w.-]+)\]')


def normalize(s):
    return " ".join(s.split())


def load_known_ids():
    ids = set()
    for name in ("requirements.csv", "risks.csv", "tests.csv"):
        with open(TRACE_DIR / name, newline="") as f:
            ids.update(row["id"] for row in csv.DictReader(f))
    return ids


def verify(text, index, known_ids):
    files = index["files"]
    problems, verified = [], []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for path, name in CODE_REF.findall(line):
            ref = f"{path}::{name}"
            if path not in files:
                problems.append((lineno, ref, "file does not exist in code index"))
            elif name not in files[path]["symbols"]:
                problems.append((lineno, ref, "function/class not found in that file"))
            else:
                verified.append(ref)
        for trace_id in TRACE_REF.findall(line):
            if trace_id not in known_ids:
                problems.append((lineno, trace_id, "ID not found in traceability CSVs"))
        for source in SOURCE_REF.findall(line):
            if not (FEEDBACK_DIR / source).exists():
                problems.append((lineno, source, "cited source file does not exist"))
        for quote, source in QUOTE_WITH_SOURCE.findall(line):
            src = FEEDBACK_DIR / source
            if src.exists():
                if normalize(quote) in normalize(src.read_text()):
                    verified.append(f'quote in {source}')
                else:
                    problems.append((lineno, f'"{quote[:40]}..."',
                                     f"quote is not verbatim in {source}"))
    return verified, problems


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    if not INDEX.exists():
        print("code_index.json not found. Run: python workflow/build_code_index.py")
        sys.exit(2)
    target = Path(sys.argv[1])
    index = json.loads(INDEX.read_text())
    verified, problems = verify(target.read_text(), index, load_known_ids())

    print(f"Checking {target}")
    print(f"  Verified citations (code + quotes): {len(verified)}")
    if problems:
        print(f"  FAILED: {len(problems)} unverifiable citation(s)")
        for lineno, ref, reason in problems:
            print(f"    line {lineno}: {ref} -> {reason}")
        print("  Result: NOT READY FOR HUMAN REVIEW. Fix or regenerate.")
        sys.exit(1)
    print("  Result: PASS. Ready for human review.")


if __name__ == "__main__":
    main()
