# PeopleComfort

**An open, local framework for comparing spatial capacity under changing user needs.** PeopleComfort evaluates how alternative zone configurations serve different user mixes. A zone may be a thermal region, task area or another documented spatial opportunity. Capacity means simultaneous users; the method does not require seats or a floor-plan image.

The package separates three questions: what each design provides, which user–zone assignments are feasible, and how a fixed design performs across development and holdout scenarios. The evaluator supports direct normalized scores and a bundled CBE PMV calculation. It reports aggregate and profile-level burden, infeasible assignments, minimax loss and minimax regret. Inputs, source statements and outputs are exported for inspection.

**Status:** v0.2.0 research software. The A3 submission is frozen at tag `a3-submission`: its decision case is `examples/extended-a3/project.json`; the general schema v2 and browser workbench are extensions for future studies. The older `examples/minimal` is a pilot, not the revised A3 result. The included projects contain constructed inputs and are not field-validated design recommendations.

## Requirements and installation

- Python 3.11 or newer.
- Node.js 18 or newer for projects that use CBE PMV. Direct-score projects work through both the Python API and CLI without Node; the CLI records no Node version when it is absent. PMV analysis fails with a clear missing-Node error.
- No Python runtime dependencies or API key. The package is installed from a repository checkout; it is not on PyPI.

```console
python -m pip install -e .
peoplecomfort --help
```

Node must be on `PATH` for PMV mode, or specify `PEOPLECOMFORT_NODE`. From a checkout, `python run.py` runs the same CLI without installing.

## Browser demonstration

Open `docs/demo.html` to try the standalone thermal workbench. Its default A3 study contains two thermal zones, three activity/clothing profiles, seven capacity alternatives and thirteen compositions, including an eight-person occupancy check. The editor exposes every JSON value, including Ta, MRT, air speed, RH, met, clo, PMV threshold, capacities, sources and rules. It calculates PMV and PPD in the browser with the same pinned CBE JavaScript used by the Python package, then converts PMV to the declared exceedance loss and compares allocations. The input conditions are hypothetical until replaced by documented measurements or validated simulation. The full JSON panel supports import, editing and download.

Rebuild the standalone page after editing `examples/a3-thermal/project.json`, `docs/workbench.template.txt` or `docs/workbench.js` with `python docs/build_demo.py`, then run `python docs/build_docs.py` to update the embedded local-server documentation copy and bundled CBE files. The public workbench is also hosted at [hey-guobaorou.github.io/ARCH7476/peoplecomfort.html](https://hey-guobaorou.github.io/ARCH7476/peoplecomfort.html).

## Quick start

Run the three-zone, two-criterion example:

```console
peoplecomfort analyze --project examples/general/project.json --out example-output
```

Inspect `example-output/report.html`, `comparison.csv`, `allocations.csv`, `metric_scores.json` and `run_manifest.json`. To use thermal regions with CBE PMV and capacity expressed as simultaneous users:

```console
peoplecomfort analyze --project examples/general-thermal/project.json --out thermal-output
```

To open the local English workbench:

```console
peoplecomfort serve --port 8765
```

Open `http://127.0.0.1:8765/framework` for schema v2. The home page shows the original A3 example. The server binds to loopback only; stop it with Ctrl+C. On Windows, `start.cmd` launches the source checkout.

## Core concepts

| Input | Meaning |
|---|---|
| Zones | Named environmental or functional regions with maximum simultaneous capacity |
| Profiles | Explicit task, activity or access requirements; not demographic stereotypes |
| Designs | Alternative capacity distributions, and optional design-specific score matrices |
| Scenarios | User counts divided into development and holdout groups |
| Metrics | Lower-is-better 0–1 losses with declared sources and weights summing to one |
| Plan metadata | Optional source, kind and scale record; geometry is not computed |
| Partial occupancy | `allow_partial_occupancy=true` permits 1..`total_people` users while physical capacity stays fixed; mean loss uses occupied people |

For a given design and user mix, `allocation_rule=optimal` finds a minimum-loss complete assignment subject to capacity and allowed-zone constraints. `priority_first_fit` is a deterministic profile-order operating alternative. `capacity_policy=equal_total` controls total places across designs; `variable_total` permits different totals but does not price extra capacity. `decision_rule` chooses baseline, minimax regret or minimax loss while retaining all comparisons. Assignment rules are declared assumptions; observed seat or area choice may differ. Scores require evidence and a documented transformation from real measurements. The framework does not infer a valid score from a raw floor plan, temperature, dB or lux value.

## Documentation

The offline [documentation site](docs/index.html) follows Overview → Quick start → workflow stages → Python API → CLI reference. The [general evaluation framework](docs/general-framework.html) explains the research question, equations, evidence ladder, floor-plan boundary and known limitations. Markdown sources are beside the generated pages; rebuild the site with:

```console
python docs/build_docs.py
```

The revised [A3 report source](coursework/A3_research_report.md) and PDF are built from the seven-design comparison in `examples/extended-a3/project.json`. Run `python coursework/analyze_extended.py` to recreate the result JSON, matrix CSV and figures, then `python coursework/build_pdf.py` to render the PDF. `verification/independent_pmv_check.py` compares six nominal CBE cases with separately maintained `pythermalcomfort==4.8.1`; install that optional verification dependency with `python -m pip install -r verification/requirements.txt`.

## Reproducibility and tests

```console
python verification/smoke_check.py
python -m unittest discover -s tests -v
peoplecomfort analyze --project examples/extended-a3/project.json --out a3-output
```

The smoke check exits nonzero on a mismatch and prints one `PASS` line for the pinned A3 input, 91 comparisons and D4 selection. The committed `results/a3-submission/` contains the CLI export; `coursework/` contains the source report, PDF, matrix, summary and build scripts. `verification/` contains the independent PMV comparison, test log and AI audit log. To reproduce the frozen submission, run `git checkout a3-submission` and `git rev-parse 'a3-submission^{commit}'` to display the exact commit SHA.

The tests cover multi-zone allocation against an independent small-case oracle, access and capacity constraints, score validation, scenario separation, deterministic reruns and 12 numerical cases compared with the deployed CBE function. Shared CBE source ancestry makes that last check an integration test, not independent physical validation. Use environmental measurements, observed use and thermal votes before making field-effect claims.

## Licensing and citation

PeopleComfort is distributed under GPL-2.0 because it bundles CBE `comfort_tool` JavaScript under that license. The source commit and preserved notices are documented in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). CBE is the calculation reference, not an endorsement. [CITATION.cff](CITATION.cff) identifies the GitHub author handle and repository. A DOI and PyPI release have not been assigned.
