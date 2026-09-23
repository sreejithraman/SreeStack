---
name: react-doctor
description: Use React Doctor to scan or fix React diagnostics, run its static design checks, capture a browser performance trace, or explain and configure Doctor rules.
---

# React Doctor

React Doctor scans React codebases for security, performance, correctness, and
architecture issues. Its 0–100 score summarizes those diagnostics, not the
whole product experience. For scan or triage requests, report findings without
editing code. Fix accepted findings when the request includes cleanup or
implementation.

## For a general scan or cleanup

Run `npx react-doctor@latest --verbose` (the default `--scope full`) to scan the
full codebase. Triage findings by impact and evidence, with errors before
warnings. Fix in-scope findings only when the task calls for changes.

## For static design diagnostics

Run `npx react-doctor@latest design --verbose`. This selects design-tagged UI
composition, typography, interaction, accessibility, and motion rules,
including focused rules that remain opt-in during a general health scan. Treat
the result as source-code findings. For an audit of the rendered interface and
real interactions, use `manual-verify` with `ui-design` rather than treating a
clean scan as a pass.

## For runtime performance problems:

Run `npx react-doctor@latest scan <url> --format json` in an interactive terminal. React Doctor opens an isolated system Chrome profile, records a DevTools trace while the user reproduces the slow interaction, and flashes purple outlines with component names as React renders. It stops when they press Enter. Read the structured summary first, then inspect the returned local `.json.gz` trace for CPU, browser, and React component evidence.

If the user needs their authenticated browser state, use `--cdp <remote-debugging-url>`. This requires Chrome to already be running with remote debugging. Never ask for cookies or copy the user's browser profile. Treat the trace as sensitive local application data and never upload it without explicit permission.

## Configuring or explaining rules

When the user wants to understand a rule, disagrees with one, or wants to disable / tune which rules run (not fix code), read [references/explain.md](references/explain.md) and follow it. Start with `npx react-doctor@latest rules explain <rule>`, then apply the narrowest control via `npx react-doctor@latest rules disable|set|category|ignore-tag …`, which edits your `doctor.config.*` (or `package.json#reactDoctor`).

## Command

```bash
npx react-doctor@latest --verbose
```

| Flag              | Purpose                                                          |
| ----------------- | ---------------------------------------------------------------- |
| `.`               | Scan current directory                                           |
| `--verbose`       | Show affected files and line numbers per rule                    |
| `--scope changed` | Only report issues introduced vs the base branch (default: full) |
| `--base`          | Git ref for `--scope changed` or `--scope lines`                 |
| `--include-untracked` | With changed/files/lines scope, also scan nonignored untracked files |
| `--scope lines`   | Only report issues on the changed lines                          |
| `--score`         | Output only the numeric score                                    |
| `design`          | Run only the focused UI design diagnostics                       |
