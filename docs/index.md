# PeopleComfort

Shared interiors can contain different thermal conditions while their future user composition is uncertain. PeopleComfort compares fixed seating-capacity configurations across explicit user mixes. It evaluates each configuration with a pinned CBE PMV implementation, exact feasible assignment and minimax regret. The tool is an illustrative research prototype; bundled conditions are constructed, not observed.

The software separates the physical decision (how many seats each zone receives) from the operating assumption (how people are assigned after their mix is known). It provides full input and result ledgers so a ranking can be inspected and rerun. The package is installed from a local repository checkout and is not on PyPI.

## Workflow

1. [Define the space and profiles](workflow/space.html) — specify two thermal zones, activities, clothing and access.
2. [Define designs and compositions](workflow/scenarios.html) — hold total seats constant and distinguish development from holdout mixes.
3. [Calculate and allocate](workflow/calculate.html) — run CBE calculations and exact constrained matching.
4. [Compare decisions](workflow/compare.html) — compare existing, baseline and robust choices.
5. [Stress-test and export](workflow/output.html) — inspect uncertainty, files and limitations.

For the expanded method, read the [General evaluation framework](general-framework.html). Start with [Quick start](getting-started.html), then see the [workflow guide](workflows.html), [Python API](api/index.html) or [CLI reference](cli/index.html).

## Citation and provenance

The CBE comfort_tool implementation is bundled at commit `e809c965dd6eb2e785bf4851de2149c7a1d3c299` under GPL-2.0. Cite CBE separately for the underlying comfort calculation. PeopleComfort v0.2.0 is an ARCH7476 A3 prototype; see `CITATION.cff` for package metadata and `THIRD_PARTY_NOTICES.md` for source attribution. The present release has no DOI or remote repository.
