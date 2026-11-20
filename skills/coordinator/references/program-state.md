# Program record and CLI

Specs, tickets, snips, PRs, and user decisions stay in their existing tools. `program.json` is the
program's single coordination record, kept in a task-owned git folder that survives worktree
cleanup (with a `reports/` subfolder). `HEAD` is authoritative; the git log is its history.

**One writer:** owners write only `reports/<ID>.md`. Only the current coordinator writes
`program.json`, after checking `chief` in `HEAD:program.json`.

## Record commands

Run from this skill's folder as
`python3 scripts/record.py <command> --state /absolute/path/program.json ...` (add `--next "<action>"`
to update `next` in the same commit; run `<command> --help` for full flags):

| Event | Command |
| --- | --- |
| Create a new program | `init --title "<t>" --goal "<g>" --chief <thread link> --request "<text>"` |
| Set/update grant, landing scope, heartbeat/wake IDs, or page URL | `grant [--source "<msg>"] [--start "..."] [--resolve "..."] [--user "..."] [--heartbeat "..."] [--wake "..."] [--landing "..."] [--hosting <url>]` |
| Add, update, scrap, or rebase a work row | `work --id W1 [--add --title "<t>" --repo "<r>" --finish-line land] [--blocked-by W0] [--provisional-basis "..." --provisional-clears "..." --provisional-on W0] [--scrap \| --rebase-onto main [--stack-on L1]] [--decision D1 --option 1 --answer-source "<msg>"]` |
| Owner started or adopted | `start --work W1 --owner "Retry owner" --session <thread link> [--mode top-level\|delegated\|adopted] [--replace]` |
| Owner report arrived | `report --work W1` |
| User answered a decision | `answer --decision W6-D1 --option 1 --source "<msg>"` (or `--text`, `--pasted` on stdin, `--stored <db_query file>`) |
| Attach pictures to an open decision | `picture --decision W6-D1 --shape before-after --image /abs/a.png --image /abs/b.png --caption "After"` (or `--option 2 --image /abs/shot.png`) |
| Coordinator settled a decision under triage | `resolve --decision W6-D2 --option 1 --basis "<source; why reversible>"` |
| Reopen a settled decision | `reopen --decision W6-D2 --why "<reason>" [--block W1:landing]` |
| Withdraw a decision | `withdraw --decision W6-D2 --why "<reason>"` |
| Passed answer to affected owners | `applied --decision W6-D1` |
| Release or update a landing | `land --work W1` or `land --landing L2 --to submitted\|landed\|withdrawn [--note "<why>"]` |
| Record or clear a wait | `wait --on "<what>" --event "<ends it>" [--work W1] [--clear]` |
| Add or route a discovery / deferred follow-up | `discovery --id W1-F1 --route "<work ID \| snip ID \| issue \| declined>"` (or `--add --origin "..." --text "..." --route "..."`) |
| Transfer coordinator ownership | `move --chief <new thread link>` (does not prompt to publish) |
| Check forge/threads and verdict | `status` (also `--heartbeat`, `--turn-end`, `--json`, `--exit-code`) |

Each command stamps ISO UTC times from its own clock, validates through `render_dashboard.py`,
commits, and stages `command-center.next.html`. A refusal changes nothing. If it refuses over an
uncommitted `program.json` change, show the printed diff to the user and settle it before building
on it (`render_dashboard.py --check` + commit to keep, or `git checkout HEAD -- program.json` to
discard).

**Never reuse IDs** (even withdrawn or scrapped ones). Store returned T3 thread links verbatim.

## Page copy

The command center is written for a human scanning on a phone, **not** as coordinator memory or a
compaction scratchpad:

- **`next`:** replace on every update — never append. Write **one short line (at most 280
  characters, enforced by `record.py`)** naming only what happens next (plus cadence/wake trigger
  when waiting). Put commit SHAs, CI run IDs, test counts, and play-by-play history in git commits,
  `work` rows, and `reports/`, never in `next`.
  - Good: `Waiting on PR #412 review and W6-D1 in Inbox (10m heartbeat; PR watch wakes sooner).`
  - Bad: appending landed SHAs, CI run numbers, or multi-paragraph forensic recaps into `next`.
- **`goal` and `finishLine`:** 1–2 plain sentences of user outcome and landing policy.
- **`work[].description`:** 1–2 plain sentences of what the outcome delivers for the user — not its
  title, current status, or implementation internals.
- **Inbox (`question`, `context`, `options`):** short, scannable choices the user can answer on a
  phone — concrete effects and brief reversal costs; omit raw file paths or commit SHAs unless the
  decision is specifically about them.

## Rare hand edits

For fields with no CLI flag yet (`corrections`, `requirements`, `approvals`, `directions`,
`revisits`, `tickets`, `owner.resources`/`handled`/`tasks`), edit `program.json` in
place — never regenerate the whole file — using `date -u +%Y-%m-%dT%H:%M:%SZ` for timestamps:

1. Check `git -C /absolute/path status --porcelain -- program.json` is clean.
2. Edit in place; check with `python3 scripts/render_dashboard.py --state /absolute/path/program.json --check`
   (which enforces all keys, enums, state/layer invariants, and picture hashes).
3. Review `git -C /absolute/path diff -- program.json`, commit naming the event, then render with
   `python3 scripts/render_dashboard.py --state /absolute/path/program.json --page /absolute/path/command-center.html`.

To add a picture by hand, copy it into `files/<first 16 hex of sha256>.<ext>` and commit it with
`program.json`. Print a decision's current revision at `HEAD` with
`python3 scripts/render_dashboard.py --state /absolute/path/program.json --revision <decision ID>`.

## Owner reports

Each owner starts `reports/<ID>.md` with a fenced `json` block (`record.py report` reads it), then
writes prose per [Implement's caller report](../../implement/references/caller-report.md):

```ts
type ReportBlock = {
  outcome: string; // work ID
  state: "planned" | "building" | "shown" | "in-review" | "ready" | "unknown"; // never terminal
  finishLine?: "land" | "try" | "pr-review" | "pr-draft"; // recorded only when row has none
  layers?: { id: string; branch: string; status: "local"|"draft"|"open"|"ready"|"closed";
    url?: string; head?: string; base?: string; stackedOn?: string }[]; // bottom first
  proof?: { assertion: string; verdict: "pass"|"fail"|"blocked"|"untested"; url?: string }[];
  shown?: { label: string; url: string; access?: string; image?: string }[]; // image: abs path
  asks?: { id: string; question: string; phase?: "start"|"access"|"proof"|"acceptance"|"landing";
    context?: string[]; pictures?: { shape?: "side-by-side"|"before-after"|"sequence";
      images: { image: string; caption?: string }[] };
    meanwhile?: string; recommendation?: string;
    options?: { label: string; effect: string; image?: string; recommended?: boolean;
      reversible?: boolean }[];
    weight?: "quick"|"judgment"; links?: { label: string; url: string }[] }[];
  followups?: { id: string; text: string; evidence?: string;
    impact?: "unrelated"|"shared-contract"|"requested-scope" }[];
  waits?: { on: string; event: string }[];
  blocked?: string | null; // null clears it
};
```

Each present field replaces that part of the row; an empty list clears it; absent leaves it alone.
`report` copies referenced absolute picture paths into `files/` by content hash and commits them,
and ingests new `followups` into `discoveries` with `status: "open"` (`route: "pending"`), which
makes `status` return `runnable` until routed via `record.py discovery`.
`report` cannot mark a layer merged — run `status` afterward to read merges from GitHub. Record
prose-only report fields (`owner.resources`, `owner.handled`, `owner.tasks`, `provisional`) when
present.

## Status verdicts and invariants

`status` reads PRs via `gh` and owner threads via the T3 CLI, updates `owner.seen` and `checkedAt`,
and returns one verdict (`runnable`, `working`, `waiting`, `done`) with a digest. Key rules
enforced by `record.py` and `render_dashboard.py`:

- **Halting vs. non-halting phases:** `start`, `access`, and `proof` halt work; `acceptance` and
  `landing` let building/proof continue (and cover a shown Try or ready stop).
- **Runnable triggers:** unstarted ready rows, idle owners with no wait/blocker/halting decision,
  unapplied answers, unrouted open discoveries (`followups`), a reversible recommended decision
  halting startable work (provisional start), or a settled decision with a `stalePick` (reopen
  request).
- **Dead base:** an outcome that was `scrapped` or whose layers are all `closed` without landing.
  Active dependents resting on it require a halting scrap-or-rebase decision, resolved atomically
  with `record.py work --scrap` or `--rebase-onto` plus `--decision`.
- **Outcome states:** `planned`, `building`, `shown` (Try with `results`), `in-review`, `ready`
  (never provisional), `landed`, `scrapped`, `unknown`. Support rows use `planned`, `building`,
  `done`, `scrapped`, `unknown`.
