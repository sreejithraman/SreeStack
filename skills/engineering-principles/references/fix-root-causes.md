# Fix Root Causes

Reproduce the actual symptom and test falsifiable causes before repairing it.
Inspect sibling callers for the same mechanism; repair at the owner within the
authorized scope. A guard is justified when it enforces the real contract, not
when it hides a failed invariant. Restart failures call for inspecting persisted
state and its recovery protocol. Use [diagnosing-bugs](../../diagnosing-bugs/SKILL.md)
for reproduction, instrumentation, repair, and regression proof.
