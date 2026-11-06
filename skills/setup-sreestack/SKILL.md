---
name: setup-sreestack
description: "Set up or update a repo for SreeStack workflows: project instructions, review and delivery conventions, domain docs, verification maps, optional issue tracking, or legacy glossary migration."
disable-model-invocation: true
---

# SreeStack Setup

Make the project's conventions discoverable to the shared skills. Reuse the
repo's existing docs, commands, and configuration; write the missing project
knowledge and concise pointers rather than copying skill procedures into it.
Setup owns project documentation. Shared skill installation, global agent
settings, credentials, and product changes are separate tasks when requested.

## Choose the scope

- **Set up this repo:** establish workflow and domain-document conventions and
  the verification foundation below.
  Include tracker configuration when the project already uses ticket workflows
  or the user requests them. A remote alone does not establish issue-tracker use.
- **Update one convention:** change that part in place, leaving other settings.
- **Migrate glossary:** follow [glossary migration](references/glossary-migration.md).
  This mode skips other setup and works without existing setup docs.
- **Set up or maintain verification:** follow
  [verification maps](references/verification-map.md) to create, prove, or update
  feature recipes.

Honor the user's requested scope and choices already made in the session.
Present concrete planned edits. Ask only about unresolved choices that affect
those edits, and apply an authorized plan without asking for the same approval.

## Discover the project

Read the inherited global and host instructions, active project instructions,
existing contributor/setup docs, `docs/agents/` or the established equivalent,
remotes, build/test scripts,
platform configuration, CI checks, PR templates, and branch conventions.
Determine which SreeStack skills and host tools are actually available; keep
project facts separate from tools observed in this environment.

Resolve domain docs with [glossary paths](../domain-modeling/references/glossary-paths.md),
including configured paths, legacy files, maps, and per-context ADRs. Inspect
existing verification documentation before proposing new files.

Before adding guidance, compare its meaning with those instructions, project
docs, and relevant shared skills; different wording can express the same rule.
Add only missing project-specific facts or explicit project overrides. Keep
existing guidance with its owner and add a concise pointer only when agents
need one to find it. Preserve the scope and conditions of existing rules.
Use the relevant branch below; a scoped update does not restart full onboarding.

## Project workflow

Use [project workflow](references/project-workflow.md) to capture the repo's
non-obvious launch/check requirements, acceptance evidence, review base, PR or
stack conventions, and available tooling. Prefer an existing contributor or
agent doc; use `docs/agents/workflow.md` only when it needs a new home.

Keep the shared workflows with their owners: `tdd` for test-driven changes,
`research` for cited findings and session notes,
`verify` for real acceptance, `show-me` for demonstrations and access,
`review-fix-loop` for independent review and fixes, `pr` for a single PR, and
`gh-stack` for stack management. `merge` owns requested landing and cleanup.
`orchestration` owns shared delegation mechanics, `swarm` supplies bounded
parallel work, `implement` owns one PR-sized change, and `chief-of-staff`
coordinates a program's PR owners and dependencies.
Record only the routes available in the target host and
needed by the project, using current local names.

## Verification foundation

During full setup or a verification-foundation update, create or reuse the index
with [verification maps](references/verification-map.md). Keep this step to the
index and its discovery pointer. State that live verification has not been run as
part of setup. Feature recipes and live proof belong to the verification scope.
Other scoped updates and glossary migration leave verification documentation alone.

## Domain documentation

Use one glossary per context. For a new layout, default to root `GLOSSARY.md`
and `docs/adr/`; use a map only when distinct domain contexts need separate
vocabularies. Package count alone does not require multiple glossaries. Preserve
existing custom locations and context boundaries.

When legacy `CONTEXT` files are domain glossaries, recommend migrating them.
An explicit request to adopt `GLOSSARY` names authorizes the unambiguous renames
and reference updates in [glossary migration](references/glossary-migration.md).
Otherwise include the migration as a choice in the plan; retain legacy paths
when declined. Apply agreed migration before recording the resulting paths.

Adapt [domain.md](domain.md) into the existing domain guide or
`docs/agents/domain.md`, replacing examples with the resolved project paths.
Record reading rules, vocabulary use, and ADR conflict handling. Glossaries and
ADR directories are created lazily by `domain-modeling`, when there is content;
setup does not create empty ones.

## Issue tracking, when in scope

Reuse the configured tracker. If ticket workflows are
requested but their tracker is unsettled, recommend the existing GitHub/GitLab
remote's tracker or local Markdown for work without a remote tracker; support
other trackers through the user's established workflow.

Adapt the matching seed into the project's existing tracker guide or
`docs/agents/issue-tracker.md`: [GitHub](issue-tracker-github.md),
[GitLab](issue-tracker-gitlab.md), or [local Markdown](issue-tracker-local.md).
For other trackers, record how to publish/read tickets, express blockers, check
and make claims, and complete work using the available integration.

## Write and check

Update existing docs and their active instruction pointers in place, preserving
project additions. Use the instruction file selected by the user or active host;
when both `AGENTS.md` and `CLAUDE.md` exist, reuse the block that owns the current
pointers. If neither exists, create `AGENTS.md` unless the user requested another
file. Reuse an existing SreeStack or Agent skills block, preserve unrelated
entries, and include only pointers to docs that exist. Keep them brief and state
when each doc should be read. Templates are seeds, not replacement files.

Check each added rule and pointer against the discovery comparison; remove
redundant additions even when their wording differs. Check that every written
pointer and map link resolves, glossary consumers use the selected paths, and
reruns add no redundant guidance or blocks and preserve established choices.
Read the scoped diff and report changed files, resolved conventions,
checks, and remaining gaps. Distinguish documented commands and discovered tools
from runtime readiness: only claim a build, workflow, or verification recipe
works when it was actually exercised.
