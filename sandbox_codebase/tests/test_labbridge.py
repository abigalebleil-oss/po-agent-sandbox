import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from labbridge.astm_parser import ASTMParseError, parse_message, parse_result_record
from labbridge.audit_log import AuditLog
from labbridge.hl7_export import build_oru_r01
from labbridge.qc_rules import check_qc_run, qc_status
from labbridge.result_validator import HOLD, RELEASE, validate_result

SAMPLE_ASTM = """
H|\\^&|||Analyzer-X
P|1|PT-0001
O|1|SPEC-123
R|1|^^^GLU|5.4|mmol/L|3.9 to 6.1|N||F
R|2|^^^K|6.2|mmol/L|3.5 to 5.1|H||F
L|1|N
"""


def test_parse_message_reads_patient_and_results():
    msg = parse_message(SAMPLE_ASTM)
    assert msg["patient_id"] == "PT-0001"
    assert [r["test_code"] for r in msg["results"]] == ["GLU", "K"]
    assert msg["results"][0]["reference_range"] == (3.9, 6.1)


def test_parse_result_record_rejects_short_record():
    with pytest.raises(ASTMParseError):
        parse_result_record("R|1|^^^GLU|5.4")


def test_qc_rules_detect_1_3s_and_pass():
    assert qc_status([100, 101, 99], target_mean=100, target_sd=2) == "pass"
    rules = {v["rule"] for v in check_qc_run([100, 107], target_mean=100, target_sd=2)}
    assert "1-3s" in rules


def test_qc_rules_detect_2_2s():
    rules = {v["rule"] for v in check_qc_run([104.5, 104.6], target_mean=100, target_sd=2)}
    assert "2-2s" in rules


def test_validator_holds_on_qc_reject_and_releases_on_pass():
    result = parse_result_record("R|1|^^^K|6.2|mmol/L|3.5 to 5.1|H||F")
    decision, reasons = validate_result(dict(result), "reject")
    assert decision == HOLD and reasons
    decision, _ = validate_result(result, "pass")
    assert decision == RELEASE
    assert result["range_flag"] == "H"


def test_hl7_contains_only_released_results():
    result = parse_result_record("R|1|^^^GLU|5.4|mmol/L|3.9 to 6.1|N||F")
    validate_result(result, "pass")
    msg = build_oru_r01("MSG1", "20261029120000", "PT-0001", [result])
    segments = msg.split("\r")
    assert segments[0].startswith("MSH|")
    assert sum(s.startswith("OBX|") for s in segments) == 1


def test_audit_log_detects_tampering():
    log = AuditLog()
    log.record("release", "tech01", "GLU released", "2026-10-29T12:00:00")
    log.record("hold", "system", "K held: QC warning", "2026-10-29T12:01:00")
    assert log.verify_chain()
    log.entries[0]["detail"] = "edited after the fact"
    assert not log.verify_chain()
