# Sequence work into verifiable units

Order dependent work into coherent increments with a check at each boundary.
Establish the baseline, make one meaningful change, inspect the result, then
build on it. Choose boundaries that localize failures and fit the workflow;
one unit may include a failing reproduction and its repair. A tool can make the
checks cheap without turning every file into a separate delivery unit.

Order reviewable delivery so the evidence explains the change: baseline before
treatment, subtraction before reshape, foundations before dependents. Use
[gh-stack](../../gh-stack/SKILL.md) when stacked delivery is requested. Its layer
checks and repository CI requirements govern what can land independently.
