# Laziness Protocol

Understand the requested behavior and actual consumers before minimizing the
solution. Try the first option that meets the requirements:

1. Remove work or a concept that is unnecessary.
2. Reuse an existing implementation or pattern in the repository.
3. Use the standard library or native platform capability.
4. Use an already-installed dependency when it fits.
5. Write the smallest clear implementation that handles the real cases.

Consolidate repeated decisions under one owner. Count the knowledge callers
must coordinate, not just changed lines. A small patch in the wrong place can
leave sibling callers broken. Preserve interfaces, adapters, and checks whose
consumers or invariants justify them.
