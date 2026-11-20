# Tool guidance

Use for skills or docs teaching a CLI, API, SDK, native tool, MCP tool, or bundled
script. For a targeted edit, check only the affected operations.

## Audit the real surface

- List public operations from the installed version, schema, or source.
- Find competing copies across skills, READMEs, help text, prompts, and other host
  installs.
- Check names, parameters, values, defaults, and actual effects—run safely or cite the
  exact source. An accepted parameter may still be ignored.
- Sample [session logs](controlled-comparison.md#learn-from-real-runs) to pick frequent
  calls and recurring errors. Without logs, label the selection provisional.
- For a native or MCP tool, verify that agents actually read the skill before calling it.
  When they rarely do, have the description say to read the skill before the first call
  and what it adds beyond the tool's own description.

## Decide what help can replace

Replace prose with tool help only when the entry an agent needs passes all five checks:

- It covers the operation and the facts being removed.
- It is focused enough to avoid an expensive unrelated read.
- An invalid operation points to a valid choice.
- An unknown parameter is reported, and accepted parameters have their stated effect.
- Common failures state how to recover.

Otherwise, keep the prose and report the defect. When the request includes fixing the
tool, repair and verify its help or errors before deleting prose. Keep a rule that must
prevent a bad first call where the agent sees it beforehand.

## Write the calling surface

Show common calls and failure-prone payloads. For a full tool guide, index remaining
operations by name and point to their help.

Match the exact syntax the agent sends:

| Interface | Write |
| --- | --- |
| Shell or HTTP through a shell | A runnable command or usage line, with flags and defaults |
| Code or SDK | The real signature, plus an example where a call is tricky |
| Native or MCP | The call object's fields, values, and structure |

Skip what a schema already declares; spend words on decisions it cannot express. Leave
volatile lists (such as model catalogs) to live discovery.

## Verify the guide

Prove every shipped call safely per the Proof ladder in `SKILL.md`. For a full audit,
confirm every public operation is discoverable through the guide or help, and add a
coverage check when drift is likely to recur.

Done: every shipped call is proved or reported unproven, every help-replacement claim
passes all five checks, and competing copies or tool defects are reported.
