# Document Apps

Preserve an established document architecture unless the task includes migration.
For a greenfield iOS, macOS, or visionOS 27 document app, use an `@Observable`
reference type conforming to `ReadableDocument`, `WritableDocument`, or their
combined `Document` protocol. These APIs are unavailable on watchOS and tvOS.

## Keep the I/O boundary explicit

The read path is:

1. `reader(configuration:)` creates a reader.
2. `DocumentReader.read(from:progress:)` produces a snapshot off the main actor.
3. `apply(snapshot:previous:)` updates the document on the main actor.

The write path is:

1. `snapshot(contentType:)` captures current state on the main actor.
2. `writer(configuration:)` creates a writer.
3. `DocumentWriter.write(snapshot:to:previous:progress:)` writes off the main
   actor with coordinated access.

Use the `DocumentGroup` viewer initializer for a read-only app and declare its
bundle document role as `Viewer`. Use `Subprogress` when custom reading or writing
needs to report progress. Register undo explicitly for edits that participate in
autosave.

Apple's [document app guide](https://developer.apple.com/documentation/swiftui/creating-a-document-based-app)
and [migration guide](https://developer.apple.com/documentation/swiftui/updating-your-document-based-app)
define the lifecycle.

## Use the final SDK signatures

`FileWrapperDocumentReader` receives one `FileWrapper`. A
`FileWrapperDocumentWriter` closure receives both the new snapshot and the
previous optional file wrapper, which supports incremental package updates.
`URLDocumentConfiguration` and its URL, modification-date, and coordinator
members are main-actor isolated.

Keep `FileDocument` or `ReferenceFileDocument` when an existing deployment target
or architecture requires it. For new OS 27 document types, use the reader and
writer protocols Apple now recommends. Validate open, edit, undo, autosave,
explicit save, conflict or external change, package updates, failure, and
read-only behavior on representative files.
