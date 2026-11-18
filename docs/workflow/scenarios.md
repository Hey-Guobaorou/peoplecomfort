# 2. Define designs and compositions

## Input and operation

Each design supplies `id`, `name` and `seats` keyed by zone ID. Every design must supply exactly `total_people` seats and respect `max_seats`. In the example, D0 assigns 9/3 seats to cooler/warmer zones, D1 6/6, and D2 3/9. They are configurations of one schematic two-zone space, not three populations or measured plans.

Each scenario supplies `id`, `name`, `split` and a count for every profile. Counts are nonnegative integers summing to `total_people`. `development` scenarios determine T2/T3; `holdout` scenarios only assess frozen choices. `existing_design` and `baseline_scenario` identify the T1 and T2 references.

## Output and quality check

The validated project appears in `project.json`; each design/scenario pair appears in `comparison.csv`. Capacity and count errors cause an explicit failure. The supported scope is 2 zones, 2–4 profiles, 3–10 designs, 1–24 people and at most 100 scenarios. The tool applies a 5,000,000 candidate-evaluation guard to limit excessive enumeration.

## Design interpretation

Holding seat number, function and resource cost constant isolates a zone-capacity choice in the prototype. The equal-resource assumption is not a measured cost estimate. The interface shows seat counts, not geographic coordinates or clearance compliance. Access rules should come from the actual task and mobility context rather than demographic stereotypes.
