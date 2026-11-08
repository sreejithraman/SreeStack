/implement

Program: <title>. Program record (read-only except your report file): <absolute path>.
Original request and accepted corrections: <link or path>.

Outcome <ID>: <title>. Tickets: <links, or none>. Prefix decision request IDs with <ID>.
Scope: <the result this outcome delivers, the code it covers, and what it leaves to other outcomes>.
Acceptance: <observations that establish the result>. Show: <what to capture and show, or why nothing>.
Delivery: <one PR | a planned stack | your call by reviewability>.

Repository and base: <repo> at <base>. Owned branches: <branches>. Owned paths: <paths>.
Inputs available at that base: <dependencies>. Uncommitted inputs: <paths, or none>.
Provisional assumptions: <another owner's unmerged branch or PR, or a recorded assumption, and the decision it waits on, or none>. Your own planned layers are not provisional. Provisional work never merges: Land becomes Try, and a requested draft or review-ready PR state can still be reached. Publish such a PR with a Provisional section in its body, per PR's body guide; that section holds its status until the condition clears and proof is refreshed.

Finish line: <Land (merged) | Try (built, proved, and shown; stop before review and the PR) | review-ready PR | draft PR>.
Merge authority: <absolute link to program record's scope and finish-line entry>, under <absolute path to Chief of Staff's Establish the program section>. Within that scope, the current chief's recorded landing release is the merge request for your PR or stack.
Landing: report readiness and end your turn. Land through Merge only on that release. Immediately before submitting, re-read the record: confirm the current chief, your active release, you as its one named lander, and no affecting hold or decision; match the forge's head/base for every PR in the set to the release. Report a mismatch instead of landing. Sets that span several owners are landed by the chief.
Holds and user gates: <hold, source, release condition, or none>.
Delegation allowance: you may start the bounded helpers your workflow needs: implementation, verification, and review helpers, and Swarm workers that fit. <Further limits, or none>. Start no new program owners; send work that needs one to the chief.

Owner report: write it to <record>/reports/<ID>.md. Send a partial report as soon as you hit a missing prerequisite, a human decision, or a pending PR, naming what continues and the event that resumes the rest.
Route: <delegated: end your turn with it; the chief thread watches your PR | top-level: send it to the chief thread <link> with t3_thread_send; you watch your PR>.
Decision requests and shared blockers use the same route as they arise. In each decision request, say what reversing each option would take and cite any recorded source that settles it.
