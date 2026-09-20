# Agent routing

Read this before spawning implementation or review agents. Reading this
reference does not authorize creating a goal.

## Choose work and role

Choose a rank by the judgment the assignment needs. Review is an assignment,
not a separate rank.

| Rank | Work |
|---|---|
| `junior` | Explicit, easily checked work with settled requirements |
| `engineer` | Routine implementation using established patterns; default worker |
| `senior` | General engineering judgment; default reviewer |
| `staff` | Substantial diagnosis, implementation requiring design judgment, or difficult unresolved reasoning such as subtle concurrency or data-loss risks |

This table is the allowed rank set. Select only these ranks, even when the host
exposes others. Map a request for another rank to the closest listed rank and
report the substitution.

Choose the likely capable rank up front; failed attempts are not a prerequisite.
File count alone does not determine difficulty. A hard task can still have one owner.

For review, start with `senior` and select another rank when the review needs
less or more judgment. `junior` fits mechanical checks with explicit criteria;
`engineer` fits straightforward changes using established patterns. Use `staff`
for substantial design questions and difficult unresolved reasoning. Choose each
reviewer's rank independently of the implementer; two reviewers may use
different ranks while both cover the full diff. Reassess each round; project
difficulty alone does not justify keeping a higher rank once its reasoning
problem is resolved.

Every review brief must say: work read-only, report findings, and leave edits to
the parent. Rank files allow implementation too, so this is an instruction rather
than an enforced filesystem restriction.

For code review, `/review-fix-loop` chooses the number of reviewers and rounds.
Reviewers count toward the same concurrency limit as workers. Treat the configured
limit as a ceiling; launch only agents with useful work ready now. Finish or close
completed agents before opening more when the host counts open threads.

## Choose context and reuse

Set `fork_turns` explicitly on every spawn. Independent reviewers must use
`fork_turns: "none"` in every round. Starting a new agent alone does not give it
fresh context. Give it a complete [review brief](../../review-fix-loop/references/review-brief.md)
without earlier verdicts or the author's defense.

For workers, use `"none"` for bounded work that a complete brief can explain.
Choose a supported partial fork (a turn count) or `"all"` when prior decisions
matter; include the needed decisions in its brief. Check the model constraints
below before choosing inheritance.

Reuse an existing worker for related fixes within its ownership. Supply the
changed requirements, current files, and checks. Start a new agent when stronger
reasoning or independent judgment is needed. Worker reuse does not apply to
independent review rounds.

## Apply settings at spawn

When a project or user overrides a listed rank's model or effort, use a spawn
path where those values take effect and pass both explicitly. Otherwise, use the
custom role for the selected allowed rank when the host exposes it. If it does
not, read that role's model and effort from its active agent file and pass both
explicitly. For routine work without a named rank, use the effective `[agents]`
defaults.

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

Leave further delegation to the parent unless it explicitly assigns that work.
