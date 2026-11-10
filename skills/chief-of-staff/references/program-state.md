# Program record and command center

Specs, tickets, snips, PRs, and user decisions stay where the project already
keeps them. The **program record** is one file, `program.json`, that links those
sources and holds the program's coordination state, organized by topic. The
**command center** renders it; the renderer picks what the page shows. Each fact
has one home in the file.

## Program record

Keep `program.json` and a `reports/` folder in a task-owned directory that the
chief and its owners can read and that survives worktree cleanup. Adopt an
existing program's folder rather than starting another. Put the folder's
absolute path in the chief's handoff and every owner kickoff.

The program folder is a git repository. Its last commit is the record: the
command center and every reader use `HEAD`, and the log is its history. The
working `program.json` is only the chief's edit buffer. A new program starts
from a new `program.json`: run `git -C /absolute/path init`, then add and
commit `program.json` once it passes the check.

**One writer:** owners write only their own `reports/<outcome ID>.md`. The
current chief alone writes `program.json`, after it
[checks the chief](chief-move.md#check-the-chief).

### Write the record

Record each owner report, answer, direction, and decision in one write, before
you reply or move on:

1. Look for an earlier uncommitted change:

   ```bash
   git -C /absolute/path status --porcelain -- program.json
   ```

   Any output means a failed commit or an outside edit. Show the user
   `git -C /absolute/path diff HEAD -- program.json` and settle it with them
   before you build on it. If they keep it, check and commit it; otherwise run
   `git -C /absolute/path checkout HEAD -- program.json`.
2. Edit `program.json` in place, changing only what the event changed. Never
   regenerate the whole file; that silently drops history.
3. Check it from this skill's folder, and fix every error it reports. When only
   the layout is wrong, run the command it prints.

   ```bash
   python3 scripts/render_dashboard.py --state /absolute/path/program.json --check
   ```

4. Read `git -C /absolute/path diff -- program.json`. A removed or changed line
   the event didn't call for is a mistake. Restore it and check again. Mark a
   change to a history entry in place instead of deleting it.
5. Commit with a message naming the event:

   ```bash
   git -C /absolute/path commit -m "R2 report: PR 12 open" program.json
   ```

6. [Publish the command center](hosting.md), except after a
   [chief move](chief-move.md), where the new chief publishes.

A write is done when its commit lands and its page is published. On a git or
publish error, stop and report it to the user.

### File format

`program.json` is one JSON object. Fields without `?` are required. Times are
ISO timestamps with a timezone, such as `2026-11-02T17:00:00Z`; dates are
`YYYY-MM-DD` or timestamps. Prose is markdown. Omit absent optional fields rather
than sending empty strings. IDs are unique within each collection, and layer IDs
are unique across the program. The [example file](../assets/example-state.json)
uses fictional work.

```ts
type Program = {
  title: string; goal: string;
  finishLine?: string; // a program-wide note, such as who decides merges
  demo?: boolean; // true only for an illustrative example
  chief: string; // the current chief thread
  hosting?: string; // the command center artifact's link
  next: string; // the next useful action
  request: { text: string; sources?: string[] }; // the original request and its message sources
  corrections?: Entry[]; // accepted corrections
  requirements?: Entry[]; // preserved requirements
  approvals?: (Entry & { id: string; covers: string; picks: string })[]; // standing approvals
  directions?: (Entry & { until?: string })[]; // standing directions; until: what releases a hold
  landingAuthority?: Entry; // the agreed scope Land covers, and its gates
  decisions: Decision[];
  work: Work[];
  revisits?: Revisit[];
  discoveries?: { date: string; origin: string; text: string; route: string }[];
  landings?: Landing[];
  waits?: { date: string; on: string; event: string; work?: string; watcher?: string }[];
};
type Entry = { date: string; source: string; text: string };
type Link = { label: string; url: string };
type Phase = "start" | "access" | "proof" | "acceptance" | "landing";

type Decision = {
  id: string; question: string;
  date: string; source: string; // when it arrived, and the report or message that raised it
  status: "open" | "answered" | "resolved" | "withdrawn"; // resolved: the chief settled it
  context?: string[];
  meanwhile?: string; // what continues while it is open
  recommendation?: string; // rationale for the recommended option, or a suggestion when there are no options
  options?: { label: string; effect: string; recommended?: boolean }[]; // at most one recommended
  weight?: "quick" | "judgment"; // default judgment; quick needs two or more options and a recommended one
  blocks?: { id: string; phase: Phase }[]; // one entry per outcome, at the earliest phase it waits
  links?: Link[];
  answer?: string; // required when answered or resolved
  basis?: string; // required when resolved: what settled it and why it is reversible
  rationale?: string; // dated reasoning the page omits, such as why it reopened; when withdrawn, why and any replacement
};

type Work = {
  id: string; title: string; repo: string;
  kind: "outcome" | "follow-up" | "support";
  state: "planned" | "building" | "shown" | "in-review" | "ready"
    | "landed" | "done" | "scrapped" | "unknown";
  description?: string; // the result it delivers, in one or two sentences
  scope?: string; // the code it covers, its proof, and what it leaves to other outcomes
  sources?: string[]; // snip and message sources
  tickets?: Link[];
  finishLine?: "land" | "try" | "pr-review" | "pr-draft"; // required unless support
  finishLineReason?: string;
  effectiveFinishLine?: "try"; // required when provisional work's finish line is land; it keeps any PR it already has
  owner?: Owner; // required while building, shown, in review, or ready
  provisional?: { basis: string; clears: string; on?: string[] }; // on: outcome IDs it rests on
  layers?: Layer[]; // bottom first; not on support
  results?: (Link & { access?: string })[]; // what the owner showed, and what opening it needs
  evidence?: Link[]; // acceptance evidence
  acceptance?: string; // blocked or untested assertions in its proof
  blockedBy?: string[]; // logical inputs not yet satisfied
  blocked?: string; // another active blocker, with what is missing and who can supply it
  unknownReason?: string; // why the state could not be read; unknown rows only
  checkedAt: string; // when its state was last observed
  required?: boolean; // false marks proposed work outside committed scope
  origin?: string; // the outcome or discovery it came from
};
type Owner = {
  name: string; session?: string; // session: the owner's thread link
  start: "top-level" | "delegated" | "adopted"; route: string; report: string;
  tasks?: string[]; model?: string; workspace?: string;
  resources?: string; // servers, ports, and databases, with their stop actions
  handled?: string[]; // follow-up messages already handled
};
type Layer = {
  id: string; branch: string;
  status: "local" | "draft" | "open" | "ready" | "merged" | "closed"; // closed: without merge
  url?: string; // the PR; required unless local
  head?: string; base?: string;
  stackedOn?: string; // the layer below, in this or another outcome
};
type Revisit = { // an accepted tradeoff
  id: string; title: string; tradeoff: string; revisit: string;
  source?: string; // decision ID or source reference
};
type Landing = {
  id: string; date: string; chief: string; lander: string; target: string;
  work: string[]; prs: { url: string; head: string; base: string }[]; // accepted head and base per PR
  state: "released" | "submitted" | "landed" | "withdrawn";
  keep?: string; // resources dependents still need
  note?: string; // such as the queue state, or why it was withdrawn
};
```

Each decision request is a **Need**: one `decisions` entry from arrival to
answer, kept after it settles so it stays reopenable. Some facts have a less
obvious home:

| Fact | Home |
| --- | --- |
| A stop for the user, including a Try choice | An open Need |
| A chief call on the plan with no question for the user | A `resolved` decision |
| A discovery that became work | That row's `origin` and `description` |
| Support work, and the outcomes it unblocks | A `support` row, named in their `blockedBy` or `blocked` |
| Branch order | Each layer's `stackedOn`, apart from `blockedBy` |
| What provisional work continues meanwhile | `provisional`, or the Need's `meanwhile` |

Date entries and cite their sources. Code claims name the repository and
revision they describe. Recheck current facts at their source before acting on
them. [Decisions](decisions.md) say when a Need is answered, resolved, reopened,
or withdrawn.

### Owner reports

Read each report against Implement's [report](../../implement/SKILL.md#report)
fields; ask no other format. Record, from each:

| Report field | Record it under |
| --- | --- |
| Outcome and finish line | `finishLine` and `state` |
| Layers | `layers`, after checking each head and base at the forge |
| Proof | `evidence`, and every blocked or untested assertion in `acceptance` |
| Shown | `results` with access limits; servers and stop actions in `owner.resources` |
| Waits | `waits`, naming the pending PRs this thread watches |
| Decisions | `decisions` with the phase each blocks, and `provisional` assumptions |
| Follow-ups | A work row or `discoveries`, each with its disposition |
| Sources | `owner.handled`, so no message is answered twice |

Also record task IDs an owner returns when it resumes in `owner.tasks`.

## Command center

Before each write, read the relevant owner reports, user direction, tickets,
and live forge state. Set a row's `checkedAt` when you observe its state. Keep an
unchecked row's old time; use `unknown` with `unknownReason` when its state
cannot be read.

A row is an outcome, a follow-up (an outcome that came from another one, with
its own finish line), or a support task. Count an outcome once whatever its
layers. Outcome states:

- `planned`: not started. `building`: building and proving.
- `shown`: a Try result built, proved, and shown, waiting for the user's merge,
  changes, or scrap choice. It needs `results`.
- `in-review`: a PR is open while review or CI continues.
- `ready`: every layer at readiness for its finish line: ready or merged for
  Land or a review-ready PR, a draft or merged for a draft PR. Provisional work
  is never ready, on any finish line: one that reaches its requested PR state
  stays `in-review` with its Provisional badge. Shown under In review with a
  readiness badge.
- `landed`: every layer confirmed merged. `scrapped`: the user scrapped it, or it
  was declined or made obsolete; the record says which.
- `done`: completed support work. An outcome never uses `done`.

`blockedBy` lists logical inputs not yet satisfied under the
[dependency rule](dependencies.md#dependencies); drop an edge once it is. A
layer's `stackedOn` names the layer below it. When that layer belongs to another
owner's outcome and is unmerged, the dependent is provisional on that outcome.
An outcome that was published before it became provisional, through a later
decision or adoption onto another owner's PR, keeps its PR layers; only a Try
finish line forbids them.

A base is the outcome that work rests on through `provisional.on` or a live
layer's `stackedOn`. A base is **dead** when it was scrapped, or when it has not
landed and every one of its layers is closed; one closed layer beside a live or
merged one does not count. Active work on a dead base, whether provisional or
the same owner's stack, needs an open Need, such as its scrap-or-rebase choice,
that halts it at `start`, `access`, or `proof`. The card shows the base once, as
a Scrapped base or Closed base blocker. A live layer stacked on a closed layer of
a base that is still alive needs the same Need, or a restack.
Before marking a row terminal, clear its active blockers and open Needs; history
stays in the record. Unresolved work stays visible even after its owner failed
or its PR was abandoned.

Each Need's `blocks` names the outcomes it holds and the earliest phase each
waits at: `start`, `access`, `proof`, `acceptance`, or `landing`. The first three
halt that outcome's work. `acceptance` and `landing` let building and proof
continue, so a shown Try waiting for its choice or a provisional build carries
an open Need without being blocked. Put what continues meanwhile in
`meanwhile`. If work lands while a Need about it is open, keep the landed row and
point the Need's `blocks` at a follow-up row for any change the answer requires.

The page shows open, answered, and resolved Needs, work, and tradeoffs, and
leaves out withdrawn Needs, decision history, owner plumbing, and program facts
other than the title, goal, and finish line. Its Updated time is the commit that
last changed it.

`--check` rejects a file whose claims the record doesn't support:
provisional work that merged, keeps Land, or claims ready on any finish line; a
Try finish line with a published PR; a shown Try with nothing to open; a ready
outcome with a layer short of its finish line; a landed outcome with an unmerged
layer; active work with no owner; a layer on another owner's unmerged layer
without a provisional mark; active work on a dead base, or a live layer on a
closed one, without a halting Need; a `start` Need on work that started; an open
Need on finished work; a withdrawn Need without its rationale; and dangling or
cyclic edges, including work blocked by itself and waits or landings that name
missing work.

Write each `description` from the outcome's scope, not its title or the owner's
next step. Store returned T3 thread links verbatim and use only real ticket, PR,
result, and artifact links.

### Render and show

The scripts need Python 3 and no third-party packages. They make no tracker,
forge, or session changes.

Each copied choice or reopen request names its decision's revision, a digest of
what the page shows for that Need. Two or more open quick picks add a batch
prompt that takes every recommendation. Print a Need's revision at `HEAD` with:

```bash
python3 scripts/render_dashboard.py --state /absolute/path/program.json --revision <decision ID>
```
