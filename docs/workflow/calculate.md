# 3. Calculate and allocate

## Input and operation

For each profile `i` and zone `z`, CBE gives PMV. With screening limit `tau`, the loss per person is `max(0, abs(PMV[i,z]) - tau)`. For every design/scenario pair, `allocate` enumerates integer profile counts placed in zone 1; remaining people go to zone 2. It checks both capacities and each profile's `allowed_zones`, then minimizes the mean person-weighted loss.

If equal mean losses occur, the allocator minimizes the largest profile mean loss and finally uses a deterministic assignment order. It reports the number of feasible allocations. If none exists, `feasible=false` and `loss=null`; no person is omitted or assigned zero loss by default.

## Output and quality check

`thermal_ledger.csv` records inputs and CBE outputs; `allocations.csv` records each profile count in each zone; `comparison.csv` gives feasibility, loss, regret, flagged users and worst-profile burden. Twelve test cases from the deployed CBE function check numerical integration. An independent per-person enumeration and a manual small example check the allocator. Shared CBE code ancestry means the numerical check is not independent physiological validation.

## Design interpretation

The assignment is the best *managed* matching under the supplied constraints. It is not a forecast of spontaneous choice, seat switching or willingness to move. The mean PMV exceedance is a screening score; it is not a measured dissatisfaction fraction or health outcome.
