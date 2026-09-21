# Suite Modernization

Use these changes selectively for existing Swift Testing suites. Keep a change when it improves a real maintenance, selection, isolation, or diagnostic problem.

## Parameterize repeated behavior

Replace repeated tests or an opaque loop with `@Test(arguments:)` when one test body describes every case. Each argument becomes its own reported case, which makes the failing input visible ([parameterized tests](https://developer.apple.com/documentation/testing/parameterizedtesting)).

- Use one collection for one varying input.
- Two collections produce their Cartesian product. Use `zip` when inputs are paired.
- Keep separate test functions when cases have materially different setup, behavior, or expected diagnostics.
- Prefer stable, encodable argument types when developers need to rerun a selected case.

## Tighten suite structure

- Put related tests in suites that match the behavior they specify. Nest suites only when inherited traits or navigation improve.
- Move repeated fixture creation into a suite initializer while keeping each test's instance independent.
- Replace shared mutable state with per-test values or concurrency-safe collaborators. Use `.serialized` only for a remaining suite-local dependency.
- Apply tags, conditions, time limits, and bug links at the narrowest level that accurately describes the affected tests. Suite traits are inherited by contained tests ([traits](https://developer.apple.com/documentation/testing/traits)).

## Improve checks and diagnostics

- Use `#require` for prerequisites and unwraps; use `#expect` for independent outcomes that can all be evaluated.
- Prefer expressions that show the relationship directly so macro diagnostics can display the relevant values.
- Use `withKnownIssue` only for a tracked, understood defect. Keep its matching and condition narrow so new failures remain visible.
- On Swift 6.2 / Xcode 26 or later, record an attachment when a value, file, image, or structured artifact materially shortens diagnosis ([availability](https://github.com/swiftlang/swift-testing/blob/main/Sources/Testing/Attachments/Attachment.swift)). Avoid routine attachments that add noise or storage without explaining failures.
- Use `confirmation` only for events delivered before its closure returns. Await ordinary async results directly.

## Check the result

Run the affected cases individually and through their containing suite. If parameterization, fixtures, or parallel safety changed, compare case discovery and run the suite repeatedly or under the project's stress method. A modernization is useful only if it preserves coverage and yields clearer selection, isolation, or failures.
