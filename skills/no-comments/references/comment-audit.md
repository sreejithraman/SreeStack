# Comment audit

Read every comment and suppression in the supplied scope with its nearby code.
Work read-only. Return proposed deletions, justified keeps, exact refactor
targets, and unresolved claims. Judge what the comment does, not its tone.

## Keep exceptions

- Legal and license headers.
- Non-obvious behavior forced by an external dependency, platform, vendor, or
  protocol that this project cannot change. Verify the constraint still applies
  on the live path.
- Formatting directives such as `prettier-ignore`; lint suppressions only when
  the rule is faulty, pedantic, or style-only, with the rule and reason identified.
- Documentation that defines a public API contract.
- Issue or RFC links explaining a constraint code cannot express.

## Delete or repair

Propose deleting narration, redundant section banners, and commented-out code.
For surprises in code we own, identify the exact in-scope symbol and a rename,
extraction, type, or boundary change that would make the behavior clear.
Intentional behavior alone is not a defect; flag its unclear expression.

Read long justifications, `IMPORTANT`, `do not remove`, `too risky`, and
`fine for now` claims against their named symbol or call. Establish whether
the explanation documents an external limit, an enforceable invariant, or a
workaround in our code. State the evidence and required repair; shortening a
justification does not fix the workaround. Mark uncertain constraints unresolved
rather than proposing their blind deletion.

Audit `eslint-disable`, `@ts-ignore`, `@ts-expect-error`, and analogous
directives even when buried in larger comments. Inspect the actual rule or
diagnostic. A suppression of correctness or safety checks requires a root-cause
fix, then removal and verification. Distinguish a negative test's intentional
`@ts-expect-error` assertion from a suppression hiding an application error;
preserve the assertion unless its test is obsolete.

For constraints such as `do not change wording` or `talk to X before changing`,
identify whether a type, runtime check, test, or lint could enforce the real
requirement. Respect project change rules and external constraints. Propose an
encoding only within scope; flag what must remain documented.

## Return

List files audited and gaps. For each finding, give its location, proposed
deletion or keep, evidence, exact refactor target if needed, and verification.
Count proposed deletions separately from comments awaiting repair or evidence.
