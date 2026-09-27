# Third-party notices

This file maps bundled material to upstream license notices. See
[SOURCES.md](SOURCES.md) for exact import revisions, paths, and local changes.
SreeStack’s original work uses the root [MIT License](LICENSE). Imported
material keeps the terms listed below; the root license does not replace them.

| Source | Bundled material | Notice |
| --- | --- | --- |
| Sree Raman / Snip Snap | add-to-snip-snap | [MIT](licenses/sreejithraman-snip-snap.txt) |
| Rudrank Riyam | app-store-connect usage and workflow guides | [MIT](licenses/rudrankriyam-app-store-connect-cli-skills.txt) |
| Matt Pocock | Skills and Standards/Spec review references listed in SOURCES.md | [MIT](licenses/mattpocock-skills.txt) |
| Emil Kowalski | animate; motion and gesture behavior; typography and materials; interface access/input and review guidance | [animate MIT](licenses/emilkowalski-animate.txt), [design engineering MIT](licenses/emilkowalski-design-eng.txt) |
| Jakub Antalík / transitions.dev | animate pattern references and tuning guidance | Unresolved: no license file found at the recorded revision |
| Dietrich Gebert / Ponytail | review-fix-loop/references/ponytail.md | [MIT](licenses/DietrichGebert-ponytail.txt) |
| Cursor | review-fix-loop/references/thermo.md | [MIT](licenses/cursor-plugins.txt) |
| Lauren Tan / pstack | project-verification, change-safety, code-why, handoff, goal-swarm, and orchestration adaptations | [MIT](licenses/lauren-tan-pstack.txt) |
| Anthropic skills | ui-design art-direction guidance | [Apache-2.0](licenses/anthropics-frontend-design.txt) ([upstream](https://github.com/anthropics/skills/blob/34040c9c568585f6929bedeaad110ad08f079624/skills/frontend-design/LICENSE.txt)) |
| Anthropic Claude Plugins Community | eli5 | [Apache-2.0](licenses/anthropics-claude-plugins-community.txt) |
| GitHub gh-stack | gh-stack | [MIT](licenses/github-gh-stack.txt) |
| s0xDk / s13k | ui-design skill, web references, and token asset | [MIT and scope note](licenses/s0xdk-refactoring-ui-skill.txt) |
| Million Software | react-doctor | [Modified MIT](licenses/millionco-react-doctor.txt) |
| Vercel Labs | react-best-practices | Unresolved: upstream repo README and skill frontmatter claim MIT; no license file found at the recorded revision |

The files in `licenses/` copy upstream license files at the revisions in
SOURCES.md. Anthropic skills was checked on 2026-09-12; App Store Connect
was checked on 2026-09-08; Vercel Labs react-best-practices was checked on
2026-09-18; the other notices were checked on 2026-09-06. Cursor’s notice comes from
`cursor-team-kit/LICENSE`. Existing per-skill notices remain in place.

React Doctor’s notice includes restrictions on model training and certain paid
products or services. Do not describe it as plain MIT. Its terms still apply alongside
the root license.

The original parent-skill import baseline for animate remains unknown; its
reference imports have recorded revisions in SOURCES.md. The redistributed
design engineering guidance is tied there to commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7`,
while its earlier local import baseline remains unknown. The imported revision
for s0xDk/refactoring-ui-skill also remains unknown. Bundled notices do not resolve
those source-history gaps.
Linked API docs, component catalogs, and other live references sit beside the
guidance they support; links alone are not bundled copies.
