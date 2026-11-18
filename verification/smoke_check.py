"""One-command check of the frozen A3 input and nominal decision."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from peoplecomfort.core import analyze

EXPECTED_SHA = "bc361fcd1a90f8c77f7e780289ab56f989b883e550ba6968464d771aa18f5210"


def main():
    project = json.loads((ROOT / "examples/extended-a3/project.json").read_text(encoding="utf-8"))
    result = analyze(project, False)
    actual = (result["input_sha256"], len(result["rows"]), result["selection"]["T3"]["winners"])
    expected = (EXPECTED_SHA, 91, ["D4"])
    if actual != expected:
        raise SystemExit(f"FAIL A3 smoke check: expected {expected}, got {actual}")
    print(f"PASS A3 input={EXPECTED_SHA} cells=91 winner=D4")


if __name__ == "__main__":
    main()
