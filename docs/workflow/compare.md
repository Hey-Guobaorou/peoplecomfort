# 4. Compare decisions

## Input and operation

`evaluate` computes loss `L(d,s)` for each design `d` and scenario `s`. Regret equals `L(d,s) - min(L(candidate,s))`, using only feasible candidates for that scenario. T1 retains `existing_design`. T2 selects the smallest loss in `baseline_scenario`. T3 selects the smallest maximum regret across all development scenarios. Exact design ties remain in the winner list. A design infeasible in any required selection scenario cannot win that rule.

## Output and quality check

`result.json` contains the three selections and all scores. The example gives T1=D0, T2=D2, T3=D1. The holdout maximum regrets are approximately D0=0.1052, D1=0.0552 and D2=0.1984. Selection uses development scenarios only; changing holdout counts cannot choose a new T2/T3 decision. Tests check this separation.

## Design interpretation

T3 controls the worst opportunity loss within the declared composition envelope, without claiming a probability distribution. An average score may hide a burden concentrated on one profile; inspect `worst_type_loss`, `type_loss` and flagged counts before making a design claim. The candidate set, objective and ideal allocation assumption affect the answer. A result for three constructed alternatives cannot establish that 6/6 is universally optimal.
