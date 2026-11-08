# Program record and command center

Specs, tickets, snips, PRs, and user decisions stay where the project already
keeps them. The **program record** links those sources and adds coordination
state. The **command center** is a rendered snapshot of that record, not a second
tracker.

## Program record

Reuse an established record, or choose a task-owned directory that the chief and
its owners can read and that survives worktree cleanup. Put its absolute path in
the chief's handoff and every owner kickoff. It needs no wiki or committed state
file.

**One writer:** owners write only their own `reports/<outcome ID>.md`. The
current chief alone writes the rest of the record and the snapshot. Before each
write, confirm the record still names this thread as chief; otherwise follow
[chief move](chief-move.md).

Keep, for the program:

- The goal, original request and message sources, accepted corrections,
  preserved requirements, the agreed scope that Land's authority covers, and
  holds with their source and release condition.
- Standing approvals, accepted tradeoffs with what would prompt revisiting them,
  and decision requests with their dispositions.
- Discoveries with origin and destination, and support work with the owners it
  affects.
- The current chief thread, the snapshot state and HTML paths, hosting details,
  and the next useful action.

Keep, for each outcome under its stable ID:

- **Sources:** the ticket, snip, PR, or message IDs it came from.
- **Scope:** the result, the code it covers, its proof, and what it leaves to
  other outcomes.
- **Finish line:** the picked line (Land, Try, review-ready PR, or draft PR) and
  why, and the effective line while it is provisional.
- **Owner:** identity, thread or task IDs and links, start mode (delegated,
  top-level, or adopted), return route, report path, model, and workspace. An
  outcome can be planned without one.
- **Inputs:** logical dependencies, branch-order constraints, and any blocks
  with what is missing, who can supply it, and what it blocks.
- **Provisional:** the branch, PR, or assumption it rests on, the decision or
  landing that clears it, and what may continue meanwhile.
- **Layers:** each PR, branch, or local artifact, with its link, head, base,
  and stack parent.
- **Results:** what the owner showed and how to open it, with what that needs.
- **Waits:** pending PRs, live helpers and watchers, and the events they await.
- **Landing:** the merge set, its one lander, target branch, pending submission
  or queue state, and the landing release (issuing chief, lander, accepted
  head/base per PR, resources dependents still need, active or withdrawn).
- **Disposition:** acceptance evidence, the delivery state, and any stop for the
  user.

Date decisions and cite their sources. Code claims name the repository and
revision they describe. Keep superseded reasoning when it explains a tradeoff,
and recheck current facts at their source before acting on them.

Each decision request keeps its ID, originating owner and message, exact
question, affected outcomes with the phase each one blocks, and disposition
under Orchestration's [decision requests](../../orchestration/SKILL.md#return).
[Decisions](decisions.md) say when a Need is answered, resolved, reopened, or
withdrawn.

### Owner reports

Read each report against Implement's [report](../../implement/SKILL.md#report)
fields; ask no other format. Record, from each:

| Report field | Record it under |
| --- | --- |
| Outcome and finish line | The outcome's finish line and delivery state |
| Layers | Layers, after checking each head and base at the forge |
| Proof | Acceptance evidence, with every blocked or untested assertion kept visible |
| Shown | Results, with access limits, servers, and stop actions |
| Waits | Waits, and which pending PRs this thread watches |
| Decisions | Needs, with the phase each blocks, and provisional assumptions |
| Follow-ups | Discoveries, each with its disposition |
| Sources | Handled follow-up messages, so none is answered twice |

Also record task IDs an owner returns when it resumes.

## Command center

Before each refresh, read the relevant owner reports, user direction, tickets,
and live forge state. Each work row carries the time its state was last
observed, separate from the snapshot's assembly time. Keep an unchecked row's
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
finish line forbids them. When a base is scrapped or its PR closed, every
dependent on it, whether provisional or the same owner's stack, stays on it only
while an open Need, such as its scrap-or-rebase choice, halts it at `start`,
`access`, or `proof`; the card shows the base as its blocker.
Before marking a row terminal, clear its active blockers and open Needs; history
stays in the record. Unresolved work stays visible even after its owner failed
or its PR was abandoned.

Each Need's `blocks` names the outcomes it holds and the earliest phase each
waits at: `start`, `access`, `proof`, `acceptance`, or `landing`. The first three
halt that outcome's work. `acceptance` and `landing` let building and proof
continue, so a shown Try waiting for its choice or a provisional build carries
an open Need without being blocked. Put what continues meanwhile in
`meanwhile`.

Every snapshot carries all open and resolved Needs, so each resolved one stays
reopenable; answered ones may remain. Omit a withdrawn or superseded Need only
after recording its disposition. If work lands while a Need about it is open,
keep the landed row and point the Need's `blocks` at a follow-up row for any
change the answer requires.

### Snapshot format

The renderer reads one JSON object. Fields without `?` are required. Times are
ISO timestamps with a timezone, such as `2026-11-02T17:00:00Z`. Omit absent
optional fields rather than sending empty strings. IDs are unique within each
collection, and layer IDs are unique across the program.

```ts
type Link = { label: string; url: string };
type Snapshot = {
  title: string;
  goal: string;
  finishLine?: string; // a program-wide note, such as who decides merges
  updatedAt: string; // snapshot assembly time
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
```

The renderer rejects a snapshot that claims more than the record supports:
provisional work that merged, keeps Land, or claims ready on any finish line; a Try finish line
with a published PR; a shown Try with nothing to open; a ready outcome with a
layer short of its finish line; a landed outcome with an unmerged layer; active
work with no owner; a layer on another owner's unmerged layer without a
provisional mark; work continuing on a scrapped or closed base without a
halting Need; a `start` Need on work that started; and dangling or cyclic
edges, including work blocked by itself.

Write each `description` from the outcome's scope, not its title or the owner's
next step. Store returned T3 thread links verbatim and use only real ticket, PR,
result, and artifact links.

### Render and show

From this skill's folder, with Python 3 and no third-party packages:

```bash
python3 scripts/render_dashboard.py --state /absolute/path/program.json --output /absolute/path/command-center.html
```

The renderer validates the snapshot, escapes content, and writes standalone
HTML stamped with a digest of the page, which open pages compare to spot a new
publication. It makes no tracker, forge, or session changes. The
[example snapshot](../assets/example-state.json) uses fictional work.

Each copied choice or reopen request names its decision's revision, a digest of
the whole Need. Two or more open quick picks add a batch prompt that takes every
recommendation. Print a Need's current revision with:

```bash
python3 scripts/render_dashboard.py --state /absolute/path/program.json --revision <decision ID>
```

Deliver the page through [dashboard hosting](hosting.md). Do not render it
inline in T3 or another chat surface.
