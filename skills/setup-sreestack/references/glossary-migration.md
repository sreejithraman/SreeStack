# Migrate legacy glossary names

Use for an explicit glossary migration or one agreed during repository setup.
The result is the same domain vocabulary under `GLOSSARY.md` and
`GLOSSARY-MAP.md`, with its consumers pointing to the new paths. Migration alone
does not configure an issue tracker or triage labels.

## Discover and plan

1. Resolve the authoritative vocabulary with
   [glossary paths](../../domain-modeling/references/glossary-paths.md). Inspect
   the configured files and map targets, including per-context glossaries.
   Read each candidate: rename `CONTEXT.md` only when it is a domain glossary,
   and `CONTEXT-MAP.md` only when it indexes domain glossaries. General context
   documents keep their names.
2. Inspect Git status and local edits. List each source and destination, keeping
   its directory: `CONTEXT.md` becomes `GLOSSARY.md`; `CONTEXT-MAP.md` becomes
   `GLOSSARY-MAP.md`. Preserve the vocabulary, context boundaries, custom
   locations, and ADRs. Leave other custom filenames alone unless the request
   includes them. Search for consumers of the exact old paths: map links,
   `docs/agents/domain.md`, `AGENTS.md`, `CLAUDE.md`, current docs, and any
   scripts or configuration that actually read those files.
3. Resolve conflicting destinations or competing authorities before moving
   that context. Preserve both files; do not overwrite, concatenate, or delete
   either to resolve a collision. Ask which vocabulary to retain when the
   evidence and existing instructions do not settle it. Include file merges
   only when explicitly requested. Show the concrete plan and use existing
   authorization; a migration request already authorizes unambiguous renames
   and their reference updates.

## Apply and verify

4. Move tracked files with `git mv -- <old-path> <new-path>`; use a filesystem
   move for untracked files. Preserve the current contents, including local
   edits. Recheck destinations before moving; a rename must not overwrite an
   existing file. If a candidate is a symlink or points outside the repo,
   resolve its ownership and scope before moving or editing its target.
5. Update the affected map links and active consumers using their existing
   relative paths. Edit path references precisely; avoid replacing the word
   “context” throughout the repo. Preserve historical notes, upstream citations,
   and unrelated documents. Update existing domain configuration and agent
   pointers in place. If neither exists, a migration-only run may finish with
   the renamed glossary; it does not need new setup docs or a steering file.
6. Read the final glossaries and maps. Check that definitions and context
   membership are preserved, all map targets exist, configuration and active
   consumers select the new paths, and no live consumer still requires a
   migrated path. Run an affected script or project check when a runtime reader
   changed. Inspect the scoped diff and Git status; preserve unrelated edits.

Report the old-to-new paths, updated consumers, checks, and anything unresolved.
A rerun with only the new names is a no-op. A collision blocks that context's
migration; report partial progress explicitly rather than claiming completion.
