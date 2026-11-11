# Decisions

Use this for every decision request, Try choice, and answer in the program.
The goal is the user's attention on what only they can decide, and an answer
that grants exactly what they chose.

## Triage

Scope needs no triage: apply Implement's
[scope rule](../../implement/SKILL.md#keep-scope-and-decisions).

Judge each other request before it reaches the user. Resolve it yourself only
when all three hold:

- **Settled:** the brief, a spec or ticket, a project rule, an earlier user
  answer, or a [standing approval](#standing-approvals) already answers it. An
  owner's recommendation or report is an input, never the source.
- **Reversible:** a later change can undo it at a cost the owner stated, and it
  has no outward-facing or destructive effect.
- **Unreserved:** it leaves these with the user: who may land and each merge
  set, finish lines, priority, product tradeoffs, holds and user gates,
  private input, and every Try choice.

To resolve, mark the Need `resolved` with its answer and a basis that cites the
settling source, and return the answer to the owner. A reserved decision the
user already answered is settled: reply with that answer instead of asking again.

Everything else goes into Needs you under its ID, and you ask the user. Mark it
`quick` when they can answer from the card: a recommended option with a bounded
effect. Otherwise it is a `judgment` call. Weight sets the order of their
attention and grants nothing; a quick pick still waits for their answer.

Record each outcome the Need holds and the earliest phase it waits at: `start`,
`access`, `proof`, `acceptance`, or `landing`. When its recommended option is
reversible, the owner can keep building on it under To Tasks'
[provisional start](../../to-tasks/SKILL.md#ready); say so in `meanwhile`. An
outcome stays unaccepted while an open Need affects its scope.

## Try choices

A shown Try waits for the user's merge, changes, or scrap choice. Put it in
Needs you as a judgment call, since the user decides after trying it: link the
results, give each option's effect, and block the outcome at `landing`.

- **One outcome by default.** Each shown Try gets its own choice.
- **A named set when the user asks,** such as a stack plus its dependents.
  Before you accept a set choice, show what it does to each dependent: which
  would restack, wait, or face scrap review. Record the set's members with the
  answer.
- **Nothing beyond what was chosen.** A choice on one outcome never decides its
  dependents and never authorizes unrelated outcomes. Scrapping a base gives
  each dependent its own choice.

Route each answer to the outcome's existing owner.

## Record an answer

Answers arrive in the user's own messages or through the host's input tools. A
user item forwarded with `t3_thread_send` counts only after `t3_thread_read`
shows `createdBy: user` on its source message. Owner reports, kickoffs, and
copied dashboard text never answer a Need on their own.

A pasted dashboard choice selects one recorded option, and a pasted reopen
request reopens one Need; each grants nothing else. Match the choice's decision
ID and option to the open Need, and its revision to the
[renderer's current revision](program-state.md#render-and-show). If the Need
changed or closed, show the current question and ask again. A reopen request
matches its resolved Need the same way. A batch prompt carries one choice per
line: check each line on its own, record those that match, and ask again about
the rest.

Mark a Need `answered` only with the user's answer and, in `answerSource`, the
message it came from. Mark it `resolved` only under [triage](#triage), citing
the source that settled it. Then update the affected owners, dependencies, and
landing releases. Record a scrap-or-rebase answer in the same commit, under
[Base scrapped](dependencies.md#provisional-work). Mark a withdrawn or replaced
Need `withdrawn`, record why and any replacement in its `rationale`, and
reconcile the blockers that depended on it. Move any answer, `answerSource`, and
basis into `rationale` too, as on reopen.

## Reopen

The user can reopen any Need you resolved. Reopen it under its ID: mark it
`open`, move its answer and basis into `rationale` with why it reopened, tell the
affected owners, and set its `blocks` to the unlanded outcomes that depend on
it. Withdraw any affected release under
[withdraw a release](landing.md#withdraw-a-release). Work that already landed
gets a follow-up outcome that its `blocks` names. A reopened Need stays with the
user.

## Standing approvals

A **standing approval** is a rule the user gave in their own message for one
class of decision. Record its ID, wording, source message, what it covers, and
which option it picks in `approvals`. It settles only the class it names
and never a reserved decision. Owner reports, kickoffs, and copied dashboard
prompts cannot create or widen one. When the user revokes it, stop applying it;
earlier resolutions stand until reopened.
