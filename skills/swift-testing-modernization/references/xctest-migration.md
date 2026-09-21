# XCTest Migration

Use this reference for XCTest unit and integration tests. Migrate one coherent class or helper boundary at a time; mixed XCTest and Swift Testing code is supported during the transition ([Apple migration guide](https://developer.apple.com/documentation/testing/migratingfromxctest)).

## Suite and fixture lifecycle

- Replace `import XCTest` with `import Testing` only after the file no longer needs XCTest. Keep both imports while content is mixed.
- Remove `XCTestCase` inheritance. Prefer a `struct` suite. Use an `actor` or `final class` when reference identity or teardown requires it.
- Move per-test setup into stored-property defaults or `init()`. The initializer may be `async throws`. Swift Testing creates a distinct suite instance for every instance test function ([suite lifecycle](https://developer.apple.com/documentation/testing/organizingtests)).
- Move synchronous teardown into `deinit` on an actor or final class. Treat `addTeardownBlock` separately: preserve cleanup after success, ordinary failure, and thrown fail-stop; last-in, first-out order; actor isolation; and async or throwing cleanup failures as test issues. A synchronous nonthrowing `defer` works only when it is registered before any exit and reproduces those semantics. For async or throwing cleanup, use a scoped helper or `do`/`catch` structure that runs cleanup on success and error while preserving the original outcome. Keep the test in XCTest when the lifecycle cannot be reproduced safely.
- Replace implicitly unwrapped fixture properties with initialized nonoptional values where the old setup guaranteed a value.
- Add `@MainActor` only where the old synchronous XCTest method actually depended on main-actor execution. Swift Testing otherwise runs tests on arbitrary tasks.

Review imports after removing XCTest. Add direct imports for APIs the file uses instead of relying on modules that XCTest happened to re-export.

### Toolchain compatibility

Check the project's compiler and Xcode versions before choosing a replacement. Current minimums for migration features that arrived after Swift Testing's first release are:

| Feature | Minimum built-in toolchain | Older-toolchain path |
| --- | --- | --- |
| Range-valued `confirmation(expectedCount:)` and the error returned by `#expect(throws:)` | Swift 6.1 / Xcode 16.3 | Use an exact confirmation count where equivalent. Use an exact error or matcher check that the compiler supports. |
| `Attachment` and `Attachable` | Swift 6.2 / Xcode 26 | Keep the XCTest attachment and its test in XCTest when the evidence must be preserved. |
| `Test.cancel()` | Swift 6.3 / Xcode 26.4 | Express a pre-run condition as a trait, or keep the dynamically skipped test in XCTest. |

These minimums come from the Swift Testing source documentation for [confirmations](https://github.com/swiftlang/swift-testing/blob/main/Sources/Testing/Issues/Confirmation.swift), [attachments](https://github.com/swiftlang/swift-testing/blob/main/Sources/Testing/Attachments/Attachment.swift), and [test cancellation](https://github.com/swiftlang/swift-testing/blob/main/Sources/Testing/Test%2BCancellation.swift). Do not raise the project's toolchain merely to complete a migration.

## Test declarations and checks

Replace the `test` naming convention with `@Test`. A containing type is already a suite; add `@Suite` when it needs a display name or suite-level traits.

Use the expression that states the relationship directly:

| XCTest | Swift Testing |
| --- | --- |
| `XCTAssert(x)`, `XCTAssertTrue(x)` | `#expect(x)` |
| `XCTAssertFalse(x)` | `#expect(!x)` |
| `XCTAssertNil(x)` | `#expect(x == nil)` |
| `XCTAssertNotNil(x)` | `#expect(x != nil)` |
| `XCTAssertEqual(x, y)` | `#expect(x == y)` |
| `XCTAssertNotEqual(x, y)` | `#expect(x != y)` |
| identity and ordering assertions | `#expect` with `===`, `!==`, `<`, `<=`, `>`, or `>=` |
| `try XCTUnwrap(x)` | `try #require(x)` |
| `XCTAssertThrowsError(try f())` | `#expect(throws: (any Error).self) { try f() }` |
| `XCTAssertNoThrow(try f())` | `#expect(throws: Never.self) { try f() }` |
| unconditional `XCTFail` | `Issue.record` |

Prefer an exact error value with `#expect(throws:)` when the error is `Equatable`. If the old closure inspected the thrown error, capture the result of `#expect(throws:)` and keep equivalent checks.

There is no direct Swift Testing equivalent for `XCTAssertEqual(_:_:accuracy:)`. Use the project's numeric comparison facility; Apple's guide points to `isApproximatelyEqual()` from Swift Numerics.

### Preserve failure control

`#expect` records an issue and continues. `try #require` records an issue and stops the current test by throwing. Preserve this distinction:

- Convert `XCTUnwrap` and prerequisite assertions to `try #require` when later code is invalid without the value or condition.
- When an XCTest method sets `continueAfterFailure = false`, use `try #require` for checks that previously stopped execution. If setup set it for the whole class, audit every method in the migrated suite.
- Override the table's continuing forms wherever fail-stop behavior applied. Convert `XCTFail("…")` to `try #require(false, "…")`. For `XCTAssertNoThrow`, call `try f()` directly so an error stops the test. When its custom message carries useful context, catch the error and terminate with `try #require(false, "context: \(error)")`. Add `throws` to the migrated test as needed.
- Do not mechanically promote every assertion to `#require`; doing so can hide independent failures that XCTest previously reported together.

## Asynchronous behavior

Prefer structured concurrency. Await an async API directly. When bridging a callback that returns one result, preserve the XCTest wait's deadline, timeout outcome, late-callback behavior, and cancellation behavior. Use the project's bounded async helper when it has one. Keep the test in XCTest when no safe bounded bridge exists; a bare checked continuation can suspend forever if the callback never arrives.

Use `confirmation` for asynchronously delivered events whose producer completes within the confirmation closure. A confirmation does not wait after its closure returns; it records an issue if the expected count was not reached by then ([testing asynchronous code](https://developer.apple.com/documentation/testing/testing-asynchronous-code)). Preserve inverted and repeated-event expectations with an appropriate expected count or range.

Do not translate `XCTestExpectation` to `confirmation` solely by syntax. First determine what caused the old wait to finish and whether the migrated closure keeps that work in scope. Exercise the missing and late callback paths when the migration changes the waiting mechanism.

## Skips, known failures, and evidence

- Express a pre-run condition with `.enabled(if:)` or `.disabled(if:)`. Put `@available` on individual `@Test` functions for platform or language availability; containing suite types must remain universally available. Use `try Test.cancel("reason")` when the reason arises during a test, and allow that test to throw.
- Map `XCTExpectFailure` with a closure to the same `withKnownIssue` scope. The no-closure form affects the rest of an XCTest method and has no direct equivalent; wrap the intended remainder of the migrated test in `withKnownIssue`. Preserve its condition, issue matching, and strictness. Mark an issue intermittent only when the original test allowed intermittent success ([Apple migration guide](https://developer.apple.com/documentation/testing/migratingfromxctest)).
- Replace `XCTAttachment` with `Attachment.record` when the evidence remains useful. Confirm the value conforms to `Attachable` and that the runner keeps attachments where the project expects them.

## Parallel execution

XCTest runs tests in a suite sequentially by default; Swift Testing runs tests in parallel by default. Remove shared mutable fixtures when practical. When behavior genuinely depends on suite-local shared state, annotate the suite with `@Suite(.serialized)` and document the dependency that justifies it. Serialization prevents overlap among the suite's descendants but does not promise a particular sequence. Remove order dependencies, combine inherently ordered stages into one test, or keep them in XCTest.

Serialization applies recursively within that suite, but does not coordinate it with unrelated suites. Give tests unique resources, place related suites under one serialized ancestor when that structure is accurate, or use a shared synchronization owner.
