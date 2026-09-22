---
name: xcode-security-audit
description: Audit or harden security-oriented Xcode build settings and capabilities. Use for compiler diagnostics, static analysis, Enhanced Security adoption, or unexplained security-setting exceptions in Apple-platform projects. Excludes certificate and profile management, notarization, ATS, and privacy manifests.
---

# Xcode Security Audit

Inspect the effective configuration before editing its source. Choose the
fastest reliable surface for each step: native Xcode project tools when exposed,
`xcodebuild` for repeatable inventory and validation, or Xcode through computer
use when its project or capability editor is simpler and safer.

## Workflow

1. **Set the outcome.** Keep repository source unchanged during an audit. When
   the user asks to enable or harden settings, adoption is authorized within
   the named project and targets. Keep generated project files under their
   generator's control.
2. **Inventory the build graph.** Read
   [Inventory and findings](references/inventory-and-findings.md). Identify the
   workspace or project, schemes, configurations, targets, product types,
   platforms, languages, configuration files, entitlements, generators, and
   binary dependencies. Record the selected Xcode version.
3. **Capture the effective baseline.** Query effective settings for every
   relevant target and configuration. Before adopting changes, run the
   project's normal build or use a current equivalent CI result. If the current
   baseline fails, report that separately from security findings.
4. **Classify findings.** Distinguish:
   - an effective protection that is already active;
   - a relevant setting that is absent or explicitly disabled;
   - a deliberate exception with a recorded rationale;
   - a setting unsupported by this Xcode, platform, product, or language;
   - an advanced adoption that changes compilation or runtime behavior.
5. **Report before mutation.** Name the affected target and configuration, the
   effective value, where it is defined, the proposed value, the protection it
   adds, compatibility risks, and the validation required. For an audit-only
   request, stop after the report.
6. **Adopt in compatible batches.** Read
   [Adoption and verification](references/adoption-and-verification.md). For
   Enhanced Security, also read
   [Enhanced Security](references/enhanced-security.md). Change the existing
   source of truth, preserve conditional settings and inheritance, then build
   and verify each batch before continuing.
7. **Record durable exceptions.** Update an existing security decision record
   when the repository has one. Create a concise record only when the work
   produces decisions future audits cannot infer from configuration. Include
   the target, configuration scope, decision, rationale, owner if known, and a
   condition or date for reconsideration.

## Invariants

- Effective settings, not raw project-file text, determine the audit result.
- Keep declared configuration, effective configuration, and the built product
  separate. Each proves a different part of the result.
- Language-specific diagnostics apply only to targets that compile that
  language.
- Experimental analyzers, bounds-safety modes, hardware memory tagging, and
  runtime hardening are explicit adoption choices with their own validation.
- A successful build proves configuration compatibility. Exercise affected app
  workflows on a representative destination when runtime behavior changes.
- Preserve a user-authored `NO` or exception until its rationale is understood.
  Report an undocumented exception as a finding rather than silently removing
  it.

Use `app-store-connect` for signing, export, notarization, and distribution.
Treat C bounds safety as separate source migration work. This skill may identify
it as a follow-up, but does not enable it as part of a general settings audit.
