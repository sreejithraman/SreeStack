/implement

Program: <title>. Program record (read-only): `git -C <program directory> show HEAD:program.json`.
Original request, accepted corrections, and preserved requirements: its `request`, `corrections`, and `requirements`.

Outcome <ID>: <title>. Sources: <tickets, snips, PRs, or messages, or none>. Prefix decision IDs with <ID>.
Scope: <result this outcome delivers, covered code, and what it leaves to other outcomes>.
Proof: <observations that establish the result>. Show: <what to capture and show, or why nothing>.
Delivery: <one PR | a planned stack | your call by reviewability>.

Repository and base: <repo> at <base>. Owned branches: <branches>. Owned paths: <paths>.
Inputs available at that base: <dependencies>. Uncommitted inputs: <paths, or none>.
Provisional assumptions: <another owner's unmerged branch/PR, or open decision's reversible recommended option with what clears it, or none>. Your own planned layers are not provisional. Provisional work never merges and never takes destructive or outward-facing actions on its own (Land becomes Try; published PRs keep a `## Provisional` section until the condition clears and proof is refreshed).

Finish line: <Land | Try | review-ready PR | draft PR>, picked because <reason>.
Grant (from `grant`, `landingAuthority`, `approvals`): coordinator may start <start>; land <landing scope and gates>; resolve <what it settles itself>. <What stays with the user> stays with the user. Land for this outcome within scope is Merge's merge request, taking effect only on the current coordinator's recorded landing release.
Your calls: edit your worktree directly; decide reversible method choices yourself and list them in your report. Send up only scope, irreversible, and taste calls.
Landing: report readiness and end your turn. Land via Merge only on that release. Immediately before submitting, re-read `HEAD:program.json`: confirm `chief`, your active release in `landings`, you as its one named lander, and no affecting hold or decision; match the forge's head/base for every PR to the release. Report a mismatch instead of landing. Sets spanning owners are landed by the coordinator.
Holds and user gates: <hold, source, release condition, or none>.
Delegation allowance: you may start bounded subagents your workflow needs (verification, review, Swarm workers). <Further limits, or none>. Start no new program owners; send work that needs one to the coordinator.

Owner report: write to `<program directory>/reports/<ID>.md`. Start with a fenced `json` block holding only fields that apply, then prose below it. Each field replaces that part of the record; an empty list clears it:

```json
{"outcome": "<ID>", "state": "building | shown | in-review | ready",
 "layers": [{"id": "<ID>-L1", "branch": "<branch>", "status": "local | draft | open | ready | merged | closed", "url": "<PR>", "head": "<sha>", "base": "<branch>", "stackedOn": "<layer below>"}],
 "proof": [{"assertion": "<what was checked>", "verdict": "pass | fail | blocked | untested", "url": "<evidence>"}],
 "shown": [{"label": "<result>", "url": "<link>", "access": "<what opening it needs>", "image": "<absolute path to a screenshot>"}],
 "asks": [{"id": "<ID>-D1", "question": "<one question>", "pictures": {"shape": "side-by-side | before-after | sequence", "images": [{"image": "<absolute path>", "caption": "<caption>"}]}, "options": [{"label": "<option>", "effect": "<effect and how to reverse it>", "image": "<absolute path>", "recommended": true, "reversible": true}], "phase": "start | access | proof | acceptance | landing", "meanwhile": "<what continues>"}],
 "followups": [{"id": "<ID>-F1", "text": "<deferred review finding or discovery>", "evidence": "<location and evidence>", "impact": "unrelated | shared-contract | requested-scope", "thread": "<GitHub thread ID if a held deferred PR reply awaits routing>"}],
 "waits": [{"on": "<what>", "event": "<what ends it>"}],
 "blocked": "<missing prerequisite and who can supply it>"}
```

Send a partial report as soon as you hit a missing prerequisite, human decision, pending PR, or a deferred finding with `shared-contract` or `requested-scope` impact, naming what continues and the event that resumes the rest.
Route: <top-level: send to current coordinator with `t3_thread_send`; initial thread <link>; you watch your PR | delegated: end turn with it; coordinator watches your PR>. Before a top-level send, follow `<coordinator skill folder>/references/coordinator-move.md` ("Check the coordinator") using the committed record above.
Decision requests and shared blockers use the same route as they arise. Give each decision one question, two or more options with effects and reversal cost (`reversible: true` only when undoing costs only rework), one recommended option, and any recorded source that settles it. For visual choices (layout, screen state, before/after), attach screenshots per option or on the decision.
