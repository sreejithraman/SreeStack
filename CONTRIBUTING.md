# Contributing

Keep changes focused. Explain which user task the change serves and how you
checked it. For skill changes, include a sample request and the expected result.

Read [AGENTS.md](AGENTS.md) and the skill’s entry in [SOURCES.md](SOURCES.md)
before editing. Preserve local changes and invocation choices when updating
from upstream. Record upstream origins, import revisions, and current differences
in SOURCES.md; follow AGENTS.md for what belongs there. Put technical citations
beside the relevant guidance and credit authors in README.md. Include license
notices and check the terms before copying material.

Keep invocation settings aligned across hosts. For an explicit-only skill, set
`disable-model-invocation: true` in `SKILL.md` for Claude Code
and `policy.allow_implicit_invocation: false` in `agents/openai.yaml` for Codex.
For automatic discovery in both hosts, omit those restrictions (or set their
opposite values). See [skill mechanics](skills/writing-for-agents/SKILL-MECHANICS.md)
for the invocation choice.

Keep each skill in one folder directly under `skills/`. Put supporting files
beside that skill. Keep repo-wide records outside `skills/`.

Run the tests and repository checks with `python3 scripts/check.py`. It needs no
setup. The first run with a set of pinned requirements needs network access and
write access to the clone's Git directory; later runs in every worktree need
neither. To run one script or test, pass it as arguments:
`python3 scripts/check.py scripts/test_sync_hosts.py`.

Before submitting:

- Run `python3 scripts/check.py` and `git diff --check`.
  CI also scans Git history for secrets.
- For skill changes, try a sample request in the intended host and report any
  tool or account requirements. Mark checks you could not run.
- Scan changes for secrets, personal paths, and account-specific values.

Original contributions use the root [MIT License](LICENSE).
