# Agent routing

Read this before spawning implementation or review agents. Reading this
reference does not invoke goal-swarm or authorize creating a goal.

## Choose work and role

Keep a cohesive task with one owner. Spawn agents for independent results whose
inputs exist, with clear ownership and checks. The parent may implement work;
it need not delegate a small task just because it coordinates other agents.

Use configured subagent defaults for routine work, `reviewer` for code review,
and `hard_worker` when the task needs difficult reasoning. A hard task can still
have one owner. For difficult reviews, use `hard_worker` with the same read-only
review contract. Choose the likely capable role up front; escalate when evidence
shows a need instead of requiring a sequence of failed attempts.

For reviews, request read-only child permissions when the host supports them.
`hard_worker` otherwise inherits the parent's permissions. The read-only review
contract still applies, but prose alone does not enforce a filesystem restriction.

For code review, `/review-fix-loop` chooses the number of reviewers and rounds.
Reviewers count toward the same concurrency limit as workers. Treat the configured
limit as a ceiling; launch only agents with useful work ready now. Finish or close
completed agents before opening more when the host counts open threads.

## Apply settings at spawn

Use the selected custom role when the host exposes it. Otherwise, read that role's
model and effort from its active agent file and pass both explicitly. For routine
work, use the effective `[agents]` defaults. Honor project and user overrides.

For Codex, custom agent values override explicit spawn values, which override
`[agents]` defaults, which override parent settings. Resolve model and effort
together; an omitted effort can select a model default or retain an inherited
value. Agent files are the source of truth for role settings. If a needed role
is missing, report that gap rather than claiming the requested model ran.
See OpenAI's [subagent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents)
for the supported fields and precedence.

Some hosts require fresh or partial context to change the child's model or
effort. On a host where full-history forks inherit the parent and reject
overrides, use `fork_turns = "none"` or a supported partial fork, with a complete
brief and explicit model and effort. Check the actual spawn result when it
exposes those values; otherwise report the requested settings as unverified.

Give each child its result, owned work, relevant paths, requirements, checks,
and return format. A fresh reviewer gets the complete current scope and raw
requirements without earlier reviewers' conclusions or the author's defense.
Leave further delegation to the parent unless it explicitly assigns that work.
