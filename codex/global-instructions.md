## Delegation and review

Use subagents when independent work can start now and adds useful speed or
coverage. Keep small, tightly connected work with the parent. Difficulty alone
calls for a stronger model, not more agents.

When the user explicitly requests goal-backed parallel work, use `/goal-swarm`.
For other delegation, read its `references/agent-routing.md` without starting
a goal. Create goals only when the user explicitly requests them.

Use `/review-fix-loop` before handing off code changes that affect behavior,
including work by multiple agents, and docs that change agent behavior, such
as skill procedures or global instructions. It owns reviewer count, full-diff
coverage, and fresh rounds. For ordinary docs, comments, or formatting alone,
the parent reviews the change and runs relevant checks; an explicit review
request still invokes the skill.

Use configured agent defaults for routine work, `reviewer` for read-only
review, and `hard_worker` for difficult reasoning. Follow the routing reference
when the host requires explicit model selection. Keep model and effort values
in config and agent files.
