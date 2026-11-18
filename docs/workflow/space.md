# 1. Define the space and profiles

## Input

Provide exactly two zones with `id`, `name`, air temperature `ta` in °C, mean radiant temperature `tr` in °C, relative humidity `rh` in percent, environmental air speed `v` in m/s, `max_seats`, `source` and `evidence_status`. Profiles provide `id`, `name`, metabolic rate `met`, clothing insulation `clo`, `allowed_zones` and `source`. Refer to [the bundled JSON](../../examples/minimal/project.json) for the complete schema.

## Operation and output

`validate(project)` checks structure and provenance. `calculate(cases)` evaluates each profile-zone six-factor condition with the pinned CBE function. The nominal calculation creates six profile-zone records in `thermal_ledger.csv`. Air speed supplied here is environmental speed; the CBE routine applies activity-related speed and clothing adjustments once.

## Quality check

The prototype accepts `ta` 15–32°C, `tr` 15–40°C, `v` 0–1m/s, `rh` 10–90%, `met` 1–2 and `clo` 0.2–1.5. Values outside these software bounds fail. Bounds are prototype restrictions, not a statement of complete PMV or standards applicability. Check measurement position, period and provenance; this package cannot infer a thermal field from plan geometry.

## Design interpretation

The two zones provide contrasting environmental opportunities. A profile describes activity and clothing assumptions, not an observed preference or a demographic group. Seat movement is assumed not to change the supplied zone environment. Verify that assumption in a real case.
