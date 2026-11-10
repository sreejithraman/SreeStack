# Program record and command center

Specs, tickets, snips, PRs, and user decisions stay where the project already
keeps them. The **program record** is one file, `program.json`, that links those
sources and holds the program's coordination state. Its top-level fields are
what the **command center** shows; its `record` object holds everything the page
never shows. Each fact has one home in it.

## Program record

Keep `program.json` and a `reports/` folder in a task-owned directory that the
chief and its owners can read and that survives worktree cleanup. Adopt an
existing program's file rather than starting another. Put its absolute path in
the chief's handoff and every owner kickoff.

The program folder is a git repository, and its log is the record's history.
When you create or adopt a program in a folder that is not one yet, run
`git init` there and commit `program.json` once it passes the check. Keep the
file indented one value per line, as the [example](../assets/example-state.json)
is, so each change shows in `git diff`.

**One writer:** owners write only their own `reports/<outcome ID>.md`. The
current chief alone writes `program.json`. Before each write, confirm
`record.chief` still names this thread; otherwise, or if the file fails to load,
follow [check the chief](chief-move.md#check-the-chief).

### Write the record

Record each owner report, answer, direction, and decision in one write, before
you reply or move on:

1. Copy the live file to a unique temp file beside it, then edit only what
   changed in the copy. Never regenerate the whole file; that silently drops
   history.

   ```bash
   mktemp /absolute/path/.program.json.XXXXXX   # prints <temp>
   cp /absolute/path/program.json <temp>
   ```

   Set `updatedAt` to the time of this write if it changes anything outside
   `record`; a write that changes only `record` keeps `updatedAt`, so open
   pages stay put.
2. Check it from this skill's folder, and fix every error it reports. On the
   first write, start a new file.

   ```bash
   python3 scripts/render_dashboard.py --state <temp> --check
   ```

3. Move it into place and read what changed:

   ```bash
   mv <temp> /absolute/path/program.json
   git -C /absolute/path diff program.json
   ```

   A removed or changed line the event didn't call for is a mistake. Restore it
   from `git -C /absolute/path show HEAD:program.json` and check `program.json`
   again. Mark a change to a history entry in place instead of deleting it.
4. Commit with a message naming the event:

   ```bash
   git -C /absolute/path add program.json && git -C /absolute/path commit -m "R2 report: PR 12 open"
   ```

The hosted page shows the new state on its next request.

### Where each fact goes

For the program:

| Fact | Field |
| --- | --- |
| The goal | `goal` |
| A program-wide finish-line note, such as who decides merges | `finishLine` |
| The original request and its message sources | `record.request` |
| Accepted corrections | `record.corrections` |
| Preserved requirements | `record.requirements` |
| The agreed scope that Land's authority covers, and its gates | `record.landingAuthority` |
| Standing directions, and holds with the condition that releases each | `record.directions`, a hold's release in `until` |
| Standing approvals | `record.approvals` |
| Accepted tradeoffs, with what would prompt revisiting them | `revisits` |
| A decision request's question, options, blocked outcomes and phases, status, answer, and basis | `needs` |
| A decision request's date, originating owner and message, and reasoning, including superseded reasoning | `record.decisions`, under the Need's ID |
| A decision with no Need in the file, such as a withdrawn one or a chief call on the plan | `record.decisions`, with its `question`, `affects`, and `disposition` |
| A discovery that became work | That row's `origin` and `description` |
| Any other discovery, with its origin and route | `record.discoveries` |
| Support work, and the outcomes it unblocks | A `support` row, named in their `blockedBy` or `blocked` |
| The current chief thread | `record.chief` |
| Hosting | `record.hosting` |
| The next useful action | `record.next` |

For each outcome, under its stable ID:

| Fact | Field |
| --- | --- |
| Ticket sources | `tickets` |
| Snip and message sources | `record.outcomes[ID].sources` |
| The result it delivers | `description` |
| The code it covers, its proof, and what it leaves to other outcomes | `record.outcomes[ID].scope` |
| The picked and effective finish lines | `finishLine`, `effectiveFinishLine` |
| Why that finish line | `record.outcomes[ID].why` |
| The owner's name and session link | `owner`, `sessionUrl` |
| The owner's task IDs, start mode, return route, report path, model, workspace, servers with their stop actions, and handled follow-up messages | `record.owners[ID]` |
| Logical dependencies | `blockedBy` |
| Branch order | Each layer's `stackedOn` |
| Another block, with what is missing and who can supply it | `blocked`, or a Need's `blocks` |
| What it rests on provisionally, what clears it, and what continues meanwhile | `provisional`, or the Need's `meanwhile` |
| Each PR, branch, or local artifact, with link, head, base, and stack parent | `layers` |
| What the owner showed and what opening it needs | `results` |
| Pending PRs, live helpers and watchers, and the events they await | `record.waits` |
| The merge set, lander, target branch, accepted head and base per PR, submission or queue state, resources dependents still need, and the release state | `record.landings` |
| Acceptance evidence links | `evidence` |
| Blocked or untested assertions in its proof | `record.outcomes[ID].acceptance` |
| The delivery state | `state` |
| A stop for the user | An open Need |

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
| Proof | `evidence`, and every blocked or untested assertion in `record.outcomes[ID].acceptance` |
| Shown | `results` with access limits; servers and stop actions in `record.owners[ID].resources` |
| Waits | `record.waits`, naming the pending PRs this thread watches |
| Decisions | `needs` with the phase each blocks, `record.decisions`, and `provisional` assumptions |
| Follow-ups | A work row or `record.discoveries`, each with its disposition |
| Sources | `record.owners[ID].handled`, so no message is answered twice |

Also record task IDs an owner returns when it resumes in `record.owners[ID].tasks`.

## Command center

Before each write, read the relevant owner reports, user direction, tickets,
and live forge state. Each work row carries the time its state was last
observed, separate from the file's `updatedAt`. Keep an unchecked row's
old observation time; use `unknown` with `unknownReason` when its state cannot be
read.

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
`meanwhile`.

The file carries all open and resolved Needs, so each resolved one stays
reopenable; answered ones may remain. Omit a withdrawn or superseded Need only
after recording its disposition. If work lands while a Need about it is open,
keep the landed row and point the Need's `blocks` at a follow-up row for any
change the answer requires.

### File format

`program.json` is one JSON object. Fields without `?` are required. Times are
ISO timestamps with a timezone, such as `2026-11-02T17:00:00Z`. Omit absent
optional fields rather than sending empty strings. IDs are unique within each
collection, and layer IDs are unique across the program.

```ts
type Link = { label: string; url: string };
type ProgramState = Snapshot & { record: ProgramRecord };
type Snapshot = { // what the page shows
  title: string;
  goal: string;
  finishLine?: string; // a program-wide note, such as who decides merges
  updatedAt: string; // the last write that changed what the page shows
  demo?: boolean;   // true only for an illustrative example
  needs: Need[];
  work: Work[];
  revisits?: Revisit[];
};
type Phase = "start" | "access" | "proof" | "acceptance" | "landing";
type Need = {
  id: string; ask: string;
  context?: string[];
  meanwhile?: string; // what continues while it is open
  recommendation?: string; // rationale for the recommended option, or a suggestion when there are no options
  options?: { label: string; effect: string; recommended?: boolean }[]; // at most one recommended
  weight?: "quick" | "judgment"; // default judgment; quick needs two or more options and a recommended one
  blocks?: { id: string; phase: Phase }[]; // one entry per outcome, at the earliest phase it waits
  links?: Link[];
  status: "open" | "answered" | "resolved"; // resolved: the chief settled it
  answer?: string; // required unless open
  basis?: string; // required when resolved: what settled it and why it is reversible
};
type Work = {
  id: string; title: string; repo: string;
  description?: string; // one or two sentences of scope
  kind: "outcome" | "follow-up" | "support";
  state: "planned" | "building" | "shown" | "in-review" | "ready"
    | "landed" | "done" | "scrapped" | "unknown";
  finishLine?: "land" | "try" | "pr-review" | "pr-draft"; // required unless support
  effectiveFinishLine?: "try"; // required when provisional work's finish line is land; it keeps any PR it already has
  owner?: string; sessionUrl?: string; // owner required while building, shown, in review, or ready
  provisional?: { basis: string; clears: string; on?: string[] }; // on: outcome IDs it rests on
  layers?: Layer[]; // bottom first; not on support
  results?: (Link & { access?: string })[]; // what the owner showed, and what opening it needs
  tickets?: Link[];
  blockedBy?: string[];
  blocked?: string; // another active blocker, such as an external dependency
  unknownReason?: string; // why the state could not be read; unknown rows only
  updatedAt: string; // last observation supporting this row
  evidence?: Link[];
  required?: boolean; // false marks proposed work outside committed scope
  origin?: string;
};
type Layer = {
  id: string; branch: string;
  status: "local" | "draft" | "open" | "ready" | "merged" | "closed"; // closed: without merge
  url?: string; // the PR; required unless local
  head?: string; base?: string;
  stackedOn?: string; // the layer below, in this or another outcome
};
type Revisit = {
  id: string; title: string; tradeoff: string; revisit: string;
  source?: string; // decision ID or source reference
};

// What the page never shows. Dates are YYYY-MM-DD or timestamps; prose is markdown.
type Entry = { date: string; source: string; text: string };
type ProgramRecord = {
  chief: string; // the current chief thread
  request: { text: string; sources?: string[] };
  corrections?: Entry[];
  requirements?: Entry[];
  approvals?: (Entry & { id: string; covers: string; picks: string })[];
  directions?: (Entry & { until?: string })[]; // until: what releases a hold
  landingAuthority?: Entry;
  landings?: Landing[];
  outcomes?: { [workId: string]: { sources?: string[]; scope?: string; why?: string; acceptance?: string } };
  owners?: { [workId: string]: Owner };
  waits?: { date: string; on: string; event: string; work?: string; watcher?: string }[];
  decisions?: Decision[];
  discoveries?: { date: string; origin: string; text: string; route: string }[];
  hosting?: { url: string; server?: string; serve?: string; stop?: string; access?: string };
  next: string;
};
type Owner = {
  start: "top-level" | "delegated" | "adopted"; route: string; report: string;
  tasks?: string[]; model?: string; workspace?: string;
  resources?: string; // servers, ports, and databases, with their stop actions
  handled?: string[]; // follow-up messages already handled
};
type Landing = {
  id: string; date: string; chief: string; lander: string; target: string;
  work: string[]; prs: { url: string; head: string; base: string }[];
  state: "released" | "submitted" | "landed" | "withdrawn";
  keep?: string; // resources dependents still need
  note?: string; // such as why it was withdrawn
};
type Decision = {
  id: string; date: string; source: string; owner?: string; rationale?: string;
  question?: string; affects?: string[]; disposition?: string; // only when no Need has this ID
};
```

The renderer rejects a file whose page claims more than the record supports:
provisional work that merged, keeps Land, or claims ready on any finish line; a
Try finish line with a published PR; a shown Try with nothing to open; a ready
outcome with a layer short of its finish line; a landed outcome with an unmerged
layer; active work with no owner; a layer on another owner's unmerged layer
without a provisional mark; active work on a dead base, or a live layer on a
closed one, without a halting Need; a `start` Need on work that started; and
dangling or cyclic edges, including work blocked by itself. In `record`, it
checks each field's shape, that per-outcome entries, waits, and landings name
existing rows, and that a decision whose Need is in the file leaves the
question, affects, and disposition to that Need.

Write each `description` from the outcome's scope, not its title or the owner's
next step. Store returned T3 thread links verbatim and use only real ticket, PR,
result, and artifact links.

### Render and show

The scripts need Python 3 and no third-party packages. `--check` (under
[write the record](#write-the-record)) and the
[dashboard server](hosting.md) render with the same code: it validates the file,
escapes content, and stamps the page with a digest that open pages compare to
spot a change. It makes no tracker, forge, or session changes. The
[example file](../assets/example-state.json) uses fictional work.

Each copied choice or reopen request names its decision's revision, a digest of
the whole Need. Two or more open quick picks add a batch prompt that takes every
recommendation. Print a Need's current revision with:

```bash
python3 scripts/render_dashboard.py --state /absolute/path/program.json --revision <decision ID>
```

Deliver the page through [dashboard hosting](hosting.md), never inline in T3 or
another chat surface.
