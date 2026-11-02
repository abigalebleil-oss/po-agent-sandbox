"""Append-only, hash-chained audit log.

Each entry stores the hash of the previous entry, so editing or deleting any past
entry breaks the chain and is detectable by verify_chain().
"""

import hashlib
import json


class AuditLog:
    def __init__(self):
        self.entries = []

    def _hash(self, payload):
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def record(self, event, user, detail, timestamp):
        prev_hash = self.entries[-1]["hash"] if self.entries else "GENESIS"
        payload = {
            "event": event,
            "user": user,
            "detail": detail,
            "timestamp": timestamp,
            "prev_hash": prev_hash,
        }
        entry = dict(payload, hash=self._hash(payload))
        self.entries.append(entry)
        return entry

    def verify_chain(self):
        prev_hash = "GENESIS"
        for entry in self.entries:
            payload = {k: v for k, v in entry.items() if k != "hash"}
            if payload["prev_hash"] != prev_hash or self._hash(payload) != entry["hash"]:
                return False
            prev_hash = entry["hash"]
        return True
