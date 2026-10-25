# Formal verification

Use for requested invariant proofs or model checking, and for maintaining
existing formal checks. Keep setup and drift repair in one workflow. A checker
establishes a property within its model, assumptions, and bounds; real product
acceptance still follows Verify's public-entry-point procedure.

## Select the property and tool

Start with the named area or failure. Otherwise inspect the code for a
consequential promise whose failure tests are unlikely to reach. State the
property and user harm in plain language, independently of the implementation.

Choose the least costly tool that answers the question. Event interleavings
often suit a small model checker, with TLA+ as a starting option. Input,
arithmetic, or memory properties may suit a verifier that checks the actual
code. Requirements beyond a finite bound may need an inductive proof. Reuse
project tooling and discover its actual version, commands, and prerequisites.
When no suitable verifier is available, report the gap; generated-input tests
against real code can add evidence but do not substitute for the requested proof.

## Establish correspondence before checking

Find existing models, proofs, harnesses, and coverage records by their function,
not a fixed file or skill name. Respect existing invocation policies. For each
check, collect its property, covered files and symbols, assumptions and bounds,
run command, tool version, and last confirmed code revision. Include relevant
uncommitted changes in the artifact identity. If no sync record exists, use the
last verification-file commit only as a provisional baseline and disclose it.

For a new check, map each modeled variable, guard, action, or proof obligation
to code a reviewer can inspect. Model an indivisible action only when the code
provides that atomicity; expose intervening reads, writes, and suspension points
that can change the outcome. State omitted effects and environment assumptions.
For a design with no code yet, label conclusions as design-model evidence.

For maintenance, run the existing check before editing and retain the result.
Inspect changes since its sync revision, including moved or split functions,
new writers of guarded state, and the current working diff. Classify each
relevant change as no effect, model/harness drift, an intentionally changed
promise, or a possible code defect. Check this against code and verification,
rather than relying on commit messages alone.

Update the model or harness from current code before judging the rerun. Change
a property only with evidence that its promised behavior intentionally changed;
record old and new wording and that evidence. Preserve bounds unless the code
requires a correction, and disclose any reduction in coverage.

## Run and challenge the result

Run the check and retain the command, artifact identity, configuration, and
raw result. Report incomplete exploration, timeouts, and missing prerequisites
as blocked evidence rather than a pass.

For a failure, explain the counterexample in domain terms and replay its steps
against the real code through reachable interfaces where possible. If a step
cannot occur, correct the model or harness and rerun. If all steps are feasible,
report a code-bug candidate with the supported harm, separating reproduced steps
from code-reading evidence. Name an introducing commit only when history or
revision checks establish it; otherwise leave onset unknown. Keep findings
separate from repairs unless the active task authorizes product changes.

For a pass, show that the check can detect the guarded failure using a known
bad revision or an isolated broken variant. For code-level verification, mutate
the real guarded path. For a hand-written model, make the corresponding model
change and explain its relation to the code defect; replay the defect against
real code when possible. A model does not automatically detect edits to code
it never reads. Record whether the experiment proves property sensitivity,
code correspondence, or both. Restore the fixture and rerun to establish the
original result; preserve existing findings rather than forcing a clean pass.

## Keep reusable checks current

Follow Verify's documentation policy: use a temporary plan unless maintaining
existing verification docs or the user requested reusable setup. Keep models,
harnesses, and property files with the project's verification tooling. Put the
rerun recipe and coverage record in the established project docs, linking from
the map when present; a generated project skill is unnecessary.

Record what code each check describes, its property and limits, the reproducible
command, and the source revision last reconciled with it. Advance that revision
only after correspondence and the check's sensitivity are established. A faithful
model that reveals a bug can be in sync while failing; store the verdict
separately. Leave a blocked check's previous sync revision intact and mark any
unverified recipe draft. Keep verification updates distinguishable from product
fixes and retain counterexamples outside disposable mutation fixtures.

Follow a new or changed recipe once as a cold reader before calling it usable.
Report correspondence as unchanged, updated, or blocked, and the property as
passed, failed, blocked, or untested, with coverage limits. Explain when an old
pass described stale code. Give counterexample steps, replay evidence, tool and
bound choices, sensitivity checks, and the rerun command. Optional diagrams use
domain labels and retain the underlying trace; a drawing is not additional proof.
