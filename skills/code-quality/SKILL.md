---
name: code-quality
description: Run Crapper, Dryer, and Mutator for complexity, duplication, and mutation-test reports on Clojure, Java, Go, TypeScript, Rust, or Python. Crapper and Mutator also support JavaScript.
---

# Code Quality

Run Crapper, Dryer, and Mutator on a target project and report their complexity,
duplication, and mutation-testing output, leaving source changes and acceptance policy to
the caller. Start from a project root and optional paths, tool subset, or flags. Leave the
tool reports on disk and a structured summary of commands, scope, exit statuses, and
findings. You are done when every selected supported tool has run (or unsupported inputs
and tool failures are reported apart from code findings) and generated report paths are
listed.

Run from the target project's root. Run all three tools unless a subset is
requested. Honor requested paths and flags; without paths, analyze the project.
Check language support for each selected tool and report unsupported inputs
as skipped.

Use `uvx` to run the pinned upstream tools. Follow the [setup](references/setup.md)
if `uvx` is unavailable.

Run the selected commands below, appending requested file or directory paths
and tool flags.

```bash
crapper_source="git+https://github.com/unclebob/crapper.git@6fd92c4c9bcc56efb64a2f8743d5a2993bcfd42d"
dryer_source="git+https://github.com/unclebob/dryer.git@66ff6d21a42c04afcad89c78a80066176d1294b0"
mutator_source="git+https://github.com/unclebob/mutator.git@a5a0cb803b66e0cdb8bf471b3b08af701d424a41"

uvx --from "$crapper_source" crapper
uvx --from "$dryer_source" dryer
uvx --from "$mutator_source" --with "crapper @ $crapper_source" mutator
```

Use each tool's `--help` for options. Supply the project's test or coverage
command when its defaults do not fit. `--changed` selects uncommitted Git
changes; for a branch comparison, resolve the changed paths against the
requested base and pass those paths explicitly.

Return the commands, analyzed scope, exit statuses, and a concise summary of
the output. Include reports written by this run: `.metrics/crap.edn`,
`.metrics/dry.edn`, and `.metrics/mutate/` for the respective tools. Distinguish
tool or coverage failures from code findings. Dryer can report duplicates with
exit status 0; Mutator uses 3 for survivors and 2 for a failed baseline.
When fresh mutation results are needed after tests or dependencies change,
use Mutator's `--mutate-all` to avoid reusing cached kills for unchanged functions.
