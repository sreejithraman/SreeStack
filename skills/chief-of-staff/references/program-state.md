# Program record and command center

Specs, tickets, PRs, and user decisions stay where the project already keeps
them. The **program record** links those sources and adds coordination state.
The **command center** is a rendered snapshot of that record, not a second
tracker.

## Program record

Reuse an established record, or choose a task-owned directory that the chief
and its owners can read and that survives worktree cleanup. Put its absolute
path in the chief's handoff and every owner kickoff. Owners write only their
own `reports/<unit ID>.md`; the chief alone writes the rest of the record and
the snapshot. It needs no wiki or committed state file.

Keep:

- Outcome, scope, original request and message sources, accepted corrections,
  preserved requirements, finish line and who may land, and holds with release
  conditions.
- PR units with stable IDs, tickets, dependencies, acceptance evidence, intended
  base, owner thread/task IDs and links, start mode and return route,
  workspace/branch, model selection, current head/base, each merge set's lander,
  target branch, pending submission or queue state, and landing release (issuing
  chief, owner, accepted head/base, active or withdrawn), and actual delivery state.
- Each owner report's disposition and evidence, handled follow-up sources,
  live helpers and waits, and task IDs returned when an owner resumes.
- Discoveries with origin and destination, support work and affected owners,
  decision requests with their dispositions, standing approvals, and accepted
  tradeoffs with what would prompt revisiting them.
- The current chief thread, the snapshot state and HTML paths, and the next
  useful action.

Date decisions and cite their sources. Code claims name the repository and
revision they describe. Keep superseded reasoning when it explains a tradeoff,
and recheck current facts at their source before acting on them.

Each decision request keeps its ID, originating owner and message, exact
question, affected work, and disposition under Orchestration's
[decision requests](../../orchestration/SKILL.md#return). Mark a Need answered
only with the user's answer and its source. Mark it resolved only under the
chief's [triage](../SKILL.md#triage-decision-requests), citing the source that
settled it; a reopened Need keeps that history. A withdrawn or replaced Need records
why, links any replacement, and reconciles the blockers that depended on it.

## Command center

Before each refresh, read the relevant owner reports, user direction, tickets,
and live forge state. Each work row carries the time its state was last
observed, separate from the snapshot's assembly time. Keep an unchecked row's
old observation time; use `unknown` with `unknownReason` when its state cannot be read.

Row states:

- `in-review`: an open PR while review or CI repairs continue.
- `mergeable`: current readiness evidence from the delivery workflow. Shown
  under In review with a Ready to merge badge.
- `merged`: confirmed landing. `closed`: closed without merge.
- `done`: completed non-PR work. A PR unit never uses `done`.

`mergeable`, `merged`, and `closed` need `kind: "pr"`; promote a follow-up or
support row to a PR row when it becomes PR work, keeping its ID, origin, and
links. `blockedBy` lists prerequisites not yet satisfied under task graphs'
[dependency rule](task-graphs.md#dependencies); drop an edge once it is, even
while a stacked parent PR stays open. Open Needs and `blocked` add blockers
without changing a row's state. Before marking a row terminal,
clear its active blockers and open Needs; history stays in the record. Unresolved
work stays visible even after its owner failed or its PR was abandoned.

Every snapshot carries all open and resolved Needs, so each resolved one stays
reopenable; answered ones may remain. Omit a
withdrawn or superseded Need only after recording its disposition. If work
lands while a Need about it is open, keep the merged row and point the Need's
`blocks` at a follow-up row for any change the answer requires.

### Snapshot format

The renderer reads one JSON object. Fields without `?` are required. Times are
ISO timestamps with a timezone, such as `2026-11-02T17:00:00Z`. Omit absent optional fields rather than sending
empty strings. IDs are unique within each collection.

```ts
type Link = { label: string; url: string };
type Snapshot = {
  title: string;
  goal: string;
  finishLine?: string; // says who may land when not the default
  updatedAt: string; // snapshot assembly time
  demo?: boolean;   // true only for an illustrative example
  needs: Need[];
  work: Work[];
  revisits?: Revisit[];
};
type Need = {
  id: string; ask: string;
  context?: string[];
  recommendation?: string; // rationale for the recommended option, or a suggestion when there are no options
  options?: { label: string; effect: string; recommended?: boolean }[]; // at most one recommended
  weight?: "quick" | "judgment"; // default judgment; quick needs two or more options and a recommended one
  blocks?: string[]; // work IDs waiting on this answer
  links?: Link[];
  status: "open" | "answered" | "resolved"; // resolved: the chief settled it
  answer?: string; // required unless open
  basis?: string; // required when resolved: what settled it and why it is reversible
};
type Work = {
  id: string; title: string; repo: string;
  description?: string; // one or two sentences of scope from the ticket
  kind: "pr" | "follow-up" | "support";
  state: "planned" | "building" | "in-review" | "mergeable" | "merged"
    | "done" | "closed" | "cancelled" | "unknown";
  owner?: string; sessionUrl?: string;
  url?: string; // actual PR URL; PR rows only
  stackedOn?: string; // parent PR row of a stacked PR; shown as landing order until it merges
  tickets?: Link[];
  blockedBy?: string[];
  blocked?: string; // another active blocker, such as an external dependency
  unknownReason?: string; // why the state could not be read; unknown rows only
  updatedAt: string; // last observation supporting this row
  evidence?: Link[];
  required?: boolean; // false marks proposed work outside committed scope
  origin?: string;
};
type Revisit = {
  id: string; title: string; tradeoff: string; revisit: string;
  source?: string; // decision ID or source reference
};
```

Write each `description` from the ticket's scope or intended outcome, not its
title or the owner's next step. Store returned T3 thread links verbatim and use only real ticket,
PR, and artifact links.

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
