---
name: how
description: Explain how existing code works, trace a subsystem's runtime and data flow, or identify current package ownership and layering. Use why for historical rationale and architect for proposed designs.
---

# How

Explore the codebase to answer "how does X work?" questions. Produce architectural explanations at the level of a senior engineer onboarding onto a subsystem, enough to build a working mental model, not so much that it reads like annotated source code.

Work read-only within the requested scope. Use [orchestration](../orchestration/SKILL.md)
for model selection, useful delegation, and acceptance. Historical motivation
belongs to [why](../why/SKILL.md); active defects to
[diagnosing-bugs](../diagnosing-bugs/SKILL.md); change risks to
[blast-radius](../blast-radius/SKILL.md). Explain existing ownership here; use
[codebase-design](../codebase-design/SKILL.md) or
[architect](../architect/SKILL.md) for proposed placement or design changes.

## 1. Assess complexity

If the scope is ambiguous, state your interpretation and explore. The user can redirect.
Anchor the question in the relevant entry points and current source revision,
including working changes that affect the explanation.

- **Simple** (a single module, a small utility, a narrow question such as "how does function X work"): explore and explain in one pass using [the explainer prompt](references/explainer-prompt.md), without the explorer-findings section. Go to step 4.
- **Complex** (a subsystem spanning multiple files or services, a cross-cutting feature, a full architectural overview): go to step 2.

When in doubt, take the simple path.

## 2. Explore (complex only)

Decompose the question into distinct slices of the subsystem, often 2 to 4 angles.
Use [the explorer prompt](references/explorer-prompt.md) with each angle filled in.
Delegate independent slices when useful and authorized; otherwise trace them
directly. Keep source inputs consistent and give each explorer a bounded question.

## 3. Synthesize (complex only)

Once exploration is complete, use [the explainer prompt](references/explainer-prompt.md)
with the question and findings. Reconcile overlapping accounts and resolve
contradictions against the source before presenting one explanation. The parent
checks the synthesis and owns the final answer.

## 4. Present

Adapt the explanation's sections to the question: Overview, Key Concepts, How
It Works, Where Things Live, Gotchas. Finish when the requested flow and boundaries
are traced to concrete code, or name exactly where the trace stops and why.
Distinguish code-derived behavior from observed execution and historical evidence;
a source walkthrough alone does not prove runtime correctness or author intent.
