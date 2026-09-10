# SreeStack

This repo is the source of truth for user skills. Edit them here, not in live
skill folders. Built-in and plugin-managed skills stay with their hosts.

- Keep `skills/` flat. Use [SOURCES.md](SOURCES.md) for upstream origins, import
  revisions, and current local differences that an upstream update must preserve.
- Use current local skill names in source records. Preserve upstream names and
  paths that identify imported sources.
- Before modifying a skill, read its entry in `SOURCES.md` for its import baseline
  and local differences, including invocation choices.
- Upstream updates must preserve local adaptations and invocation choices
  unless the user asks to change them. The recorded revision is the import
  baseline, not the latest version checked.
- Update `SOURCES.md` when an origin, import baseline, or local difference changes.
  Describe the current difference, not how the skill was built. Keep local-only
  skills to a short origin note. Git holds edit, rename, and review history.
- Put workflow rules in the skill, technical citations beside the guidance they
  support, and purpose, setup, and credits in [README.md](README.md). A source
  note belongs in `SOURCES.md` if it helps identify the upstream material or
  prevents an upstream update from undoing an intentional local choice.
