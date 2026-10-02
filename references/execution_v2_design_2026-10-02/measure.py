#!/usr/bin/env python3
"""Representation sizing, not resolution, execution or a performance benchmark."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
inputs = json.loads((ROOT / "sizing-input.json").read_text())


def size(value):
    return len(json.dumps(value, separators=(",", ":")).encode())


def index_size(models, slots):
    # Fixed-size SHA-256 placeholder: these are not approved resolution digests.
    return size({"schema": "rx.execution-report-index.v2",
                 "entries": [[model, slot, "0" * 64]
                             for model in range(models) for slot in range(slots)]})


result = {
    "scope": "Exact index representation size; v1 payload extrapolation, not a dense resolve run",
    "dense_slots": 2400,
    "models": 2,
    "nodes": 8,
    "concrete_parameter_artifacts": 2 * 2400 * 8,
    "literal_parameter_ref_array_bytes": 2 + sum(
        row["parameter_ref_compact_bytes"] * 2400 for row in inputs.values())
        + 2 * 2400 * 8 - 1,
    "v1_parameter_payload_extrapolated_bytes": sum(
        row["parameter_bytes"] * 2400 for row in inputs.values()),
    "v1_report_payload_extrapolated_bytes": sum(
        row["report_compact_utf8_bytes"] * 2400 for row in inputs.values()),
    "report_index_bytes": index_size(2, 2400),
    "max_report_index_bytes": index_size(8, 2400),
    "unique_definition_digests_in_ab_receipts": len({
        digest for row in inputs.values() for digest in row["definition_digests"]}),
    "timing": "NOT_MEASURED; v2 resolver/qualification integration not implemented",
}
print(json.dumps(result, indent=2))
