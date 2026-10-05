# Spec review

Review the supplied scope against the requirements supplied by the parent.
Read the spec, issue, or user request and trace each requirement through the
changed code, nearby callers, and tests. Report findings; leave fixes and
further delegation to the parent.

## Review brief

Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding. Under 400 words.

For each finding, include the code location, evidence, impact, and suggested
fix. Separate requirements from assumptions. Report each requirement as covered,
missing, partial, or blocked. If no requirements were supplied, report "no spec
available" instead of inventing a spec.

## Why two axes

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other.

Return this report separately from Standards. The parent owns triage and fixes
and retains each finding’s source. No findings does not imply full coverage
when gaps remain.
