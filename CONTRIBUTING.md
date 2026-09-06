# Contributing

Keep changes focused. Explain which user task the change serves and how you
checked it. For skill changes, include a sample request and the expected result.

Read [AGENTS.md](AGENTS.md) and the skill’s entry in [SOURCES.md](SOURCES.md)
before editing. Preserve local changes and invocation choices when updating
from upstream. Credit new sources in README.md and record their imported
revision in SOURCES.md. Include their license notices and check the terms
before copying material.

Keep each skill in one folder directly under `skills/`. Put supporting files
beside that skill. Keep repo-wide records outside `skills/`.

Before submitting:

- Run `git diff --check`.
- Check that relative links and referenced files exist.
- For skill changes, try a sample request in the intended host and report any
  tool or account requirements. Mark checks you could not run.
- Scan changes for secrets, personal paths, and account-specific values.

The root license is pending. Resolve the release items in
[OPEN_SOURCE_READINESS.md](OPEN_SOURCE_READINESS.md) before inviting outside
contributions.
