# Tool guidance

Use for skills teaching a CLI, API, SDK, native tool, MCP tool, or bundled script.
For a [targeted change](working-on-skills.md#change-an-existing-skill), check only the
affected operations.

## Find what works

1. List public operations from the installed version, schema, or source.
2. Find competing copies in skills, READMEs, help, prompts, and other host installs.
3. Check names, parameters, values, defaults, and promised effects. Prove drift by
   running the call safely or citing the exact source. An accepted parameter may
   still be ignored.
4. Use session logs to choose frequent calls and recurring errors. Record the sample
   window and denominator, and count resumed or forked calls once. Without logs,
   label the selection provisional.
5. For a native or MCP tool, check that agents read the skill before calling it.

## Decide what help can replace

Replace prose with help only when the entry an agent needs passes all of these:

- It covers the operation and the facts being removed.
- It is focused enough to avoid an expensive unrelated read.
- An invalid operation points to a valid choice.
- An unknown parameter is reported, and accepted parameters have their stated effect.
- Common failures say how to recover.

Otherwise, keep the guidance and report the defect. When the request covers repairing
the tool, repair its help or errors first. Then verify the repair before you delete the
prose. Keep a rule that must prevent a
first call where the agent sees it before that call.

## Write the calling surface

Give the common calls and the payloads that fail in practice. For a full tool guide,
index the remaining operations by name and point to their help.

Match the syntax the agent actually sends:

| Interface | Write |
| --- | --- |
| Shell or HTTP through a shell | A runnable command or usage line, with flags and defaults |
| Code or SDK | The real signature, and an example where a call is hard |
| Native or MCP | The call object's fields, values, and structure |

Skip what a schema already gives the agent. Spend words on decisions it cannot
express. Leave changing values, such as model lists, to tool discovery.

## Verify the guide

Prove each shipped call. Run it only if it risks nothing a [guardrail](../SKILL.md#writing-for-agents)
covers, or the request authorizes it.
Otherwise use a documented dry run, a disposable fixture, or a real-schema stub, or cite the exact
source, and report its live effect as unproven. A stub proves call construction, not effects. For a full
audit, every public operation must be discoverable through the guide or help. Keep a
coverage check when drift is likely to recur.
