# Build the Lever

For substantial edits, migrations, analyses, or checks, consider a rerunnable
codemod, script, query, generator, or shared task recipe. Prefer the smallest tool
that makes the work or its proof reproducible. Do one representative unit to learn
the recipe, then compare the automated result with that known case. Make reruns
safe and keep the tool when future verification or maintenance needs it.

Use a deterministic pass for mechanical work it can cover; reserve independent
agents for decisions and slices that benefit from them. Keep shared recipes and
acceptance criteria outside delegates' writable scope. Small obvious edits can
remain direct; tool-building should earn its setup and maintenance cost.
