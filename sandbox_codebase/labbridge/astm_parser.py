"""Parse simplified ASTM E1394-style records sent by an analyzer.

Supported record types (first field):
    H  header      P  patient      O  order      R  result      L  terminator

Example result record:
    R|1|^^^GLU|5.4|mmol/L|3.9 to 6.1|N||F
    fields: type|seq|test id|value|units|reference range|abnormal flag||result status
"""

FIELD_DELIM = "|"
COMPONENT_DELIM = "^"


class ASTMParseError(ValueError):
    """Raised when a record cannot be parsed."""


def parse_test_code(test_field):
    """Extract the test code from a universal test ID like '^^^GLU'."""
    parts = test_field.split(COMPONENT_DELIM)
    code = parts[-1].strip() if parts else ""
    if not code:
        raise ASTMParseError(f"Missing test code in field: {test_field!r}")
    return code


def parse_reference_range(range_field):
    """Turn '3.9 to 6.1' into (3.9, 6.1). Returns None if the field is empty."""
    if not range_field.strip():
        return None
    low, sep, high = range_field.partition(" to ")
    if not sep:
        raise ASTMParseError(f"Unrecognized reference range: {range_field!r}")
    return float(low), float(high)


def parse_result_record(line):
    """Parse one 'R' record into a result dictionary."""
    fields = line.strip().split(FIELD_DELIM)
    if not fields or fields[0] != "R":
        raise ASTMParseError(f"Not a result record: {line!r}")
    if len(fields) < 9:
        raise ASTMParseError(f"Result record has too few fields: {line!r}")
    return {
        "sequence": int(fields[1]),
        "test_code": parse_test_code(fields[2]),
        "value": float(fields[3]),
        "units": fields[4],
        "reference_range": parse_reference_range(fields[5]),
        "instrument_flag": fields[6] or None,
        "status": fields[8],
    }


def parse_message(text):
    """Parse a full ASTM message. Returns {'patient_id': str|None, 'results': [..]}."""
    patient_id = None
    results = []
    for raw in text.strip().splitlines():
        line = raw.strip()
        if not line:
            continue
        record_type = line.split(FIELD_DELIM, 1)[0]
        if record_type == "P":
            fields = line.split(FIELD_DELIM)
            patient_id = fields[2] if len(fields) > 2 and fields[2] else None
        elif record_type == "R":
            results.append(parse_result_record(line))
        elif record_type in ("H", "O", "L"):
            continue
        else:
            raise ASTMParseError(f"Unknown record type {record_type!r}")
    return {"patient_id": patient_id, "results": results}
