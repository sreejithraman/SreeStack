---
name: show-dont-tell
description: Reduce the explanations and reminders agents need from code and documentation. Use for clarity passes or during PR preparation.
---

# Show, Don't Tell

Make the thing carry its intent so agents need fewer explanations and reminders.
Improve what needs explaining before adding another explanation. Apply this to
the caller's scope while preserving intended behavior and contracts.

When inspecting explanations in code or docs, including comments and suppressions,
read the [explanation audit](references/explanation-audit.md).

## Make code self-documenting

Express purpose through domain names, types, interfaces, and ownership. Make
correct usage obvious and enforce invariants where practical. A comment saying
“call A before B” may point to an interface that should own that ordering.
Choose changes that reduce what agents must infer or remember; extra layers
and types must earn their place.

Apply the same principle to docs: keep one authoritative home for each rule.
Preserve instruction meaning, permissions, and necessary ordering.

Remove prose after its knowledge is carried elsewhere or verified obsolete.
When enforcement replaces a reminder, verify that it rejects a violation.
Fix a suppressed correctness problem before removing its directive.

## Record consequential decisions

Use an ADR when a decision meets all
[three criteria](../domain-modeling/SKILL.md#offer-adrs-sparingly): hard to reverse,
surprising without context, and the result of a real trade-off. Keep local
rationale near its subject when an ADR would add no value.

## Keep useful documentation

Keep prose that supplies necessary intent, constraints, rationale, or operating
context an agent cannot cheaply and reliably obtain elsewhere. Examples include
unencoded requirements or promises, external prerequisites, and recovery
decisions that require judgment. A document's category alone does not justify it.

Prefer scripts, command help, schemas, tests, and precise domain types over
prose restating that information. Use brief pointers to existing sources of truth
or context that would otherwise be costly to discover.

Keep remaining prose brief, accurate, and close to its use. Preserve legal
notices. Resolve conflicting claims against authoritative requirements; implementation alone
cannot redefine a contract. Retain unresolved constraints until verified.

Use the owning workflow's checks and review. Report what explanation became
unnecessary and what knowledge remains useful.
