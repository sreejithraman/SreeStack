# Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), which
provides `uvx`. The tools require Python 3.11+, Git, and the target project's
test dependencies. Confirm that `uvx --version` works before running the skill.

The [skill commands](../SKILL.md) fetch pinned Git revisions into uv's isolated
cache on first use. Later runs reuse the cached environments. Clearing the
cache or changing the source or environment requirements can trigger setup
again. Mutator's command includes Crapper as an additional dependency, so it
can import Crapper without sibling checkouts.

Only `uvx` needs to be on `PATH`; the tools need no global command links or
checkout directories. See [uv's tool guide](https://docs.astral.sh/uv/guides/tools/)
for Git sources and additional dependencies.

Coverage runs may install missing test tooling in the target project; reuse
existing coverage or supply project commands when appropriate.
