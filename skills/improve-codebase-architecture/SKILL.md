---
name: improve-codebase-architecture
description: Find structural improvements, compare designs, and produce evidence-backed architecture recommendations or migration plans. HTML reports are optional.
disable-model-invocation: true
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities**—refactors
that turn shallow modules into deep ones for testability and AI-navigability.
Start from a named area, pain point, or recent codebase hot spots. Leave
evidence-backed recommendations in chat (an HTML report only when requested) and,
for a design or migration request, a checked plan. You are done when worthwhile
candidates have evidence, reasons, and confidence—and any requested design or
migration plan has checked technical uncertainties (or explicit gaps) and
concrete migration and verification steps.

Resolve glossary paths with
[glossary paths](../domain-modeling/references/glossary-paths.md) before reading
or writing domain vocabulary (`GLOSSARY.md` names good seams; ADRs in `docs/adr/`
record settled decisions). Use
[Codebase Design](../codebase-design/SKILL.md)'s exact vocabulary (**module**,
**interface**, **depth**, **seam**, **adapter**, **leverage**, **locality**)
without drifting into "component," "service," "API," or "boundary," along with
the deletion test, "the interface is the test surface," and "one adapter =
hypothetical seam, two = real."

Own structural improvement; [Correct](../correct/SKILL.md) owns mining repeated
agent mistakes and proving their prevention (use its findings as input when
addressing an evidenced failure class). Apply
[Redesign From First Principles](../engineering-principles/references/redesign-from-first-principles.md)
when shaping candidates,
[Model the Domain](../engineering-principles/references/model-the-domain.md)
when ownership or event order governs correctness, and
[Migrate Callers Then Delete Legacy APIs](../engineering-principles/references/migrate-callers-then-delete-legacy-apis.md)
when moving callers.

## Choose the finish line

Default to interactive exploration: present candidates, let the user pick one,
then explore its design together. For a requested autonomous investigation or
experiment-backed plan, carry strong candidates through design and technical
checks before returning the recommendation; resolve routine technical questions
from code and experiments, asking only for product, access, or scope decisions
that materially change the result. Both paths return recommendations; a planning
request never authorizes production refactoring.

## 1. Explore

**Scope before scanning (YAGNI):** if the user named a module, subsystem, or pain
point, use it; otherwise inspect recent commit history (`git log --oneline`) to
prioritize actively changing hot spots before widening the net. Read `GLOSSARY.md`
and relevant ADRs first.

Assign a read-only exploration through [Orchestration](../orchestration/SKILL.md)
with the scope, domain vocabulary, ADRs, and an evidence-backed findings report
as its completion check. Direct the child to apply
[preventing recurring mistakes](../codebase-design/references/preventing-mistakes.md),
[architecture signals](../codebase-design/references/architecture-signals.md),
and the **deletion test** (would deleting a shallow module concentrate
complexity or merely relocate it?) across these friction questions:

- Where does understanding one concept require bouncing across many small modules?
- Where are modules **shallow** (interface nearly as complex as implementation)?
- Where were pure functions extracted for testability while real bugs hide in
  caller wiring (no **locality**)?
- Where do tightly coupled modules leak across seams?
- Which parts are untested or hard to test through their current interface?

Require caller traces, constructible states, and maintenance history—never layout
or size preferences alone. Accept the findings against the assigned scope and
evidence before recommending changes.

## 2. Share findings and recommendations

Lead in chat with the strongest recommendation first. For each worthwhile
candidate give:
- **Finding:** where the current design causes friction, with file links or examples.
- **Recommendation:** what should change, in plain language using domain and
  Codebase Design terms.
- **Why:** expected benefit, key tradeoffs, and why it earns its cost.
- **Confidence:** `Strong`, `Worth exploring`, or `Speculative`.

If nothing earns a refactor, say so and why. Flag ADR conflicts only when
observed friction justifies reopening them.

Generate an HTML report only on request: follow [HTML-REPORT.md](HTML-REPORT.md),
write `<tmpdir>/architecture-review-<timestamp>.html` (`$TMPDIR`/`/tmp`, `%TEMP%`
on Windows), open it with the platform file opener, share its absolute path, and
still include the high-level recommendation in chat.

In interactive mode, ask which candidate to explore before designing interfaces.
In autonomous mode, pick the strongest candidate (or compare contenders when a
real tradeoff remains) and continue below.

## 3. Explore the design

In interactive mode, use [Grilling](../grilling/SKILL.md) after the user chooses
a candidate (constraints, dependencies, deepened interface, what sits behind the
seam, surviving tests). In autonomous mode, settle those from code, ADRs, and
evidence, escalating only user-judgment or missing-access questions.

- **Untested technical assumptions:** run a focused
  [architecture experiment](../codebase-design/references/experiments.md)
  comparing caller requirements, migration cost, enforceable invariants, and
  valid measurements; return commands, observations, and limits, keeping unrun
  proposals distinct from checked designs.
- **Lifecycle candidates:** include a compact transition table per Model the
  Domain's stateful behavior rules, comparing lifecycle ownership and caller
  obligations, and carry observed event sequences into verification plans.
- **Alternative interfaces:** compare structurally distinct designs through
  [Arena](../arena/SKILL.md) (comparison-only by default unless synthesis is
  requested) using [Design It Twice](../codebase-design/DESIGN-IT-TWICE.md).
- **Glossary and ADRs:** in interactive mode, use
  [Domain Modeling](../domain-modeling/SKILL.md) to add or sharpen terms in
  `GLOSSARY.md` (creating it lazily) and offer an ADR when the user rejects a
  candidate for a durable load-bearing reason (skip ephemeral or self-evident
  reasons). In autonomous mode, record proposed glossary and ADR changes in the
  plan instead of writing them.

## 4. Return a usable plan

For a migration plan, connect the finding to the target interface and owner,
affected callers and compatibility paths, migration order, enforcement,
verification, tradeoffs, rejected alternatives, experiment artifacts/commands,
proposed checks, and any glossary or ADR updates.

Production implementation happens only within the user's authorized scope; hand
selected designs that need design-in-the-loop implementation to
[Architect](../architect/SKILL.md), carrying forward checked findings and
experiments.
