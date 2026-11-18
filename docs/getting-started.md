# Quick start

## Install

Requirements: Python 3.11 or newer and Node.js 18 or newer. Extract the complete package, open a terminal in its root, and install locally:

```console
python -m pip install -e .
peoplecomfort --help
```

PeopleComfort is not published to PyPI. No account, API key or network connection is required after obtaining the complete package. Node must be on `PATH`; alternatively set `PEOPLECOMFORT_NODE` to its executable. Installation is optional if you use `python run.py` from the source root.

## Run the bundled example

```console
peoplecomfort analyze --project examples/minimal/project.json --out example-output
```

Inspect `example-output/report.html`, `comparison.csv`, `allocations.csv` and `run_manifest.json`. The example contains 3 designs and 9 population scenarios, producing 27 comparison cells and an 81-condition stress grid. A typical nominal selection is T1=D0, T2=D2 and T3=D1. These are conditional results for constructed inputs.

## Open the local workbench

```console
peoplecomfort serve --port 8765
```

Open `http://127.0.0.1:8765` in a browser. Import a project JSON or edit displayed values, run the comparison, then export the result ZIP. Stop the server with Ctrl+C. On Windows, `start.cmd` runs the source version from the package directory.

## Verify before interpreting

```console
python -m unittest discover -s tests -v
```

Check that composition counts equal `total_people`, designs use equal total seats, zone capacities and access rules are credible, and environmental inputs have documented sources. Tests verify software behaviour and numerical agreement for selected cases; they do not validate a real room or occupants. Follow the [workflow guide](workflows.html) for stage-by-stage inspection.

## Run the general framework

```console
peoplecomfort analyze --project examples/general/project.json --out general-output
peoplecomfort analyze --project examples/general-thermal/project.json --out thermal-output
```

The first example uses three zones and two direct 0–1 criteria. The second uses three thermal regions and a CBE PMV criterion; capacity means simultaneous users and does not presume seats. In the local workbench, open `/framework` to edit a schema-v2 project JSON. Read [the general framework](general-framework.html) before interpreting ratings or design rankings.
