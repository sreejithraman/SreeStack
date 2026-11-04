/implement

Program: <title>. Program record (read-only except your report file): <absolute path>.
Original request and accepted corrections: <link or path>.

PR unit <ID>: <title>. Tickets: <links>. Prefix decision request IDs with <ID>.
Scope: <what this PR changes and what it leaves to other units>.
Acceptance: <observations that establish the result>.

Repository and base: <repo> at <base>. Owned branch: <branch>. Owned paths: <paths>.
Inputs available at that base: <dependencies>. Uncommitted inputs: <paths, or none>.

Finish line: <local changes | review-ready PR | merged>.
Merge authority: <absolute link to program record's scope and finish-line entry>, under <absolute path to Chief of Staff's Establish the program section>. Within that scope, the current chief's recorded landing release is the merge request for this PR.
Landing: report PR readiness and end your turn. Land through Merge only on that release. Immediately before submitting, re-read the record: confirm the current chief, your active release, and no affecting hold or decision; match the forge's head/base to the release. Report a mismatch instead of landing.
Holds and user gates: <hold, source, release condition, or none>.
Delegation allowance: <helpers you may start>.

Owner report: write it to <record>/reports/<ID>.md.
Route: <delegated: end your turn with it; the chief thread watches your PR | top-level: send it to the chief thread <link> with t3_thread_send; you watch your PR>.
Decision requests and shared blockers use the same route as they arise. In each decision request, say what reversing each option would take and cite any recorded source that settles it.
