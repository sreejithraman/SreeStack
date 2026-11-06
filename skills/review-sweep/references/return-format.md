# Return Format

Return canonical issues grouped by class, retaining their normalized records:

```text
Workflow: [workflow_id]; current pass: [pass or unknown]

Must-fix:
- [id] location - claim
  First seen: [pass or unknown]
  Reports: [source IDs, assignments/passes, relationships]
  Reason:
  Action: [repair state; applied snapshot and change evidence, or pending/unknown]
  Evidence: [claim evidence; check state, snapshot, method, result, scope, limits]

Worth-fixing:
- ...

Defer:
- [id] location - claim
  Reason:
  Parent decision needed:
  Suggested follow-up:

Acknowledge:
- ...

Won't do:
- ...
```

Use the same identity and source-report fields for every class. For accepted
issues, distinguish acceptance from an applied repair and a relevant check.
State unavailable evidence explicitly. Link retained records and artifacts
instead of duplicating their contents. Repeated reports remain attached to the
existing issue; they do not add rejected findings to the summary.

Include:

- changed files
- verification results and the snapshot they apply to
- review coverage gaps
- blockers
- every stop with its decision needed, under `Stops:` above the classes, and parent-owned defers

The parent should be able to see what was fixed, what remains, and which deferred decisions it owns.
