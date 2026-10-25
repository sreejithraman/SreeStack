---
name: setup-sreestack
description: "Set up or update a repo for SreeStack workflows: project instructions, review and delivery conventions, domain docs, a verification foundation, optional issue tracking, or legacy glossary migration."
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
- **Set up verification:** use [Verify](../verify/SKILL.md) to create and prove the
  requested feature recipes beyond the foundation. Full recipe creation and
  live verification require that scope; ordinary setup establishes the index.

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

During full setup or a research-note convention update, ensure the repo's root
`.gitignore` ignores `/docs/research/`. Reuse an equivalent existing rule; add
the entry when missing and verify it with `git check-ignore`. Report any already
tracked research notes separately; changing their tracking needs an explicit
request.

Keep the shared workflows with their owners: `tdd` for test-driven changes,
`verify` for real acceptance, `showroom` for demonstrations and access,
`review-fix-loop` for independent review and fixes, `pr` for a single PR, and
`gh-stack` for stack management. `merge` owns requested landing and cleanup.
`orchestration` owns
ordinary delegation and ticket scheduling; `goal-swarm` applies only to an
explicit goal or swarm request. Record only the routes available in the target host and
needed by the project, using current local names.

## Verification foundation

During full setup or a verification-foundation update, create or reuse the
project's verification index using
[Verify's map format](../verify/references/project-map.md#location-and-authoritative-index).
Preserve established map locations, recipes, and coverage; add only missing
shared facts and a discovery pointer in the project's agent instructions.

Populate a new index from project discovery: known prerequisites, links to
authoritative launch and check commands, and coverage gaps. Mark unknown or
unexercised details explicitly. With no recipes, state that feature coverage is
not yet documented and live verification has not been run as part of setup.
Keep this step to the index and its pointer; feature recipes and live proof
belong to verification work. Other scoped updates and glossary migration leave
verification documentation alone.

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

Reuse the configured tracker and label vocabulary. If ticket workflows are
requested but their tracker is unsettled, recommend the existing GitHub/GitLab
remote's tracker or local Markdown for work without a remote tracker; support
other trackers through the user's established workflow.

Adapt the matching seed into the project's existing tracker guide or
`docs/agents/issue-tracker.md`: [GitHub](issue-tracker-github.md),
[GitLab](issue-tracker-gitlab.md), or [local Markdown](issue-tracker-local.md).
For other trackers, record how to publish/read tickets, express blockers,
claim work, and complete it using the available integration. Keep external
PR/MR triage disabled unless requested or already configured.

Configure [triage labels](triage-labels.md) only when `triage` is available and
triage is in scope. Preserve an existing mapping. For a new mapping, recommend
`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and `wontfix`;
ask for alternatives only when that choice is unresolved. Document strings in
`docs/agents/triage-labels.md` or the established guide.

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
