/implement

Program: <title>. Program record (read-only): <absolute path to program.json>.
Original request and accepted corrections: its `record.request` and `record.corrections`.

Outcome <ID>: <title>. Sources: <tickets, snips, PRs, or messages, or none>. Prefix decision request IDs with <ID>.
Scope: <the result this outcome delivers, the code it covers, and what it leaves to other outcomes>.
Proof: <observations that establish the result>. Show: <what to capture and show, or why nothing>.
Delivery: <one PR | a planned stack | your call by reviewability>.

Repository and base: <repo> at <base>. Owned branches: <branches>. Owned paths: <paths>.
Inputs available at that base: <dependencies>. Uncommitted inputs: <paths, or none>.
Provisional assumptions: <another owner's unmerged branch or PR, or the recommended option of an open decision you build on, with what clears it, or none>. Your own planned layers are not provisional. Provisional work never merges and never takes destructive or outward-facing steps on its own; the user's scrap allows its scoped cleanup per Implement. Land becomes Try, and a requested draft or review-ready PR state can still be reached. Publish such a PR with a Provisional section in its body, per PR's body guide; that section holds its status until the condition clears and proof is refreshed.

Finish line: <Land | Try | review-ready PR | draft PR>, picked because <reason>.
Landing authority: `record.landingAuthority` and this outcome's finish line. Land within that scope is the merge request Merge needs, and it takes effect only on the current chief's recorded landing release for your PR or stack.
Landing: report readiness and end your turn. Land through Merge only on that release. Immediately before submitting, re-read the record: confirm `record.chief`, your active release in `record.landings`, you as its one named lander, and no affecting hold or decision; match the forge's head/base for every PR in the set to the release. Report a mismatch instead of landing. Sets that span several owners are landed by the chief.
Holds and user gates: <hold, source, release condition, or none>.
Delegation allowance: you may start the bounded helpers your workflow needs as your own subagents: implementation, verification, and review helpers, and Swarm workers that fit. <Further limits, or none>. Start no new program owners; send work that needs one to the chief.

Owner report: write it to <program directory>/reports/<ID>.md. Send a partial report as soon as you hit a missing prerequisite, a human decision, or a pending PR, naming what continues and the event that resumes the rest.
Route: <top-level: send it to the chief thread <link> with t3_thread_send; you watch your PR | delegated: end your turn with it; the chief thread watches your PR>.
Decision requests and shared blockers use the same route as they arise. In each decision request, say what reversing each option would take and cite any recorded source that settles it.
