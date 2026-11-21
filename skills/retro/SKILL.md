---
name: retro
description: "Conduct a retrospective on a coding session."
disable-model-invocation: true
---

# Retro

Conduct a retrospective on a coding session to recommend improvements to the agent's
environment for future runs. Start from the session the user specifies, defaulting to the
current one. Leave severity-ordered recommendations backed by session evidence and current
repo artifacts. You are done when each recommendation cites observed session evidence
checked against current artifacts and stays advisory unless the user asked to implement
changes.

Keep repository-wide failure prevention with [correct](../correct/SKILL.md). When session
evidence suggests repeated code mistakes, report the examples and recommend that
investigation; use it directly only when the user's request includes investigating or
repairing that class.

## Steps

1. Apply [writing-for-agents](../writing-for-agents/SKILL.md) to decide where a recommended
   instruction, standard, or doc belongs and how hosts load it.

2. Read the primary sources for the specified session (default: the current one). In T3
   Code, prefer scoped `t3_thread_read` and `t3_thread_search` for app history and task
   receipts. Use local session logs when app history is unavailable or the session belongs
   to another host. Check current artifacts before treating a historical statement as the
   present state.

3. Look for improvement candidates across these categories:

- **Navigation:** how easily did the agent find the right files? Are there hidden
  dependencies between files? Would a navigation pointer help? *Use when* the session took a
  long time to find a piece of information.
- **Automated checks:** could automated checks catch errors the agent made (linting, typing,
  tests, filesystem linters)? Read the repo's own check command first (`package.json` or
  build-tool `lint`/`check` scripts, CI workflow), so an existing unwired or silently broken
  check is the finding rather than a reinvention. A repo with no guardrail (no pre-commit
  hook and no CI job running its lint/typecheck/test command) is a finding only when the
  session shows a mistake, omission, or exposure such a check would have caught; otherwise
  offer a guardrail setup audit as a separate, optional scope. *Use when* the session shows
  a mistake, omission, or exposure an automated check could have caught.
- **Coding standards:** should the reviewer agent get a new rule, or have an existing one
  removed or clarified? Classify the violation first: a **mechanical** one (a fixed
  syntactic pattern, banned API, import shape, or file-location rule) gets a deterministic
  check (custom linter rule, pre-commit hook, or CI job — whichever the repo's language and
  existing guardrail make cheapest). Default to building the check over writing a rule.
  Reserve `CODING_STANDARDS.md` for genuine **judgement calls** (cross-file consistency,
  "matches the surrounding style", anything no guardrail can substitute for). *Use when* the
  reviewer agent failed to catch a mistake.
- **Global `AGENTS.md`:** are steering instructions better moved to coding standards or
  automated checks? *Use when* `AGENTS.md` is particularly large in the repo or global
  scope.
- **Tool economy:** did the agent make expensive tool calls that could be streamlined, or is
  custom tooling (CLIs, MCPs) token-inefficient? *Use when* the agent made an expensive tool
  call.
- **No-ops:** look for instructions in steering files that do not modify the agent's
  behavior. *Use when* steering files are large and unwieldy.
- **Information access:** look for opportunities to increase the agent's access to
  information (teeing dev server logs, read-only access to third-party services). *Use when*
  a crucial piece of information was not available to the agent.

4. Present candidates in severity order with the session evidence and proposed change for
   each. A retrospective produces recommendations; implement them only when requested. When
   the user asks to prove a recommendation against the old version, hand it to
   [Tune Stack](../tune-stack/SKILL.md).

## Reference

### Implementation vs review

The implementer explores, writes code, and debugs, so it carries the most context and should
carry as few rules as possible. Turn mechanical rules into automated checks, which catch
mistakes during implementation. Send judgment rules to review through the project's coding
standards, where the reviewer receives a diff and has room to apply them. Review runs when
[pr](../pr/SKILL.md) publishes, not in every session, so a rule left only to review catches
its mistake later — one more reason to prefer a check. Keep root instruction files light.

### Where guidance belongs

Consult the project's existing coding standards and docs before proposing new ones, using
`writing-for-agents` to place each instruction, standard, or doc in its strongest home.
