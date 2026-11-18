# Python API reference

The public functions below follow the stages of the [workflow guide](../workflows.html). The listed signatures match v0.2.0 source. Import from an installed package or from the repository's `src` directory. Node.js remains required for comfort calculations.

| Function | Task |
|---|---|
| `peoplecomfort.core.validate(project)` | Check schema and scenario constraints |
| `peoplecomfort.comfort.calculate(cases)` | Evaluate CBE PMV for six-factor cases |
| `peoplecomfort.core.allocate(counts, capacities, pmvs, limit, allowed)` | Find best exact two-zone matching |
| `peoplecomfort.core.evaluate(project, matrix, limit)` | Score all designs × scenarios |
| `peoplecomfort.core.select(rows, scenario_ids, design_ids, metric="regret")` | Choose minimum of maximum selected metric |
| `peoplecomfort.core.analyze(project, uncertainty=True)` | Run full workflow without mutating input |
| `peoplecomfort.exports.save(result, target)` | Write JSON/CSV/SVG/HTML |

See [function details](functions.html) for parameters, return values and a runnable example. Lower-level helpers and the JavaScript bridge are implementation details.

## General schema-v2 API

Use `peoplecomfort.framework.validate(project)` and `peoplecomfort.framework.analyze(project, uncertainty=True)` for a multi-zone project. `peoplecomfort.framework_exports.save(result, target)` writes the v2 run outputs. See [the general framework](../general-framework.html) for data contracts, score normalization, plan metadata and limits. The legacy functions above remain for schema-v1 A3 projects.
