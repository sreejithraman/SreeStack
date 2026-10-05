# OpenCode v2 external review

Investigated 2026-10-05. The initial investigation below established source and CLI behavior. The skill was subsequently updated; validation of that update is recorded at the end. No upgrades or saved authentication/configuration changes were performed. This is not a completed external model review or a runtime security audit.

## Conclusion

The installed OpenCode v2.0.23 retains native review. What disappeared is the v1 CLI invocation expected by the local skill, not the built-in review method. The updated skill uses a restricted fresh session, invokes `session.command` with `name: "review"`, waits for completion, and inspects the resulting session. It preserves the review packet, scope, model, read-only restrictions, coverage, and completion checks. A plain review prompt is another technical option, but accepting it as the required native review would change the current local policy.

## Versions and evidence

Local `opencode --version` reports v2.0.23. `opencode run --help` supports `--standalone`, `--server`, `--agent`, `--model provider/model#variant`, `--format json`, and `--auto`; it does not expose `--command`, `--pure`, `--dir`, or a separate `--variant`. At investigation time, the official npm registry's `@opencode/cli/latest` endpoint also returned 2.0.23. An upgrade is therefore not an evidenced solution to this mismatch. These are time-specific observations, not a claim about future releases. [Official package registry](https://registry.npmjs.org/@opencode/cli/latest), [pinned run source](https://github.com/anomalyco/opencode/blob/v2.0.23/packages/cli/src/run/run.ts).

The findings below use the v2.0.23 tag, whose GitHub ref resolves to `0fd7e2829449b052abf0078666669302923d77af`. Live stable v2 documentation is supporting guidance; it is not a replacement for the pinned source. Development documentation can differ materially from stable documentation. [Tag reference](https://api.github.com/repos/anomalyco/opencode/git/ref/tags/v2.0.23).

## Native method and API

The built-in `opencode.command` plugin registers `review` and expands its built-in review template into a durable session prompt. It uses the current session, unlike the v1 implementation's obligatory review subtask. The template requests full-file context, correctness and regression checks, and actionable feedback, and selects uncommitted, commit, branch, or PR scope from the arguments. The parent should still supply the complete evidence packet and explicit resolved scope. [Pinned command registration](https://github.com/anomalyco/opencode/blob/v2.0.23/packages/core/src/plugin/command.ts), [pinned native review template](https://github.com/anomalyco/opencode/blob/v2.0.23/packages/core/src/plugin/command/review.txt).

`POST /api/session/{sessionID}/command`, operation `session.command`, is the native API route. The pinned handler accepts `name`, `text`, optional files/agents/skills, and delivery; the command call does not choose the session's model or primary agent. Select those when creating the session. A successful command response is submission, not proof of a finished review. The HTTP API is experimental, so check the installed server's contract when implementing. [Official API](https://opencode.ai/v2/docs/api/), [pinned handler](https://github.com/anomalyco/opencode/blob/v2.0.23/packages/server/src/handlers/session.ts), [pinned dispatch](https://github.com/anomalyco/opencode/blob/v2.0.23/packages/core/src/session/command.ts).

A proposed adapter sequence is:

1. Gather resolved base/head, Git state, diff, untracked contents, requirements, and coverage criteria outside the reviewed diff.
2. Start one private server and use its returned address consistently; avoid reconnecting to the ordinary shared server.
3. Inspect configuration, agent, model, command registry, and loaded plugins. Require the built-in review implementation and reject an overridden command.
4. Create a fresh session in the target directory, with the exact model and a primary reviewer agent, plus explicit session permission rules.
5. Submit `session.command` with `name: "review"` and trusted instructions to read the supplied evidence packet and honor its scope.
6. Wait for execution completion, inspect message/tool/error history and exported session, validate actual model and substantive findings/coverage, and compare repository state with the snapshot.

These steps are an implementation proposal inferred from the API and source, not a tested wrapper. `command.list` exposes command names/descriptions, not their complete expanded implementation; matching its description alone cannot prove built-in provenance. Verify the expanded stored prompt against the pinned template and control command sources before invocation. [Pinned command registry](https://github.com/anomalyco/opencode/blob/v2.0.23/packages/core/src/command.ts).

## Restrictions

Native V2 configuration uses `agents`, ordered `permissions` arrays, and action names `shell` and `subagent`. Use those fields in the adapter rather than treating the v1 `agent`, `permission`, `bash`, and `task` shape as the native v2 schema. Last matching rule wins. A reviewer should deny all actions, then allow only the necessary `read`, `glob`, and `grep` actions plus a narrowly scoped `external_directory` exception for the packet. Keep shell, edits, subagents, MCP, web tools, questions, and code execution denied. V2 does not list `list` as a built-in permission action. [Official permissions](https://opencode.ai/v2/docs/permissions/).

`session.create` accepts a permissions array. Pinned permission evaluation merges the selected agent's permissions first and the session's permissions second, allowing explicit session restrictions to override agent rules. Use deny-all and only the required exceptions in the created session and inspect the resulting metadata. A separate child agent has its own permissions, so preventing additional delegation remains necessary. This governs checked model tools; it does not sandbox arbitrary plugins or host preprocessing. [Pinned session handler](https://github.com/anomalyco/opencode/blob/v2.0.23/packages/server/src/handlers/session.ts), [pinned permission evaluation](https://github.com/anomalyco/opencode/blob/v2.0.23/packages/core/src/permission.ts), [official agents](https://opencode.ai/v2/docs/agents/).

## Configuration isolation

`--standalone` gives a private server; it does not by itself suppress global/project configuration, plugins, compatibility sources, or command overrides. The pinned server process recognizes `OPENCODE_CONFIG_DIR`, `OPENCODE_CONFIG_PROJECT_DISABLE` (legacy alias `OPENCODE_DISABLE_PROJECT_CONFIG`), `OPENCODE_CONFIG`, and `OPENCODE_CONFIG_CONTENT`. Inline content loads last, after discovered configuration. Use process-scoped configuration and retain ordinary saved configuration unchanged. [Pinned server process](https://github.com/anomalyco/opencode/blob/v2.0.23/packages/cli/src/server-process.ts), [pinned configuration load order](https://github.com/anomalyco/opencode/blob/v2.0.23/packages/core/src/config.ts).

A dedicated `OPENCODE_CONFIG_DIR` and disabled project configuration improve isolation, but discovery also includes home compatibility directories `~/.claude` and `~/.agents`. Core has an internal `global: false` option that suppresses them, but the v2.0.23 exposed ServerOptions config schema does not include that switch. There is no verified CLI equivalent to v1 `--pure`. Validate all remaining sources, including provider-supplied well-known configuration, compatibility discovery and executable plugins, before treating the adapter as a restricted native-review replacement. Do not assume a temporary config directory alone creates a clean environment. [Pinned discovery](https://github.com/anomalyco/opencode/blob/v2.0.23/packages/core/src/config/discovery.ts), [pinned options](https://github.com/anomalyco/opencode/blob/v2.0.23/packages/server/src/options.ts), [pinned core options](https://github.com/anomalyco/opencode/blob/v2.0.23/packages/core/src/config.ts).

Custom slash-command shell blocks execute outside the agent permission flow. An overridden `/review` can therefore defeat a shell-denied agent before model tool execution; controlling and verifying command sources is required. [Official command preprocessing](https://opencode.ai/v2/docs/commands/#shell).

## Headless completion and model selection

For a packet-only alternative, v2 `run` supports stdin, explicit agent/model, private server, and JSON events. It reads cwd rather than accepting `--dir`. V2 model variants are part of the model argument (`provider/model#variant`). Without `--auto`, noninteractive permission requests are rejected; `--auto` answers them with allow-once, so omit it for the restricted workflow. [Pinned run implementation](https://github.com/anomalyco/opencode/blob/v2.0.23/packages/cli/src/run/run.ts), [pinned noninteractive handling](https://github.com/anomalyco/opencode/blob/v2.0.23/packages/cli/src/run/noninteractive.ts).

JSON output contains tool calls, errors and step finishes. A step finish is not full-session completion, and exit success alone does not prove adequate scope or model selection. For either transport, require the actual requested model, a final substantive review, coverage of every scoped file, resolved denied-read gaps, no unexplained tool errors, and unchanged repository state. These acceptance checks preserve the existing local review contract; they are proposed workflow checks, not upstream claims.

## Alternatives

- **Preferred:** use the v2 native API session workflow above. This preserves the native-review policy and uses the already installed current stable version.
- **Packet-only `run`:** simpler transport with tools denied and full evidence supplied, but it is a deliberate change to the current local code-review contract. It can miss context outside the packet.
- **T3 OpenCode delegation:** the parent verified that its live provider catalog allows cross-provider child tasks and contains the required `opencode-go/glm-5.3-flash` model. This supplies another transport, not proof of authentication/quota, native review activation, or runtime permission isolation. Carry the same checks into any delegated task.
- **Pin a separate v1 binary:** potentially preserves the existing CLI adapter during migration, but requires a deliberate version and installation choice; no downgrade or install was performed.
- **Gemini after quota reset / another approved reviewer:** can restore independent review without waiting for OpenCode migration, but must honor exact requested model/provider and review policy rather than silently substituting them.

## Skill update validation

The rewritten skill shares private-server setup, model selection, explicit session permissions, HTTP body transport, terminal-outcome checks, and cleanup between native review and tool-free packet analysis. Gemini and OpenCode now keep common execution in SKILL.md and the complete review workflow in one review.md. OpenCode discloses only its HTTP helper in api.md. `README.md` records setup; invocation metadata is unchanged.

Live OpenCode v2.0.23 tests with a local deterministic OpenAI-compatible fixture verified:

- Successful tool-free packet execution with no tools exposed to the fixture.
- Exact preservation from original file bytes through acquisition, HTTP body,
  provider input, and exported prompt of a UTF-8 packet larger than 1 MB,
  including CRLF, bare CR, Unicode, literal shell syntax and file-reference
  syntax, without executing it.
- A follow-up in the same session with a new idle transition.
- Reuse of that session after restarting the owned server, and recovery from a
  bounded client wait timeout without duplicating submission.
- Settled preflight inventories with the intended primary agents, effective
  restrictions, active built-in plugins, native command, and fixture model before
  submission and after restart.
- Native `review` activation, verified by the expanded built-in template with argument placeholders substituted in the stored prompt.
- Successful reads of the external packet and repository file, with only `read`, `glob`, and `grep` exposed.
- Detection of a clipped long source line despite `truncated: false`, and exact
  delivery of every row of its lossless bounded-width packet copy. Reconstruction
  checks also covered CRLF, control characters, and non-BMP text.
- Suppression of planted project JSON and Markdown review-command overrides; their shell markers were not created, and the repository fixture remained unchanged.

These tests exercise the real CLI/server and the HTTP helper in `api.md` and session/prompt examples in `SKILL.md`. The fixture supplies scripted responses, so they demonstrate transport and enforcement behavior, not model review quality. The temporary acceptance driver, transcript, and provider-request evidence were retained locally for review; they are not portable repository artifacts.

Actual provider probes reached terminal `failed` states: GLM 5.3 Flash through `opencode-go` returned HTTP 403 requiring an active Go subscription; the free Console model returned HTTP 403 rejecting free-tier use. The full external review packet was also attempted through Gemini (quota exhausted) and the required GLM fallback (Go access rejected). Neither counts as a completed external review. Authentication remains a separate prerequisite from catalog availability.

`git diff --check`, skill-creator's `quick_validate.py skills/opencode`, and `python3 scripts/check_skills.py` passed. Independent instruction reviews identified command-argument limits, native line clipping, startup inventory readiness, and packet newline conversion; HTTP body transport, lossless evidence copies, bounded activation preflight, and unchanged byte acquisition address them.
