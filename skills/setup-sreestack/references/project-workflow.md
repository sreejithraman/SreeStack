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
- **Acceptance:** link the verification index established by
  [Setup's foundation step](../SKILL.md#verification-foundation), or the existing
  map for a scoped workflow update. Record established demonstration or access
  conventions. `verify` owns feature recipes and real workflow checks;
  `showroom` chooses demonstrations and access.
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
  ticket graphs. Use `goal-swarm` for explicit goal or swarm requests. Link
  orchestration's shared model policy for agent defaults;
  preserve explicit project/user overrides. Do not infer new model or effort
  preferences from this setup run or duplicate the shared policy in project docs.

Include only conventions relevant to the requested project and skills available
in its target host. When a needed tool is absent, name the prerequisite and
leave installation to an explicit environment-setup request.

## Instruction pointers

Apply Setup's [existing-guidance comparison](../SKILL.md#discover-the-project)
before adapting these concise, request-shaped pointers into the project's
existing block. Include only pointers needed to reach relevant guidance:

```markdown
## SreeStack

Before implementation, review, or PR preparation, read the project-specific
workflow conventions in `docs/agents/workflow.md`.
Before naming domain concepts or changing their model, read
`docs/agents/domain.md` and its relevant glossary/ADR paths.
For ticket work, read `docs/agents/issue-tracker.md`.
For triage label changes, read `docs/agents/triage-labels.md`.
For acceptance checks, read `docs/agents/verification/index.md`.
When work produces something the user can inspect or try, use `showroom`
before handoff; use it during UI iteration when showing progress helps feedback.
```

Use actual resolved paths and include only docs that exist and belong to the
requested scope. A pointer to a verification map does not establish that its
recipes have passed; their evidence remains with Verify.
