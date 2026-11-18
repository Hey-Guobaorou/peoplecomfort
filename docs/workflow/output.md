# 5. Stress-test and export

## Input and operation

The `uncertainty` object gives `temperature_offsets`, `gradient_offsets`, `clothing_offsets` and `thresholds`. Each list contains 1–5 finite values; their Cartesian product may contain at most 100 conditions. Common temperature shifts affect Ta and MRT in both zones; opposing shifts subtract from Z1 and add to Z2; clothing shifts change every profile's `clo`. Nominal selection remains frozen while the grid diagnoses sensitivity. Use `--no-uncertainty` to skip it.

The example's 3×3×3×3 grid has 81 conditions. D1 is selected in 39, D0 in 33 and D2 in 9. These are grid counts, not probabilities or confidence levels. Ranges are exploratory and were not calibrated from instruments or participant data.

## Output files

| File | Meaning |
|---|---|
| `project.json` | Exact validated input snapshot |
| `result.json` | Complete selection, rows, thermal ledger and stress records |
| `run_manifest.json` | Python, Node, platform, input hash and CBE provenance |
| `comparison.csv` | One row per design/composition pair |
| `thermal_ledger.csv` | Profile-zone conditions and CBE outputs |
| `allocations.csv` | Assigned counts by design, scenario, profile and zone |
| `uncertainty.json` | Joint grid and design-selection sensitivity |
| `comparison.svg` | Static comparison diagram |
| `report.html` | Offline summary of the run |

The browser's Export results ZIP contains these run outputs and a brief rerun note. The software source is distributed separately. `save(result, directory)` writes the same files from Python.

## Quality check and interpretation

Inspect `project.json` and the manifest before comparing runs. Check CSV counts, infeasible rows, thermal inputs near the PMV threshold and the allowed-zone constraints. The SVG and HTML summarize the run but do not replace the complete JSON or ledger. File-format and numerical checks do not establish field predictive validity. Real application requires environmental measurements, usable seat geometry, activity/clothing evidence, accessibility constraints and observed user response.
