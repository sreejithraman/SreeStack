# Glossary paths

Resolve the domain glossary before reading or writing vocabulary:

1. Use the paths configured by the project, including `docs/agents/domain.md`
   or its agent instructions.
2. Otherwise follow an existing `GLOSSARY-MAP.md` or legacy `CONTEXT-MAP.md`
   to the glossary for the topic. Read the map's linked paths as written.
3. For a single context, use an existing `GLOSSARY.md` or legacy `CONTEXT.md`.
   Treat `CONTEXT.md` as a glossary only when its content serves that purpose.
4. When no domain glossary exists, readers proceed without one. Domain modeling
   creates `GLOSSARY.md` lazily when the first term is resolved.

Use `GLOSSARY-MAP.md` for a new multi-context layout. Preserve established
paths and names; introduce a rename only when the user requests a migration.
If competing files disagree and configuration does not select one, resolve
which is authoritative before writing. Keep one vocabulary source per context.

In skill examples, `GLOSSARY.md` means the resolved glossary, and
`GLOSSARY-MAP.md` means the resolved map. This applies to legacy and custom paths.
