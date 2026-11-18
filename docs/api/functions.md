# Python functions

## `analyze(project, uncertainty=True)`

`project` is a dictionary with the [bundled project schema](../../examples/minimal/project.json). `uncertainty` is a boolean; when false, no stress grid is evaluated. The function validates and deep-copies input and returns a dictionary with `project`, `rows`, `thermal_ledger`, `selection`, `uncertainty`, engine provenance and SHA-256 input hash. It raises `ValueError` for invalid inputs or `RuntimeError` if Node/CBE execution fails.

```python
import json
from pathlib import Path
from peoplecomfort.core import analyze
from peoplecomfort.exports import save
project = json.loads(Path("examples/minimal/project.json").read_text(encoding="utf-8"))
result = analyze(project, uncertainty=True)
print(result["selection"]["T3"]["winners"])
save(result, "example-output")
```

## `validate(project)` and `calculate(cases)`

`validate` returns the validated project dictionary or raises `ValueError`/`KeyError`; it does not infer missing evidence. `calculate` takes a list of dictionaries with numerical `ta`, `tr`, `v`, `rh`, `met`, `clo`. It returns a same-length list of CBE output dictionaries. Its bounds are documented in [stage 1](../workflow/space.html). Do not add activity-generated air speed a second time.

## `allocate(counts, capacities, pmvs, limit, allowed)`

`counts` is a list of profile counts; `capacities` has two integer zone capacities; `pmvs[i][z]` is the thermal score of profile `i` in zone `z`; `limit` is the positive screening threshold; `allowed[i][z]` is a boolean. The result contains `feasible`, `loss`, `allocation`, flagged count, worst-profile loss, type losses and feasible-allocation count when feasible. Infeasible output contains a reason and null loss. This function assumes validated numerical inputs when used directly.

## `evaluate(project, matrix, limit)` and `select(rows, scenario_ids, design_ids, metric="regret")`

`evaluate` calculates every design/scenario row from a profile × zone PMV matrix and returns rows including regret. `select` takes those rows and ID lists, then returns `winners` and per-design maximum `scores` for the requested metric. `metric="loss"` selects the minimum worst loss over selected scenarios; the full workflow uses it for the single baseline. If no candidate is feasible throughout required scenarios, `winners` is empty.

## `save(result, target)`

Writes a directory of nine run files described in [stage 5](../workflow/output.html). It does not return a path. Existing files with matching names are overwritten. `peoplecomfort.exports.archive(result)` produces the same run outputs as ZIP bytes for the browser export.
