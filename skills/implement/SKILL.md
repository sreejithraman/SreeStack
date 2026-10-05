---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

Use /tdd where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Before review, check the implemented behavior, using `verify` when real-workflow
acceptance adds confidence. Supply the results to /review-fix-loop, which reviews
the work and fixes accepted findings.

Commit your work to the current branch.
