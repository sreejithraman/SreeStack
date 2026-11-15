/implement

Program: <title>. Program record (read-only): `git -C <program directory> show HEAD:program.json`.
Original request, accepted corrections, and preserved requirements: its `request`, `corrections`, and `requirements`.

Outcome <ID>: <title>. Sources: <tickets, snips, PRs, or messages, or none>. Prefix decision request IDs with <ID>.
Scope: <the result this outcome delivers, the code it covers, and what it leaves to other outcomes>.
Proof: <observations that establish the result>. Show: <what to capture and show, or why nothing>.
Delivery: <one PR | a planned stack | your call by reviewability>.

Repository and base: <repo> at <base>. Owned branches: <branches>. Owned paths: <paths>.
Inputs available at that base: <dependencies>. Uncommitted inputs: <paths, or none>.
Provisional assumptions: <another owner's unmerged branch or PR, or the recommended option of an open decision you build on, with what clears it, or none>. Your own planned layers are not provisional. Provisional work never merges and never takes destructive or outward-facing steps on its own; the user's scrap allows its scoped cleanup per Implement. Land becomes Try, and a requested draft or review-ready PR state can still be reached. Publish such a PR with a Provisional section in its body, per PR's body guide; that section holds its status until the condition clears and proof is refreshed.

Finish line: <Land | Try | review-ready PR | draft PR>, picked because <reason>.
Grant, from the record's `grant`, `landingAuthority`, and `approvals`: the coordinator may start <start>; land <landing scope and gates>; and resolve <what it settles itself>. <What stays with the user> stays with the user. Land for this outcome within that scope is the merge request Merge needs, and it takes effect only on the current coordinator's recorded landing release for your PR or stack.
Your calls: decide reversible method choices yourself and list them in your report. Send up only scope, irreversible, and taste calls.
Landing: report readiness and end your turn. Land through Merge only on that release. Immediately before submitting, re-read the record: confirm `chief`, your active release in `landings`, you as its one named lander, and no affecting hold or decision; match the forge's head/base for every PR in the set to the release. Report a mismatch instead of landing. Sets that span several owners are landed by the coordinator.
Holds and user gates: <hold, source, release condition, or none>.
Delegation allowance: you may start the bounded helpers your workflow needs as your own subagents: implementation, verification, and review helpers, and Swarm workers that fit. <Further limits, or none>. Start no new program owners; send work that needs one to the coordinator.

Owner report: write it to <program directory>/reports/<ID>.md. Start it with a fenced `json` block holding only the fields that apply, then write the report in prose below it. Each field replaces that part of the record; an empty list clears it:

```json
{"outcome": "<ID>", "state": "building | shown | in-review | ready",
 "layers": [{"id": "<ID>-L1", "branch": "<branch>", "status": "local | draft | open | ready | closed", "url": "<PR>", "head": "<sha>", "base": "<branch>", "stackedOn": "<layer below>"}],
 "proof": [{"assertion": "<what was checked>", "verdict": "pass | fail | blocked | untested", "url": "<evidence>"}],
 "shown": [{"label": "<result>", "url": "<link>", "access": "<what opening it needs>"}],
 "asks": [{"id": "<ID>-D1", "question": "<one question>", "options": [{"label": "<option>", "effect": "<effect and how to reverse it>", "recommended": true, "reversible": true}], "phase": "start | access | proof | acceptance | landing", "meanwhile": "<what continues>"}],
 "waits": [{"on": "<what>", "event": "<what ends it>"}],
 "blocked": "<missing prerequisite and who can supply it>"}
```

Send a partial report as soon as you hit a missing prerequisite, a human decision, or a pending PR, naming what continues and the event that resumes the rest.
Route: <top-level: send it to the coordinator thread <link> with t3_thread_send; you watch your PR | delegated: end your turn with it; the coordinator thread watches your PR>.
Decision requests and shared blockers use the same route as they arise. Give each decision request one question, two or more options with their effects, and one recommended option. Say what reversing each option would take, mark `reversible: true` only when undoing it costs only rework, and cite any recorded source that settles it.
