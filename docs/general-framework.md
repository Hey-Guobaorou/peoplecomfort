# General spatial evaluation framework

## Research question

How can designers compare capacity and environmental configurations of shared space when the future mix of users, tasks and environmental conditions is uncertain? The decision is made before a composition is known; assignment of users to zones may occur later. A zone may be a thermal region, acoustic region, activity area or other evidence-backed environmental opportunity. A seat is only one possible unit of capacity. The package currently assumes one capacity unit per person and discrete, simultaneous occupancy.

The proposed research gap is methodological and conditional: make the link from **physical configuration** to **feasible use under heterogeneous demand** explicit, inspectable and sensitive to uncertainty. It is not a claim that thermal seat matching is novel. [Spacematch](https://arxiv.org/abs/2006.09570) demonstrates real-time preference-informed workspace matching, while [CBE field work](https://escholarship.org/uc/item/9vv4z3gg) documents differences in local conditions and preferences. [Personal comfort model studies](https://escholarship.org/uc/item/9xd5q2sf) show the data burden and potential value of individual calibration. [Seat-change and HVAC research](https://publications.ibpsa.org/conference/paper/?id=asim2024_1308) addresses operating control. PeopleComfort instead compares a frozen spatial configuration across future mixes using declared criteria and constraints. This positioning requires a broader systematic review before any priority claim.

## Conceptual structure

| Layer | Required information | Current schema-v2 implementation | Evidence needed for real use |
|---|---|---|---|
| Spatial units | Zone IDs, names, maximum capacity | 2–8 zones | Measured or justified boundaries and usable capacity |
| Users and tasks | Profile types, counts, accessible zones | 1–8 profiles; scenario counts | Observed tasks, access needs, participation |
| Environment and suitability | Loss for each profile × zone × metric | Direct 0–1 loss tables or CBE PMV; optional per-design score tables | Measurements and empirical calibration |
| Design alternatives | Places per zone; optional changed score fields | 3–20 alternatives; equal or variable total capacity | Buildable plans, resource accounting and comparable costs |
| Allocation | Full assignment subject to capacity/access | Exact minimum-cost flow or declared priority first-fit | Observed choice, mobility and operating rules |
| Decision rule | Single mix or multiple future mixes | Existing, baseline, minimax loss, minimax regret | Predeclared objectives and governance |
| Verification | Test and sensitivity cases | Holdout compositions, explicit score worlds, unit tests | Independent field outcomes and external sites |

**Floor plan:** The engine does not require an image or CAD plan to compare zone-level capacities. The optional `plan` field stores `kind`, `source`, and `scale` metadata if measured. It is provenance only; it does not compute area, path length, accessibility or environmental fields. A spatial claim about specific seat coordinates, walking distance, thermal boundaries or code compliance therefore needs a separate geometric workflow. If geometry changes environmental conditions, provide design-specific scores; reusing nominal zone ratings would be invalid.

## Evaluation model

Let `a[d,z]` be the capacity offered by design `d` in zone `z`, `n[s,i]` the number of profile `i` users in scenario `s`, and `x[d,s,i,z]` the assigned count. The constraints are `sum_z x=n`, `sum_i x<=a`, nonnegative integer `x`, and zero allocation to forbidden zones. `capacity_policy=equal_total` requires every design to offer exactly `total_people` places; `variable_total` allows different totals and marks insufficient or otherwise unassignable designs infeasible. A variable-capacity comparison must separately account for construction, floor area and operating cost because the current loss objective does not price additional capacity. `loss[m,i,z]` is a **declared lower-is-better score in [0,1]** for metric `m`. Metric weights are nonnegative and sum to one. The combined cell loss is `sum_m weight[m] * loss[m,i,z]`; design/scenario mean loss is `sum_i,z x*combined / total_people`.

A direct score table can represent task suitability, measured acoustic exposure transformed by a documented rule, or a calibrated personal preference model. The framework does not infer a 0–1 conversion from raw lux, dB, temperature or distance. Researchers must document direction, acceptable range, scaling and source. PMV mode calculates CBE PMV then uses `min(1,max(0,abs(PMV)-threshold))`; this is a transparent screening transform, not an observed dissatisfaction probability. The cap prevents one criterion from numerically dominating solely because it has a wider unbounded scale. Both threshold and cap remain value choices. Weights are tradeoff assumptions, not estimated causal effects.

For each design/scenario, `allocation_rule=optimal` uses integer minimum-cost flow to find the lowest combined loss under the declared constraints. `priority_first_fit` places profiles in their listed order, each into its lowest-loss allowed zone with remaining capacity. This deterministic operating rule may fail even when a feasible global assignment exists; it is not a behavioural prediction. Optional `max_individual_loss` removes profile-zone edges above a common ceiling; this is a *per-placement* safeguard, not a guarantee of equal group outcomes. Result rows also show each group's mean burden and the worst group. Fairness can be checked, but an aggregate minimum is not inherently fair. If no complete assignment exists under the declared rule, the row is infeasible and has null loss.

Regret is design loss minus the best feasible candidate loss within that scenario. `baseline` minimizes loss in one named development mix. `minimax_regret` minimizes maximum regret across development mixes; `minimax_loss` minimizes worst absolute loss. `decision_rule` makes one of these the explicitly selected result while retaining all three comparisons. Holdout compositions are excluded from selection. `existing` preserves the status quo ID without implying it is optimal. There is no occurrence probability unless an external study supplies one. The score-world extension reevaluates alternate complete score matrices; those worlds diagnose sensitivity and are not a statistical distribution. Design-specific score fields and world fields cannot be combined in v2.0.

## Three demonstration levels

1. **Thermal-zone capacity:** use `cbe_pmv` for activity/clothing profiles and measured zone conditions. Capacity may be standing places, work positions or seats. With no floor plan, conclusions are at zone level.
2. **Multi-criterion shared space:** use the bundled three-zone example with 0–1 task and environmental suitability losses. It demonstrates the data contract and two weighted criteria. Its ratings are constructed, not empirical.
3. **Changed environmental design:** include `design_scores` to supply a complete score matrix for every candidate when boundaries, controls or layouts change environmental opportunities. The provenance field `design_scores_source` is mandatory. For PMV-derived scores, run and document the external per-design calculation before supplying the matrix; this mode does not internally recalculate different CBE zone environments for each design.

## Validation ladder

**Software validity:** unit tests compare a small multi-zone allocation with independent person-level enumeration, check access and ceiling constraints, deterministic reruns, scenario split isolation, and invalid-score rejection. The legacy A3 path additionally checks 12 cases against the deployed CBE function; shared source ancestry limits that to numerical integration.

**Construct validity:** compare declared 0–1 scores, profile definitions and weights with independent observations or stakeholder judgements. Survey actual seating, task suitability, acceptability and constraints. A PMV-derived score alone cannot establish individual thermal preference; [CBE personal comfort research](https://escholarship.org/uc/item/54n6b7m3) gives reason to test that limitation.

**Decision validity:** freeze candidate designs and evaluation rules, test on holdout mixes and other periods/sites, compare predicted and observed assignments, and report group-level harms alongside aggregate improvements. Recompute environmental scores when a design changes the environmental field. Distinguish model selection, implementation feasibility and post-occupancy outcomes.

## Known limits and next experiments

The current solver treats people within a profile as interchangeable, allocates once for simultaneous occupancy and assumes an operator can implement the computed assignment. There is no spontaneous-choice model, temporal switching cost, geometry engine, energy simulation, probabilistic forecasting or direct fairness optimization. The next empirical study should measure at least one real multi-zone environment, observe profile-specific use and acceptability, compare optimized and actual assignments, and evaluate whether alternative metric weights or access constraints reverse the selected design. A separate geometry module should test spatial boundaries and paths before claiming plan-level feasibility.

## Reproduce the general example

```console
python run.py analyze --project examples/general/project.json --out general-output
python -m unittest discover -s tests -v
python run.py serve
```

Open `http://127.0.0.1:8765/framework` for the English JSON workbench. The example contains three zones, three user/task profiles, three capacity alternatives, five compositions and two direct criteria. A separate `examples/general-thermal/project.json` uses three thermal regions with CBE PMV and capacity measured as simultaneous users rather than seats. Results include complete JSON, comparison CSV, allocation CSV, metric scores, a manifest and HTML summary. The original A3 two-zone example remains available at `/`.
