# PeopleComfort

**An open, local framework for comparing spatial capacity under changing user needs.** PeopleComfort evaluates how alternative zone configurations serve different user mixes. A zone may be a thermal region, task area or another documented spatial opportunity. Capacity means simultaneous users; the method does not require seats or a floor-plan image.

The package separates three questions: what each design provides, which user–zone assignments are feasible, and how a fixed design performs across development and holdout scenarios. The evaluator supports direct normalized scores and a bundled CBE PMV calculation. It reports aggregate and profile-level burden, infeasible assignments, minimax loss and minimax regret. Inputs, source statements and outputs are exported for inspection.

**Status:** v0.2.0 research software. The included projects contain constructed inputs and are not field-validated design recommendations. The original ARCH7476 A3 two-zone example remains supported as schema v1; new projects should use schema v2.

## Requirements and installation

- Python 3.11 or newer.
- Node.js 18 or newer for projects that use CBE PMV. Direct-score projects can run without Node when using `framework.analyze`, although the CLI export currently probes Node only when installed.
- No Python runtime dependencies or API key. The package is installed from a repository checkout; it is not on PyPI.

```console
python -m pip install -e .
peoplecomfort --help
```

Node must be on `PATH` for PMV mode, or specify `PEOPLECOMFORT_NODE`. From a checkout, `python run.py` runs the same CLI without installing.

## Browser demonstration

Open `docs/demo.html` to try a standalone interactive example. It lets visitors change the development user mix, criterion weights and a fourth custom zone-capacity design. The page uses constructed direct scores and runs without a Python server. For GitHub Pages, configure **Settings → Pages → Deploy from a branch → main /docs** after pushing the repository. The resulting page will be `https://hey-guobaorou.github.io/peoplecomfort/demo.html` once Pages deployment succeeds.

Rebuild the standalone page after editing `examples/general/project.json` or `docs/demo.js` with `python docs/build_demo.py`, then run `python docs/build_docs.py` to update the embedded local-server documentation copy.

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

For a given design and user mix, the program finds a minimum-loss complete assignment subject to capacity and allowed-zone constraints. That assignment assumes managed placement; observed seat or area choice may differ. Scores require evidence and a documented transformation from real measurements. The framework does not infer a valid score from a raw floor plan, temperature, dB or lux value.

## Documentation

The offline [documentation site](docs/index.html) follows Overview → Quick start → workflow stages → Python API → CLI reference. The [general evaluation framework](docs/general-framework.html) explains the research question, equations, evidence ladder, floor-plan boundary and known limitations. Markdown sources are beside the generated pages; rebuild the site with:

```console
python docs/build_docs.py
```

## Reproducibility and tests

```console
python -m unittest discover -s tests -v
peoplecomfort analyze --project examples/minimal/project.json --out a3-output
```

The tests cover multi-zone allocation against an independent small-case oracle, access and capacity constraints, score validation, scenario separation, deterministic reruns and 12 numerical cases compared with the deployed CBE function. Shared CBE source ancestry makes that last check an integration test, not independent physical validation. Use environmental measurements, observed use and thermal votes before making field-effect claims.

## Licensing and citation

PeopleComfort is distributed under GPL-2.0 because it bundles CBE `comfort_tool` JavaScript under that license. The source commit and preserved notices are documented in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). CBE is the calculation reference, not an endorsement. [CITATION.cff](CITATION.cff) supplies project-level citation metadata without attributing a personal identity or claiming a DOI; repository maintainers can replace the collective project name with verified author credits before scholarly release.

No GitHub repository, DOI or PyPI release is claimed by this source tree.
