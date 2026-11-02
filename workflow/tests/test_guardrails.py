"""Tests for the guardrail scripts themselves. A checker nobody tests is just another guess."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "workflow"))

import build_code_index
import trace_check
import verify_citations


def _index():
    return build_code_index.build_index()


def test_index_contains_known_function():
    files = _index()["files"]
    assert "validate_result" in files["sandbox_codebase/labbridge/result_validator.py"]["symbols"]


def test_good_example_passes():
    text = (ROOT / "examples/impact_analysis_good.md").read_text()
    _, problems = verify_citations.verify(text, _index(), verify_citations.load_known_ids())
    assert problems == []


def test_hallucinated_example_fails_on_all_three_fabrications():
    text = (ROOT / "examples/impact_analysis_hallucinated.md").read_text()
    _, problems = verify_citations.verify(text, _index(), verify_citations.load_known_ids())
    refs = {p[1] for p in problems}
    assert "sandbox_codebase/labbridge/result_validator.py::override_hold" in refs
    assert "sandbox_codebase/labbridge/auth.py::check_role" in refs
    assert "RISK-004" in refs


def test_paraphrased_quote_is_caught():
    text = '- "The screen shows HELD but never why." [source: 01_night_shift_tech.md]'
    _, problems = verify_citations.verify(text, _index(), verify_citations.load_known_ids())
    assert problems and "not verbatim" in problems[0][2]


def test_verbatim_quote_passes():
    text = '- "The screen says HELD but not why." [source: 01_night_shift_tech.md]'
    _, problems = verify_citations.verify(text, _index(), verify_citations.load_known_ids())
    assert problems == []


def test_trace_check_flags_planted_gap():
    _, gaps = trace_check.check()
    assert gaps == ["REQ-004: no verifying test"]
