# Tool guidance

Use for skills teaching CLI, API, SDK, native, or MCP tools, including bundled
scripts. Audit the affected interface before deleting guidance in favor of help.
For a narrow edit, inspect the affected operations and dependencies; a full
tool-skill rewrite needs the public interface inventory below.

## Establish what works

Inventory public operations from the installed version, schema, or source,
excluding internals. Find competing copies in skills, READMEs, help, prompts,
context dumps, and other host installs. Identify the authoritative tool version
and the skill copy being tested.

Check documented names, parameters, allowed values, defaults, and promised
effects. Prove drift through safe execution or exact source locations. A parser
accepting a parameter does not show that the implementation uses it. Include
silently ignored options, undocumented public operations, and broken behavior.
Source evidence can establish implementation facts; label unexercised runtime
behavior separately. Work within the user's authorized scope when repairing tools.

Use available session logs to choose frequent calls and recurring error cases.
Count stable call IDs once across resumed/forked histories, associate child work
with its parent, and account for calls embedded in code-mode results. For APIs
and SDKs, include endpoints/functions in generated code. Record the sample window
and denominator. If logs are unavailable, use required task operations and label
the selection provisional. For native/MCP tools, also check whether agents read
the skill before calling the tool; guidance they never reach cannot help.

## Decide what help can replace

Check the particular help entry an agent would need:

- It covers the operation and the facts being removed.
- It is discoverable and focused enough to avoid an expensive unrelated read.
- Invalid operation names help the agent find a valid choice.
- Unknown parameters are reported, and accepted parameters have the stated effect.
- Common failures provide useful recovery information.

Retain guidance for missing or unreliable facts. Repair owned help/errors first
when that is in scope, then verify the replacement before deleting the prose.
Keep rules that must prevent a first call reachable before that call. Put
recoverable mistakes in useful errors when the tool can carry them. Use
[Show Don't Tell](../../show-dont-tell/SKILL.md) for enforcement and underlying repairs.

## Write the calling surface

Provide a compact set of common calls and demonstrated failure-prone payloads.
For a full tool guide, index remaining public operations by grouped names and
point to their help. Preserve meaningful discovery without reproducing a manual.

Match the syntax the agent actually sends:

| Interface | Useful representation |
| --- | --- |
| Shell or HTTP through a shell | A runnable command or usage line with flags and defaults |
| Code or SDK | The language's actual signature and a necessary call example |
| Native or MCP | The actual call object's fields, values, and required structure |

For example, a real CLI might use `lookup <id> [--format json|text]` with a
stated default. A difficult shell JSON argument merits a fully quoted example;
an operation index needs names and a help pointer. Label illustrative examples
and validate shipped calls against the actual tool. A schema already available
to the agent supplies field definitions; spend prose on decisions it cannot express.
Keep printable model lists, presets, and other changing values in tool discovery.

## Verify the guide

For a full audit, every named operation must resolve, every public operation must
be discoverable through the guide's index/help route, and documented parameters
and values must work as stated. For a narrow edit, check its affected subset.
Keep a small repeatable coverage check when tool drift is likely to recur; run
it after relevant owned-tool changes or an external version update. Link and
metadata checks alone do not establish interface correctness.

For comparative trials, keep the tool version and landed help fixes the same
across variants. The no-skill control retains the same tool interface and help.
Cover frequent calls, difficult payloads, ignored-parameter cases, and important
rare constraints. Report valid first calls, wrong guesses, later failures, and
help loaded when observed; distinguish absent telemetry from zero events.
Use [evaluation](evaluating-skills.md) for session isolation and acceptance.

Use a disposable tool or a real-schema stub when live effects are outside scope.
A stub can verify call construction and sequencing, but cannot prove the real
tool's effects. Keep those assertions untested until exercised appropriately.
