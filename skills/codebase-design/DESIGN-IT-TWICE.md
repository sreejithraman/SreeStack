# Design It Twice

When exploring alternative interfaces for a chosen deepening candidate, compare
independent designs against shared criteria before choosing or synthesizing. Your
first idea is unlikely to be the best.

Uses Codebase Design's vocabulary: **module**, **interface**, **seam**,
**adapter**, **leverage**, **locality**. Resolve the project's glossary before
preparing the brief.

## Frame the problem space

When the calling workflow prepares independent candidates, explain the problem
space for the chosen candidate first:

- The constraints any new interface would need to satisfy.
- The dependencies it would rely on, and which category they fall into
  (see [DEEPENING.md](DEEPENING.md)).
- A rough illustrative code sketch to ground the constraints, not a proposal.

Show this to the user, then proceed. The user reads and thinks while the
candidates work independently.

## Compare whole interfaces

Give independent candidates one technical brief with the file paths, coupling,
dependency categories, what sits behind the seam, and the project vocabulary.
Require structurally distinct interfaces that satisfy the same caller
requirements. Useful directions include minimizing the public surface, maximizing
flexibility, or making the most common caller trivial. Judge each against the
same criteria: **depth**, **locality**, and **seam placement**.
If independent candidates converge, record the consensus and rejected
alternatives rather than forcing different shapes.

Each candidate supplies its interface (including invariants, ordering, and
error modes), realistic usage, the complexity hidden behind the seam,
dependency strategy and adapters, and tradeoffs. Use
[architecture experiments](references/experiments.md)
when a proposal alone cannot establish caller compatibility or behavior.

Default to comparison-only output: present the designs sequentially so the user
can absorb each one, then compare them in prose. Give your own recommendation:
which design is strongest and why. Propose a hybrid when its parts would combine
well. Synthesize a combined design only when requested, preserving any explicit
user choice or checkpoint. Production implementation follows only within the
caller's authorized scope.
