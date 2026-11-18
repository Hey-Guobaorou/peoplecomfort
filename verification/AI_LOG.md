# AI-assisted work and verification log

The engine, browser page, analysis script and report were drafted with AI assistance. Numerical claims were checked against rerunnable program output; citations and scientific limits were reviewed separately. This log records claims that changed after checking, rather than treating generated prose as evidence.

| Claim or output | Check | Decision |
|---|---|---|
| 6/6 is the robust design | Enumerate all seven feasible splits in the fixed 12-place case | Reject; 7/5 is nominal minimax winner, with 6/6 in the 0.01 near-optimal set |
| The PMV adapter agrees with the reference | Compare six nominal cases with pythermalcomfort 4.8.1 and inspect CBE input fields | Accept as numerical cross-implementation check; no field-validity claim |
| The 33.3% figure justifies changing capacity | Inspect holdout maxima, mean regrets, ten pairwise comparisons and 81 stress conditions | Reject as a field recommendation; retain D0 pending evidence |
| The action thresholds were frozen before holdout | Search for dated preregistration or prior commit | Reject; mark 20%, 0.01 and 75% exploratory/post hoc |
| The temperature pair represents a real room | Inspect input source fields and cited literature | Pending; exact 23.5/27.5 C pair is constructed |

Run `python verification/smoke_check.py`, `python coursework/analyze_extended.py` and `python verification/independent_pmv_check.py` from the repository root to inspect the underlying claims. The last command needs `verification/requirements.txt` installed.
