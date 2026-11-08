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

## seo

- Local: `skills/seo` (SreeStack), automatically discoverable website SEO diagnosis,
  implementation, and deployed verification. Conceptual input from [Suraj Sharma](https://x.com/suraj_sharma14/status/2116062550416871512)
  and [Rakesh Patel](https://x.com/rakeshpatelco/status/2116065801279291422), checked
  2026-10-30; independently written with technical citations to official documentation.

## create-image

- Local: `skills/create-image` (SreeStack), automatically discoverable image
  generation and editing through a standard-library CLI for the OpenAI Images API,
  with automatic fallback to a host subscription image tool. Written from official
  OpenAI documentation.

## agent-login

- Local: `skills/agent-login` (SreeStack) task routes for machine setup, credential use and item management, and application login, plus a private alias-based CLI.
- [openclaw/openclaw / skills/1password](https://github.com/openclaw/openclaw/tree/a229456f487f713315fc799767a97990f407bea6/skills/1password) — `SKILL.md`, `references/get-started.md`, and `references/cli-examples.md`; adaptation baseline commit `a229456f487f713315fc799767a97990f407bea6`. MIT notice in `licenses/openclaw.txt`.

One automatically discoverable skill owns application sign-in and approved
credential use. `SKILL.md` is the only router: it holds the three task routes,
their finish lines, and the rules every route shares. Each route reads
`references/access.md` (authorization, 1Password authentication, and the access
boundary) and one task reference: `machine-setup.md`, `secrets-for-programs.md`,
or `browser-login.md`. Upstream's auth-mode detection, `op whoami` check, and
desktop-integration guidance live in `access.md`; its `op read`/`op run`
examples became process-local delivery in `secrets-for-programs.md`. Current CLI
support is 1Password and existing local Chromium CDP tabs. Adds user-designated
vault-scoped service-account access, optional automatic item management, and
task-specific personal approval, distinguishing behavioral scope from 1Password
enforcement. Machine administration is separate from consumer tasks. Replaces
upstream secret-printing examples with process-local reads and stdin writes.
Adds shared private environment-file provisioning for local Codex runtimes and,
through a bundled loader and SessionStart hook, Claude Code, preserving
unrelated agent variables, host-specific Touch ID diagnosis, and
provisioning-source-specific runtime checks. Omits OpenClaw install metadata,
gateway-specific IPC assumptions, tmux/session-export workflows, `op inject`
examples, and the Claude in Chrome credential-tool section. API claims link to
official documentation. README.md provides discovery links.

## snip-snap

- [sreejithraman/snip-snap / .agents/skills/snip-snap](https://github.com/sreejithraman/snip-snap/tree/ae14ef0b89ed2806afef7332caf249ecc9ee1cc5/.agents/skills/snip-snap) — `SKILL.md` and `references/writes.md`; import baseline commit `ae14ef0b89ed2806afef7332caf249ecc9ee1cc5`. MIT notice in `licenses/sreejithraman-snip-snap.txt`.

Both files match upstream. Automatically discoverable in both hosts. Chore
selection and execution live in `snipsnap-do-chores`, which uses this skill's
saved-work lifecycle.

## snipsnap-do-chores

- Local: `skills/snipsnap-do-chores` (SreeStack). Selects saved mechanical work
  through Snip Snap; Implement owns one outcome, Chief of Staff
  coordinates several outcomes, and Swarm supplies bounded parallel work.

## animate

- [emilkowalski/skills](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/animate) — `skills/animate/SKILL.md` and `RECIPES.md`; reference import commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7`. The original parent-skill import baseline remains unknown. MIT notice in `licenses/emilkowalski-animate.txt`.
- [emilkowalski/skills / skills/emil-design-eng](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/emil-design-eng) — press feedback and measured rendering guidance; content verified against commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7`, while the earlier local import baseline remains unknown.
- [emilkowalski/skills / skills/apple-design](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/apple-design) — gesture-intent guidance; content verified against commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7`, while the earlier local import baseline remains unknown.
- [vojtaholik/good-css / skills/good-css](https://github.com/vojtaholik/good-css/tree/e074e76a011dbadc4f0a7fbd6c661ed79deb6371/skills/good-css) — CSS motion reference adaptation baseline `e074e76a011dbadc4f0a7fbd6c661ed79deb6371`; explanations and technical citations checked in upstream `PRACTICES.md`. MIT notice in `licenses/vojtaholik-good-css.txt`.
- [Jakubantalik/transitions.dev](https://github.com/Jakubantalik/transitions.dev/tree/598d3d6ad89dabb4bdf742fd2e887ca53914a888/skills) — `skills/transitions-dev/` and `skills/transitions-polish/`; commit `598d3d6ad89dabb4bdf742fd2e887ca53914a888`. No license file found in this revision; see `THIRD_PARTY_NOTICES.md`. Newer [skill terms](https://github.com/Jakubantalik/transitions.dev/blob/3bc58021c69725d8bf42108632ac6cf14f2b1d3c/skills/transitions-dev/LICENSE.txt) restrict republishing the collection as a competing library, template pack, or component kit. Further imports are held pending redistribution clarification; the import baseline remains unchanged.

- One automatically discoverable cross-platform skill owns motion decisions,
  implementation, tuning, and checks. Its short decision guide prefers system
  component behavior, then built-in effects or presets, then custom motion for
  an unmet requirement. Native Liquid Glass interaction and morphing follow the
  same preference. Added motion must serve the interaction; frequency
  classifications and structured purpose/handoff reports are omitted. Apple
  pitfalls, web implementation/recipes, and web tuning are conditional reads.
  Apple guidance keeps state, lifecycle, gestures, accessibility, and verification
  constraints; routine API catalogs are omitted. Component and material setup,
  including glass availability and fallbacks, stays with the framework skills.
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
- `good-css/references/motion.md` opt-in movement and timing join `references/web.md`;
  typed values, shadow crossfades, and document transitions map to
  `patterns/registered-properties.md`, `card-elevation.md`, and
  `document-navigation.md`; the active indicator joins `tabs-sliding.md`.
  `show-and-hide.md` discrete dialog/popover transitions, native details, and
  clip reveals join `modal.md`, `menu-dropdown.md`, `accordion.md`, and
  `panel-reveal.md`. `scroll-and-viewport.md` edge decoration maps to
  `scroll-overflow-feedback.md`. All pattern paths are under `references/`.
  Preserves purposeful added motion, timing tokens, lifecycle, interruption, and
  reduced-motion paths. Scope inherited opt-ins to components; retain usable
  static states and native event ownership. Browser versions and upstream
  measurements are omitted; target support and rendering require checks.
  Performance guarantees, fade exemptions, and unconditional no-fallback rules
  are replaced with contextual decisions. Existing invocation stays automatic.

## app-intents

- Local: `skills/app-intents` (SreeStack); shares design and retry principles.

## app-store-connect

- [rorkai/app-store-connect-cli-skills](https://github.com/rorkai/app-store-connect-cli-skills/tree/7de1ef7cc831f62d205dfa589063f3831f66391b) — `skills/`; commit `7de1ef7cc831f62d205dfa589063f3831f66391b`, imported 2026-11-01. Author: Rudrank Riyam; MIT notice in `licenses/rudrankriyam-app-store-connect-cli-skills.txt`.

- One discoverable skill: upstream `skills/asc-cli-usage/SKILL.md` supplies the
  entrypoint; the other `skills/<name>/SKILL.md` files map to local
  `references/<name>/guide.md`. Guides retain supporting paths and local links
  and omit skill frontmatter. The skill omits upstream scripts and app settings.
- Guide selection by task, checks against the installed CLI, and IDs and release
  rules from the project. API key creation requires a setup request. Apple Ads
  detail lives in its guide only. In-app events and Asset Library media are
  discoverable through this entrypoint; cross-guide handoffs use local links.
- First-version and multi-item event recovery use release assembly. Review
  monitoring preserves exact target IDs and re-reads them after latest-version
  waits. Task routing covers read-only pricing and schedule inspection.
- IAP lookups reflect CLI 6.3.0 multi-territory filters, automatic price-filter
  pagination, and territory includes for candidate and equalized price points.
- Screenshot cleanup uses working copies; associative-array examples require
  Bash 4. The guides qualify unsupported ranking claims and distinguish App Store
  description, promotional text, and release-note guidance. Build-ID guidance
  uses the `--build-id` flag required by the installed CLI.
- Screenshot device operations route through `simulator-lifecycle` and the host
  driver contract. Raw examples are limited to authorized unmanaged targets;
  disposable multi-locale work uses manager leases rather than hand-created devices.

Authentication reuses cached profiles and web sessions, verifies providers, and
serializes interactive challenges. Developer Portal cache recovery follows
status/provider/error diagnosis. macOS package export checks `--pkg-path`
support and retains raw Xcode export when unavailable.


## blast-radius

- [cursor/plugins / pstack/skills/blast-radius](https://github.com/cursor/plugins/tree/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack/skills/blast-radius) — commit `ecc249f1e306fc64ddf83c7bed16cacf7c2239db`. MIT notice in `licenses/lauren-tan-pstack.txt`.

Automatically discoverable in both hosts. Locally written, scoped to blast-radius
questions and subtle diffs. Preserves
the safety-assumption and executable-proof method without pstack's mandatory
arena, prose-cleanup, or Cursor-specific routing.

## why

- [cursor/plugins / pstack/skills/why](https://github.com/cursor/plugins/tree/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack/skills/why) — `SKILL.md` and `references/epistemics.md`; commit `ecc249f1e306fc64ddf83c7bed16cacf7c2239db`. MIT notice in `licenses/lauren-tan-pstack.txt`.

Automatically discoverable in both hosts. Locally written around code-anchored
historical evidence and calibrated claims. Current execution routes to `how`.
Searches sources proportionally without mandatory parallel investigators,
model settings, or Cursor MCP discovery.

## codebase-design

- [mattpocock/skills / skills/engineering/codebase-design](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/codebase-design) — v1.2.3, commit `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.
- [cursor/plugins / pstack architecture and correction guidance](https://github.com/cursor/plugins/tree/dbf49813a39c1a5389c5e28cb8e4c1c2379e2454/pstack/skills) — `architect/references/design-red-flags.md` and `correct/SKILL.md`; addition baseline `dbf49813a39c1a5389c5e28cb8e4c1c2379e2454`. MIT notice in `licenses/lauren-tan-pstack.txt`.
- [Maze / codebase indicators post](https://x.com/mazeincoding/status/2115575731585507796) — conceptual input for `references/architecture-signals.md`; checked 2026-10-29. Independently written diagnostic prompts require caller, state, or maintenance evidence and distinguish architecture exploration from review of a supplied change.

Glossary examples use the upstream `GLOSSARY.md` / `GLOSSARY-MAP.md` names;
resolution preserves configured or existing legacy paths, keeps one glossary per
context, and creates new files lazily. Cross-skill calls use host-neutral wording.

Alternative-interface proposals use arena's shared brief, rubric, independent
candidates, and cross-judge, with orchestration's model table and bounded
ownership. The user-requested comparison remains conditional and defaults to
recommendations; synthesis is requested separately. Candidate counts follow the
decision rather than a fixed panel of three, and architect can carry a selected
design through authorized implementation.

Deep-module vocabulary, deletion tests, seam techniques, and alternative-interface
design stay local. Generic design, testability, and enforcement guidance use
`engineering-principles`. `references/preventing-mistakes.md` owns contributor-path
assessment and historical guard proof; `correct` owns recurring-mistake investigation
and repair. Design and review return recommendations. Legitimate adapters and
compatibility paths remain supported.

`references/architecture-signals.md` supplies shared discovery prompts for
structural friction, including hidden caller obligations, invalid states,
implicit state machines, scattered ownership, and validation. Architecture
exploration and Thermo use the same reference. Signals need evidence;
size, layout, duplication, or wrapper counts alone do not justify a refactor.
The diagnostic table stands on its own. Deeper reading requires a concrete
candidate needing further validation; agents reuse relevant guidance already read.
Lifecycle ownership is a deep-module principle, with state-machine mechanics
kept in the shared domain principle.

## correct

- [cursor/plugins / pstack/skills/correct](https://github.com/cursor/plugins/tree/dbf49813a39c1a5389c5e28cb8e4c1c2379e2454/pstack/skills/correct) — `SKILL.md`; adaptation baseline `dbf49813a39c1a5389c5e28cb8e4c1c2379e2454`. MIT notice in `licenses/lauren-tan-pstack.txt`.

Automatically discoverable in both hosts so related skills can reach it for
requested failure prevention. Uses bounded history and available session records,
counts independent occurrences, checks current exposure, and ranks live classes.
Shared design and enforcement selection use `engineering-principles`; guard proof
remains in `codebase-design`. Technical experiments use the architecture reference.
Planning and implementation honor
the requested finish line and reuse existing delivery workflows. Program execution routes through `chief-of-staff`; bounded parallel work
uses `swarm`.
Automatic correction triggers, mandatory rule tables, per-class commit requirements, and
blanket exception policies are omitted.

## diagnosing-bugs

- [mattpocock/skills / skills/engineering/diagnosing-bugs](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/diagnosing-bugs) — v1.2.3, commit `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.
- [cursor/plugins / pstack measurement and diagnostic guidance](https://github.com/cursor/plugins/tree/dbf49813a39c1a5389c5e28cb8e4c1c2379e2454/pstack/skills) — `benchmark-checklist/SKILL.md`, `principle-explain-the-number/SKILL.md`, and the diagnostic-signal addition in `principle-fix-root-causes/SKILL.md`; addition baseline `dbf49813a39c1a5389c5e28cb8e4c1c2379e2454`. MIT notice in `licenses/lauren-tan-pstack.txt`.
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

Browser reproductions follow host routing before standalone drivers. Apple
Simulator launch and control follow `simulator-lifecycle` and the host's device
rules; physical devices use `verify`'s iOS device route. Build identity and
capture choices stay local.

Repairs run through `tdd`'s red → green cycle at a seam that reaches the actual
failure and its caller chain. Diagnosis keeps the original-scenario rerun and
causal evidence. A repair that affects a user workflow finishes only with a
passing `verify` verdict.

Performance claims use `references/measurement-validity.md` for completed work,
correctness, settings, bottlenecks, plausibility, repeatability, and user relevance.
Apple guidance shares that procedure. Run counts fit cost and noise rather than
a fixed minimum; ballparks remain labeled estimates. Diagnostic cleanup proposes
a cheap persistent signal with runtime/privacy costs after a deep investigation;
implementation stays within the authorized fix and temporary probes still leave.
Recurring-class evidence passes to `correct` when the user's scope includes
broader prevention; active diagnosis keeps its reproduction and repair loop.
Shared evidence guidance covers root-cause decisions and revisiting a failed
premise; the runnable diagnosis phases and measurement procedure remain local.
Timing and lifecycle reproductions capture starting state, event order, and
operation identity; invalid-transition repairs use the shared domain principle.

The entrypoint consolidates repeated feedback-loop and cleanup guidance while
retaining all six diagnosis phases. Minimising, comparing hypotheses, and
bisecting apply when the causal uncertainty calls for them, and the loop's
time bar is the shortest faithful bounded run rather than seconds. Sensitive
artifacts pass through redaction before inspection output enters the conversation, including
initial reads. Conditional references follow the same conditional gates; the
HITL script and invocation remain unchanged.

## engineering-principles

- [cursor/plugins / pstack principle skills](https://github.com/cursor/plugins/tree/850d7f2e9f5e55dff7eb00a0a479337fe79eb22f/pstack/skills) — all 24 `principle-*/SKILL.md` files; adaptation baseline `850d7f2e9f5e55dff7eb00a0a479337fe79eb22f`. MIT notice in `licenses/lauren-tan-pstack.txt`.
- [cursor/plugins / pstack behavior-test and idempotency refinements](https://github.com/cursor/plugins/commit/e5136d82418d2db3165ea1050d17577cd618cc05) — `pstack/skills/principle-test-behavior-not-implementation/SKILL.md` and `pstack/skills/principle-make-operations-idempotent/SKILL.md`; addition baseline `e5136d82418d2db3165ea1050d17577cd618cc05`. MIT notice in `licenses/lauren-tan-pstack.txt`.
- [DietrichGebert/ponytail / skills/ponytail](https://github.com/DietrichGebert/ponytail/tree/974d940a1c5344210874150b98ff0d2c861fab6a/skills/ponytail) — simplicity ladder shared with the local review reference; baseline `974d940a1c5344210874150b98ff0d2c861fab6a`. MIT notice in `licenses/DietrichGebert-ponytail.txt`.
- [David Khourshid's state-machine guidance](https://stately.ai/blog/2021-01-20-you-dont-need-a-library-for-state-machines) and [UI-independent logic](https://stately.ai/blog/2019-11-13-no-disabling-a-button-is-not-app-logic) — conceptual input checked 2026-10-15; state-modeling guidance is independently written, with no upstream prose or code copied.
- [Redux: Treat Reducers as State Machines](https://redux.js.org/style-guide/#treat-reducers-as-state-machines) — supporting guidance for current-state/event decisions and typed state variants, checked 2026-10-15.

Each reference is one principle. Upstream paths use
`pstack/skills/principle-<source-name>/SKILL.md`:

| Local reference | Upstream source name |
| --- | --- |
| `references/attack-the-premise.md` | `attack-the-premise` |
| `references/exhaust-the-design-space.md` | `exhaust-the-design-space` |
| `references/prove-it-works.md` | `prove-it-works` |
| `references/fix-root-causes.md` | `fix-root-causes` |
| `references/test-behavior-not-implementation.md` | `test-behavior-not-implementation` |
| `references/explain-the-number.md` | `explain-the-number` |
| `references/laziness-protocol.md` | `laziness-protocol` |
| `references/subtract-before-you-add.md` | `subtract-before-you-add` |
| `references/minimize-reader-load.md` | `minimize-reader-load` |
| `references/build-the-lever.md` | `build-the-lever` |
| `references/sequence-work-into-verifiable-units.md` | `sequence-verifiable-units` |
| `references/guard-the-context-window.md` | `guard-the-context-window` |
| `references/never-block-on-the-human.md` | `never-block-on-the-human` |
| `references/encode-lessons-in-structure.md` | `encode-lessons-in-structure` |
| `references/foundational-thinking.md` | `foundational-thinking` |
| `references/redesign-from-first-principles.md` | `redesign-from-first-principles` |
| `references/model-the-domain.md` | `model-the-domain` |
| `references/boundary-discipline.md` | `boundary-discipline` |
| `references/type-system-discipline.md` | `type-system-discipline` |
| `references/experience-first.md` | `experience-first` |
| `references/outcome-oriented-execution.md` | `outcome-oriented-execution` |
| `references/make-operations-idempotent.md` | `make-operations-idempotent` |
| `references/migrate-callers-then-delete-legacy-apis.md` | `migrate-callers-then-delete-legacy-apis` |
| `references/separate-before-serializing-shared-state.md` | `separate-before-serializing-shared-state` |

One automatically discoverable index groups direct links by task and gives each
principle a short applicability hint adapted to its local guidance. Each reference
filename follows its full principle title, and all 24 titles match their source
headings verbatim. Workflows retain procedures and completion criteria; generic
decisions have one shared home. Existing invocation choices stay intact.
Exhaust the Design Space routes independent synthesis through arena and
consequential design-through-implementation work through architect. Tools and prototype counts fit the decision's cost and uncertainty;
actor censuses apply to actor-distribution questions. Permissions and product
choices remain with the host/user, required compatibility stays supported, and
temporary development breakage stays behind coherent delivery checkpoints.
Internal trust does not remove runtime authorization or changing-state checks;
unsafe type operations require an auditable interface. Behavior-test quality is
judged by detected failures rather than assertion syntax. Language/platform API
manuals, mandatory per-task principle reports, and upstream mode wrappers are omitted.
Behavior tests must also survive internal refactors that preserve their contract;
external payloads remain observable behavior. Crash leftovers require reliable
ownership and recovery evidence, preserving live work while reclaiming stale work.
The domain principle covers explicit lifecycle states, accepted events, derived
flags, effect ownership, stale completions, and conditional statechart adoption.
Product requirements remain the independent source for behavior checks.
The stateful-behavior practice is self-contained, with guards and a submission
example; external source URLs stay in this provenance record.
Event-order-dependent correctness calls for an explicit lifecycle model before
handler design; valid state shapes and allowed transitions are distinct concerns.

## domain-modeling

- [mattpocock/skills / skills/engineering/domain-modeling](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/domain-modeling) — v1.2.3, commit `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.

Glossary examples use the upstream `GLOSSARY.md` / `GLOSSARY-MAP.md` names;
resolution preserves configured or existing legacy paths, keeps one glossary per
context, and creates new files lazily. Cross-skill calls use host-neutral wording.

`CONTEXT-FORMAT.md` maps to `GLOSSARY-FORMAT.md`. The local
`references/glossary-paths.md` is the shared compatibility rule for writers and
readers; glossary reading alone does not invoke domain modeling.

The entrypoint keeps term resolution and immediate recording together; layout
examples live in the glossary format. Path precedence lives only in the shared
path reference, and the three ADR criteria live in the entrypoint at the stable
`offer-adrs-sparingly` anchor. ADR formatting preserves system/context placement
and sequential numbering. Discovery and invocation settings remain unchanged.


## explain

- Local: `skills/explain` (SreeStack). Conceptual input from Cursor pstack's
  [bro](https://github.com/cursor/plugins/blob/main/pstack/skills/bro/SKILL.md),
  [teach](https://github.com/cursor/plugins/blob/main/pstack/skills/teach/SKILL.md),
  and [in-your-own-words](https://github.com/cursor/plugins/blob/main/pstack/skills/in-your-own-words/SKILL.md),
  checked 2026-11-01. Independently written, user-invoked only in both hosts. Technical
  explanations using "explain it to a PM or junior engineer" as the instruction.
  Adds brief teaching guidance. No upstream prose copied.

## eli5

- [anthropics/claude-plugins-community / eli5/skills/eli5](https://github.com/anthropics/claude-plugins-community/tree/f4c9452f5ca091f1be7064d9faab1b001ea21645/eli5/skills/eli5) — commit `f4c9452f5ca091f1be7064d9faab1b001ea21645`.

Aims at a smart adult new to the topic and keeps the logic while simplifying the
vocabulary. The description lists triggers only.

## gauntlet-loop

- [robonuggets/gauntlet-loop / .claude/skills/gauntlet-loop](https://github.com/robonuggets/gauntlet-loop/tree/9b1975a1b8f01981f3f1e6b667ad3aaf907178ea/.claude/skills/gauntlet-loop) — `SKILL.md`; import baseline commit `9b1975a1b8f01981f3f1e6b667ad3aaf907178ea`. CC BY 4.0 notice in `licenses/robonuggets-gauntlet-loop.txt`.

User-invoked only in Claude Code and Codex. Preserves prompt generation,
user selection of a named/fetchable/comparable bar, separate builder and harsh
critic, blind comparison, iteration until a win, and the offer to run the prompt.
Consolidates repeated examples and failure guidance into one workflow. Uses
portable iteration and subagent instructions instead of assuming `/loop` or
`ultracode` support. Adds equivalent comparison conditions, disclosure of blind
comparison limits, measurable acceptance and integrated-result checks, blocked
comparison reporting, and workspace-scoped progress. Execution follows an
explicit run request and available host capabilities; no default budget or
round cap is added.

## chief-of-staff

- Local: `skills/chief-of-staff` (SreeStack). Original program workflow and
  dashboard implementation, informed by the user-supplied `chief-of-staff.zip`
  (attachment `0b05f3ba-72ce-4fe1-b35e-e1f0a28adff3`, reviewed 2026-11-02).
- [mattpocock/skills / skills/in-progress/chief-of-staff](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/in-progress/chief-of-staff) and [skills/engineering/implement-spec](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/implement-spec) — adaptation baseline `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`. MIT notice in `licenses/mattpocock-skills.txt`.
- [cursor/plugins / pstack/skills/poteto-mode](https://github.com/cursor/plugins/tree/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/poteto-mode) — `SKILL.md` and `playbooks/orchestrate.md`, `playbooks/autonomous-run.md`, and `playbooks/multi-phase-plan.md`; adaptation baseline `ae5650febf4320793844c12c4adaa937f417f8da`. MIT notice in `licenses/lauren-tan-pstack.txt`.
- [lauren / empirical review post](https://x.com/poteto/status/2117437607940681849) and [clarification](https://x.com/poteto/status/2117440753551204735) — conceptual input, read with the user's supplied history assessment on 2026-11-03. No post text copied.
- [Alex Hillman / between-turn judge post](https://x.com/alexhillman/status/2111972827452612679) — conceptual input for decision triage, read 2026-11-04. No post text copied.
- [DeepSeek / dsh-superagent-prototype](https://github.com/deepseek-ai/dsh-superagent-prototype/tree/8c32a9dc5d72c033816c6a8110b37f40cf94fba4) — conceptual input reviewed at `8c32a9dc5d72c033816c6a8110b37f40cf94fba4`: `docs/000-philosophy.md`, `docs/001-domain.md`, `docs/003-execution.md`, `docs/004-prompts.md`, and the `prompts/` role, dispatch, work, reply, handoff, scope, communication, and delivery instructions. Informs Chief of Staff, Implement, Orchestration, and Show Me; no code or prose copied.
- [Lucide Icons](https://lucide.dev/guide/lucide/getting-started) — external browser dependency, version `1.67.0`, loaded asynchronously from `https://cdn.jsdelivr.net/npm/lucide@1.67.0/dist/umd/lucide.min.js` with SHA-384 integrity and no referrer. No Lucide source assets or license text are vendored. [Upstream package license](https://cdn.jsdelivr.net/npm/lucide@1.67.0/LICENSE) covers ISC and applicable Feather MIT notices.

Automatically discoverable program owner. It carries several outcomes, each
through one Implement owner that delivers one PR or its own planned stack. Input
is any set of work, and a spec is optional. To Tasks splits a body of work and
owns readiness, including its provisional start for a decision with a reversible
recommended option. Owners start from `assets/owner-kickoff.md` with an explicit
return route and report file; a running Implement session is adopted, never
duplicated. The chief reads Implement's owner report fields, accepts outcomes
under Orchestration, watches delegated owners' pending PRs, and routes
discoveries through an explicit disposition table.

Each outcome takes Implement's Land, Try, or PR finish line. Land picked under
that policy authorizes merging within the agreed program scope, with Merge's
requirements as the gate; the chief's landing release decides when. Owners land
their own outcome on release, and the chief lands only sets that span owners,
with one recorded lander, one pending landing per target branch including queued
merges, and withdrawal recorded before notifying. Provisional work, on another
owner's unmerged layer or an open decision's recommended option, builds and is
shown but never lands. A shown Try waits for the user's merge, changes, or scrap
choice, one outcome at a time unless the user names a set, after seeing the
effect on dependents. The chief triages decision requests: it resolves
reversible, unreserved ones that a recorded source or the user's standing
approval settles, and the user can reopen any of them. Holds, project rules, and
a calling workflow's finish line narrow the default. `references/dependencies.md`
keeps the upstream frontier scheduling, adds verification at the dependent's
base and provisional bases, and linearizes fork-and-join inputs into reviewable
stacks. Existing trackers stay authoritative; there is no mandatory wiki,
Linear, Slack, cloud runtime, or recurring schedule.

The original command center renders a checked JSON snapshot of the program
record (`scripts/render_dashboard.py`, `assets/command-center.html`) with
Needs you before Work, collapsible sections, per-row observation times, copyable
decision prompts that name one recorded option, judgment calls ahead of quick
picks with a batch prompt, reopenable chief-resolved decisions, and accepted
tradeoffs. Each work row is one outcome, follow-up, or support task, counted once,
with its finish line, results to open, provisional condition, owner, and PR
layers; each decision names the outcomes it blocks and the phase each waits at.
Below 900px it stays one column; wider, Needs you is a dual-pane inbox and Work a
board of stage lanes. It replaces the supplied archive's Claude artifact database
and integrations; no archive code or prose is copied. Validation rejects
provisional landings, PRs on a Try, stacks on another owner's unmerged layer
without a provisional mark, and terminal rows with active blockers. Delivery is
hosted only; `references/hosting.md` serves the page through Show Me's web
sharing, including Tailscale Serve. A hosted page polls its own URL and swaps in
a newer published digest without a server push, keeping the viewer's place per
URL in session storage; the chief stays the only publisher.

## implement

- [mattpocock/skills / skills/engineering/implement](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/implement) — adaptation baseline `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`. MIT notice in `licenses/mattpocock-skills.txt`.
- [cursor/plugins / pstack/skills/figure-it-out](https://github.com/cursor/plugins/tree/88d47514b82e7c44f00f2b2a72ff6dd12158038c/pstack/skills/figure-it-out) and [poteto-mode/playbooks/autonomous-run.md](https://github.com/cursor/plugins/blob/88d47514b82e7c44f00f2b2a72ff6dd12158038c/pstack/skills/poteto-mode/playbooks/autonomous-run.md) — measurable-target pursuit, baseline `88d47514b82e7c44f00f2b2a72ff6dd12158038c`. MIT notice in `licenses/lauren-tan-pstack.txt`.
- Conceptual input: DeepSeek source and revision recorded under [chief-of-staff](#chief-of-staff); no code or prose copied.

Automatically discoverable workflow that carries one outcome, as one PR or a
planned stack from the same owner, to its finish line, written against a generic
caller. Keeps upstream spec/ticket resolution, asking on an ambiguous ticket,
TDD at meaningful seams, and verification; no tracker is required for a supplied
spec. Upstream's unconditional review-then-commit ending is replaced by finish
lines: it picks **Land** for settled, reversible work and **Try** otherwise,
states the pick so the user can override it, and keeps an explicitly requested
PR state. Land selected under that policy is the merge request Merge needs;
outline approval grants no landing; holds, caller finish lines, and destructive
or outward-facing actions stop it. Try stops before review and the PR. Under a
chief, the owner lands its own PR or stack on the chief's release.
Adds preflight through Agent Login, Show Me baselines and showing at each stop,
provisional work that stops at Try, the upstream pstack measurable-target
pursuit that keeps hard targets and rejects regressions (its host-specific wake
loop and broad side-fix authority are omitted), invariant escalation through
Attack the Premise, follow-up routing with separate finish lines, promotion to
Chief of Staff for several outcomes, adoption without a second writer, and an
outcome-based owner report with early partial reports. In a top-level thread, a
subagent writes the change under Orchestration, and a child writes it itself.
Native goal tracking stays optional and explicitly requested.

## swarm

- [cursor/plugins / pstack/skills/swarm](https://github.com/cursor/plugins/tree/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/swarm) — adaptation baseline `ae5650febf4320793844c12c4adaa937f417f8da`. MIT notice in `licenses/lauren-tan-pstack.txt`.

Automatically discoverable bounded parallel tool that returns to its caller.
Keeps upstream coverage, races, mixed assignments, declared selection rules,
disjoint outputs, and the single rerun for a result missing its named revision
and method. A lost required slice stays required instead of upstream's "proceed
with N-1". Owns the decision to run work in parallel, with its own independence
test that keeps cohesive work with one owner. Orchestration supplies delegation
rights, self-contained briefs, model selection, writer separation, the child
limit, recovery, and acceptance; Arena keeps candidate synthesis. Cloud placement,
upstream model defaults, mandatory fan-out, and program or native-goal ownership
are omitted.

## gh-stack

- [github/gh-stack / skills/gh-stack](https://github.com/github/gh-stack/tree/d4ab7ab47e5b3e3708a27c8c42abcdf4bc321419/skills/gh-stack) — commit `d4ab7ab47e5b3e3708a27c8c42abcdf4bc321419`.

Invocation remains unchanged. Checks installed-extension capabilities before
newer worktree behavior. Conflict staging follows the diagnostic owner, and
sync rollback guidance preserves partial-restoration recovery state instead of
promising unconditional rollback.
History-changing operations use the shared PR preservation reference to back up
retained local files affected by tracking deletions and verify restoration.

Scoped PR layers follow `pr`’s publish step, which links every layer in T3; CLI
publication does not substitute for that link. Layers get `pr`’s review step before
`submit`, or `link` when it creates PRs or marks them ready, and `gh stack merge` runs only from `merge`’s land step.

Ordinary publication uses `submit --auto --open` or `link --open`, with drafts only
on request, to match `pr`. Branch deletion after a merge goes through `repo-cleanup`
rather than `sync --prune`, which doesn't check merge-time heads. Layers split only
for dependency order and reviewability, and can emerge as the work takes shape;
tests and docs stay with the behavior they prove, and independent outcomes get
separate stacks or PRs even inside one feature.

The entrypoint keeps common calls and first-action guards inline; installation,
state fields, and exit-code details live with command behavior. Existing recovery
references retain specialized semantics. Direct reference reads
also gate newer worktree/catalog behavior against installed capabilities;
missing path-mode support uses manual owner discovery rather than invented
flags or automatic upgrades. The description lists triggers only and limits
discovery to stacked branches and dependent PRs.
Numeric merge targets are checked for stack-number precedence before selecting
the requested PR set.

## grill-with-docs

- [mattpocock/skills / skills/engineering/grill-with-docs](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/grill-with-docs) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## grilling

- [mattpocock/skills / skills/productivity/grilling](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/productivity/grilling) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

Asks only frontier decisions that would change the outcome and that the agent
can't predict, highest stakes first, and lists the rest in one Assuming block.
Always asks decisions that risk data loss, private data, security, or can't be
undone. Opens on settling the decisions that change the result rather than an
exhaustive interview. Keeps safe, local discovery going while answers are
pending. An answer that picks a direction settles it without a request to
justify it, and a recommendable detail that is easy to change later goes under
Assuming. The user's substantive answers are the confirmation, with no separate
approval round; it returns the decisions and one Assuming block to its caller,
and decisions it had to ask stay open until answered. The description lists
triggers only.

## handoff

- [mattpocock/skills / skills/productivity/handoff](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/productivity/handoff) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.
- [cursor/plugins / pstack session-pickup and pause-safely playbooks](https://github.com/cursor/plugins/tree/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack/skills/poteto-mode/playbooks) — `session-pickup.md` and `pause-safely.md`; commit `ecc249f1e306fc64ddf83c7bed16cacf7c2239db`. MIT notice in `licenses/lauren-tan-pstack.txt`.

The manual-only invocation remains in both hosts. The local skill writes an
off-repo resume note with operational state and supports checking that note on
pickup. It omits pstack's automatic WIP commit and transcript-specific paths.

T3 history supplies scoped evidence and task receipts; the portable note retains
thread/task identity, ownership, and live-work state. Invocation stays manual-only.

## how

- [cursor/plugins / pstack/skills/how](https://github.com/cursor/plugins/tree/99b609a72323b70204eab407c622f436e858e112/pstack/skills/how) — `SKILL.md`, `references/explorer-prompt.md`, and `references/explainer-prompt.md`; adaptation baseline `99b609a72323b70204eab407c622f436e858e112` (pstack 0.15.32). MIT notice in `licenses/lauren-tan-pstack.txt`.

Automatically discoverable in both hosts. Retains the upstream explanation goal,
simple/complex split, exploration fields, synthesis method, output structure, and
most supporting-prompt wording. Local orchestration owns model selection,
delegation, and acceptance. Narrow questions use one reader; independent complex
slices can be delegated when useful and authorized. Source revision, trace gaps,
code-derived versus observed behavior, and evidence for historical claims are
explicit. Current ownership stays here; proposed designs, rationale, defects,
and change risk route to existing owners. Cursor-specific tools, model defaults,
mandatory spawns, and restrictions on parent synthesis edits are omitted.

## improve-codebase-architecture

- [mattpocock/skills / skills/engineering/improve-codebase-architecture](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/improve-codebase-architecture) — v1.2.3, commit `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.

Returns findings, recommendations, and reasons in chat; creates an HTML report
only on request.

Glossary examples use the upstream `GLOSSARY.md` / `GLOSSARY-MAP.md` names;
resolution preserves configured or existing legacy paths, keeps one glossary per
context, and creates new files lazily. Cross-skill calls use host-neutral wording.

Exploration delegates through orchestration with a bounded read-only findings
contract and shared model defaults. Manual invocation remains unchanged.
Exploration also uses Codebase Design's ownership and enforcement reference for
evidenced friction, preserving recommendation-only ownership.
Interactive candidate selection remains the default. Requested autonomous
investigations select and test candidates through disposable technical experiments
and return migration and verification plans. The shared experiment reference
serves `correct` too, while `prototype` retains UI ownership. Autonomous planning
records proposed glossary and ADR changes for review instead of applying them.
Shared design and migration decisions use `engineering-principles`; candidate
exploration, technical experiments, planning, and glossary/ADR handling remain local.
Selected designs can continue through architect within the requested scope,
carrying forward checked findings and experiments.

Exploration also uses Codebase Design's shared architecture signals, grounded in
caller traces, state validity, and maintenance history rather than layout or size.
Lifecycle candidates include a transition table, compare lifecycle ownership and
caller obligations, and carry observed event sequences into verification plans.

## arena

- [cursor/plugins / pstack/skills/arena](https://github.com/cursor/plugins/tree/019a6a20592c10bf92869e5740368f578a9997fd/pstack/skills/arena) — `SKILL.md`; import baseline `019a6a20592c10bf92869e5740368f578a9997fd`. MIT notice in `licenses/lauren-tan-pstack.txt`.

Retains the Frame, Fan out, Cross-judge, Pick, Graft, and Verify flow and its
base-selection, selective-grafting, and synthesis-record guidance. Automatically
discoverable in both hosts. Orchestration owns model defaults, host delegation,
isolation, capacity, and bounded recovery. Candidates share the task and criteria;
relevant uncommitted inputs are supplied explicitly to isolated candidates.
Synthesis is the default; comparison-only requests return recommendations.
Explicit candidate counts and requested choice gates stay intact, fewer than
two usable candidates is incomplete, and synthesis gets its
own evidence. UI and technical experiments, production verification, review,
and publication use existing local owners. No Cursor model panel or tool syntax
is required.

## architect

- [cursor/plugins / pstack/skills/architect](https://github.com/cursor/plugins/tree/019a6a20592c10bf92869e5740368f578a9997fd/pstack/skills/architect) — `SKILL.md`, `references/runner-prompt.md` (local `references/design-candidate.md`), and `references/rationale-template.md` (local `references/design-rationale.md`); import baseline `019a6a20592c10bf92869e5740368f578a9997fd`. MIT notice in `licenses/lauren-tan-pstack.txt`.

Retains Ground, Sketch, Agree, Implement, and Scrap; caller usage before types;
competing whole designs; interface-depth comparison; the implementation contract;
and repeated-friction signals for restarting the design. Automatically
discoverable in both hosts for consequential design work. Grounding uses local
code, glossary, ADRs, and why. Codebase Design supplies vocabulary and
ownership/enforcement checks rather than a second red-flag reference. Arena and
orchestration own candidate synthesis and execution. Prototype and the shared
architecture experiment reference resolve empirical questions. Design-only and
planning requests stop at their requested artifacts; selected designs and
current evidence carry forward without repeating settled exploration.
Implementation continues only within scope and respects requested checkpoints.
Review, verification, demonstrations and access, and publication keep their
existing owners. Independent
consensus is recorded without requiring artificial structural differences.
The rationale keeps detailed sketches and evidence alongside its concise prose.
Design candidates and rationales include a transition table for correctness
that depends on event order, with lifecycle ownership and caller obligations
included in design comparison. Important sequences carry into implementation checks.
Candidate briefs end at their assigned output; rationale selection records
cover supplied designs as well as fresh synthesis, and distinguish checked
claims from unproven runtime behavior. Cursor-specific models and fixed file-hop thresholds
are omitted.

## ios-haptics

- Local: `skills/ios-haptics` (SreeStack); shares experience and evidence principles.

## swift-testing-modernization

- Local: `skills/swift-testing-modernization` (SreeStack); shares test-contract and state-isolation principles.

## swiftui

- Local: `skills/swiftui` (SreeStack).
- [emilkowalski/skills / skills/emil-design-eng](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/emil-design-eng) — component-behavior and access guidance redistributed from the retired local `design-eng` adaptation; content verified against commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7`, while the earlier local import baseline remains unknown.
- [superagents-lab/xcode27-skills / swiftui-whats-new-27](https://github.com/superagents-lab/xcode27-skills/tree/6f9ff8d5ad6000491cb0f483a776b7062e41cd97/swiftui-whats-new-27) — commit `6f9ff8d5ad6000491cb0f483a776b7062e41cd97`, used as a coverage map for independently written SDK 27 guidance.

Includes focused guidance for current platform materials and Liquid Glass rather
than keeping a separate visual-effect skill. Redistributed behavior and access
guidance, button sizing and hit-region checks, and current SDK migration
and feature guidance are folded into the normal SwiftUI workflow; automatic
invocation remains framework- and task-based.

The entrypoint selects shared design and state/recovery principles for ownership,
boundaries, and overlapping effects; SwiftUI implementation guidance stays local.

## uikit

- Local: `skills/uikit` (SreeStack).
- [emilkowalski/skills / skills/emil-design-eng](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/emil-design-eng) — component-behavior and access guidance redistributed from the retired local `design-eng` adaptation; content verified against commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7`, while the earlier local import baseline remains unknown.

Redistributed behavior and access guidance is folded into the normal UIKit
workflow; automatic invocation remains framework- and task-based.

The entrypoint selects shared design and state/migration principles for controller
boundaries, lifecycle recovery, and caller migration; UIKit mechanics stay local.

## verify

- Local: `skills/verify` (SreeStack).
- [emilkowalski/skills / skills/emil-design-eng](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/emil-design-eng) — interface-review criteria; content verified against commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7`, while the earlier local import baseline remains unknown.
- [emilkowalski/skills / skills/apple-design](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/apple-design) — contrast and reduced-transparency review criteria; content verified against commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7`, while the earlier local import baseline remains unknown.
- [cursor/plugins / pstack/skills/create-verification-skill](https://github.com/cursor/plugins/tree/dbf49813a39c1a5389c5e28cb8e4c1c2379e2454/pstack/skills/create-verification-skill) — `SKILL.md`; import baseline `dbf49813a39c1a5389c5e28cb8e4c1c2379e2454`. MIT notice in `licenses/lauren-tan-pstack.txt`.
- [cursor/plugins / pstack/skills/maintain-verification-skill](https://github.com/cursor/plugins/tree/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack/skills/maintain-verification-skill) — `SKILL.md`; import baseline `ecc249f1e306fc64ddf83c7bed16cacf7c2239db`. MIT notice in `licenses/lauren-tan-pstack.txt`.
- [cursor/plugins / pstack formal-verification workflows](https://github.com/cursor/plugins/tree/99b609a72323b70204eab407c622f436e858e112/pstack/skills) — `create-formal-verification-skill/SKILL.md` and `maintain-formal-verification-skill/SKILL.md`; adaptation baseline `99b609a72323b70204eab407c622f436e858e112` (pstack 0.15.32). Combined in `references/formal-verification.md`. MIT notice in `licenses/lauren-tan-pstack.txt`.
- [emilkowalski/skills / skills/mobile-native](https://github.com/emilkowalski/skills/tree/e8a175de22ae1e49370fc144c1f3bb9aeedf988d/skills/mobile-native) — mobile browser behavior and matching verification assertions; import baseline `e8a175de22ae1e49370fc144c1f3bb9aeedf988d`.
- [emilkowalski/skills / skills/break-ui](https://github.com/emilkowalski/skills/tree/e8a175de22ae1e49370fc144c1f3bb9aeedf988d/skills/break-ui) — realistic edge-data method, catalog, and content-constrained layout decisions; import baseline `e8a175de22ae1e49370fc144c1f3bb9aeedf988d`.

One automatically discoverable skill owns real-workflow selection, launch, driving,
acceptance judgments, evidence, and cleanup. It writes no docs in any repo, except formal check records under the
formal reference's conditions: it uses a temporary plan without a map, reads a map when one exists, and reports drift.
Adds a read-only doctor before driving, red-first reproduction against the base
revision, rerunnable scripts, and refusal of an assertion with no independent
expectation or way to run it. Formal checks use one conditional reference, also
reached when a change touches an existing check. It retains tool selection,
code/model correspondence, bounds, negative controls, counterexample replay,
drift classification, and sync-revision records. Model sensitivity and real-code
correspondence have distinct proof levels; a synchronized model can expose a code
bug. The standalone statechart scripts and mandatory statechart invocation are
excluded; domain traces and optional diagrams need no bundled renderer.
Stateful workflow checks carry architecture-discovered event sequences into
public-entry-point checks with expectations grounded in product requirements.
Interactive driving follows Orchestration's UI operation rule while Verify keeps
verdicts. Existing project skills may provide facts consistent with their
invocation policies; this skill retains procedure ownership and leaves migration
explicit.
Concurrent and long checks plan resource ownership; authorized harness isolation
changes prove concurrent isolation and independent cleanup.
Imported interface criteria retain full requested audit coverage. Web and iOS
checks follow the requested deployment or Simulator/device target. The iOS
reference reuses project harnesses and prefers XCTest with XCUIAutomation for new
iOS UI workflow tests, Swift Testing for new Swift unit tests, and XCTest for
performance tests. Suite execution preserves target identity, required-check
execution, failure evidence, and isolated state; new harness setup checks failure
detection with a disposable negative control. Evidence can be interactive or
automated and needs assertion coverage beyond a successful command. Targeted
suites preserve required integration gates, reconcile every selected test and
attempt, and require matching runtime evidence for pre-existing failure claims.
Terminal and service checks use process or PTY driving, bounded completion, public
protocols, and fresh persisted-output reads. Keeps bounded reproduction attempts,
failed-attempt evidence, authorization, isolation, redaction, run-owned cleanup,
and separate defect-reproduction reporting.
Authenticated workflows reuse designated test accounts and standing scope,
delegate application sign-in and command/API credential use to `agent-login`,
check delivery in the actual host interface, and distinguish provider
authentication, automatic login, and post-login verification. Inspectable results
route to `show-me`, and physical-device installs to its device delivery reference.
Readiness requires usable workflow state after initialization, migrations, and
fixtures. Setup/first-run checks prove isolated empty-data launch; ordinary checks
can reuse known state. Substitute environments leave target-specific setup
unverified. Missing fixtures retain assertions with local failed/blocked verdicts.
Edge-data workflow and catalog map to `references/edge-data.md`, with mobile
assertions in `references/web.md`. Comparison controls are optional, fixtures
are type-correct and task-scoped, existing authorization governs fixes, and
retention is proportional. Missing schema limits are distinguished from verified
unbounded input. Emulation and unavailable hardware checks carry explicit
evidence limits. Greetings and attribution instructions are omitted.

## repo-cleanup

- Local source: `~/.agents/skills/post-merge-cleanup`; upstream origin unrecorded.

Accepts merge completion handoffs from `merge`. Cleanup includes verified
task-owned development processes, simulator/emulator installs, disposable test
data, and temporary devices created solely for the task. Reused devices are
preserved and shut down only when the task booted them and no consumer remains.
Cleanup reconstructs process, device, and install ownership from available
session history and tool results, with logs, current state, and optional handoffs
as supporting evidence. Discovery and cleanup rules live together in
`references/development-resources.md`. SimLock resources route through
`simulator-lifecycle`: release the acquiring lease and leave device reclamation
to its manager. Run receipts support recovery and host-output cleanup; legacy
ownership can still be reconstructed without launch-time bookkeeping.
Preserves shared installs, retained data, inspection lifetimes, and resources
needed by unmerged stack layers.

## show-dont-tell

- [cursor/plugins / pstack](https://github.com/cursor/plugins/tree/5108b719a7aa484ef1a9781f587c7bbeac793f92/pstack) — `skills/no-comments/SKILL.md` and `agents/comment-sicko.md`; import baseline `5108b719a7aa484ef1a9781f587c7bbeac793f92`, imported 2026-10-13. MIT notice in `licenses/lauren-tan-pstack.txt`.

Automatically discoverable in both hosts for code and documentation clarity
passes and callable from PR preparation. A short guide reduces the
need for explanation through self-documenting code, structural enforcement,
and one authoritative home for documented rules. Uses Domain Modeling's ADR
criteria. Documentation must supply necessary knowledge agents cannot cheaply
and reliably obtain elsewhere; document categories have no blanket exemption.
Legal notices remain protected. Enforcement must reject a violation before
replacing a reminder; correctness suppressions require repair before removal. Scope and
contracts stay intact. `references/explanation-audit.md` classifies why prose
exists across code and docs, with focused checks for defensive justifications,
embedded suppressions, formatting directives, and negative-test assertions.
Delegation, review, and delivery belong to the caller.

## merge

- Local: `skills/merge` (SreeStack).

## prototype

- [mattpocock/skills / skills/engineering/prototype](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/prototype) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

UI prototypes for web, mobile, and desktop; no logic-prototype mode. The local
workflow chooses enough distinct options to expose the decision, coordinates
with `ui-design`, `animate`, `swiftui` or `uikit`, `verify`, and
`show-me`, and adds explicit rules for live side effects, unavailable target
tooling, comparison-control verification, durable decisions, and proportional
prototype retention and cleanup.
Show Me chooses demonstrations and access for the prototype result.

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
measurement through the shared evidence principle and its measurement-validity
reference, and checks project versions and existing architecture. How to Use
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

## code-quality

Local command-runner skill for Crapper, Dryer, and Mutator; instructions are
independently written. Tools run through `uvx` from pinned upstream Git sources;
Mutator's environment includes Crapper as an additional dependency. Setup is
contained in the skill's supporting references.
Command and setup baselines checked 2026-10-26:

- [unclebob/crapper](https://github.com/unclebob/crapper/tree/6fd92c4c9bcc56efb64a2f8743d5a2993bcfd42d) — `6fd92c4c9bcc56efb64a2f8743d5a2993bcfd42d`.
- [unclebob/dryer](https://github.com/unclebob/dryer/tree/66ff6d21a42c04afcad89c78a80066176d1294b0) — `66ff6d21a42c04afcad89c78a80066176d1294b0`.
- [unclebob/mutator](https://github.com/unclebob/mutator/tree/a5a0cb803b66e0cdb8bf471b3b08af701d424a41) — `a5a0cb803b66e0cdb8bf471b3b08af701d424a41`.

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

- [vojtaholik/good-css / skills/good-css](https://github.com/vojtaholik/good-css/tree/e074e76a011dbadc4f0a7fbd6c661ed79deb6371/skills/good-css) — web CSS reference adaptation baseline `e074e76a011dbadc4f0a7fbd6c661ed79deb6371`; explanations and technical citations checked in upstream `PRACTICES.md`. MIT notice in `licenses/vojtaholik-good-css.txt`.
- [s0xDk/refactoring-ui-skill](https://github.com/s0xDk/refactoring-ui-skill) — imported revision: unknown; its `SKILL.md`, reference write-ups, and CSS tokens are adapted into the local entrypoint, web references, and token asset.
- [anthropics/skills / skills/frontend-design](https://github.com/anthropics/skills/tree/34040c9c568585f6929bedeaad110ad08f079624/skills/frontend-design) — art-direction calibration and critique; commit `34040c9c568585f6929bedeaad110ad08f079624`.
- [emilkowalski/skills / skills/emil-design-eng](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/emil-design-eng) — web typography, component behavior, and access guidance; content verified against commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7` while the earlier local import baseline remains unknown.
- [emilkowalski/skills / skills/apple-design](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/apple-design) — typography, materials, press activation and cancellation, contrast, and reduced-transparency guidance; content verified against commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7`, while the earlier local import baseline remains unknown.
- [emilkowalski/skills / skills/mobile-native](https://github.com/emilkowalski/skills/tree/e8a175de22ae1e49370fc144c1f3bb9aeedf988d/skills/mobile-native) — mobile browser behavior and matching verification assertions; import baseline `e8a175de22ae1e49370fc144c1f3bb9aeedf988d`.
- [emilkowalski/skills / skills/break-ui](https://github.com/emilkowalski/skills/tree/e8a175de22ae1e49370fc144c1f3bb9aeedf988d/skills/break-ui) — realistic edge-data method, catalog, and content-constrained layout decisions; import baseline `e8a175de22ae1e49370fc144c1f3bb9aeedf988d`.
- [Emil Kowalski's mobile browser fixes](https://x.com/emilkowalski/status/2116144374170235224) — October 30, 2026 post and attached checklist; concrete input-font, tap-highlight, and selection recipes.

The automatically discoverable skill owns cross-platform visual hierarchy,
system decisions, and art direction plus browser component behavior and
accessibility. It routes web visual work to adapted Refactoring UI references
and an optional CSS token asset, browser interaction work to a focused behavior
reference, and SwiftUI or UIKit visual work to Apple-platform guidance grounded
in current Apple documentation. Native structure, behavior, and accessibility
remain with `swiftui` and `uikit`; motion remains with `animate`. Inherited
numeric recipes are contextual fallback heuristics rather than requirements.
The entrypoint separates inspection, diagnosis, scoped execution, and acceptance
from task-based reference routing. Visual-only and behavior-only work preserve
each other's contracts; advisory work returns concrete changes and checks.
Typography and component composition live with web visual systems, content-width
choices with layout, and identity levers with art direction. Diagnosis rows are
hypotheses to test against the rendered surface. HSL and dark-appearance recipes
remain contextual options with measured contrast, not fixed palette rules.
List grouping explains combined line-height and item spacing; dark-surface
separation includes a measured color-pair example rather than a universal ratio.
The art-direction reference preserves Anthropic's subject-matter grounding,
generated-design tells, two-pass self-critique, restraint guidance, and Chanel
editing mnemonic while removing CSS implementation and general copywriting
material.

Mobile web guidance maps to `references/mobile-web.md`; edge-data layout choices
join `references/web-behavior-and-accessibility.md`. Uses current platform
capabilities and documentation rather than blanket CSS resets or device labels;
preserves zoom, selection, valid activation, and browser gesture ownership.
The 16px input-font value is an iOS troubleshooting baseline with target-browser
retesting; tap-highlight and selection declarations stay scoped to affected
controls rather than global resets.
Greetings and attribution instructions are omitted.
Browser behavior routes interacting state and async transitions to the shared
domain principle; controls reflect action rules enforced in the underlying logic.

Web CSS and responsive-layout implementation are explicit discovery branches;
automatic invocation remains enabled. Upstream `good-css/references/` maps by task:
`foundations.md` to `references/web-css-foundations.md`; `layout.md` and
`spacing-and-shape.md` to `references/web-layout.md`; `text-and-media.md` media
geometry, numeric figures, label trimming, and icon metrics to
`references/techniques.md`, and truncation to
`references/web-behavior-and-accessibility.md`. `interaction.md` joins that
behavior reference; `show-and-hide.md` semantics and anchor positioning also
join it, while transition mechanics belong to `animate`. Carousel, bounded
panels, and sticky-header offsets from `scroll-and-viewport.md` join
`references/mobile-web.md`; root overscroll and safe areas retain its existing
contextual guidance. Its edge decoration belongs to `animate`.

Preserves product tokens, authoring stack, reset, selection, semantic contracts,
and native ownership. Retains useful declaration sets and prerequisites while
replacing blanket reset/color rewrites, geometry/easing prohibitions, automatic
acceptance of unselectable card text, and no-fallback rules. The carousel's
global script is replaced by instance-owned stepping and lifecycle requirements
covering gaps, changing widths, RTL, and resize. Textarea wrapper animation is
optional and requires observer/box ownership. Container/subgrid restrictions
are axis-dependent; safe alignment is limited to positional values. Fluid-font
ratios and upstream browser measurements are not treated as accessibility proof.
Technical citations accompany guidance; browser-target checks replace frozen
version tables. Global text trimming and destructive layout resets are omitted.


## research

- [mattpocock/skills / skills/engineering/research](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/research) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

Research owns a cited primary-source note and uses shared research defaults.
Notes default to host-provided session scratch storage outside the repo, with
a unique writable OS temp directory as fallback. Project output follows an
explicit request or a task's maintained-document requirement. Handoffs and
compaction summaries retain absolute note paths; continued work rereads and
updates the note, keeping it available for the session and dependent workers.
YouTube retrieval uses Gemini and X posts use Grok through orchestration's
configured selections. Assigned researchers own synthesis; their briefs permit
needed source tasks, whose retrievers work directly. Parents check source
evidence and access gaps before acceptance.

## shape

- Local: `skills/shape` (SreeStack), a user-started workflow that turns a rough
  idea into a settled brief, or one spec for several outcomes, through
  conversation. It chains `reframe`, `grilling`, `prototype`, `show-me`, and
  `to-spec`.

## reframe

- Local: `skills/reframe` (SreeStack). Conceptual input from [Felix Rieseberg's ambition framework](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/) (article checked 2026-11-02) and [Ray Amjad's examples](https://www.youtube.com/watch?v=RbfQayMNtJc) (checked 2026-10-18).
- [robonuggets/be-ambitious / SKILL.md](https://github.com/robonuggets/be-ambitious/blob/dc116a3ebd8cf772e4d0930626f67369bd60399d/SKILL.md) — conceptual comparison at `dc116a3ebd8cf772e4d0930626f67369bd60399d`, checked 2026-11-02; no upstream prose copied.

Independently written brief preparation and acceptance planning, model-discoverable for requested
reframing, ambition, prompt improvement, and brief formation for a calling workflow. Scales
to uncertainty and considers harder targets, raw evidence, testable discoveries,
cross-field methods, and lasting workflows with explicit setup and ownership.
Preserves authorized scope and the agreed finish line, allows qualitative
evaluation, and returns to the calling workflow. Standalone reframing ends with
the brief; prompt rewriting returns a copyable prompt. The brief names the code it
covers and what is out of scope. No mandatory ladder,
expert roster, numerical stretch target, or fixed output template.
`references/acceptance.md` pairs outcomes with constraints and suitable evaluation,
including qualitative judgment and research uncertainty. Brownfield discovery grows
checks with actual risks. Evidence identity and comparison detail are required
where claims depend on them; existing independent review assesses consequential
evidence changes.

## review

- Local: `skills/review` (SreeStack).
- [Vox / review-noise post](https://x.com/Voxyz_ai/status/2115518965443076573) — conceptual input for shared bug evidence and Review Sweep's exposure/impact policy; checked 2026-10-28. Independently written qualitative guidance preserves rare material failures and explicit contracts; no numeric threshold or upstream prose copied.

Reviewer references:

- [DietrichGebert/ponytail / skills/ponytail-audit](https://github.com/DietrichGebert/ponytail/tree/c982cd411abb53323c4baa1baa3c2f020b8d0b08/skills/ponytail-audit) — explicit whole-tree deletion-evidence guidance in `references/ponytail.md`; addition baseline `c982cd411abb53323c4baa1baa3c2f020b8d0b08`. The composite brief's other material retains the baseline below.

- `references/standards.md` and `references/spec.md`: [mattpocock/skills / skills/engineering/code-review](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/code-review) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.
- `references/thermo.md`: [cursor/plugins / cursor-team-kit/skills/thermo-nuclear-code-quality-review](https://github.com/cursor/plugins/tree/a29f5a8ca161b1de4ffc5484454958bebc04eaa5/cursor-team-kit/skills/thermo-nuclear-code-quality-review) — commit `a29f5a8ca161b1de4ffc5484454958bebc04eaa5`.
- `references/adversarial.md`: [openai/codex-plugin-cc / plugins/codex/prompts/adversarial-review.md](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/plugins/codex/prompts/adversarial-review.md) and [schemas/review-output.schema.json](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/plugins/codex/schemas/review-output.schema.json) — import baseline `db52e28f4d9ded852ab3942cea316258ae4ef346`, Apache-2.0. Preserves the prompt's wording, XML structure, review criteria, and JSON verdict contract; `references/adversarial-output.schema.json` is byte-identical to upstream. Local edits add a heading and modification comment, remove the fixed model persona, bind the four template placeholders to the supplied brief, link the schema, put Review's coverage metadata in the JSON summary, and retain parent settlement/read-only limits and equivalent agent-procedure tracing. License and copyright notice: `licenses/openai-codex-plugin-cc.txt` and `licenses/openai-codex-plugin-cc-NOTICE.txt`.
- `references/opencode.md`: [anomalyco/opencode / packages/core/src/plugin/command/review.txt](https://github.com/anomalyco/opencode/blob/68bc26b7da1990ce10ffecfbc1e09eb13aa5d824/packages/core/src/plugin/command/review.txt) — v2.1.4, import baseline `68bc26b7da1990ce10ffecfbc1e09eb13aa5d824`, MIT. Preserves upstream wording and sections, including target-discovery commands and tool guidance. Local edits add a heading, bind `$ARGUMENTS` to the caller's request/target, and establish Review's resolved scope, read-only/coverage contract, parent settlement, and direct search when further delegation is not authorized. License: `licenses/anomalyco-opencode.txt`.
- `references/gemini.md`: [gemini-cli-extensions/code-review / skills/code-review-commons/SKILL.md](https://github.com/gemini-cli-extensions/code-review/blob/dd1a10d2c9d07b2ebade866590fdfa59cd8f9d04/skills/code-review-commons/SKILL.md) and [commands/code-review.toml](https://github.com/gemini-cli-extensions/code-review/blob/dd1a10d2c9d07b2ebade866590fdfa59cd8f9d04/commands/code-review.toml) — v0.1.0, import baseline `dd1a10d2c9d07b2ebade866590fdfa59cd8f9d04`, Apache-2.0. Preserves the commons body verbatim, including persona, severity guidance, changed-line restriction, and technical constraints; removes host frontmatter because this is a reference. Includes the command's output block with only its merge-ready assertion removed and the required coverage report allowed. Local integration adds a modification comment and Review's supplied scope, assigned criteria, read-only/procedure checks, coverage metadata, and parent settlement. No fixed `origin/HEAD` discovery, PR-posting command, or installed wrapper imported. License: `licenses/gemini-cli-extensions-code-review.txt`.
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
Explicit assignments select criteria while retaining full-scope reading;
standalone assessment defaults to the existing correctness and code-quality
criteria, with Adversarial used when requested or assigned. OpenCode harness
and Gemini model reviews additionally load their checked-in provider references;
these supplement assigned lenses under the shared review contract and require
no native plugin or command activation. Later-round briefs include
prior findings and dispositions for independent reassessment.
Bug findings establish supported triggers, practical exposure, and consequences,
distinguishing observed behavior, inference, and unknowns. Blocking findings need
material impact or an explicit requirement or contract violation.
Standards and Spec keep separate labeled reports, their upstream review bars,
and 400-word limits. Thermo and Ponytail apply within the supplied scope;
structural suggestions require evidence and a concrete benefit. Ponytail omits
persistent modes, installation, benchmark displays, and whole-repo debt ledgers.
Ponytail also assesses redundant defensive code through traced guarantees and
error paths, preserves changing-state checks and resource lifetimes, and judges
helpers by semantic value rather than caller count. Its findings require the
smallest safe cut and the behavior to preserve.
Structural findings connect the change to introduced or worsened friction and
separate broader existing debt. Thermo uses Codebase Design's shared architecture
signals. Its file-size guidance prompts investigation of responsibilities and
caller knowledge; size alone is not a finding or blocker. Structural blocking
findings require concrete impact or regression under the shared evidence and
settlement rules.
Indirect-consumer checks use `blast-radius`; React or Next assessments use
`react-best-practices` and current changed-scope React Doctor diagnostics.
The shared review brief carries applicable evaluation criteria and evidence,
including empirical comparison conditions and qualitative judgments. Review checks
changes to tests, fixtures, and measurement methods.
Delegated review evidence adds explicit workflow/pass identities, configured
model metadata, task-specific output paths, supported read-range receipts,
frozen-source citation checks, and caller-retained original artifacts.
Common inputs are separate from same-round peer outputs; briefs state the
cooperative peer-read boundary and exposure uses the existing failure policy.
Source snapshots exclude designated generated review artifacts while retaining
other nonignored untracked source.

## review-fix-loop

- Local: `skills/review-fix-loop` (SreeStack). T3-owned passes map required
  assessments to their named model defaults. Impact-based coverage selects one
  Primary for contained work, Primary plus a fitting lens for contained risk, and
  staged Primary, Ponytail, and Thermo, then Adversarial, for substantial work.
  Fixes route by what they change to new tasks on the original reviewers'
  models for those angles, under Orchestration's review-pass rule; Primary's integrated check covers
  cumulative repairs; and repeated repairs to an invariant trigger a parent
  design checkpoint. The first independent pass adds one random optional reviewer
  from each provider pool. The loop owns provider-reference
  delivery, skips, and stable snapshots. Generic
  delegation and handoff use Orchestration, with tasks mapped to review
  assignments and workflow/pass identities; findings use Review Sweep with
  stable issue IDs and per-issue repair/check evidence.

## pr

- Local: `skills/pr` (SreeStack).
- [t3dotgg/tstack / babysit-pr](https://github.com/t3dotgg/tstack/blob/7de017b3fc9d50c03cf3ecb98fb71e0ca65a78bd/skills/babysit-pr/SKILL.md) — workflow comparison informing parent-owned event watching, handoff cleanup, rate-limit recovery, and base-freshness checks. No upstream prose, scripts, or bot-specific merge gates copied.
- [cursor/plugins / pstack PR feedback pagination fix](https://github.com/cursor/plugins/tree/dbf49813a39c1a5389c5e28cb8e4c1c2379e2454/pstack/skills/poteto-mode/scripts/watch-pr) — pagination/completeness requirement adapted from `github.ts`; addition baseline `dbf49813a39c1a5389c5e28cb8e4c1c2379e2454`. No watcher code imported. MIT notice in `licenses/lauren-tan-pstack.txt`.
- [mattpocock/skills / skills/engineering/pr](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/pr) — PR-body structure, visual selection, evidence, and merge-risk guidance adapted into `references/pr-body.md`; import baseline `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`. Upstream credits [HumanLayer / show-me](https://github.com/humanlayer/skills/tree/ca7c8088db69e315a8b2deea43820270457f8f3c/plugins/show-me/skills/show-me) for visual guidance; the origin revision used by Matt is unrecorded. HumanLayer MIT notice checked at `ca7c8088db69e315a8b2deea43820270457f8f3c` in `licenses/humanlayer-skills.txt`.

The local name and UI are `pr`, with automatic discovery. It owns PR text, publication, and
watching. Fixing feedback moved to `review-sweep` and merging to `merge`. Publishing reuses
matching review evidence, and runs `show-dont-tell` then the review loop when there is none.
`scripts/pr_state.py` reads one head's checks, threads, comments, and reviews through every page,
replacing hand-read readiness with `blockers`, `pending`, and `to_settle`.
The body guide uses Summary/Evidence/Merge Danger by default, defers to project
PR templates, and preserves local why/effect/root-cause/stack facts. It expands
visual selection to algorithm, runtime, UI, file, interaction, diff, and complete
block views with a locally written diff example. Evidence is observed and revision-
appropriate, with unavailable before states disclosed. Reversibility, concrete
consumers, rollout, and restoration limits replace a forced one-word blast-radius
rating. Small PRs can use concise prose; publication refreshes the guide's facts
against the current scope/head.
A delegated owner returns a pending report instead of watching; the parent
watches and resumes that same owner for repairs. Unavailable watchers and exhausted
rate limits remain explicit pending states without custom polling.
Evidence reuses Show Me's checked demonstrations and access links when available.
History changes share a local preservation reference with Merge and gh-stack:
back up current retained bytes outside affected checkouts, preserve both versions
on conflicts, and verify hashes after success or recovery.

## review-sweep

- Local: `skills/review-sweep` (SreeStack). Canonical issues retain workflow/pass,
  source-report relationships, and assignment/model provenance. Acceptance,
  applied repairs, and snapshot-specific checks remain separate; accepted fixes
  follow orchestration's repair routing.
  Settlement weighs supported exposure and impact, preserving rare material and
  required failures while deferring low-impact work and rejecting hypotheticals.

## setup-sreestack

- [mattpocock/skills / skills/engineering/setup-matt-pocock-skills](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/setup-matt-pocock-skills) — prerelease-main import baseline `d81f3a183412e71a5b1e84ca21bc1a35eea03a60` (the skill folder matches v1.3.1).
- [cursor/plugins / pstack/skills/create-verification-skill](https://github.com/cursor/plugins/tree/dbf49813a39c1a5389c5e28cb8e4c1c2379e2454/pstack/skills/create-verification-skill) and [maintain-verification-skill](https://github.com/cursor/plugins/tree/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack/skills/maintain-verification-skill) — map and recipe format; import baselines as recorded under `verify`. MIT notice in `licenses/lauren-tan-pstack.txt`.

Manual-only in both hosts. The local name and UI are SreeStack Setup. One setup
workflow owns project-specific conventions and pointers, with scoped update,
glossary migration, optional ticket configuration, and verification maps. Full
setup creates or reuses the index, records known setup facts and coverage gaps, and
adds a discovery pointer. `references/verification-map.md` owns map creation and
upkeep, on request and only in the user's own repos. It writes project docs and
runnable helpers rather than generating project skills, adapts the pstack formula
to five shared parts (launch, doctor, drive, evidence, cleanup) and feature recipes
with descriptions and sub-features, entry points, harness driving with assertions
and proof, and gotchas. It seeds the top 3 to 5 features, proves at least one live
through `verify`, supports targeted updates and source-and-live whole-map audits,
and keeps useful human assertions. Feature directories are created with the first
recipe. Scoped updates and glossary migration
preserve their requested scope. Project workflow guidance
uses current local review, PR, stack, merge, acceptance, and delegation owners;
host settings and installation remain separate. Program ownership uses `chief-of-staff`, one outcome uses `implement`,
and bounded parallel work uses `swarm`. Native tracking follows explicit requests. Agent defaults link the shared
orchestration policy rather than duplicating host rank settings. Existing commands and standards
are linked rather than duplicated. Active instruction files are selected by the
user/host or existing pointer ownership, with `AGENTS.md` for a new default.
Setup compares proposed guidance by meaning across inherited global/host
instructions, project docs, and shared skills. Additions supply missing project
facts, explicit overrides, or needed pointers while preserving existing scope
and conditions; final checks catch paraphrased duplication and redundant reruns.
Project workflow pointers call `show-me` for inspectable results and useful
UI iteration feedback; demonstration and access procedures remain in that skill.
Simulator projects record their runner/host integration and retained targets
through `simulator-lifecycle`; ordinary setup does not claim environment adoption
or native proof from a documentation pointer.
Research owns session-note storage; setup leaves research directories and
ignore rules to explicit project requirements.

Domain defaults use `GLOSSARY.md` / `GLOSSARY-MAP.md`; established legacy/custom
paths and one vocabulary source per context remain supported. Context boundaries,
not package count alone, determine layout. `domain.md` is adapted to actual
project paths. Glossary migration preserves vocabulary, local edits, custom
locations, and ADRs; updates consumers; handles collisions; and is a no-op on
rerun. General context documents remain outside that migration. Tracker seeds
keep the import's issue, blocking, and claim conventions, and leave out triage
labels, PR request surfaces, and wayfinding maps. The GitHub seed adds and reads
blocking edges through `gh issue`, and each seed's claim checks that a
self-chosen ticket is free to take. Full setup writes only the
configured/requested docs, preserves project additions, and distinguishes
documented commands from exercised readiness.

PR workflow references use the local `pr` entry point.


## show-me

- Local: `skills/show-me` (SreeStack). Shows results in the user's thread during the work and at every stop, in model-selected forms, and covers web sharing and device delivery, including physical-device recovery. Verify retains acceptance.
- Conceptual input: DeepSeek source and revision recorded under [chief-of-staff](#chief-of-staff); no code or prose copied.

## simulator-lifecycle

- [callstackincubator/simlock](https://github.com/callstackincubator/simlock) — generated skill from published `simlock@0.4.0`, `dist/instructions/skill.js` (`src/instructions/skill.ts` upstream); package git revision unrecorded. MIT notice in `licenses/callstackincubator-simlock.txt`.

Preserves the upstream setup and installed-instructions steps. Local name is
`simulator-lifecycle`; automatic discovery covers simulators/emulators rather
than test phones. Adds host-routing, retained-target and shared-requester ownership
gates plus fresh lease-identity requirements, and links local
run/handoff, runner-integration and adoption references, including bounded iOS
agent-device helper preparation, bounded failure diagnostics and bridge capability
checks. Failure guidance defers to host recovery instructions and preserves unresolved
ownership conflicts. Owns T3 Device panel routing, returned driver and session flags,
and Xcode and platform tool routes for reaching a device. Adds a last-resort, coordinated CoreSimulator restart for repeated iOS boot failures before a grant, guarded by a local script. Runtime lease rules stay
with `simlock instructions`. Technical citations use checked upstream source
documents rather than inaccessible deployed documentation routes.

## tdd

- [mattpocock/skills / skills/engineering/tdd](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/tdd) — v1.2.3, commit `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.

Automatic discovery includes feature and bug work, but not ordinary
integration-test additions by themselves. Seams established by the spec or
project conventions count as pre-agreed; user confirmation is reserved for
material unresolved choices.
The review stage uses `review-fix-loop`.
Shared behavior-test guidance uses `engineering-principles`; seam selection,
vertical red/green cycles, specialist examples, mocking, and local pitfalls stay here.
Each cycle covers one behavior, not upstream's one test; cases of that behavior can go together.
The event-sequence example checks duplicate submission and failure/retry through
a public API, inspecting payloads only at the external persistence boundary.
Cancellation and late-completion scenarios remain conditional on the contract.

The UI summary describes red/green development, matching the rule that
refactoring belongs to review. Requests phrased as red-green-refactor remain
part of automatic discovery.

Glossary examples use the upstream `GLOSSARY.md` / `GLOSSARY-MAP.md` names;
resolution preserves configured or existing legacy paths, keeps one glossary per
context, and creates new files lazily. Cross-skill calls use host-neutral wording.


## to-spec

- [mattpocock/skills / skills/engineering/to-spec](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/to-spec) — v1.2.3, commit `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.

Writes the spec into the shaping record, the one `shape` keeps or one chosen by
its record rule, and publishes to the tracker only when the user asks. Publishing
uses supplied or project-configured tracker information, without a readiness
label, and leaves a link to the issue in the record. Unresolved required choices
can be supplied directly or through the manual setup skill. Synthesizes without
interviewing: it reuses settled decisions and seams, and asks only a missing
decision that changes the spec, in one Grilling round. The template adds one
entry per outcome with proof, covered code, preserved behavior, inputs and
access, exclusions, assumptions, and finish line, and keeps every settled brief
field when it replaces the brief; scales user stories to the settled coverage
instead of upstream's extensive list; and allows paths where they pin down
scope, keeping upstream's ban on line numbers and code snippets.

Setup references use the local `setup-sreestack` entry point.


## to-tasks

- [mattpocock/skills / skills/engineering/to-tickets](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/to-tickets) — v1.2.3, commit `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.

Model-invoked, so workflows can reach it. It produces a task list. Publishing to a tracker
happens only on request and stays user-approved. Uses supplied or project-configured tracker
information, with no labels.

Each task delivers one result. This skill owns the parallelism test and the ready rule, which the
tracker seeds and `chief-of-staff` point to. The ready rule allows a provisional start on an open
decision's reversible recommended option; acceptance and landing wait for the answer. A shared resource becomes a note under Inputs, and
blocking edges mean one task needs another's output or decision.

Setup references use the local `setup-sreestack` entry point.

## writing-for-agents

- [mattpocock/skills / skills/productivity/writing-for-agents](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/productivity/writing-for-agents) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.
- [nicobailon/skill-diet](https://github.com/nicobailon/skill-diet/tree/5f41df1220eb5759c413390206f1b9e6c63be754) — commit `5f41df1220eb5759c413390206f1b9e6c63be754`; `SKILL.md`, `references/diet.md`, `references/tool-skills.md`, `references/formats.md`, `references/eval.md`, and `references/adapter.md` inform the revision, tool-guidance, and evaluation procedures, and `scripts/eval.mjs` is adapted into `scripts/compare.py` (MIT).

A local rewrite around one test: a line stays only if removing it changes what an
agent does. Keeps the upstream concepts that change behavior: pointers, placement,
completion conditions, leading words, and pruning. Adds a ranked choice of home for
guidance, goal-first writing, capability and workflow contracts, plain-writing rules,
test-based rules, and retesting after model releases. Drops router skills and the
upstream goal of the same process on every run.

Documents paired Claude Code and Codex invocation settings, writes context pointers
as request-shaped triggers, and limits a model-invoked description to its triggers.
Existing invocation choices are preserved.
Rewrites start fresh, then settle old rules by the failure they prevent. Tool guidance
covers drift, help quality, call syntax, and usage-derived examples. Working on Skills
starts from real runs. Controlled Comparison keeps matched variants, calibration,
full outcome checks, and normal host integration.

`scripts/compare.py` ports `eval.mjs` to the Python standard library with Claude Code
and Codex adapters in `scripts/hosts.py`. It reads a versioned manifest, hashes every
input, rejects a missing cell or a result whose inputs changed, keeps failed runs and
work dirs as evidence, and takes blind judge verdicts. Calibration also checks that
installed skills don't leak in and that each variant's collection loads. Scoring
judges one declared target, lets any failed required case veto, reports
unavailable telemetry, and never claims equivalence or significance. It drops the
upstream MISS and WORSE pass rules, regex answer scoring, full-weight token sums, and
the one-skill-per-version layout. Paid runs stay out of the checks.

Keeps skill-diet's steps for adding a rule, its level rule, and its counts of 10–15
requests and three runs. Holds an added rule to the three runs a removal needs, in
place of one fresh session. Exempts a named set of guardrails from the line test.

`SKILL.md` covers writing for any agent document and ends by routing to a guide for
each kind of document. `references/agent-instructions.md` is local, built from host
documentation and published evaluations checked on 2026-11-05, plus load tests on Claude
Code 2.1.318 and Codex 0.166.0.

Uses shared review owners. Does not adopt fixed size or growth budgets,
inactivity-based host removal, schema-field hiding, fixed safety-line counts, or
automatic deletion from no-skill success. Bytes, measured task context, cache usage,
and cost remain distinct. Scorer repairs require comparable reruns; failed required
cases cannot be averaged away.

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
- Conceptual input: DeepSeek source and revision recorded under [chief-of-staff](#chief-of-staff); no code or prose copied.

The entrypoint owns who does the work, assignment, dispatch, return, and
acceptance. It keeps one owner per slice, separate writer paths, serial git and
index work, and the child limit, which apply whenever two agents run; `swarm`
owns the decision to run work in parallel. `references/models.md` is a lookup: one editable table owns working,
research, source-retrieval, and review model defaults, including effort and
additional review pools, with row choice, raising a row, and UI operation.
`references/reuse-and-recovery.md` owns reuse, review passes, owner replacement,
recovery, and availability fallbacks. Live host instructions own APIs, transport,
task lifecycle, permissions, and workspace binding. Local policy owns concurrency
and bounded recovery, subject to caller-specific failure policy.

The table says what to launch, not who may work. A top-level thread gives every
project-file edit to a subagent, in the background, and stays free;
`global/AGENTS.md` carries that rule because not every model loads this skill.
Children do their own work and delegate only when their task says to. A stuck agent asks up; a parent answers and resumes it, can
launch a read-only reviewer for a second opinion, and replaces an owner only on
evidence of repeated failure. A further replacement with no new evidence is a blocker.
A thread that cannot launch a subagent says so and asks. A slice's owner is the agent that wrote it. Repairs go to that
owner first, by resuming its thread, because T3's rule bars a new delegate and resuming
starts none. No owner left means its thread is gone or can't be resumed, not a finished run; T3's
rule then applies, and a repair it does not cover launches from the table. A lost owner
follows recovery, not the repeated-failure test.

Row choice distinguishes source review and research, dedicated UI operation, UI
building, document writing and revision, then Simple, Standard, or Hardest
implementation. Hardest is rare and requires evidence that Standard is insufficient;
its Codex fallback is GPT-6 Astra at X-High. The existing agent handles routine UI
operation; a dedicated operator is reserved for substantial work, specialized
capabilities, required independence, or repeated operational difficulty, at a tier
set by flow complexity and false-pass cost, with Verify retaining assertions and
verdicts. Listed availability fallbacks apply to quota, unavailable providers/models,
and provider runtime failures while preserving acceptance, review criteria, and
explicit choices. A listed fallback is the user's standing permission to switch. A
user-named model blocks rather than falling back unless the user authorized a substitute.

Names no callers. Briefs carry the original request and accepted corrections;
explicit human holds persist until released.
A new assignment prefers a retained agent when its context helps and it matches the
row's model and effort, workspace, and a host continuation that is both supported and
permitted. In-scope follow-up stays
with its owner whatever its model. An agent that wrote or directed a change is excluded
from later independent assessment of it. The first review pass uses fresh agents on the
review rows; later passes use a new task on the same model as that reviewer, with its
outputs archived and same-round peer content kept out. Children return decision requests
that stay open until answered or withdrawn. A result is accepted only
after inspecting its artifact at a named revision; every required slice is accounted for.
Acceptance and delivery stay separate, and a failed handoff is resent only to its original recipient. Review Fix Loop owns assessment
coverage, and PR runs that loop when no matching review evidence exists. Goals and
recurring work start only on request.

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

## stageshow

- [benjitaylor/skills / stageshow](https://github.com/benjitaylor/skills/tree/802057409787133703c56001080169e347305572/stageshow) — complete `stageshow/` folder; import baseline commit `802057409787133703c56001080169e347305572`. MIT notice in `licenses/benjitaylor-stageshow.txt`; bundled asset terms remain in `skills/stageshow/NOTICE.md` and its linked notices.

Imported unchanged, including instructions, references, React kit, examples,
playground, scripts, dependency lockfile, and license notices. Automatically
discoverable in both hosts, as upstream. Root `.gitattributes` preserves the
upstream Discover SVG's CRLF and teaching reference's final blank line during
whitespace checks without changing their bytes.

## retro

- [mattpocock/skills / skills/engineering/retro](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/retro) — `SKILL.md` and `agents/openai.yaml`; import baseline `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`. MIT notice in `licenses/mattpocock-skills.txt`.

Manual-only in both hosts, as upstream. Retains upstream categories, mechanical
check preference, reference structure, and examples. Cross-skill wording is
host-neutral; findings carry session evidence and remain recommendations until
implementation is requested. Review applies the project's coding standards,
mechanical rules become checks, and `pr` owns review timing. `writing-for-agents`
owns where instructions belong and how hosts load them. A missing hook or CI
guardrail is a finding only when the session shows a mistake, omission, or
exposure it would have caught; otherwise retro offers a separate setup audit.

T3 session sources prefer scoped app history; other hosts retain local-log
inspection. Historical claims are checked against current artifacts.
Repository-wide recurring failure prevention belongs to `correct`; retro reports
the session evidence and routes further investigation only within the user's scope.


## Shared global instructions

- [unclebob/ub-mode / SKILL.md](https://github.com/unclebob/ub-mode/blob/57a8bdd28e45ed41900ace0bafa2ff76dd9ed70f/SKILL.md) — conceptual input checked at revision `57a8bdd28e45ed41900ace0bafa2ff76dd9ed70f` on 2026-10-25; no upstream prose or code copied.

`global/AGENTS.md` expresses simplicity, behavior-verification, and
failed-assumption defaults in locally written guidance. Simplification stays
within the requested scope; verification uses independent expectations and
reports gaps when meaningful automation is impractical. Detailed engineering
and testing procedures stay in their existing skills. Tool-specific gates,
action diaries, automatic cleanup, and push-to-main instructions are omitted.
It also carries the user's standing Snip Snap capture instruction.
`scripts/sync_hosts.py` links it as `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md`
and links skills per host from the `codex/` and `claude/` setup manifests, from
the stable clone on `main` only. Its `reference-transaction` hook syncs after
local `main` updates and chains into existing hooks without replacing them or
changing their reference input. Sync refreshes its owned handler; hook health
checks report drift separately from host links. Checks from linked worktrees
use the stable clone's script and manifests.
README.md documents sync, the hook, and Claude Code's personal skill links.
`scripts/host_settings.py` merges the leaf keys of `claude/settings.json` into
`~/.claude/settings.json` and of `codex/config.toml` into `~/.codex/config.toml`
and `~/.codex-t3/config.toml` during that sync; private keys stay in those local
files. The pinned `tomlkit` package is installed in the stable clone's ignored
`.venv` from `scripts/requirements-sync.txt`; its source is not in this repo.
Provider model settings stay separate; technical claims link to the host
documentation beside the setup steps. User-level instruction-file selection
keeps project `AGENTS.md` loading alongside Claude-specific instructions.

## T3 integration comparison

[uzairansaruzi/p3-stack](https://github.com/uzairansaruzi/p3-stack/tree/09909ebb5c0125e27fad3e57d96b81e832696d69)
— comparison revision `09909ebb5c0125e27fad3e57d96b81e832696d69`, checked
2026-10-12. Its task briefs, app monitoring, history recall, and proof boundaries
informed locally written orchestration, PR, handoff, retro, and verification
integration. No upstream prose or code imported; existing skill import baselines
and invocation choices remain unchanged. T3 API claims cite the T3 source beside
the applicable guidance rather than treating p3-stack as an API specification.
