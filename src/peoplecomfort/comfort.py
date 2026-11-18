"""Single adapter for CLI, UI and reports. Environmental v is corrected by CBE once."""
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess

VENDOR = Path(__file__).parent / "_cbe"
MODE = "CBE pmvElevatedAirspeed; self-generated air speed ON; wme=0"


def calculate(cases):
    bounds = {"ta":(15,32), "tr":(15,40), "v":(0,1), "rh":(10,90),
              "met":(1,2), "clo":(.2,1.5)}
    for x in cases:
        for key, (lo, hi) in bounds.items():
            value = x.get(key)
            if isinstance(value, bool) or not isinstance(value, (float,int)) or not math.isfinite(value) or not lo <= value <= hi:
                raise ValueError(f"{key}: value missing or outside prototype domain [{lo},{hi}]")
    node = os.environ.get("PEOPLECOMFORT_NODE") or shutil.which("node")
    if not node:
        raise RuntimeError("Node.js 18+ is required; install Node or set PEOPLECOMFORT_NODE")
    result = subprocess.run([node, str(VENDOR / "bridge.cjs")], input=json.dumps(cases),
                            capture_output=True, text=True, timeout=60, check=False)
    if result.returncode:
        raise RuntimeError("CBE engine failed: " + result.stderr[-1500:])
    outputs = json.loads(result.stdout)
    if len(outputs) != len(cases):
        raise RuntimeError("CBE result length mismatch")
    return outputs


def provenance():
    source = json.loads((VENDOR / "upstream.json").read_text())
    source.update(mode=MODE, hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in VENDOR.glob("*.js")})
    return source
