# Workflow guide

`peoplecomfort analyze` runs five stages in order. Each stage below states its inputs, transformation, outputs, quality check and design meaning. The Python functions are documented in the [API reference](api/index.html).

1. [Define the space and profiles](workflow/space.html)
2. [Define designs and compositions](workflow/scenarios.html)
3. [Calculate and allocate](workflow/calculate.html)
4. [Compare decisions](workflow/compare.html)
5. [Stress-test and export](workflow/output.html)

The whole calculation is deterministic for a fixed project, CBE source and runtime. The exported manifest records versions and hashes. Changing a supplied environmental condition changes every relevant profile-zone calculation; changing a composition changes allocation and selection but not the thermal ledger.
