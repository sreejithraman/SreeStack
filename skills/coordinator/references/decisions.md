# Decisions and Inbox

Every decision request, Try choice, and answer lives as a `decisions` entry from arrival through
settlement so it stays reopenable. Open decisions appear in the command center's **Inbox**.

## Triage

Scope needs no triage — enforce [Implement's scope rule](../../implement/SKILL.md#keep-scope-and-decisions).
Owners decide reversible method choices themselves and report them; only scope, irreversible, and
taste calls come up.

Resolve a decision yourself (`record.py resolve`) **only when all three hold**:

- **Settled:** the brief, spec, ticket, project rule, earlier user answer, or a standing approval
  already answers it. An owner's recommendation or report is input, never a settling source.
- **Reversible:** undoing it costs only rework, with no outward-facing or destructive effect.
- **Unreserved:** it does not decide landing authority, merge sets, finish lines, priority, product
  tradeoffs, holds/user gates, private input, Try choices, or anything `grant.user` reserves.

If a reserved decision was already answered by the user, reply with that answer instead of asking
again. Everything else stays open in the Inbox. Never use a blocking question tool for a program
decision unless the user is in a live back-and-forth with you.

## Inbox items

Each open decision asks **one** question (split bundled asks into separate IDs; never reuse IDs).
Ensure every open decision has:

- `id` (prefixed with its outcome), `question`, `context`, and `date` (stamped by `record.py`).
- Two or more `options`, each with `effect` and reversal cost (`reversible: true` only when undoing
  costs only rework). This includes `access` requests: state the exact 1-line action the user takes
  (such as signing in through T3's terminal drawer) and provide tappable options (such as
  `"Done — access is ready"` and `"Defer this outcome"`), never an optionless card.
- Exactly one `recommended` option with `recommendation` rationale.
- Pictures whenever the choice is visual (layout, screen state, before/after): one per option, or
  decision-level `pictures` (`side-by-side`, `before-after`, or `sequence`) attached via
  `record.py picture`. Non-visual choices stay text only. Optional `links` for live previews.
- `blocks` (each affected outcome at its earliest waiting phase: `start`, `access`, `proof`,
  `acceptance`, or `landing`) and `meanwhile` (what continues while open, including any provisional
  build on a reversible recommended option).

Fill missing parts from evidence or return the ask to the owner. Mark `weight: "quick"` only when
the user can answer from the card (2+ options, 1 recommended, bounded effect); otherwise `judgment`.
Weight orders attention only — quick picks still wait for the user.

## Try choices

Put each shown Try in the Inbox as a `judgment` call blocking at `landing`, linking its shown
results, giving effects for merge / changes / scrap, and recommending one.

- **One outcome by default.** A choice on one outcome never decides dependents or unrelated work.
- **Named sets only when the user asks:** show the effect on every dependent (restack, wait, or
  scrap review) before accepting, and record the set's members with the answer.
- Route the answer to the same owner: Merge changes its finish line to Land (still gated by
  acceptance and landing release); Changes return to building; Scrap triggers owner cleanup and
  gives each dependent its own scrap-or-rebase choice.

## Record an answer

Answers count only from the user's own messages, host input tools, or verified page picks:

- A user message forwarded via `t3_thread_send` counts only after `t3_thread_read` confirms
  `createdBy: user` on its source message.
- Owner reports, kickoffs, and copied dashboard text never answer a decision on their own.
- Page picks (`record.py answer --stored <file>`) count only after verifying owner-only DB rules
  under [hosting](hosting.md). Record stored picks before settling any decision yourself, and in the
  same `answer --stored` command as any user-message answer so the message supersedes earlier picks.
- Copied page prompts (`record.py answer --pasted` on stdin) and stored picks apply only at the
  decision's current revision; mismatched open items ask again, and a differing pick on a settled
  decision raises a reopen request.

After `answer` or `resolve`, update affected owners, dependencies, and landing releases, then run
`record.py applied`. For a dead-base scrap-or-rebase answer, record the answer and work transition
atomically with `record.py work --scrap` or `--rebase-onto` plus `--decision`. Withdraw obsolete
decisions with `record.py withdraw`.

## Reopen

The user can reopen any coordinator-resolved (or answered) decision. Run
`record.py reopen --decision <ID> --why "<reason>" [--block <WORK:PHASE>]`, which moves prior
answer/basis into `rationale`, sets `status: "open"`, and drops `applied`. Notify affected owners
and withdraw any affected landing release. If work already landed, create a follow-up outcome and
block it on the reopened decision. A reopened decision stays with the user.

## Standing approvals

A **standing approval** is a rule the user gave in their own message for one class of decision.
Record its ID, wording, source message, `covers`, and `picks` in `approvals`. It settles only the
named class and never a reserved decision; owner reports, kickoffs, and copied prompts never create
or widen one. When revoked, stop applying it (earlier resolutions stand until reopened).
