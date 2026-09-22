#!/usr/bin/env python3
"""Run the unique Python check embedded in each handover analysis document."""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = (
    "21_declaration_reuse_measurement.md",
    "22_open_items_boundary.md",
    "23_handover_counterexamples.md",
)

for name in DOCUMENTS:
    document = ROOT / "docs" / name
    text = document.read_text(encoding="utf-8")
    openings = re.findall(r"^```python[^\S\n]*$", text, re.MULTILINE)
    blocks = re.findall(
        r"^```python[^\S\n]*\n(.*?)^```[^\S\n]*$",
        text, re.MULTILINE | re.DOTALL,
    )
    if len(openings) != 1 or len(blocks) != 1:
        raise SystemExit(f"{name}: expected exactly one complete Python fence")
    print(f"Checking docs/{name}", flush=True)
    # The document remains the only source; separate interpreters isolate globals.
    result = subprocess.run([sys.executable, "-c", blocks[0]], cwd=ROOT)
    if result.returncode:
        raise SystemExit(f"{name}: embedded check failed (exit {result.returncode})")
