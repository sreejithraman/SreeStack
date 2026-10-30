# Revising skills

Keep the requested improvement and the behavior that must survive it together,
using [Verify's acceptance guidance](../../verify/references/acceptance-contract.md).
Preserve the skill's recorded local adaptations and invocation settings unless
the user asks to change them. Edit the source of truth identified by the project.

## Choose the depth

For a small correction, inspect its consumers and the affected branch, edit the
existing meaning, and try the motivating request in a fresh session. Run relevant
structural checks. A path correction needs no full comparative benchmark.

For a substantial rewrite, removal of guidance, or change to discovery or
handoffs, use the workflow below. Run only the affected parts for a narrower
behavior change. Claims about agent-outcome equivalence or task context savings
also need [evaluation](evaluating-skills.md). Focused diff and metadata checks
can establish unchanged text or invocation settings without an agent experiment.

## Establish the baseline

1. Preserve the original folder, including references, scripts, and invocation
   metadata. Record its revision or content hashes with relevant local changes.
2. Find consumers: linked skills, embedded instructions, tool descriptions,
   prompts, and tests that assert text anywhere in the folder. Check installed
   copies and name resolution when testing in a host. Establish which copy the
   agent actually reads; source edits alone do not establish live installation.
   Check documented read limits when truncation could hide required guidance.
3. State the improvement, preserved requirements, and realistic requests before
   rewriting. Include affected triggers, reference discovery, rare constraints,
   and handoffs. Use disposable fixtures for calls with external effects.
4. For context work, distinguish description, body, conditional references, and
   host/plugin overhead. Measure what tasks actually load, including later reads.
   Label bytes or estimates as such; neither is tokenizer-measured context use.

Finish baseline preparation when the original can be recovered, affected
consumers are identified, and expected outcomes do not depend on the candidate.

## Revise

For tool instructions, complete the relevant [tool audit](tool-guidance.md)
before deciding what help can replace. Keep tool changes and instruction changes
distinct in comparisons so a better tool is not credited to shorter prose.

Use the entrypoint's writing principles to place and prune material. For an
explanation that may belong in structure or enforcement, use
[Show Don't Tell](../../show-dont-tell/SKILL.md) and its explanation audit.

Account for each removed or relocated rule, example, and constraint in the
working notes: its new home, authoritative replacement, evidence that it is
obsolete, or the case that tests behavior without it. Group equivalent items;
ordinary edits need no permanent registry. A reference read by most relevant
tasks may belong inline; use observed reads when available rather than guessing.

Keep critical guidance reachable before the action it constrains. Preserve
supported hosts and invocation choices; lack of recent personal usage alone
does not establish that another consumer no longer needs them.

## Check and accept

Exercise affected requests against the candidate and original when behavior
comparison matters. Check reference paths, invocation metadata, and affected
consumers with the project's actual checks. Rerun only evidence affected by
subsequent changes.

Have the existing independent review account for the old guidance and verify
new factual claims against sources. When an uncovered removal could change
behavior, add a preservation case and run it in fresh sessions. Repeat uncertain
cases enough to expose variation; retain or restore necessary guidance when
evidence is insufficient. A successful no-skill example supports only that case.

Use [Review Fix Loop](../../review-fix-loop/SKILL.md) for agent-procedure changes.
That workflow owns reviewer selection and rounds; this reference adds no second
review loop. Route a discovered failure to its cause: an unreachable pointer,
wrong placement, missing instruction, faulty tool, or invalid check.

Accept when preserved requirements pass and the requested improvement has
appropriate evidence. Report the changes, checks, removed/relocated knowledge,
tool dependencies, and remaining gaps. For measured claims, retain raw outcomes
and comparable conditions using [evaluation](evaluating-skills.md).
