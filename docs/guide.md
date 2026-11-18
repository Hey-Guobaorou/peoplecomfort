# PeopleComfort

**Population scenarios for auditable seating decisions.** A local research prototype for ARCH7476 Assignment 03. All bundled environmental and population data are illustrative.

## Quick start

Install Python 3.11+ and Node.js 18+. Extract the complete source package and open a terminal in its root directory:

```console
python run.py serve
```

Open http://127.0.0.1:8765 . The server listens only on your computer. Stop with Ctrl+C. Use `--port 8766` if the default port is busy. The core has no third-party Python dependencies, does not require an API key and runs offline.

```console
python run.py analyze --project examples/minimal/project.json --out results
python -m unittest discover -s tests -v
```

Optionally install the local package with `python -m pip install .`, then use `peoplecomfort serve` or `peoplecomfort analyze`. Node must remain available. Set `PEOPLECOMFORT_NODE` to its executable path if it is not on PATH. This is a repository-installable package, not a published PyPI release.

## Workflow 1: define the space

The current engine supports exactly two zones, 2-4 profiles, 3-10 designs and 1-24 people. Each zone has a capacity and externally supplied air temperature, mean radiant temperature, relative humidity and environmental air speed. Enter temperatures separately. Do not add activity-generated air speed yourself: the CBE function applies the correction once.

The schematic is not a measured floor plan. Seat capacity, access, equipment and circulation need project-specific checking. Coordinates do not generate thermal conditions. Moving seats is assumed not to materially alter the supplied environment; if this fails, supply updated environmental evidence before interpreting a layout change.

## Workflow 2: define profiles and populations

Profiles describe activity and clothing rather than validated individual preferences. No age, sex or birthplace coefficient is used. Allowed zones can express documented task/equipment/access restrictions; they do not perform a geometric accessibility audit.

Composition counts must be nonnegative integers, cover every profile and sum to the fixed total population. Development scenarios select designs; holdout scenarios assess frozen selections. A constructed composition grid has no implied occurrence probability.

## Workflow 3: define designs

Every design provides the same total seats and respects each zone's capacity. The example compares 9/3, 6/6 and 3/9 seat distributions. Seats have identical functionality and assumed equal resources. These are controlled assumptions, not measured cost estimates or verified furniture layouts.

For each design and composition, the same allocator finds a minimum-loss feasible assignment. It represents ideal managed matching with known inputs. It does not predict spontaneous choices, negotiation or behavioural compliance.

## Workflow 4: calculate and compare

For profile i and zone z, exceedance is e(i,z)=max(0,abs(PMV(i,z))-tau). The objective is the person-weighted mean exceedance. Cold and warm deviations cannot cancel. The result is a model-distance score, not discomfort intensity, a health metric or an individual dissatisfaction probability.

The two-zone algorithm enumerates integer profile counts in zone 1; remainders go to zone 2. Capacity and allowed-zone constraints are enforced. Ties in mean loss are broken by the worst profile's mean loss, then a deterministic allocation ordering. Tied design recommendations are retained.

T1 retains the configured existing design. T2 minimizes loss in the baseline development composition. T3 minimizes maximum regret across development compositions, where regret is a design's loss minus that composition's best feasible candidate loss. If no design is jointly feasible, the result remains unresolved.

## Workflow 5: stress-test and export

The joint grid varies common temperature offset, opposing zone shifts, common clothing offset and screening threshold. Air and radiant temperatures shift together. These are declared correlated perturbations, not calibrated error distributions. Counts of winning designs are not probabilities. Behaviour, activity uncertainty, costs and occupancy-to-environment feedback remain outside the grid.

Exported results include the complete input, row-level thermal calculations, allocations, summary CSV, uncertainty results, an SVG figure, an offline HTML report and a run manifest. The interface export contains one run, not the software source; the full source package is supplied separately.

## Input schema

| Object | Required fields | Interpretation |
|---|---|---|
| Project | schema_version, title, total_people, pmv_limit, existing_design, baseline_scenario | Schema version 1; project screening rule |
| zones | id, name, ta, tr, rh, v, max_seats, source, evidence_status | Degrees C, RH percent, m/s; explicit provenance |
| profiles | id, name, met, clo, allowed_zones, source | Activity/clothing and admissible regions |
| designs | id, name, seats | Seat counts keyed by zone ID |
| scenarios | id, name, split, counts | development or holdout; counts keyed by profile ID |
| uncertainty | temperature_offsets, gradient_offsets, clothing_offsets, thresholds, source | Cartesian grid and its evidence status |

Missing numeric input, inconsistent totals, excessive capacity, unknown IDs and excessive enumeration work produce errors. Infeasible assignments are recorded as infeasible, not zero loss. No unassigned person disappears from a denominator.

## Python API

```python
from peoplecomfort.core import analyze
from peoplecomfort.exports import save
result = analyze(project_dict, uncertainty=True)
save(result, "results")
```

- `validate(project)`: schema, provenance, counts, capacity, scenario roles and enumeration budget.
- `calculate(cases)`: six-factor inputs passed to the vendored CBE engine through Node.
- `allocate(counts, capacities, pmvs, limit, allowed)`: exact two-zone integer allocation.
- `analyze(project, uncertainty=True)`: complete workflow, without mutating the input.
- `save(result, target)`: JSON, CSV, SVG and HTML export.

## CLI reference

`analyze --project PATH --out DIRECTORY [--no-uncertainty]` runs a project. The bundled example is used if project is omitted. `serve --port 8765` starts the loopback interface. Both use the same core, input schema and calculation conventions.

## Calculation conventions and verification

CBE comfort_tool commit e809c965dd6eb2e785bf4851de2149c7a1d3c299 is vendored unchanged. The adapter calls `pmvElevatedAirspeed`, enables self-generated air speed, sets external work to zero and leaves dynamic clothing and cooling-effect treatment to that function. Raw and effective inputs are retained.

Twelve reference cases were collected from the publicly deployed CBE calculation function on 2026-11-18. They check adapter and version agreement, not independent physiological validity. Individual-enumeration tests and manual cases separately check the allocation logic. The application does not declare complete standards compliance.

Re-running the bundled project reproduces result.json and comparison.svg byte for byte on the tested environment. The manifest records Python/Node versions, engine commit and hashes, and the canonical input hash. Full A3 findings, limitations and failure records accompany the source package.

## Sources and licensing

- [CBE PMV documentation](https://cbe-berkeley.gitbook.io/thermal-comfort-tool/documentation/pmv)
- [CBE source repository](https://github.com/CenterForTheBuiltEnvironment/comfort_tool)
- [samy-wgen documentation reference](https://forge-lab-hku.github.io/samy-wgen/)
- [thermBAL interface reference](https://caadfutures2025.hku.hk/thermBAL/simulator.html?import=staged)

The distribution uses GPL-2.0 and preserves CBE copyright and license notices. No thermBAL or samy-wgen source was copied. Reference to these projects does not imply endorsement.
