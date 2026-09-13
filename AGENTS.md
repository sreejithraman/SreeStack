# SreeStack

This repo is the source of truth for user skills. Edit them here, not in live
skill folders. Built-in and plugin-managed skills stay with their hosts.

- Design each skill as one coherent tool for its current task. On every revision,
  especially a large one, reconsider its structure as if writing it from scratch.
  Preserve useful behavior and important details, not inherited file layouts or
  wording. Merge overlap and resolve conflicting guidance.
- Organize references by the task, concept, or interaction they teach. Link them
  from `SKILL.md` where an agent needs them. Source authors and upstream skill
  boundaries must not shape the skill's instructions or reference groups.
- Keep origins, import history, and source mappings in `SOURCES.md`; put credits
  in `README.md` and required license notices in the repo's notice files. Skill
  instructions should stand on their own without origin notes. Keep technical
  citations beside guidance when they support an API or behavior claim.
- Keep `skills/` flat. Put each skill’s supporting files inside its folder.
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
- Keep workflow rules in the skill and purpose and setup in [README.md](README.md).
