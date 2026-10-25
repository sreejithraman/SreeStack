# Test Behavior, Not Implementation

Call the subject through its consumer-facing interface and assert an independently
established result or observable effect. Expected values should come from the
contract, a worked example, or a trusted fixture. The test must fail if the relevant
behavior is removed or returns the wrong result. For mocked effects, inspect the
meaningful payload; for an empty or absent result, exercise a contrasting case
when it distinguishes correct behavior from doing nothing.

The same test should keep passing when internals change while the observable
contract stays the same. Assert an external service's meaningful payload when
that effect is part of the contract; avoid pinning private helper calls or
internal ordering that consumers cannot observe.

Empty results, error assertions, relation checks, and compile-time type tests can
be valid contracts. Judge what they detect instead of banning assertion syntax.
Keep [tdd](../../tdd/SKILL.md)'s seam selection and vertical red/green workflow
for implementation, and its examples for tests and mocking.
