---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when discussing codebase terminology, writing or editing a domain glossary, or recording or editing an ADR.
---

# Domain Modeling

Sharpen the domain model as terms and decisions arise. Reading an existing
glossary for vocabulary alone does not invoke this workflow.

## Resolve the vocabulary

Before reading or writing terms, follow [glossary paths](references/glossary-paths.md)
for configured, mapped, legacy, and new layouts. Preserve the project's paths
and one vocabulary source per context.

- Surface conflicts with the existing glossary immediately and ask which
  meaning is intended before recording a resolution.
- Replace vague or overloaded language with precise canonical terms. Distinguish
  concepts such as Customer and User rather than treating both as "account."
- Probe domain relationships with concrete edge-case scenarios that clarify
  boundaries between concepts.
- Check behavioral claims against the code. Surface contradictions, such as
  whole-order versus item-level cancellation, and ask which behavior is intended.

## Record resolved terms

Update the resolved glossary as each term is settled, using
[GLOSSARY-FORMAT.md](GLOSSARY-FORMAT.md) for entries and layout examples.
Keep definitions about the domain; implementation choices, specifications, and
working notes belong elsewhere. Create a glossary only when the first resolved
term needs recording, and an ADR directory only when there is a decision to record.

## Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse**: the cost of changing your mind later is meaningful
2. **Surprising without context**: a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off**: there were genuine alternatives and you picked one for specific reasons

If any criterion is missing, skip the ADR. For a qualifying decision, use
[ADR-FORMAT.md](ADR-FORMAT.md) for placement, numbering, and the brief format.
