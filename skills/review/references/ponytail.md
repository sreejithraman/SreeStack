# Ponytail Review

Review the parent’s supplied diff for unnecessary complexity. The diff’s best
outcome is getting shorter. Read and report; leave edits, triage, and further
delegation to the parent.

## Understand first

Trace the actual flow through every file the change touches before proposing
a simplification.

Account for every changed hunk and untracked file in the supplied scope. Read
nearby code, callers, dependencies, and repo rules before claiming a cut is safe.
Search for helpers, utilities, types, and patterns already in the repo. Before
recommending deletion, search the whole tree for the symbol, including tests,
fixtures, strings, and dynamic references.

## Assess proposed cuts

When choosing what to remove, reuse, or replace, read **Laziness Protocol**,
**Subtract Before You Add**, and **Minimize Reader Load** in
[simplicity principles](../../engineering-principles/references/simplicity.md).
For a bug-fix diff, read **Fix Root Causes** in
[evidence principles](../../engineering-principles/references/evidence.md) and
check the affected callers before recommending a smaller fix.

Hunt redundant dependencies, pass-through wrappers, dead flags and config,
speculative flexibility, and hand-rolled platform features. Prove each candidate
against actual uses and requirements; a single caller alone does not establish
that a useful interface can be removed.

## Deliberate shortcuts

A simplification that cuts a real corner needs a known ceiling and upgrade path.
For a proposed shortcut, recommend a `ponytail:` comment, for example:

```python
# ponytail: global lock, per-account locks if throughput matters
```

Within the reviewed scope, check existing `ponytail:` comments for the limit and
trigger to revisit. Flag a missing trigger as `no-trigger`; check whether a named
ceiling is already exceeded. Keep the review scoped to the diff and nearby effects;
the separate upstream debt skill’s whole-repo ledger is not part of this pass.

## When NOT to be lazy

Never simplify away: input validation at trust boundaries, error handling that
prevents data loss, security measures, accessibility basics, public contracts,
or anything explicitly requested. Propose cuts within those requirements.

Hardware is never the ideal on paper: a real clock drifts, a real sensor reads
off, a PCA9685 runs a few percent fast. Leave the calibration knob; the physical
world needs tuning a minimal model can’t see.

Lazy code without its check is unfinished. A smoke test or `assert`-based
self-check is not bloat. Preserve checks that protect real behavior; non-trivial
logic needs a runnable check that fails if it breaks. Fit the repo’s test practice.

Correctness, security, and performance findings belong to the parent’s normal
review triage. This review hunts complexity; safety constraints still decide
whether a proposed cut is valid.

## Findings

One concise item per proven cut: location, tag, what to cut, what replaces it,
and the code evidence that makes the replacement safe.

- `delete:` dead code, unused flexibility, speculative feature. Replacement: nothing.
- `reuse:` something this repo or an installed dependency already supplies. Name it.
- `stdlib:` hand-rolled thing the standard library ships. Name the function.
- `native:` dependency or code doing what the platform already does. Name the feature.
- `yagni:` abstraction with one implementation, config nobody sets, layer with one caller.
- `shrink:` same logic, fewer lines. Show the shorter form.

Examples of the desired wording, once the code supports the claim:

- `L4: native: moment.js imported for one format call. Intl.DateTimeFormat, 0 deps.`
- `repo.py:L88: yagni: AbstractRepository with one implementation. Inline it until a second one exists.`
- `L30-44: shrink: manual loop builds dict. dict(zip(keys, values)), 1 line.`

Rank biggest cuts first: concepts, dependencies, files, then lines. End with
coverage, gaps, and estimated net line/dependency cuts, or `unknown` where they
cannot be grounded. Estimates describe proposed cuts to existing code, not
measured savings. Never claim savings against code that was never written or
apply upstream benchmark numbers to this repo.

If nothing survives the evidence, report `Lean already. No cuts found.` with
coverage and any gaps. The parent decides whether the whole change can ship.
