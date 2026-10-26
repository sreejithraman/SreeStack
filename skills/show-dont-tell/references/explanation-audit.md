# Explanation audit

Inspect explanatory prose in the supplied scope alongside the artifact and its
consumers. Establish what knowledge each passage contributes before changing it.
A passage can serve several purposes; preserve necessary knowledge while
repairing the reason for the explanation.

| Why the explanation exists | What to do |
| --- | --- |
| Narrates readily discoverable facts | Remove the repetition or point to the source. |
| Compensates for confusing structure | Improve the underlying code or document before removing its explanation. |
| Reminds agents about an enforceable rule | Encode the rule and verify enforcement before removing the reminder. |
| Repeats knowledge maintained elsewhere | Keep one authoritative home and link when useful. |
| Explains a consequential decision | Apply the [three ADR criteria](../../domain-modeling/SKILL.md#offer-adrs-sparingly); keep smaller rationale local. |
| Supplies necessary knowledge unavailable elsewhere | Keep it concise and near its use. |

Read defensive claims such as `IMPORTANT`, `do not remove`, `too risky`, and
`fine for now` against the actual constraint or workaround. Identify what forces
the behavior and whether its cause can be repaired within scope. Shortening the
justification does not repair the cause. Keep uncertain constraints documented.

## Code comments and directives

- Read every comment and embedded suppression in scope, including directives
  buried inside larger comment blocks.
- Remove redundant narration, section banners, and obsolete commented-out code
  only after verifying that their knowledge is unnecessary or carried elsewhere.
- Preserve necessary formatting directives and justified exceptions for faulty
  or style-only rules. Inspect the actual diagnostic before proposing a repair;
  fix correctness problems before removing their suppressions.
- Distinguish intentional negative-test assertions such as `@ts-expect-error`
  from directives hiding application errors. Preserve the assertion unless its
  test is obsolete.

For each proposed change, identify the passage, why it exists, the underlying
repair or authoritative replacement, and what knowledge must remain.
