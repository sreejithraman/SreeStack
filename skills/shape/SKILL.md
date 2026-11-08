---
name: shape
description: Shape a rough idea into a settled brief, or a spec for several outcomes, through conversation before anything is built.
disable-model-invocation: true
---

# Shape

Turn a rough idea into ready work through conversation and evidence. Start from
the user's idea and the sources they point to. Leave one settled brief, or one
spec when the idea holds several outcomes, in a record the user can open. You
are done when every decision that changes the outcome is settled, except one
recorded as the question Try will answer, and the brief or spec is usable, or
the user drops the idea and the record says why.

You own the conversation, the record, which capability to use next, and the
stop. Each linked skill owns its own procedure and returns to you. Shaping builds
nothing for production: [Implement](../implement/SKILL.md) or
[Chief of Staff](../chief-of-staff/SKILL.md) does that after you stop.
Invoking Shape with an idea asks you to shape it, not build it; only an explicit
ask to build or implement is a build request.

## The record

Keep one record for the whole shaping. Reuse an existing spec or task record you
are authorized to write. Otherwise keep a task-owned Markdown draft outside the
repo, in the host's scratch space, and link its absolute path in the thread. Move
it to project docs or the tracker only when the user asks. Keep drafts out of
the glossary and ADRs.

The record holds:

- **Status:** Draft, Settled, or Dropped.
- **Sources and evidence:** links to the idea's sources, research notes,
  prototypes, and captures.
- **The brief** in [Reframe](../reframe/SKILL.md)'s contract, with each decision
  written into the part it changes as soon as the user makes it. Keep a rejected
  option only when its reason will matter later.
- **Open questions:** each with what it blocks.

Keep no transcript and no separate decision log. Show the user the record when a
decision changes it.

## 1. Ground and frame

Read the idea, the sources it names, and the code and records it touches. When
the outcome, proof, and scope are already clear, say so. A clear single outcome
needs no record: route the request as its brief under
[stage 5](#5-show-and-route). Clear work with several outcomes opens the record
and goes to [stage 4](#4-settle-ready-work) for its spec. Otherwise form the
first brief with Reframe and open the record as Draft.

Done when the desired change, its sources, and the next uncertainty are explicit,
and the record's path is in the thread. For a clear single outcome, done when
Implement has the request or the user has the offer.

## 2. Resolve what matters

Take the open question that would change the outcome most, and route it:

| The question needs | Use |
| --- | --- |
| A choice only the user can make | [Grilling](../grilling/SKILL.md) |
| A fact | Look it up, or [Research](../research/SKILL.md) for a cited answer |
| Seeing it, including a feel such as "less cluttered" | [Stage 3](#3-try-a-direction-when-seeing-helps), before abstract preference questions |
| Agreed terms, or a decision worth an ADR | [Domain Modeling](../domain-modeling/SKILL.md) |
| A consequential interface or ownership design | [Architect](../architect/SKILL.md), design only |

Specialists are optional; use one only when its question is open. Write each
answer into the record. When the outcome or its proof changes, run Reframe again
on what changed. Keep doing safe, reversible discovery while a question waits.

Done when no open decision would change the outcome, or each one left names
exactly what it waits on.

## 3. Try a direction when seeing helps

When trying an interface would change the decision, build the options with
[Prototype](../prototype/SKILL.md) and put them in front of the user with
[Show Me](../show-me/SKILL.md). Give Prototype the record as the place for its
verdict. Then keep talking: trying a direction is part of the conversation, and
a prototype grants no permission to ship.

Done when the user can open each option, the evidence tells them apart, and the
verdict and the prototype's disposition are in the record.

## 4. Settle ready work

Every intended outcome needs its proof, covered code, preserved behavior, out of
scope, inputs and access, decisions and assumptions, and one finish-line field:
the line the user requested, or else a line marked proposed with its reason, from
Implement's
[finish-line policy](../implement/SKILL.md#2-state-the-finish-line-and-prepare).
A question only trying the built thing can answer, such as a visual direction,
doesn't block Settled: record it as the question Try will answer, and propose
Try. A settled brief is not Land by itself; the execution owner states its finish
line when it starts.

For one outcome, reconcile the brief with Reframe. For several, turn the same
record into one spec with [To Spec](../to-spec/SKILL.md). Splitting the spec into
tasks stays with the chief.

Mark the record Settled without a separate approval. Showing the settled
record with the offer or handoff in stage 5 is the user's chance to correct it;
a correction reopens the record as Draft.

When the user drops the idea, mark the record Dropped with the reason and what
was learned. When something outside the conversation blocks settling, leave the
record as Draft with the exact gap and what it blocks.

Done when the record is Settled and every outcome has each field above, with no
open choice that would change one other than a recorded Try question.

## 5. Show and route

Show the record with Show Me. When the user already asked to build, hand the
record to Implement for one outcome or to Chief of Staff for a spec, without
asking again. Otherwise offer that step. Publish to a tracker only when the user
asks.

After a handoff, the execution owner carries the conversation, including a Try
result. Keep the record as its input; don't restart shaping or copy the record.

Done when the user can open the final record, and the next owner has it or the
user has seen the offer.
