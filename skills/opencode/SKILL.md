---
name: opencode
description: Prompt models through OpenCode headlessly for a second opinion, research, analysis, or code review.
---

# OpenCode

Give the model a self-contained task: the question, relevant evidence, scope,
constraints, and the kind of answer you need. It cannot see this conversation.
Gather evidence in the parent and supply its contents. For an independent opinion, leave out earlier reviewers'
conclusions and the author's defense.

Use [headless.md](references/headless.md) to select a model and send the task
through `opencode run` for general analysis. Its packet agent denies tools.
Start a fresh session for an independent task; use the returned session ID for
a follow-up.

For code or docs review, use [review.md](references/review.md) for the complete
scope and completion checks: code or mixed changes use OpenCode's native
`/review` with a restricted agent; documentation-only changes use a packet.
The caller owns review policy, including when to
run OpenCode, any required model, and whether an incomplete review blocks work.

Assess the answer against the task and available evidence. Supply missing
context when a material gap needs clarification. Tell the caller which model
answered, what it found, what you recommend and why, and any limits or
disagreements. An incomplete run is not an answer.
