# Return Format

Return findings grouped by class:

```text
Must-fix:
- [id] location - claim
  Reason:
  Action:
  Evidence:

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

Include:

- changed files
- verification results and the snapshot they apply to
- review coverage gaps
- blockers
- every parent-owned defer

The parent should be able to see what was fixed, what remains, and which deferred decisions it owns.
