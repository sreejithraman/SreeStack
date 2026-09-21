---
name: swift-testing-modernization
description: Modernize existing Swift unit or integration tests, including incremental migration from XCTest to Swift Testing. Use for test-suite migration or restructuring; use XCTest workflows for UI and performance tests.
---

# Swift Testing Modernization

Modernize tests without changing the behavior they specify. Preserve coverage, failure semantics, platform assumptions, and the command the project uses to run the suite.

Use the project's supported Xcode and Swift versions as the API boundary. Swift Testing ships with Xcode 16 and Swift 6 toolchains; prefer the built-in module rather than adding the `swift-testing` package unless the project already has a reason to use it ([distribution guidance](https://github.com/swiftlang/swift-testing/blob/main/Documentation/Distributions.md)).

Check each migration API against that boundary. Swift Testing gains APIs between toolchain releases; when the supported version lacks a semantics-preserving replacement, keep that test or construct in XCTest as a deliberate holdout.

## Establish the baseline

1. Find the test targets, test plans, package manifests, CI commands, and supported toolchain versions.
2. Classify the affected tests as XCTest unit or integration tests, Swift Testing tests, performance tests, or XCTest UI automation.
3. Run the narrowest existing command that covers the slice. Record selected tests, failures, skips, and known flaky behavior. If the baseline cannot run, identify that constraint before editing.
4. Choose a small, coherent slice. XCTest and Swift Testing can coexist in one target and source file, so migration need not be all at once ([Apple migration guide](https://developer.apple.com/documentation/testing/migratingfromxctest)).

Keep UI automation and performance tests in XCTest. Swift Testing is intended for unit and integration tests that call code directly; Apple still directs UI and performance testing through XCTest ([Xcode testing systems](https://developer.apple.com/documentation/xcode/adding-tests-to-your-xcode-project)).

## Choose the work path

- For XCTest unit or integration tests, read [XCTest migration](references/xctest-migration.md) before editing. Account for every setup, teardown, assertion, skip, expected failure, asynchronous wait, attachment, and execution-order dependency in the selected slice.
- For tests already using Swift Testing, read [suite modernization](references/suite-modernization.md). Apply only changes that improve diagnostics, isolation, selection, or maintenance for the current suite.
- If the user asks for test-first or red-green work, use the `tdd` skill. For ordinary coverage additions, use the project's test workflow. This skill handles the structure and semantics of an existing suite.
- If the request is only to diagnose a failing test, use the `diagnosing-bugs` skill. Return here only when diagnosis identifies a bounded migration or suite-structure change.

## Make a behavior-preserving slice

Trace each old test to its replacement. Preserve what makes execution stop, what may continue after a failed check, which actor owns thread-sensitive work, and whether cases share mutable state.

Prefer isolated fixtures and parallel-safe tests. Add serialization only when the selected slice still depends on shared state that cannot reasonably be removed. A serialized suite prevents its descendants from running concurrently; it does not guarantee their sequence or coordinate them with unrelated tests ([parallelization rules](https://developer.apple.com/documentation/testing/parallelization)).

Keep names and comments that explain business behavior. Use display names, tags, bug links, conditions, known issues, and attachments when they improve test selection or failure diagnosis. Avoid broad cleanup outside the selected slice.

## Verify the migration

1. Build and run the same narrow command used for the baseline.
2. Compare discovery and outcomes: the intended cases still run, expected skips and known issues remain visible, and no assertion became weaker or non-fatal by accident.
3. Run the containing target or test plan. Exercise parallel execution when the migration changed fixture ownership, global state, actor isolation, or serialization.
4. Inspect at least one representative failure when assertion or async-event mechanics changed. Confirm the failure points to the useful expression or event and stops or continues at the intended place.
5. Report the migrated slice, commands and outcomes, deliberate XCTest holdouts, and any baseline failure that prevented a comparison.

The slice is complete when the same behavior is covered, the intended tests are discovered in the project's normal runner, and the broader affected target passes or its pre-existing failures are clearly separated.
