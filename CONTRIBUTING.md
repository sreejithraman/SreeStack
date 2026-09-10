# Contributing

Keep changes focused. Explain which user task the change serves and how you
checked it. For skill changes, include a sample request and the expected result.

Read [AGENTS.md](AGENTS.md) and the skill’s entry in [SOURCES.md](SOURCES.md)
before editing. Preserve local changes and invocation choices when updating
from upstream. Record upstream origins, import revisions, and current differences
in SOURCES.md; follow AGENTS.md for what belongs there. Put technical citations
beside the relevant guidance and credit authors in README.md. Include license
notices and check the terms before copying material.

Keep invocation fields aligned: manual-only skills use
`disable-model-invocation: true` in `SKILL.md` and
`allow_implicit_invocation: false` in `agents/openai.yaml`; automatically
discoverable skills use the opposite values or omit both.

Keep each skill in one folder directly under `skills/`. Put supporting files
beside that skill. Keep repo-wide records outside `skills/`.

Install the checker dependency with
`python3 -m pip install -r scripts/requirements-checks.txt`.

Before submitting:

- Run `python3 scripts/check_skills.py` and `git diff --check`.
  CI also scans Git history for secrets.
- For skill changes, try a sample request in the intended host and report any
  tool or account requirements. Mark checks you could not run.
- Scan changes for secrets, personal paths, and account-specific values.

Original contributions use the root [MIT License](LICENSE).
