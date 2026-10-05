# Upstream sources and local differences

Use this file when updating imported skills. Each entry records the upstream
material, the revision last imported, and current local differences.
Source mappings also cover imported references inside locally written skills.
See [AGENTS.md](AGENTS.md) for maintenance rules and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for license notices and gaps.

Commits are import baselines, not the latest versions checked. Unknown means the
baseline was not recorded. A local source path does not prove original authorship.
An entry without a difference note does not prove that its files match upstream.

Keep one entry per skill and one bullet per imported source, followed by plain
descriptions of current local differences, including invocation choices.
Local-only skills need just an origin note.

## 1password

- [openclaw/openclaw / skills/1password](https://github.com/openclaw/openclaw/tree/a229456f487f713315fc799767a97990f407bea6/skills/1password) — `SKILL.md`, `references/get-started.md`, and `references/cli-examples.md`; adaptation baseline commit `a229456f487f713315fc799767a97990f407bea6`. MIT notice in `licenses/openclaw.txt`.

Automatically discoverable in both hosts; triggers on task credential needs
without an explicit 1Password request. Adds user-designated vault-scoped
service-account access, optional automatic item management, and task-specific
personal approval, distinguishing behavioral scope from 1Password enforcement.
Setup, authentication, and credential delivery/storage use task-based references;
machine administration is separate from project consumption. Replaces upstream
secret-printing examples with process-local reads and stdin writes, and browser
filling with capability-based delivery or user sign-in. Omits OpenClaw install
metadata, gateway-specific IPC assumptions, and tmux/session-export workflows.
API claims link to official documentation; README.md holds purpose and setup
prerequisites.

## snip-snap

- [sreejithraman/snip-snap / .agents/skills/snip-snap](https://github.com/sreejithraman/snip-snap/tree/5c1950172f8040a59f6ce4947a13223a30b3ecca/.agents/skills/snip-snap) — commit `5c1950172f8040a59f6ce4947a13223a30b3ecca`. MIT notice in `licenses/sreejithraman-snip-snap.txt`.

## animate

- [emilkowalski/skills](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/animate) — `skills/animate/SKILL.md` and `RECIPES.md`; reference import commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7`. The original parent-skill import baseline remains unknown. MIT notice in `licenses/emilkowalski-animate.txt`.
- [emilkowalski/skills / skills/emil-design-eng](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/emil-design-eng) — press feedback and measured rendering guidance; content verified against commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7`, while the earlier local import baseline remains unknown.
- [emilkowalski/skills / skills/apple-design](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/apple-design) — gesture-intent guidance; content verified against commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7`, while the earlier local import baseline remains unknown.
- [Jakubantalik/transitions.dev](https://github.com/Jakubantalik/transitions.dev/tree/598d3d6ad89dabb4bdf742fd2e887ca53914a888/skills) — `skills/transitions-dev/` and `skills/transitions-polish/`; commit `598d3d6ad89dabb4bdf742fd2e887ca53914a888`. No license file found in this revision; see `THIRD_PARTY_NOTICES.md`. Newer [skill terms](https://github.com/Jakubantalik/transitions.dev/blob/3bc58021c69725d8bf42108632ac6cf14f2b1d3c/skills/transitions-dev/LICENSE.txt) restrict republishing the collection as a competing library, template pack, or component kit. Further imports are held pending redistribution clarification; the import baseline remains unchanged.

- One automatically discoverable cross-platform skill owns motion decisions,
  implementation, tuning, and checks. Its entrypoint holds the shared motion gate
  and routes web work to the imported task-based pattern guides and SwiftUI or
  UIKit work to guidance grounded in current Apple documentation.
  Origin notes and source-based groups are absent from the skill. Current project
  tokens, platform conventions, component behavior, and measured results take
  precedence over examples.
- `transitions-dev/01-*.md` through `32-*.md` map to
  `references/patterns/<name>.md` with numeric prefixes removed. Exceptions:
  `18-texts-reveal.md` maps to `stagger.md`; `29-reasoning-stream.md` maps to
  `log-stream.md`. Pattern variables, state hooks, reduced-motion blocks, and detailed mechanics
  remain. The learn-more hover selectors add fine-pointer/hover gating; other
  pattern code keeps the source behavior except that input-clear’s easing parser
  accepts whitespace in its declared cubic-bezier defaults. Comments use direct wording. Origin
  prose and demo-token mappings are
  removed. Log-stream guidance uses real application status and logs. Card-tilt
  guidance makes touch drag optional and states its scrolling cost. Reduced-motion
  notes correct animation-only and partial guards and require any needed
  JavaScript bypass or cleanup. Log-stream labels its loop as mechanics and
  states the required lifecycle controller. Spinning-counter supplies CSS plus
  construction steps, without claiming a bundled JavaScript builder. Banner
  stacking states its host-size prerequisite.
- `RECIPES.md` sections join the matching menu-dropdown, tooltip, modal, toast,
  accordion, stagger, and tabs-sliding guides as variants chosen by component
  behavior. Its remaining sections map to button-press, drawer, hold-to-confirm,
  scroll-reveal, drag-to-dismiss, crossfade, and programmatic-animation guides.
  Prose gives local use criteria and checks. Code examples remain except for
  the drag dismissal test, which uses recent signed velocity toward the exit
  instead of absolute whole-gesture average speed. Drag dismissal also preserves
  an intent threshold and an explicit browser pan-axis contract before claiming
  direction, and shared web guidance keeps press feedback separate from valid
  action commitment. Curve defaults live beside examples that use them.
  Unsupported performance guarantees are omitted.
- `references/implementation.md` covers shared lifecycle, access, token, and
  measured rendering checks, including inherited custom-property scope.
  `references/tuning.md` adapts the polish scale and rules,
  scopes scans to the request, treats blur and values as choices, and counts
  stagger delay from the last item's zero-based index. Toast close guidance
  uses the pattern's 250ms starting point. Per-pattern variable blocks replace
  the separate `_root.css` copy; global token aliases are omitted.
- Separate dev/polish skills, command and approval flows, automatic token
  replacement, and Refine-panel integration are omitted.

## app-intents

- Local: `skills/app-intents` (SreeStack).

## app-store-connect

- [rorkai/app-store-connect-cli-skills](https://github.com/rorkai/app-store-connect-cli-skills/tree/9a093fa52177d1b784fcbb06f9abfef4974e7701) — `skills/`; commit `9a093fa52177d1b784fcbb06f9abfef4974e7701`, imported 2026-10-03. Author: Rudrank Riyam; MIT notice in `licenses/rudrankriyam-app-store-connect-cli-skills.txt`.

- One discoverable skill: upstream `skills/asc-cli-usage/SKILL.md` supplies the
  entrypoint; the other `skills/<name>/SKILL.md` files map to local
  `references/<name>/guide.md`. Guides retain supporting paths and local links
  and omit skill frontmatter. The skill omits upstream scripts and app settings.
- Guide selection by task, checks against the installed CLI, and IDs and release
  rules from the project. API key creation requires a setup request. Apple Ads
  detail lives in its guide only.
- Screenshot cleanup uses working copies; associative-array examples require
  Bash 4. The guides qualify unsupported ranking claims and distinguish App Store
  description, promotional text, and release-note guidance. Build-ID guidance
  uses the `--build-id` flag required by the installed CLI.

Authentication reuses cached profiles and web sessions, verifies providers, and
serializes interactive challenges. Developer Portal cache recovery follows
status/provider/error diagnosis. macOS package export checks `--pkg-path`
support and retains raw Xcode export when unavailable.


## change-safety

- [cursor/plugins / pstack/skills/blast-radius](https://github.com/cursor/plugins/tree/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack/skills/blast-radius) — commit `ecc249f1e306fc64ddf83c7bed16cacf7c2239db`. MIT notice in `licenses/lauren-tan-pstack.txt`.

Locally written, scoped to change-safety questions and subtle diffs. Preserves
the safety-assumption and executable-proof method without pstack's mandatory
arena, prose-cleanup, or Cursor-specific routing.

## code-why

- [cursor/plugins / pstack/skills/why](https://github.com/cursor/plugins/tree/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack/skills/why) — `SKILL.md` and `references/epistemics.md`; commit `ecc249f1e306fc64ddf83c7bed16cacf7c2239db`. MIT notice in `licenses/lauren-tan-pstack.txt`.

Locally written around code-anchored historical evidence and calibrated claims.
Searches sources proportionally without mandatory parallel investigators,
model settings, or Cursor MCP discovery.

## codebase-design

- [mattpocock/skills / skills/engineering/codebase-design](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/codebase-design) — v1.2.3, commit `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.

Glossary examples use the upstream `GLOSSARY.md` / `GLOSSARY-MAP.md` names;
resolution preserves configured or existing legacy paths, keeps one glossary per
context, and creates new files lazily. Cross-skill calls use host-neutral wording.


## diagnosing-bugs

- [mattpocock/skills / skills/engineering/diagnosing-bugs](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/diagnosing-bugs) — v1.2.3, commit `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.
- Local adaptation: adds conditional Apple-platform references for runtime,
  performance, and memory diagnosis. They use current Apple documentation and
  local Xcode capability discovery, with Instruments as the default profiler
  and ETTrace as an optional project choice. Allows provisional, artifact-backed
  diagnosis when a runnable reproduction is unavailable without treating it as
  verification of a fix.

Glossary examples use the upstream `GLOSSARY.md` / `GLOSSARY-MAP.md` names;
resolution preserves configured or existing legacy paths, keeps one glossary per
context, and creates new files lazily. Cross-skill calls use host-neutral wording.

Markdown import baseline is `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`. The bundled HITL
shell template remains at `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`; its upstream
comment-only changes are omitted.


## domain-modeling

- [mattpocock/skills / skills/engineering/domain-modeling](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/domain-modeling) — v1.2.3, commit `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.

Glossary examples use the upstream `GLOSSARY.md` / `GLOSSARY-MAP.md` names;
resolution preserves configured or existing legacy paths, keeps one glossary per
context, and creates new files lazily. Cross-skill calls use host-neutral wording.

`CONTEXT-FORMAT.md` maps to `GLOSSARY-FORMAT.md`. The local
`references/glossary-paths.md` is the shared compatibility rule for writers and
readers; glossary reading alone does not invoke domain modeling.


## eli5

- [anthropics/claude-plugins-community / eli5/skills/eli5](https://github.com/anthropics/claude-plugins-community/tree/f4c9452f5ca091f1be7064d9faab1b001ea21645/eli5/skills/eli5) — commit `f4c9452f5ca091f1be7064d9faab1b001ea21645`.

## goal-swarm

- Local: `skills/goal-swarm` (SreeStack).
- [cursor/plugins / pstack/skills/swarm](https://github.com/cursor/plugins/tree/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack/skills/swarm) — commit `ecc249f1e306fc64ddf83c7bed16cacf7c2239db`. MIT notice in `licenses/lauren-tan-pstack.txt`.

Locally written goal lifecycle that chooses solo or parallel execution within
an explicitly requested parent goal. It uses pstack's up-front split and
selection rule, gives child goals to agents with independent outcomes, and
leaves agent routing and result integration to `orchestration`. A PR finish
line routes through `pr`; pstack's cloud and model defaults are excluded.

## gemini

- Local: `skills/gemini` (SreeStack).

Locally written agy workflow with prompted analysis and installed-command code
review; invocation remains model-discoverable.

## opencode

- Local: `skills/opencode` (SreeStack).

Locally written OpenCode v2 session workflow with tool-free prompted analysis
and restricted built-in code review; invocation remains model-discoverable.

## gh-stack

- [github/gh-stack / skills/gh-stack](https://github.com/github/gh-stack/tree/d4ab7ab47e5b3e3708a27c8c42abcdf4bc321419/skills/gh-stack) — commit `d4ab7ab47e5b3e3708a27c8c42abcdf4bc321419`.

Invocation remains unchanged. Checks installed-extension capabilities before
newer worktree behavior. Conflict staging follows the diagnostic owner, and
sync rollback guidance preserves partial-restoration recovery state instead of
promising unconditional rollback.


## grill-with-docs

- [mattpocock/skills / skills/engineering/grill-with-docs](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/grill-with-docs) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## grilling

- [mattpocock/skills / skills/productivity/grilling](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/productivity/grilling) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## handoff

- [mattpocock/skills / skills/productivity/handoff](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/productivity/handoff) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.
- [cursor/plugins / pstack session-pickup and pause-safely playbooks](https://github.com/cursor/plugins/tree/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack/skills/poteto-mode/playbooks) — `session-pickup.md` and `pause-safely.md`; commit `ecc249f1e306fc64ddf83c7bed16cacf7c2239db`. MIT notice in `licenses/lauren-tan-pstack.txt`.

The manual-only invocation remains in both hosts. The local skill writes an
off-repo resume note with operational state and supports checking that note on
pickup. It omits pstack's automatic WIP commit and transcript-specific paths.

## improve-codebase-architecture

- [mattpocock/skills / skills/engineering/improve-codebase-architecture](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/improve-codebase-architecture) — v1.2.3, commit `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.

Returns findings, recommendations, and reasons in chat; creates an HTML report
only on request.

Glossary examples use the upstream `GLOSSARY.md` / `GLOSSARY-MAP.md` names;
resolution preserves configured or existing legacy paths, keeps one glossary per
context, and creates new files lazily. Cross-skill calls use host-neutral wording.


## ios-haptics

- Local: `skills/ios-haptics` (SreeStack).

## swift-testing-modernization

- Local: `skills/swift-testing-modernization` (SreeStack).

## swiftui

- Local: `skills/swiftui` (SreeStack).
- [emilkowalski/skills / skills/emil-design-eng](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/emil-design-eng) — component-behavior and access guidance redistributed from the retired local `design-eng` adaptation; content verified against commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7`, while the earlier local import baseline remains unknown.
- [superagents-lab/xcode27-skills / swiftui-whats-new-27](https://github.com/superagents-lab/xcode27-skills/tree/6f9ff8d5ad6000491cb0f483a776b7062e41cd97/swiftui-whats-new-27) — commit `6f9ff8d5ad6000491cb0f483a776b7062e41cd97`, used as a coverage map for independently written SDK 27 guidance.

Includes focused guidance for current platform materials and Liquid Glass rather
than keeping a separate visual-effect skill. Redistributed behavior and access
guidance, button sizing and hit-region checks, and current SDK migration
and feature guidance are folded into the normal SwiftUI workflow; automatic
invocation remains framework- and task-based.

## uikit

- Local: `skills/uikit` (SreeStack).
- [emilkowalski/skills / skills/emil-design-eng](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/emil-design-eng) — component-behavior and access guidance redistributed from the retired local `design-eng` adaptation; content verified against commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7`, while the earlier local import baseline remains unknown.

Redistributed behavior and access guidance is folded into the normal UIKit
workflow; automatic invocation remains framework- and task-based.

## verify

- Local: `skills/verify` (SreeStack).
- [emilkowalski/skills / skills/emil-design-eng](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/emil-design-eng) — interface-review criteria; content verified against commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7`, while the earlier local import baseline remains unknown.
- [emilkowalski/skills / skills/apple-design](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/apple-design) — contrast and reduced-transparency review criteria; content verified against commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7`, while the earlier local import baseline remains unknown.
- [cursor/plugins / pstack verification skills](https://github.com/cursor/plugins/tree/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack/skills) — `create-verification-skill/SKILL.md` and `maintain-verification-skill/SKILL.md`; commit `ecc249f1e306fc64ddf83c7bed16cacf7c2239db`. MIT notice in `licenses/lauren-tan-pstack.txt`.
- [emilkowalski/skills / skills/mobile-native](https://github.com/emilkowalski/skills/tree/e8a175de22ae1e49370fc144c1f3bb9aeedf988d/skills/mobile-native) — mobile browser behavior and matching verification assertions; import baseline `e8a175de22ae1e49370fc144c1f3bb9aeedf988d`.
- [emilkowalski/skills / skills/break-ui](https://github.com/emilkowalski/skills/tree/e8a175de22ae1e49370fc144c1f3bb9aeedf988d/skills/break-ui) — realistic edge-data method, catalog, and content-constrained layout decisions; import baseline `e8a175de22ae1e49370fc144c1f3bb9aeedf988d`.

One automatically discoverable skill owns real-workflow selection, launch,
driving, acceptance judgments, evidence, cleanup, and project documentation.
Ordinary checks use a temporary plan when no map exists and maintain affected
recipes when a map is already set up. Creating a map requires a setup or reusable
documentation request; verification can also explicitly leave existing docs alone.
Reads the project index before selected recipes, expanding to all recipes for
whole-app or whole-map requests. Discloses map-writing examples and interface
audit or accessibility guidance through conditional references.
Centralizes documentation policy and shared verification rules in the main
procedure; map and platform references retain their task-specific guidance.
Uses an authoritative index and feature recipes in project docs, defaulting to
`docs/agents/verification/`, rather than generating project skills. Adapts the
pstack feature formula to user descriptions and sub-features, entry points,
harness driving with assertions and proof, and gotchas. Supports proportional
targeted updates, whole-app verification, source-and-live whole-map maintenance,
and rewriting or reorganizing maps while preserving useful human assertions.
Existing project skills may provide facts consistent with their invocation
policies; this skill retains procedure ownership and leaves migration explicit.
Imported interface criteria retain full requested audit coverage. Web and iOS
checks follow the requested deployment or Simulator/device target. iOS routing
uses available Xcode MCP, CLI, and interface tools without a Build iOS Apps plugin
dependency. Terminal and service checks use process or PTY driving, bounded
completion, public protocols, and fresh persisted-output reads. Harness selection
follows host routing and public user paths, including CLI-driven UIs. Keeps
bounded reproduction attempts, failed-attempt evidence, authorization, isolation,
redaction, run-owned cleanup, and separate documentation and product verdicts.

Edge-data workflow and catalog map to `references/edge-data.md`, with mobile
assertions in `references/web.md`. Comparison controls are optional, fixtures
are type-correct and task-scoped, existing authorization governs fixes, and
retention is proportional. Missing schema limits are distinguished from verified
unbounded input. Emulation and unavailable hardware checks carry explicit
evidence limits. Greetings and attribution instructions are omitted.


## repo-cleanup

- Local source: `~/.agents/skills/post-merge-cleanup`; upstream origin unrecorded.

Accepts merge completion handoffs from `merge`. Cleanup includes verified
task-owned simulator/emulator installs and disposable test data while preserving
shared installs, retained data, and resources needed by unmerged stack layers.

## merge

- Local: `skills/merge` (SreeStack).

PR workflow references use the local `pr` entry point.


## prototype

- [mattpocock/skills / skills/engineering/prototype](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/prototype) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

UI prototypes for web, mobile, and desktop; no logic-prototype mode. The local
workflow chooses enough distinct options to expose the decision, coordinates
with `ui-design`, `animate`, `swiftui` or `uikit`, `verify`, and
`showroom`, and adds explicit rules for live side effects, unavailable target
tooling, comparison-control verification, durable decisions, and proportional
prototype retention and cleanup.

## react-best-practices

- [vercel-labs/agent-skills / skills/react-best-practices](https://github.com/vercel-labs/agent-skills/tree/063bee94c3f4df8453406c830b0a7df0f2860278/skills/react-best-practices) — commit `063bee94c3f4df8453406c830b0a7df0f2860278`. Upstream repo README and skill frontmatter claim MIT; no license file found at this revision.

Keeps all 70 upstream rule topics and a task-based index.
`client-event-listeners` retains the shared-listener pattern with an app-owned
boundary instead of an SWR subscription and module-wide callback registry.
`js-cache-storage` retains the repeated-read pattern with a bounded operation
example instead of a module-level storage or cookie cache. Local name is
`react-best-practices` (upstream frontmatter name is
`vercel-react-best-practices`).
Omits the compiled `AGENTS.md`, contributor README, metadata, rule template, and
section compiler files. Origin notes and license frontmatter are omitted from the
skill. Description is limited to React or Next performance work (waterfalls,
bundle size, server rendering, data fetching, re-renders) rather than upstream's
broader write/review/refactor trigger. When to Apply stays limited to
performance work. The entrypoint retains upstream category priorities as a
triage aid, treats actual impact as workload-dependent, requires before/after
measurement, and checks project versions and existing architecture. How to Use
sits above Quick Reference and selects matching prefixes from the bottleneck,
task, or diff when the skill is a review
reference, then opens only linked files whose ids and one-liners match. As a
review reference, it reports findings and leaves edits to the parent;
otherwise it applies only fitting rules. Quick Reference entries link to the
matching rule files. Two original index one-liners differ from upstream so
they name the file's actual API or fix:
`advanced-use-latest` (`useEffectEvent`) and `bundle-barrel-imports` (barrel-file
import cost). Additional one-liners reflect the adapted caching, SWR, and
hydration guidance. The cross-request LRU example caches only immutable,
versioned public data and requires access scope and invalidation for mutable
data. Function caching excludes auth state. SWR examples apply only when SWR is
already the project's data layer and scope
session-dependent keys to identity and authorization. The hydration guide
replaces a DOM-mutating inline script with server-consistent theme guidance.
The memoization rule follows React Compiler guidance without urging removal
of existing memoization. The lazy initializer
example uses pure state instead of browser storage or changing props. Trailing
whitespace is stripped from copied rule files. Automatic discovery stays
enabled.

## react-doctor

- [millionco/react-doctor / skills/react-doctor](https://github.com/millionco/react-doctor/tree/499a0208fca5c0422b713bdedf2b83fcc8e29d20/skills/react-doctor) — commit `499a0208fca5c0422b713bdedf2b83fcc8e29d20`.

Description covers diagnostics scans or fixes, static design checks, browser
performance traces, and rule config. It omits `/doctor`, finishing a feature,
fixing a bug, and committing React code. The changed-scope regression scan lives in
`review`, with affected diagnostics rechecked by `review-sweep` after fixes. The skill omits the upstream
"After making React code changes" commit gate and the `/doctor` remote playbook. The example command is
the full verbose scan. The flag table includes `--base` and
`--include-untracked` for partial scopes. Scan-only requests report findings
without edits, and static design diagnostics do not stand in for a rendered UI
audit. The unsupported upstream `version` frontmatter field is omitted.
Automatic discovery stays enabled.

## ui-design

- [s0xDk/refactoring-ui-skill](https://github.com/s0xDk/refactoring-ui-skill) — imported revision: unknown; its `SKILL.md`, reference write-ups, and CSS tokens are adapted into the local entrypoint, web references, and token asset.
- [anthropics/skills / skills/frontend-design](https://github.com/anthropics/skills/tree/34040c9c568585f6929bedeaad110ad08f079624/skills/frontend-design) — art-direction calibration and critique; commit `34040c9c568585f6929bedeaad110ad08f079624`.
- [emilkowalski/skills / skills/emil-design-eng](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/emil-design-eng) — web typography, component behavior, and access guidance; content verified against commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7` while the earlier local import baseline remains unknown.
- [emilkowalski/skills / skills/apple-design](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/apple-design) — typography, materials, press activation and cancellation, contrast, and reduced-transparency guidance; content verified against commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7`, while the earlier local import baseline remains unknown.
- [emilkowalski/skills / skills/mobile-native](https://github.com/emilkowalski/skills/tree/e8a175de22ae1e49370fc144c1f3bb9aeedf988d/skills/mobile-native) — mobile browser behavior and matching verification assertions; import baseline `e8a175de22ae1e49370fc144c1f3bb9aeedf988d`.
- [emilkowalski/skills / skills/break-ui](https://github.com/emilkowalski/skills/tree/e8a175de22ae1e49370fc144c1f3bb9aeedf988d/skills/break-ui) — realistic edge-data method, catalog, and content-constrained layout decisions; import baseline `e8a175de22ae1e49370fc144c1f3bb9aeedf988d`.

The automatically discoverable skill owns cross-platform visual hierarchy,
system decisions, and art direction plus browser component behavior and
accessibility. It routes web visual work to adapted Refactoring UI references
and an optional CSS token asset, browser interaction work to a focused behavior
reference, and SwiftUI or UIKit visual work to Apple-platform guidance grounded
in current Apple documentation. Native structure, behavior, and accessibility
remain with `swiftui` and `uikit`; motion remains with `animate`. Inherited
numeric recipes are contextual fallback heuristics rather than requirements.
The art-direction reference preserves Anthropic's subject-matter grounding,
generated-design tells, two-pass self-critique, restraint guidance, and Chanel
editing mnemonic while removing CSS implementation and general copywriting
material.

Mobile web guidance maps to `references/mobile-web.md`; edge-data layout choices
join `references/web-behavior-and-accessibility.md`. Uses current platform
capabilities and documentation rather than blanket CSS resets or device labels;
preserves zoom, selection, valid activation, and browser gesture ownership.
Greetings and attribution instructions are omitted.


## research

- [mattpocock/skills / skills/engineering/research](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/research) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## review

- Local: `skills/review` (SreeStack).

Reviewer references:

- [DietrichGebert/ponytail / skills/ponytail-audit](https://github.com/DietrichGebert/ponytail/tree/c982cd411abb53323c4baa1baa3c2f020b8d0b08/skills/ponytail-audit) — explicit whole-tree deletion-evidence guidance in `references/ponytail.md`; addition baseline `c982cd411abb53323c4baa1baa3c2f020b8d0b08`. The composite brief's other material retains the baseline below.

- `references/standards.md` and `references/spec.md`: [mattpocock/skills / skills/engineering/code-review](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/code-review) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.
- `references/thermo.md`: [cursor/plugins / cursor-team-kit/skills/thermo-nuclear-code-quality-review](https://github.com/cursor/plugins/tree/a29f5a8ca161b1de4ffc5484454958bebc04eaa5/cursor-team-kit/skills/thermo-nuclear-code-quality-review) — commit `a29f5a8ca161b1de4ffc5484454958bebc04eaa5`.
- `references/ponytail.md`: combines these sources from `DietrichGebert/ponytail`
  at commit `974d940a1c5344210874150b98ff0d2c861fab6a`:
  - [ponytail](https://github.com/DietrichGebert/ponytail/tree/974d940a1c5344210874150b98ff0d2c861fab6a/skills/ponytail) — core language, ladder, and safety limits.
  - [ponytail-review](https://github.com/DietrichGebert/ponytail/tree/974d940a1c5344210874150b98ff0d2c861fab6a/skills/ponytail-review) — tags, examples, and review boundaries.
  - [ponytail-audit](https://github.com/DietrichGebert/ponytail/tree/974d940a1c5344210874150b98ff0d2c861fab6a/skills/ponytail-audit) — bloat targets and cut ranking.
  - [ponytail-debt](https://github.com/DietrichGebert/ponytail/tree/974d940a1c5344210874150b98ff0d2c861fab6a/skills/ponytail-debt) — shortcut ceilings and upgrade triggers.
  - [ponytail-gain](https://github.com/DietrichGebert/ponytail/tree/974d940a1c5344210874150b98ff0d2c861fab6a/skills/ponytail-gain) — limits on savings claims.

Imported material remains in read-only assessment references. Review is
model-agnostic and returns findings and coverage for one supplied snapshot;
reviewer dispatch, tool execution, fixes, and repeats belong to callers.
Standards and Spec keep separate labeled reports, their upstream review bars,
and 400-word limits. Thermo and Ponytail apply within the supplied scope;
structural suggestions require evidence and a concrete benefit. Ponytail omits
persistent modes, installation, benchmark displays, and whole-repo debt ledgers.
Indirect-consumer checks use `change-safety`; React or Next assessments use
`react-best-practices` and current changed-scope React Doctor diagnostics.

## review-fix-loop

- Local: `skills/review-fix-loop` (SreeStack). Coordinates Review, native and
  external reviewers, and Review Sweep over a stable base. Gemini failures can
  fall back to OpenCode on GLM Flash 5.3 within permitted access. External gaps
  are disclosed; required native coverage remains a completion prerequisite.

## pr

- Local: `skills/pr` (SreeStack).
- [mattpocock/skills / skills/engineering/pr](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/pr) — PR-body structure, visual selection, evidence, and merge-risk guidance adapted into `references/pr-body.md`; import baseline `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`. Upstream credits [HumanLayer / show-me](https://github.com/humanlayer/skills/tree/ca7c8088db69e315a8b2deea43820270457f8f3c/plugins/show-me/skills/show-me) for visual guidance; the origin revision used by Matt is unrecorded. HumanLayer MIT notice checked at `ca7c8088db69e315a8b2deea43820270457f8f3c` in `licenses/humanlayer-skills.txt`.

The local name and UI are `pr`. Retains automatic discovery and the full local
readiness/publication/CI/feedback/merge handoff workflow, with a separate route
for title/body drafting and explicitly requested remote-description edits.
The body guide uses Summary/Evidence/Merge Danger by default, defers to project
PR templates, and preserves local why/effect/root-cause/stack facts. It expands
visual selection to algorithm, runtime, UI, file, interaction, diff, and complete
block views with locally written examples. Evidence is observed and revision-
appropriate, with unavailable before states disclosed. Reversibility, concrete
consumers, rollout, and restoration limits replace a forced one-word blast-radius
rating. Small PRs can use concise prose; publication refreshes the guide's facts
against the current scope/head. Cross-skill references use the current local name.


## review-sweep

- Local: `skills/review-sweep` (SreeStack).

## setup-sreestack

- [mattpocock/skills / skills/engineering/setup-matt-pocock-skills](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/setup-matt-pocock-skills) — prerelease-main import baseline `d81f3a183412e71a5b1e84ca21bc1a35eea03a60` (the skill folder matches v1.3.1).

Manual-only in both hosts. The local name and UI are SreeStack Setup. One setup
workflow owns project-specific conventions and pointers, with scoped update,
glossary migration, optional ticket/triage configuration, and explicitly
requested verification-map setup through `verify`. Project workflow guidance
uses current local review, PR, stack, merge, acceptance, and delegation owners;
host settings and installation remain separate. Existing commands and standards
are linked rather than duplicated. Active instruction files are selected by the
user/host or existing pointer ownership, with `AGENTS.md` for a new default.

Domain defaults use `GLOSSARY.md` / `GLOSSARY-MAP.md`; established legacy/custom
paths and one vocabulary source per context remain supported. Context boundaries,
not package count alone, determine layout. `domain.md` is adapted to actual
project paths. Glossary migration preserves vocabulary, local edits, custom
locations, and ADRs; updates consumers; handles collisions; and is a no-op on
rerun. General context documents remain outside that migration. The GitHub tracker
seed lists external PRs through the paginated REST endpoint and its
`author_association` field instead of an unsupported `gh pr list` JSON field,
fetching comments separately. Other tracker conventions retain their import
behavior; the triage mapping uses an author-neutral role
heading. Full setup writes only the configured/requested docs, preserves project
additions, and distinguishes documented commands from exercised readiness.

PR workflow references use the local `pr` entry point.


## showroom

- Local: `skills/showroom` (SreeStack).

## tdd

- [mattpocock/skills / skills/engineering/tdd](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/tdd) — v1.2.3, commit `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.

Automatic discovery includes feature and bug work, but not ordinary
integration-test additions by themselves. Seams established by the spec or
project conventions count as pre-agreed; user confirmation is reserved for
material unresolved choices.
The review stage uses `review-fix-loop`.

Glossary examples use the upstream `GLOSSARY.md` / `GLOSSARY-MAP.md` names;
resolution preserves configured or existing legacy paths, keeps one glossary per
context, and creates new files lazily. Cross-skill calls use host-neutral wording.


## to-spec

- [mattpocock/skills / skills/engineering/to-spec](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/to-spec) — v1.2.3, commit `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.

Uses supplied or project-configured tracker and label information; unresolved
required choices can be supplied directly or through the manual setup skill.

Setup references use the local `setup-sreestack` entry point.


## to-tickets

- [mattpocock/skills / skills/engineering/to-tickets](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/to-tickets) — v1.2.3, commit `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.

Uses supplied or project-configured tracker and label information; unresolved
required choices can be supplied directly or through the manual setup skill.

Setup references use the local `setup-sreestack` entry point.


## triage

- [mattpocock/skills / skills/engineering/triage](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/triage) — v1.2.3, commit `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.

Glossary examples use the upstream `GLOSSARY.md` / `GLOSSARY-MAP.md` names;
resolution preserves configured or existing legacy paths, keeps one glossary per
context, and creates new files lazily. Cross-skill calls use host-neutral wording.

Reads supplied or configured label mappings; a missing mapping blocks only the
mutation that requires it. Setup stays user-invoked. Workflow reproduction can
use `verify` when needed to resolve uncertainty; missing intended behavior requires clarification.

Setup references use the local `setup-sreestack` entry point.


## web-component-inspiration

- Local: `skills/web-component-inspiration` (SreeStack); explicit-only and
  web-scoped.

## wayfinder

- [mattpocock/skills / skills/engineering/wayfinder](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/wayfinder) — v1.2.3, commit `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.

Uses supplied or configured tracker information, with the existing local-file
fallback. Cross-skill calls are host-neutral and the prototype route remains
UI-only.


## writing-for-agents

- [mattpocock/skills / skills/productivity/writing-for-agents](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/productivity/writing-for-agents) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.
- Local adaptation: documents paired Claude Code and Codex invocation settings
  for shared skills and writes context pointers as request-shaped triggers.

## xcode-security-audit

- [superagents-lab/xcode27-skills / audit-xcode-security-settings](https://github.com/superagents-lab/xcode27-skills/tree/6f9ff8d5ad6000491cb0f483a776b7062e41cd97/audit-xcode-security-settings) — commit `6f9ff8d5ad6000491cb0f483a776b7062e41cd97`, used as coverage input.
- Local adaptation: a greenfield workflow grounded in current Apple
  documentation and effective Xcode settings. It chooses among native Xcode
  tools, command-line tools, structured project editing, and Xcode through
  computer use based on which is easiest and reliable. It does not require an
  Xcode-hosted agent, mutate during an audit, keep a fixed settings catalog, or
  fold C bounds-safety migration into general hardening.

## orchestration

- Local: `skills/orchestration` (SreeStack).
- [cursor/plugins / pstack/skills/swarm](https://github.com/cursor/plugins/tree/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack/skills/swarm) — commit `ecc249f1e306fc64ddf83c7bed16cacf7c2239db`. MIT notice in `licenses/lauren-tan-pstack.txt`.

- [mattpocock/skills / skills/engineering/implement-spec](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/implement-spec) — task-graph/frontier scheduling adapted into `references/task-graphs.md`; import baseline `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.

Locally written general delegation flow. Parallel coverage and competing
approaches are framed before dispatch; revision-bound verification and measured
results are checked during integration. Local agent routing permits only
`engineer`, `senior`, and `staff`, even when the host exposes other ranks.
It does not create goals or require pstack's cloud worker setup. `pr` owns review
when it will review the same integrated scope before publication.

The task-graph reference preserves existing integration, review, PR and cleanup
owners. Workspaces preserve unexpected edits; dependency outcomes require
integration and verification. Scheduling does not create a goal or assume a
worker's last merge guarantees a fast-forward.


## koubou

- [bitomule/Koubou / skills/koubou](https://github.com/bitomule/Koubou/tree/2d2e0034687c2a7d6f59c6186877aa3145143a7a/skills/koubou) — import baseline commit `2d2e0034687c2a7d6f59c6186877aa3145143a7a`. `SKILL.md` supplies the design workflow; the six supporting Markdown files map to `skills/koubou/references/` with their upstream names retained. MIT notice in `licenses/bitomule-koubou.txt`.

Automatically discoverable in both hosts. The entrypoint condenses repeated
setup, intake, design, and verification guidance into one workflow with
task-based reference links. Host-specific allowed-tool and invocation metadata
are omitted. Setup reuses project installations and favors isolated Python
environments when needed. Capture and preview use project run paths and host
tools. Step-by-step requests return one checked slide before expanding.
Style intake and interview use supplied direction without mandatory
reconfirmation. Campaign planning and QA are scoped to requested outputs,
including one-slide trials and targeted edits. The design guide reconciles
typographic contrast and text-length rules, makes background treatments
subordinate to supplied direction, and omits unsupported view-rate and
conversion claims. YAML guidance accounts for Koubou 0.20.0's generation logs
and incomplete localized JSON inventory, and explains mixed device/brand assets without
framing icons. Artifact license checks and release authorization remain
explicit. The feature-list example aligns with its HTML template, and technical
source links sit beside API guidance. Hero examples include their template's
background variables. Measured sidecar QA applies to HTML; content-mode output
uses visual and configured-geometry checks with the measurement gap disclosed.
Localized asset maps are documented for both HTML and content modes. Named
output canvases are listed separately from frame/hardware models. Other design,
configuration, and capabilities guidance is retained, with content-mode text
controls and linear-gradient angles corrected against the 0.20.0 implementation.
Text examples distinguish supported fill/stroke combinations; live guidance
accounts for external HTML assets absent from the watch set.
Checked exports use fresh output directories and generation-error checks to
avoid stale localized files after a masked per-language failure.
HTML framing guidance identifies the PNG/JPEG extension condition and the
passthrough behavior of other formats.

## retro

- [mattpocock/skills / skills/engineering/retro](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/retro) — `SKILL.md` and `agents/openai.yaml`; import baseline `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`. MIT notice in `licenses/mattpocock-skills.txt`.

Manual-only in both hosts, as upstream. Retains upstream categories, mechanical
check preference, reference structure, and examples. Cross-skill wording is
host-neutral; findings carry session evidence and remain recommendations until
implementation is requested. Review may inspect surrounding contracts, and
project standards inform both implementation and review.
