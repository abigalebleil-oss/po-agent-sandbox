"""Build a simplified HL7 v2.5 ORU^R01 (observation result) message for the LIS."""

SEGMENT_SEP = "\r"


def build_msh(message_id, timestamp):
    return f"MSH|^~\\&|LABBRIDGE|LAB|LIS|HOSPITAL|{timestamp}||ORU^R01|{message_id}|P|2.5"


def build_pid(patient_id):
    return f"PID|1||{patient_id}"


def build_obx(set_id, result):
    low_high = ""
    if result.get("reference_range"):
        low, high = result["reference_range"]
        low_high = f"{low}-{high}"
    flag = result.get("range_flag") or ""
    return (
        f"OBX|{set_id}|NM|{result['test_code']}||{result['value']}|"
        f"{result['units']}|{low_high}|{flag}|||F"
    )


def build_oru_r01(message_id, timestamp, patient_id, released_results):
    """Only released results should be passed in; held results never leave LabBridge."""
    segments = [build_msh(message_id, timestamp), build_pid(patient_id), "OBR|1"]
    for i, result in enumerate(released_results, start=1):
        segments.append(build_obx(i, result))
    return SEGMENT_SEP.join(segments)
