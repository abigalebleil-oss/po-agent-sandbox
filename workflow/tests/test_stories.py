"""Tests for check_stories.py, the PRI -> milestones -> user stories guardrail."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "workflow"))

import build_code_index  # noqa: E402
import check_stories  # noqa: E402
import verify_citations  # noqa: E402


def _check(name):
    if not verify_citations.INDEX.exists():
        build_code_index.main()
    return check_stories.check((ROOT / "examples" / name).read_text())


def test_good_plan_passes():
    milestones, stories, problems = _check("stories_PRI-001.md")
    assert problems == []
    assert list(milestones) == ["M1", "M2", "M3"]
    assert len(stories) == 5


def test_flawed_plan_fails_on_every_planted_problem():
    _, _, problems = _check("stories_PRI-001_flawed.md")
    text = "\n".join(problems)
    assert "hl7_export.py::send_alert" in text
    assert "not verbatim in 02_lab_supervisor.md" in text
    assert "STORY-01 AC-2: vague, untestable wording 'promptly'" in text
    assert "STORY-02: user need is not" in text
    assert "STORY-03: does not trace to any requirement" in text
    assert "STORY-04: milestone M4 is not defined" in text
    assert "M3: milestone has no stories" in text
    assert "REQ-003: linked in PRI-001 but not covered by any story" in text


def test_unsafe_but_well_formed_ac_is_not_caught_by_script():
    """Known limit: an AC that breaks a safety non-negotiable but is well formed passes Layer 1.
    That is the human safety review's job (evals/review_checklist.md)."""
    _, _, problems = _check("stories_PRI-001_flawed.md")
    assert not any(p.startswith("STORY-03 AC-1") for p in problems)


def test_vague_words_detected():
    assert check_stories.VAGUE.search("then it is shown promptly")
    assert check_stories.VAGUE.search("in a user-friendly way")
    assert not check_stories.VAGUE.search("then the banner appears within 60 seconds")


def test_readiness_report_flags_untested_requirement():
    milestones, stories, _ = _check("stories_PRI-001.md")
    report = check_stories.readiness_report(milestones, stories)
    m1 = next(l for l in report.splitlines() if l.startswith("M1"))
    assert "REQ-004" in m1
