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

## agent-login

- Local: `skills/agent-login` (SreeStack) application login workflow and private alias-based CLI.
- [openclaw/openclaw / skills/1password](https://github.com/openclaw/openclaw/tree/a229456f487f713315fc799767a97990f407bea6/skills/1password) — `SKILL.md`, `references/get-started.md`, and `references/cli-examples.md`; adaptation baseline commit `a229456f487f713315fc799767a97990f407bea6`. MIT notice in `licenses/openclaw.txt`.

One automatically discoverable skill owns application sign-in and approved
credential use. Provider access, authentication, and setup are in
`references/1password.md`; runtime provisioning and delivery/storage use
separate task references. Current CLI support is 1Password and existing local
Chromium CDP tabs. Adds user-designated vault-scoped service-account access,
optional automatic item management, and task-specific personal approval,
distinguishing behavioral scope from 1Password enforcement. Machine
administration is separate from consumer tasks. Replaces upstream
secret-printing examples with process-local reads and stdin writes. Adds shared
private environment-file provisioning for local Codex runtimes, preserving
unrelated agent variables, host-specific Touch ID diagnosis, and
provisioning-source-specific runtime checks. Omits OpenClaw install metadata,
gateway-specific IPC assumptions, and tmux/session-export workflows. API claims
link to official documentation; README.md holds purpose and setup prerequisites.

## snip-snap

- [sreejithraman/snip-snap / .agents/skills/snip-snap](https://github.com/sreejithraman/snip-snap/tree/5c1950172f8040a59f6ce4947a13223a30b3ecca/.agents/skills/snip-snap) — commit `5c1950172f8040a59f6ce4947a13223a30b3ecca`. MIT notice in `licenses/sreejithraman-snip-snap.txt`.

- Storage operations can support active work; chore selection and execution
  live in `snipsnap-do-chores`.

## snipsnap-do-chores

- Local: `skills/snipsnap-do-chores` (SreeStack). Selects saved mechanical work
  through Snip Snap and executes it with Goal Swarm.

## animate

- [emilkowalski/skills](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/animate) — `skills/animate/SKILL.md` and `RECIPES.md`; reference import commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7`. The original parent-skill import baseline remains unknown. MIT notice in `licenses/emilkowalski-animate.txt`.
- [emilkowalski/skills / skills/emil-design-eng](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/emil-design-eng) — press feedback and measured rendering guidance; content verified against commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7`, while the earlier local import baseline remains unknown.
- [emilkowalski/skills / skills/apple-design](https://github.com/emilkowalski/skills/tree/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/apple-design) — gesture-intent guidance; content verified against commit `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7`, while the earlier local import baseline remains unknown.
- [vojtaholik/good-css / skills/good-css](https://github.com/vojtaholik/good-css/tree/e074e76a011dbadc4f0a7fbd6c661ed79deb6371/skills/good-css) — CSS motion reference adaptation baseline `e074e76a011dbadc4f0a7fbd6c661ed79deb6371`; explanations and technical citations checked in upstream `PRACTICES.md`. MIT notice in `licenses/vojtaholik-good-css.txt`.
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
- `good-css/references/motion.md` opt-in movement and timing join `references/web.md`;
  typed values, shadow crossfades, and document transitions map to
  `patterns/registered-properties.md`, `card-elevation.md`, and
  `document-navigation.md`; the active indicator joins `tabs-sliding.md`.
  `show-and-hide.md` discrete dialog/popover transitions, native details, and
  clip reveals join `modal.md`, `menu-dropdown.md`, `accordion.md`, and
  `panel-reveal.md`. `scroll-and-viewport.md` edge decoration maps to
  `scroll-overflow-feedback.md`. All pattern paths are under `references/`.
  Preserves the local motion gate, timing tokens, lifecycle, interruption, and
  reduced-motion paths. Scope inherited opt-ins to components; retain usable
  static states and native event ownership. Browser versions and upstream
  measurements are omitted; target support and rendering require checks.
  Performance guarantees, fade exemptions, and unconditional no-fallback rules
  are replaced with contextual decisions. Existing invocation stays automatic.

## app-intents

- Local: `skills/app-intents` (SreeStack); shares design and retry principles.

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
- [cursor/plugins / pstack architecture and correction guidance](https://github.com/cursor/plugins/tree/dbf49813a39c1a5389c5e28cb8e4c1c2379e2454/pstack/skills) — `architect/references/design-red-flags.md` and `correct/SKILL.md`; addition baseline `dbf49813a39c1a5389c5e28cb8e4c1c2379e2454`. MIT notice in `licenses/lauren-tan-pstack.txt`.

Glossary examples use the upstream `GLOSSARY.md` / `GLOSSARY-MAP.md` names;
resolution preserves configured or existing legacy paths, keeps one glossary per
context, and creates new files lazily. Cross-skill calls use host-neutral wording.

Alternative-interface proposals use arena's shared brief, rubric, independent
candidates, and cross-judge, with orchestration's working selection and bounded
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

## correct

- [cursor/plugins / pstack/skills/correct](https://github.com/cursor/plugins/tree/dbf49813a39c1a5389c5e28cb8e4c1c2379e2454/pstack/skills/correct) — `SKILL.md`; adaptation baseline `dbf49813a39c1a5389c5e28cb8e4c1c2379e2454`. MIT notice in `licenses/lauren-tan-pstack.txt`.

Automatically discoverable in both hosts so related skills can reach it for
requested failure prevention. Uses bounded history and available session records,
counts independent occurrences, checks current exposure, and ranks live classes.
Shared design and enforcement selection use `engineering-principles`; guard proof
remains in `codebase-design`. Technical experiments use the architecture reference.
Planning and implementation honor
the requested finish line and reuse existing delivery workflows. Automatic
correction triggers, mandatory rule tables, per-class commit requirements, and
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

Browser reproductions follow host routing, including T3 collaborative-preview
selection and recovery, before standalone drivers.

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

## engineering-principles

- [cursor/plugins / pstack principle skills](https://github.com/cursor/plugins/tree/850d7f2e9f5e55dff7eb00a0a479337fe79eb22f/pstack/skills) — all 24 `principle-*/SKILL.md` files; adaptation baseline `850d7f2e9f5e55dff7eb00a0a479337fe79eb22f`. MIT notice in `licenses/lauren-tan-pstack.txt`.
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
The domain principle covers explicit lifecycle states, accepted events, derived
flags, effect ownership, stale completions, and conditional statechart adoption.
Product requirements remain the independent source for behavior checks.
The stateful-behavior practice is self-contained, with guards and a submission
example; external source URLs stay in this provenance record.

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

## goal-swarm

- Local: `skills/goal-swarm` (SreeStack). Host goal state remains separate from
  T3 delegated tasks and schedules.
- [cursor/plugins / pstack/skills/swarm](https://github.com/cursor/plugins/tree/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack/skills/swarm) — commit `ecc249f1e306fc64ddf83c7bed16cacf7c2239db`. MIT notice in `licenses/lauren-tan-pstack.txt`.

Locally written goal lifecycle that chooses solo or parallel execution within
an explicitly requested parent goal. It uses pstack's up-front split and
selection rule, gives child goals to agents with independent outcomes, and
leaves agent routing and result integration to `orchestration`. A PR finish
line routes through `pr`; pstack's cloud and model defaults are excluded.

## gh-stack

- [github/gh-stack / skills/gh-stack](https://github.com/github/gh-stack/tree/d4ab7ab47e5b3e3708a27c8c42abcdf4bc321419/skills/gh-stack) — commit `d4ab7ab47e5b3e3708a27c8c42abcdf4bc321419`.

Invocation remains unchanged. Checks installed-extension capabilities before
newer worktree behavior. Conflict staging follows the diagnostic owner, and
sync rollback guidance preserves partial-restoration recovery state instead of
promising unconditional rollback.

Scoped PR layers follow `pr`’s T3 thread-registration rules; CLI publication
does not substitute for app registration.

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

T3 history supplies scoped evidence and task receipts; the portable note retains
thread/task identity, ownership, and live-work state. Invocation stays manual-only.

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
code, glossary, ADRs, and code-why. Codebase Design supplies vocabulary and
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
prefers T3’s Device panel and returned driver/session flags where available;
Xcode MCP and platform CLIs supply build/log operations or host-supported fallback. Terminal and service checks use process or PTY driving, bounded
completion, public protocols, and fresh persisted-output reads. Harness selection
follows host routing, including T3 preview opening and actionable-error recovery,
and public user paths, including CLI-driven UIs. Keeps
bounded reproduction attempts, failed-attempt evidence, authorization, isolation,
redaction, run-owned cleanup, and separate documentation and product verdicts.
Authenticated workflows reuse designated test accounts and standing scope,
delegate application sign-in and command/API credential use to `agent-login`,
check delivery in the actual host interface, and
distinguish provider authentication, automatic login, and post-login verification.
Routes inspectable results to `showroom` for demonstrations and access while
retaining acceptance selection and judgments.
Provider mechanics stay in agent-login’s references; maps link the authoritative
approved mapping and record delivery setup.

Readiness requires usable workflow state after initialization, migrations, and
fixtures. Setup/first-run recipes prove isolated empty-data launch; ordinary checks
can reuse known state. Substitute environments leave target-specific setup
unverified. Missing fixtures retain assertions with local failed/blocked verdicts,
rather than requiring every missing precondition to be a product failure.

Edge-data workflow and catalog map to `references/edge-data.md`, with mobile
assertions in `references/web.md`. Comparison controls are optional, fixtures
are type-correct and task-scoped, existing authorization governs fixes, and
retention is proportional. Missing schema limits are distinguished from verified
unbounded input. Emulation and unavailable hardware checks carry explicit
evidence limits. Greetings and attribution instructions are omitted.
Stateful acceptance selects relevant event sequences and proves visible outcomes
and external effects through public entry points, beyond transition tests alone.


## repo-cleanup

- Local source: `~/.agents/skills/post-merge-cleanup`; upstream origin unrecorded.

Accepts merge completion handoffs from `merge`. Cleanup includes verified
task-owned simulator/emulator installs and disposable test data while preserving
shared installs, retained data, and resources needed by unmerged stack layers.

## no-comments

- [cursor/plugins / pstack](https://github.com/cursor/plugins/tree/5108b719a7aa484ef1a9781f587c7bbeac793f92/pstack) — `skills/no-comments/SKILL.md` and `agents/comment-sicko.md`; import baseline `5108b719a7aa484ef1a9781f587c7bbeac793f92`, imported 2026-10-13. MIT notice in `licenses/lauren-tan-pstack.txt`.

Preserves manual-only invocation in both hosts, independent comment auditing,
the keep exceptions, suppression/root-cause checks, bounded audit rerun, scoped
repairs, and constraint encoding. Audit rules live in
`references/comment-audit.md`; the auditor is read-only and the parent owns edits.
T3 orchestration and local review, history, and design skills replace upstream
agent types and slash commands. Persona, mandatory architect gate, and separate
encoding approval are omitted; existing task authorization governs repairs.
Unresolved constraints and suppressions remain until their evidence or repair
is settled. Encoding must catch a violation before its comment is removed.
Intentional negative-test assertions remain distinct from application suppressions.

## merge

- Local: `skills/merge` (SreeStack).

PR workflow references and T3 thread registration use the local `pr` entry point.


## prototype

- [mattpocock/skills / skills/engineering/prototype](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/prototype) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

UI prototypes for web, mobile, and desktop; no logic-prototype mode. The local
workflow chooses enough distinct options to expose the decision, coordinates
with `ui-design`, `animate`, `swiftui` or `uikit`, `verify`, and
`showroom`, and adds explicit rules for live side effects, unavailable target
tooling, comparison-control verification, durable decisions, and proportional
prototype retention and cleanup.
Showroom chooses demonstrations and access for the prototype result.

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

Research owns a cited primary-source note. Independent background reading uses
orchestration’s working defaults; assigned researchers execute directly, with
further delegation limited by their brief. Parents check evidence before acceptance.

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
Explicit assignments select criteria while retaining full-scope reading;
standalone assessment defaults to all criteria. Later-round briefs include
prior findings and dispositions for independent reassessment.
Standards and Spec keep separate labeled reports, their upstream review bars,
and 400-word limits. Thermo and Ponytail apply within the supplied scope;
structural suggestions require evidence and a concrete benefit. Ponytail omits
persistent modes, installation, benchmark displays, and whole-repo debt ledgers.
Indirect-consumer checks use `change-safety`; React or Next assessments use
`react-best-practices` and current changed-scope React Doctor diagnostics.

## review-fix-loop

- Local: `skills/review-fix-loop` (SreeStack). T3-owned review rounds coordinate
  primary Spec/Standards and randomly assigned Ponytail/Thermo assessments,
  priority-tier alternate selection and replacement, shared model policy,
  stable snapshots, and Review Sweep.

## pr

- Local: `skills/pr` (SreeStack).
- [cursor/plugins / pstack PR feedback pagination fix](https://github.com/cursor/plugins/tree/dbf49813a39c1a5389c5e28cb8e4c1c2379e2454/pstack/skills/poteto-mode/scripts/watch-pr) — pagination/completeness requirement adapted from `github.ts`; addition baseline `dbf49813a39c1a5389c5e28cb8e4c1c2379e2454`. No watcher code imported. MIT notice in `licenses/lauren-tan-pstack.txt`.
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
Evidence reuses Showroom's checked demonstrations and access links when available.

T3 PR registration is shared by all PR routes and reused by stack/merge entrypoints.
CI waiting uses app watches and fresh state after waking; GitHub confirms merge
completion. Drafting alone remains local.
Feedback collection exhausts relevant pages and treats incomplete collection as
unproven readiness. App watching and existing forge/tool selection remain unchanged.

## review-sweep

- Local: `skills/review-sweep` (SreeStack). Findings retain assignment/model
  provenance; accepted fixes use orchestration's implementation selection.

## setup-sreestack

- [mattpocock/skills / skills/engineering/setup-matt-pocock-skills](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/setup-matt-pocock-skills) — prerelease-main import baseline `d81f3a183412e71a5b1e84ca21bc1a35eea03a60` (the skill folder matches v1.3.1).

Manual-only in both hosts. The local name and UI are SreeStack Setup. One setup
workflow owns project-specific conventions and pointers, with scoped update,
glossary migration, optional ticket/triage configuration, and explicitly
requested verification-map setup through `verify`. Project workflow guidance
uses current local review, PR, stack, merge, acceptance, and delegation owners;
host settings and installation remain separate. Agent defaults link the shared
orchestration policy rather than duplicating host rank settings. Existing commands and standards
are linked rather than duplicated. Active instruction files are selected by the
user/host or existing pointer ownership, with `AGENTS.md` for a new default.
Project workflow pointers call `showroom` for inspectable results and useful
UI iteration feedback; demonstration and access procedures remain in that skill.

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

- Local: `skills/showroom` (SreeStack). Owns demonstrations and access for
  inspectable results, with model-selected formats and delivery paths.

## tdd

- [mattpocock/skills / skills/engineering/tdd](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/tdd) — v1.2.3, commit `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.

Automatic discovery includes feature and bug work, but not ordinary
integration-test additions by themselves. Seams established by the spec or
project conventions count as pre-agreed; user confirmation is reserved for
material unresolved choices.
The review stage uses `review-fix-loop`.
Shared behavior-test guidance uses `engineering-principles`; seam selection,
vertical red/green cycles, specialist examples, mocking, and local pitfalls stay here.
The event-sequence example checks duplicate submission and failure/retry through
a public API, inspecting payloads only at the external persistence boundary.
Cancellation and late-completion scenarios remain conditional on the contract.

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

- Local: `skills/web-component-inspiration` (SreeStack); web-scoped and
  explicit-only in both hosts, with Showroom owning demonstrations and access.

## wayfinder

- [mattpocock/skills / skills/engineering/wayfinder](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60/skills/engineering/wayfinder) — v1.2.3, commit `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.

Uses supplied or configured tracker information, with the existing local-file
fallback. Cross-skill calls are host-neutral and the prototype route remains
UI-only.

Research assignments use shared orchestration defaults and disjoint note paths
in the parent checkout. The parent accepts findings and resolves tickets; separate
research branches require explicitly requested, workspace-bound ordinary threads.
Manual invocation and the one-decision-per-session rule remain unchanged.

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

Locally written T3-oriented delegation flow with one editable Markdown table
of model defaults in the routing reference. Alternate priorities prefer exact
free OpenCode DeepSeek and GLM routes before Gemini and primary-model fallback.
Assignment briefs replace a generic
agent-rank taxonomy; discovery resolves working defaults before direct work,
and the main procedure owns the direct-work match/delegate gate.
Live host instructions own API/transport details and routing
owns local concurrency and bounded recovery.
Assignment, runtime selection, and acceptance remain distinct. Native children
are used when they support the exact selection; T3 owns cross-provider tasks
and review rounds. Parallel coverage, competing approaches, revision-bound
verification, and measured results are checked during integration. It does not
create goals or require pstack's cloud worker setup. `pr` owns review when it
will review the same integrated scope before publication.
Integrated results the user can inspect or try route to `showroom` for
demonstrations and access, reusing applicable verification evidence.

The task-graph reference preserves existing integration, review, PR and cleanup
owners. Delegated workers can share the integration checkout with disjoint
ownership or use host-managed isolated worktrees; separate ordinary threads
remain explicit. Isolated workers receive relevant uncommitted inputs explicitly
and report their starting revision. Workspaces
preserve unexpected edits; dependency outcomes require integration and verification. Scheduling does not create a goal or assume a
worker's last merge guarantees a fast-forward.
Design and implementation work selects useful `engineering-principles` references
and includes them in implementation briefs. Review prompts retain their source
wording and criteria. Principles do not replace runtime selection, assignment,
or acceptance.


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

T3 session sources prefer scoped app history; other hosts retain local-log
inspection. Historical claims are checked against current artifacts.
Repository-wide recurring failure prevention belongs to `correct`; retro reports
the session evidence and routes further investigation only within the user's scope.


## T3 integration comparison

[uzairansaruzi/p3-stack](https://github.com/uzairansaruzi/p3-stack/tree/09909ebb5c0125e27fad3e57d96b81e832696d69)
— comparison revision `09909ebb5c0125e27fad3e57d96b81e832696d69`, checked
2026-10-12. Its task briefs, app monitoring, history recall, and proof boundaries
informed locally written orchestration, PR, handoff, retro, and verification
integration. No upstream prose or code imported; existing skill import baselines
and invocation choices remain unchanged. T3 API claims cite the T3 source beside
the applicable guidance rather than treating p3-stack as an API specification.
