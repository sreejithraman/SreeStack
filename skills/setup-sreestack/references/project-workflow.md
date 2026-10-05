# Project workflow conventions

Use during project setup or a workflow update. The output is the project facts
that the shared skills need, kept beside existing contributor/agent guidance.
Avoid a second source of truth for commands, standards, or shared procedures.

## Discover and record

- **Launch and checks:** locate the authoritative scripts, Xcode scheme or
  workspace, service configuration, and CI jobs. Link those owners. Record
  non-obvious prerequisites and invocation details, such as the correct working
  directory, target, simulator, fixture, or required service. Keep platform
  instructions specific to the repo; a web harness, Apple device tool, or CLI
  being available elsewhere does not make it available here.
- **Acceptance:** link the existing verification map and visual-evidence
  convention, if any. `verify` owns real workflow checks; `showroom` packages
  visual proof. An explicit verification-setup request uses Verify's map setup
  workflow rather than a generated per-project verification skill. Leave new
  maps to that request and report any unproven recipes as draft.
- **Review:** identify the intended review base and required project checks.
  Link existing standards. Mechanical rules belong in existing tooling;
  `CODING_STANDARDS.md` is for genuine judgement calls, created only when such
  standards are actually supplied or resolved. `review-fix-loop` owns
  independent assessment and fixes; project setup records its inputs rather
  than prescribing extra reviewers or copying its loop.
- **Delivery:** preserve the repo's branch policy, PR template, required checks,
  and merge requirements. Route single PR preparation through `pr`; route
  stacks through `gh-stack` and each layer's PR workflow. `merge` handles landing
  when requested. Document deviations or missing host support without promising
  automatic publication or merging from a setup request.
- **Delegation:** link `orchestration` when the project uses parallel work or
  ticket graphs. Keep goal-backed execution explicitly requested through
  `goal-swarm`. Agent models, ranks, and effort stay in their existing host
  configuration, not new project defaults inferred from this setup run.

Include only conventions relevant to the requested project and skills available
in its target host. When a needed tool is absent, name the prerequisite and
leave installation to an explicit environment-setup request.

## Instruction pointers

Adapt concise, request-shaped pointers into the project's existing block, for
example:

```markdown
## SreeStack

Before implementation, review, or PR preparation, read the project-specific
workflow conventions in `docs/agents/workflow.md`.
Before naming domain concepts or changing their model, read
`docs/agents/domain.md` and its relevant glossary/ADR paths.
For ticket work, read `docs/agents/issue-tracker.md`.
For triage label changes, read `docs/agents/triage-labels.md`.
For acceptance checks, read `docs/agents/verification/index.md`.
```

Use actual resolved paths and include only docs that exist and belong to the
requested scope. Preserve existing instructions that already supply these
facts. A pointer to a verification map does not establish that its recipes have
passed; their evidence remains with Verify.
