# Interface audits and accessibility checks

Use this reference for requested interface audits, or when acceptance checks
involve accessibility or platform material changes. Keep driving, evidence,
assertion statuses, and cleanup with the main Verify procedure.

## Full interface audits

Treat a whole-surface visual, interaction-quality, or accessibility judgment as
an interface audit. Identify the requested dimensions and load only their
specialists: `ui-design` for visual systems and web behavior or accessibility,
`animate` for motion, and `swiftui` or `uikit` for native Apple behavior or
accessibility. Without a matching specialist, use project platform guidance and
the main observe-act-observe loop.

Inventory every surface, component, state, input method, and accessibility path
relevant to those dimensions. Turn every applicable specialist criterion into
an assertion; cover the full requested dimension rather than representative
samples. A feature map supplies useful paths but does not bound audit coverage.
When acceptance and an audit are both requested, apply their completeness rules
to their respective scopes.

An audit is complete only when every inventoried item and applicable specialist
criterion has a status under the main reporting rules. It passes only when all
required assertions pass.

## Accessibility and materials

When accessibility is in scope, check names, roles, values, states, label and
error relationships, task-ordered focus, keyboard traps, text scaling, and async
status announcements when focus stays put. For affected materials, check
increased contrast and reduced transparency where the platform exposes them.

For acceptance work, apply the relevant assertions to the selected workflows.
For an audit, cover them across the full inventory for the requested dimensions.

## Audit findings

Report each issue's location, observed behavior, exact proposed change, and
reason, ranked by user impact. Include the inventory's assertion statuses and
any blocked or untested coverage so audit completeness and passing remain
separate judgments.
