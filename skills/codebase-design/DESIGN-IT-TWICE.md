# Design It Twice

When the user wants to explore alternative interfaces for a chosen deepening
candidate, use [arena](../arena/SKILL.md) for independent designs, comparison,
and any requested synthesis. Your first idea is unlikely to be the best.

Uses the vocabulary in [SKILL.md](SKILL.md): **module**, **interface**,
**seam**, **adapter**, **leverage**, **locality**. Resolve the project's glossary
through Codebase Design before preparing the brief.

## Frame the problem space

Before dispatch, explain the problem space for the chosen candidate:

- The constraints any new interface would need to satisfy.
- The dependencies it would rely on, and which category they fall into
  (see [DEEPENING.md](DEEPENING.md)).
- A rough illustrative code sketch to ground the constraints, not a proposal.

Show this to the user, then proceed. The user reads and thinks while the
candidates work independently.

## Compare whole interfaces

Give arena one technical brief with the file paths, coupling, dependency
categories, what sits behind the seam, and the project vocabulary. Require
structurally distinct interfaces that satisfy the same caller requirements.
Useful directions include minimizing the public surface, maximizing flexibility,
or making the most common caller trivial. Judge each against the same criteria:
**depth**, **locality**, and **seam placement**.
If independent candidates converge, use arena's consensus branch and record
the agreement and rejected alternatives rather than forcing different shapes.

Each candidate supplies its interface (including invariants, ordering, and
error modes), realistic usage, the complexity hidden behind the seam,
dependency strategy and adapters, and tradeoffs. Use
[architecture experiments](../improve-codebase-architecture/references/experiments.md)
when a proposal alone cannot establish caller compatibility or behavior.

For this interface exploration, select arena's comparison-only finish line:
present the designs sequentially so the user can absorb each one, then compare
them in prose. Give your own recommendation: which design is strongest and
why. Propose a hybrid when its parts would
combine well. When synthesis is requested, arena owns choosing a base,
grafting, and checking the combined design. Preserve the user's requested
choice or checkpoint. Production implementation follows only within scope;
use [architect](../architect/SKILL.md) when the selected design needs to stay
in the loop through implementation.
