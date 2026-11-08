---
name: to-spec
description: "Turn the settled conversation into a spec in its shaping record, and publish it to the issue tracker when you ask."
disable-model-invocation: true
---

# To Spec

Write down what the conversation settled as one spec an execution owner can
start from. Start from a conversation or shaping record whose outcomes are
settled. Leave the spec in that record, and in the issue tracker only when the
user asks. You are done when every settled outcome is in the spec with its
proof, covered code, exclusions, assumptions, and requested finish line, and
the user can open it.

This is synthesis, not an interview. Take each decision from the conversation,
the record, and the code, and don't ask it again. Ask only for a missing decision
that would change the spec and that nothing settled answers. Group those into
one round under [Grilling](../grilling/SKILL.md)'s rules.

## Process

1. **Read what is settled.** Read the record, the conversation, and enough of
   the code to name what each outcome covers. Use the project's domain glossary
   vocabulary throughout the spec, and respect any ADRs in the area you're
   touching.

2. **Settle the test seams.** Reuse seams the conversation or record already
   settled. Otherwise sketch them: prefer existing seams to new ones, use the
   highest seam possible, and propose any new seam at the highest point you
   can. The fewer seams across the codebase, the better; the ideal number is
   one. Check new seams with the user in the same round as any other missing
   decision.

3. **Write the spec into the record.** Replace the brief in the shaping record
   with the spec, so one copy exists. Without a shaping record, choose its home
   by Shape's [record rule](../shape/SKILL.md#the-record). Use the template below.

4. **Publish only on request.** When the user asks to publish, use the issue
   tracker the user or project configuration supplies. If a required choice
   remains unknown, ask the user to supply it or run `/setup-sreestack`. Then
   replace the spec in the record with a link to the issue, which is now the
   authoritative copy.

<spec-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## Outcomes

One entry per settled outcome:

- **Outcome:** the change and who it serves.
- **Proof:** each claim's independent expected result and how to run it, or the
  qualitative criteria and judge.
- **Covers:** the modules, and paths where they pin down scope, that the outcome
  changes or must preserve.
- **Out of scope:** what this outcome excludes.
- **Assumptions:** what it rests on that nobody confirmed.
- **Finish line:** the line the user requested, or else a line marked proposed,
  with its reason.

## User Stories

A numbered list of user stories covering the settled behavior: one per distinct
actor and need, and none the settled coverage lacks. Each user story should be in
the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Name modules and interfaces. Give file or directory paths where they pin down
scope; leave out line numbers and code snippets, which go stale.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- The seams from step 2, and which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

What the whole spec excludes, beyond each outcome's own exclusions.

## Further Notes

Any further notes about the feature.

</spec-template>
