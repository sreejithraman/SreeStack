---
name: retro
description: "Conduct a retrospective on a coding session."
disable-model-invocation: true
---

The user has asked for a **retrospective**. You are suggesting improvements to the coding agent's **environment** to improve future runs.

Keep repository-wide failure prevention with [correct](../correct/SKILL.md).
When session evidence suggests repeated code mistakes, report the examples and
recommend that investigation. Use it directly when the user's request includes
investigating or repairing that class; a retrospective alone remains recommendations.

## Steps

1. Apply `writing-for-agents` for the writing style guide.

2. Read the primary sources for the session the user specifies; default to the
   current one. In T3 Code, prefer scoped `t3_thread_read` and `t3_thread_search`
   for app history and task receipts. Use local session logs when app history is
   unavailable or the requested session belongs to another host. Check current
   artifacts before treating a historical statement as the present state.

3. Look for candidates for improvement in these categories.

- **Navigation**: how easy was it for the agent to find the right files? Are there hidden dependencies between files? Would a **navigation pointer** make it easier? _Use when_ the session took a long time to find a piece of information.
- **Automated checks**: are there automated checks that could catch errors the agent made? Linting, typing, tests, filesystem linters? Read the repo's own check command first (its `package.json`/build-tool `lint`/`check` scripts, its CI workflow), so a check that already exists but sits unwired or silently broken is the finding, not a reinvention. A repo with no **guardrail** (no pre-commit hook and no CI job running its lint/typecheck/test command) is a finding only when the session shows a mistake, omission, or exposure that such a check would have caught. Otherwise, offer a guardrail setup audit as a separate, optional scope. _Use when_ the session shows a mistake, omission, or exposure an automated check could have caught.
- **Coding standards**: should the **reviewer agent** be given a new rule to enforce? Should an existing rule be removed or clarified? Classify the violation first: a **mechanical** one (a fixed syntactic pattern, a banned API, an import shape, a file-location rule) gets a deterministic check, full stop: a custom rule in the repo's own linter, a new pre-commit hook, or a new CI job, whichever the repo's language and existing guardrail make cheapest. Default to building the check over writing the rule. Reserve `CODING_STANDARDS.md` for genuine **judgement calls** (cross-file consistency, "matches the surrounding style," anything no guardrail could ever substitute for). _Use when_ the reviewer agent failed to catch a mistake.
- **Global AGENTS.md**: are there any steering instructions that should be moved to coding standards (or automated checks) instead? _Use when_ the AGENTS.md file is particularly large - in the repo OR the user's global scope.
- **Tool economy**: did the agent make expensive tool calls that could be streamlined? Is there any custom tooling (CLI's, MCP's) that is particularly token-inefficient? _Use when_ the agent made an expensive tool call.
- **No-ops**: look for instructions in steering files that don't modify the agent's behavior. _Use when_ the steering files are large and unwieldy.
- **Information access**: look for opportunities to increase the agent's access to information. Teeing dev server logs, readonly access to third-party services. _Use when_ a crucial piece of information was not available to the agent.

4. Present these candidates to the user, in order of severity, with the session evidence and proposed change for each. A retrospective produces recommendations; implement them only when the user has requested those changes.

## Reference

### Implementation vs review

The implementer explores, writes code, and debugs, so it carries the most context
and should carry as few rules as possible. Turn mechanical rules into automated
checks, which catch the mistake during implementation. Send judgment rules to
review through the project's coding standards: review receives a diff and has room
to apply them. Review runs when [pr](../pr/SKILL.md) publishes, not in every
session, so a rule left only to review catches its mistake later; that is one more
reason to prefer a check. Keep the root instruction files light.

### Where guidance belongs

Use [writing-for-agents](../writing-for-agents/SKILL.md) to decide where a
recommended instruction, standard, or doc belongs and how hosts load it. Consult
the project's existing coding standards, and look for existing docs before
proposing new ones.
