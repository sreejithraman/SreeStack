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
you reply or move on. Run the event's command from this skill's folder as
`python3 scripts/record.py <command> --state /absolute/path/program.json ...`:

| Event | Command |
| --- | --- |
| An owner starts or is adopted | `start --work W1 --owner "Retry owner" --session <thread link>` |
| An owner report arrives | `report --work W1` |
| The user answers a Need | `answer --decision W6-D1 --option 1 --source "<the user's message>"` |
| The user pastes a page prompt | `answer --pasted --source "<the user's message>"`, with the prompt on stdin |
| You settle a Need under [triage](decisions.md#triage) | `resolve --decision W6-D2 --option 1 --basis "<settling source; why it is reversible>"` |
| You release a landing | `land --work W1` |
| A landing moves | `land --landing L2 --to submitted`, `landed`, or `withdrawn --note "<why>"` |
| A wait starts or ends | `wait --on "PR 44 checks" --event "Required checks finish" --work W1`; add `--clear` to end it |
| A heartbeat, wake, or resume | `status` |

Add `--next "<action>"` to set the program's `next` in the same commit. Run
`--help` on a command for its other options.

Each command stamps times from its own clock, fills defaults, changes only what
its event changes, validates, commits with a message naming the event, and
renders. A refusal changes nothing: fix the input and run it again. When it
refuses over an uncommitted `program.json` change, show the user the diff it
prints and settle it with them before you build on it. If they keep it, check
it with step 3 below and commit it; otherwise run
`git -C /absolute/path checkout HEAD -- program.json`.

For a change no command covers, such as a new work row, a correction, a reopen,
a withdrawal, a scrap-or-rebase answer, or a [chief move](chief-move.md), edit
by hand:

1. Run `git -C /absolute/path status --porcelain -- program.json`. Settle any
   output with the user, as above.
2. Edit `program.json` in place, changing only what the event changed. Never
   regenerate the whole file; that silently drops history. Take each time from
   `date -u +%Y-%m-%dT%H:%M:%SZ`, never from memory.
3. Check it, and fix every error it reports:

   ```bash
   python3 scripts/render_dashboard.py --state /absolute/path/program.json --check
   ```

4. Read `git -C /absolute/path diff -- program.json`. Restore any removed or
   changed line the event didn't call for. Mark a change to a history entry in
   place instead of deleting it.
5. Commit with a message naming the event, then render under
   [render and publish](hosting.md#render-and-publish).

A write is done when its commit lands and the published page matches the
record: publish whenever the output says `page: behind record`, except after a
[chief move](chief-move.md), where the new chief publishes. Hosting-link
commits follow [publication bookkeeping](hosting.md#render-and-publish). On a
git or publish error, stop and report it to the user.

### File format

`program.json` is one JSON object. Fields without `?` are required, and
`--check` rejects fields the sketch doesn't name. Times are ISO timestamps with
a timezone, such as `2026-11-02T17:00:00Z`; dates are `YYYY-MM-DD` or
timestamps. Prose is markdown. Omit absent optional fields rather than sending
empty strings. IDs are unique within each collection, and layer IDs
are unique across the program. The [example file](../assets/example-state.json)
uses fictional work.

```ts
type Program = {
  title: string; goal: string;
  finishLine?: string; // a program-wide note, such as who decides merges
  demo?: boolean; // true only for an illustrative example
  chief: string; // the current chief thread
  hosting?: string; // the current published command center's URL
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
  waits?: { date: string; on: string; event: string; work?: string }[];
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
  answerSource?: string; // required when answered: the user's message that answered it
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
  start: "top-level" | "delegated" | "adopted"; route: string;
  tasks?: string[]; workspace?: string;
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

Each owner starts `reports/<outcome ID>.md` with a fenced `json` block, then
writes Implement's [report](../../implement/SKILL.md#report) in prose below it.
The [kickoff](../assets/owner-kickoff.md) asks for it. `report` reads the block:

```ts
type ReportBlock = {
  outcome: string; // the work ID
  state: Work["state"];
  finishLine?: Work["finishLine"]; // recorded only when the row has none
  layers?: Layer[]; // bottom first, each with its head and base
  proof?: { assertion: string; verdict: "pass" | "fail" | "blocked" | "untested"; url?: string }[];
  shown?: (Link & { access?: string })[]; // becomes results
  asks?: { id: string; question: string; phase?: Phase; // phase defaults to acceptance
    context?: string[]; meanwhile?: string; recommendation?: string;
    options?: Decision["options"]; weight?: Decision["weight"]; links?: Link[] }[];
  waits?: { on: string; event: string }[];
  blocked?: string | null; // a missing prerequisite; null clears it
};
```

Each field in the block replaces that part of the row. An absent field leaves it
as it was, and an empty list clears it. Proof with a `url` becomes `evidence`,
and every verdict other than `pass` goes into `acceptance`. Each new ask becomes
an open Need dated by the command; [triage](decisions.md#triage) it. A wait the
owner still reports keeps its first date. After `report`, run `status` to check
each layer's head and base at the forge.

Record the prose parts by hand:

| Report field | Record it under |
| --- | --- |
| Servers and stop actions under Shown | `owner.resources` |
| Provisional assumptions under Decisions | `provisional` |
| Follow-ups | A work row or `discoveries`, each with its disposition |
| Sources | `owner.handled`, so no message is answered twice |
| Task IDs an owner returns when it resumes | `owner.tasks` |

## Command center

Before each write, read the relevant owner reports, user direction, tickets,
and live forge state. `status` reads each PR through `gh` and each owner's
thread through the T3 CLI, records what they show, and sets `checkedAt` on each
row it fully read. An unread row keeps its old time. Settle by hand each forge
fact it reports the rules reject. Use `unknown` with `unknownReason` when a
row's state cannot be read.

`status --turn-end` commits nothing. It fails while an open row has no running
owner, recorded wait, open Need, blocker, or pending landing, or while the
published page is behind the record.

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
  was declined or made obsolete.
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
the same owner's stack, needs an open Need that halts it at `start`, `access`,
or `proof`, such as its scrap-or-rebase choice. Its answer moves the work off the
dead base in the same commit, under [Base scrapped](dependencies.md#provisional-work).
The card shows the base once, as a Scrapped base or Closed base blocker. A live
layer stacked on a closed layer of a base that is still alive needs the same
Need, or a restack.
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
