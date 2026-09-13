## Delegation and review

Use `/orchestration` when deciding whether to delegate or coordinating workers.
For independent review, `/review-fix-loop` reads orchestration’s routing reference
directly and owns reviewer dispatch.
When the user explicitly requests goal-backed parallel work, use `/goal-swarm`.
Create goals only when the user explicitly requests them.

Use `/review-fix-loop` before handing off code changes that affect behavior,
including work by multiple agents, and docs that change agent behavior, such
as skill procedures or global instructions. It owns reviewer count, full-diff
coverage, and fresh rounds. For ordinary docs, comments, or formatting alone,
the parent reviews the change and runs relevant checks; an explicit review
request still invokes the skill.

Follow orchestration’s routing reference for worker and reviewer selection, including when
the host requires explicit model settings. Keep model and effort values in
config and agent files.
