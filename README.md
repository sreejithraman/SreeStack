# SreeStack

A collection of agent skills for planning, coding, review, research, and UI work,
with T3 Code orchestration and optional shared Codex host defaults.
It includes original workflows and adapted skills from the projects credited below.
Browse [skills/](skills/) and see [SOURCES.md](SOURCES.md) for upstream origins
and local differences to preserve during updates.

## Use

Clone the repo, then link the skills you want into your agent’s skill directory.
For a host that reads `~/.agents/skills`:

```bash
git clone https://github.com/sreejithraman/SreeStack.git
cd SreeStack
mkdir -p ~/.agents/skills
ln -s "$PWD/skills/tdd" ~/.agents/skills/tdd
```

Repeat the last command for other skills. If that destination already exists,
keep it or move it aside before linking. To uninstall, remove only the symlink
you created. Pull changes in this clone to update linked skills.

Read each skill before use. Delegation and review target T3 Code's orchestration
MCP tools and its configured provider runtimes. Other workflows may need goal
state tools, GitHub CLI, optional Tailscale sharing, or Apple development tools. Linking skills
does not install provider executables, authenticate accounts, or enable models.

### How the skills fit together

T3 supplies the live model catalog, child-task lifecycle, thread history, PR
notifications, and collaborative browser and device controls. SreeStack supplies
model defaults, bounded assignments, review criteria, acceptance checks, and
handoff artifacts. Skills use those app capabilities through the host's current
instructions rather than maintaining another API manual.

| Task | Owner |
| --- | --- |
| Clarify requirements or architecture | `grilling`, `domain-modeling`, `codebase-design`; optional manual planning commands |
| Form or improve a task brief | `reframe`, requested directly or used by Goal Swarm for goal formation |
| Choose engineering approaches | `engineering-principles`; workflows retain their procedures and checks |
| Compare independent candidates and synthesize a result | `arena` |
| Understand current code, historical decisions, or change risks | `how`, `why`, and `blast-radius`, respectively |
| Design a consequential change and guide its implementation | `architect`, using `codebase-design`, `arena`, and experiments |
| Prevent recurring code mistakes | `correct`, using shared design principles and historical proof |
| Implement or diagnose | The relevant platform/domain skill, using orchestration's working model |
| Delegate independent work | `orchestration`; `research` owns cited investigations |
| Prove behavior | `verify` |
| Run complexity, duplication, or mutation tools | `code-quality` |
| Show results and make them available to try | `showroom` chooses demonstrations and access |
| Sign in or use approved authentication credentials | `agent-login`; provider mechanics live in its references |
| Review and repair | `review-fix-loop` coordinates, `review` assesses, `review-sweep` settles and fixes |
| Publish and monitor | `pr`; `gh-stack` manages dependent layers |
| Land and clean up | `merge`, then `repo-cleanup` |
| Transfer context or improve the environment | Explicit `handoff` or `retro` |

Use only the skills triggered by the task. A small change needs no global mode,
mandatory design panel, or planning registry. Specialists retain their current
invocation choices; setup, planning commands, handoff, and retrospective remain
explicit where configured. Ordinary work creates no goals, schedules, or new
conversations. Explicit goal or swarm requests use `goal-swarm`; native goal
tracking is optional and follows the host's instructions.

[Reframe](skills/reframe/SKILL.md) forms goals from the user's request and
context as Goal Swarm's normal starting step. It scales to what is unsettled:
a precise request may need only a concise confirmation. Goal Swarm reuses the
settled brief through execution and revisits it when evidence or user direction
changes. Material scope or tradeoff changes need authorization; routine framing
adds no approval checkpoint.

You can also invoke `$reframe` in Codex or `/reframe` in Claude Code directly.
For example, “Reframe our upload errors around helping users recover, preserving
existing upload behavior” returns a brief with methods and suitable evaluation.
It needs the task context and relevant evidence; investigation may need the
project's tools. Reframing alone ends with the brief. When Goal Swarm calls it,
Reframe returns the brief to that owner, which continues execution.

[Goal Swarm](skills/goal-swarm/SKILL.md) pursues a clear outcome and preserves
required constraints, working solo or through bounded worker tasks. Evaluation
starts with what should improve, what must hold, and how the result will be judged;
checks grow with the risks discovered. Qualitative work uses criteria and
judgment. It asks for unresolved preferences or tradeoffs that materially change
the result. For example, “Use Goal Swarm to reduce search p95 to 200 ms while
preserving results and existing resource limits” keeps a correct 300 ms result
as progress and continues toward 200 ms. It completes at the requested finish
line; user approval is needed when that finish line requires it. Native goal
tracking is used when explicitly requested and supported. Unattended continuation
needs host runtime support; a prompt alone does not supply wakeups.

[Engineering Principles](skills/engineering-principles/SKILL.md) is automatically
discoverable. Its task-based index links to 24 reference files, one per principle,
for data and interface design, simplification, state and migration, evidence,
and execution. Orchestration
and specialist workflows point to useful guidance for design and implementation.
Review prompts retain their wording and criteria. The principles guide choices;
the workflow owns its steps and completion criteria. For example, “Design this
retryable import and explain how
it handles a crash halfway through” reaches state ownership, idempotency, and
failure-proof guidance while the implementation workflow supplies the checks.
“Attack the premise” selects the named principle when repeated fixes fail.

For example, “Build a cancellable upload with retry” reaches explicit states,
allowed events, and effect ownership through Model the Domain. TDD checks
relevant event sequences at the public seam; Verify exercises the affected
product entry points and checks that stale completion cannot replace the
current operation's result. Simple state can stay simple.

### T3 Code orchestration and model defaults

[Orchestration](skills/orchestration/SKILL.md) assigns work and resolves models
from T3's live catalog. Edit
[model-defaults table](skills/orchestration/references/agent-routing.md#model-defaults)
to change working/research/review models, source-retrieval routes, effort, and
additional-review pools.
The local concurrency ceiling is in that same reference. This is the one source
for skill model defaults; explicit user/project requirements are resolved by
[agent routing](skills/orchestration/references/agent-routing.md).

Enable and authenticate the providers named in that table in T3 Code. Routing
resolves their exact instance/model IDs and supported options from the live
catalog; an ambiguous match needs an explicit selection. Gemini's effort selection
is encoded in its model ID, while other providers may expose an option. Catalog availability does
not establish quota or successful access. T3's injected MCP tools or supported
ACP bridge must be reachable from the agent. OpenCode and Gemini reviewers read
their review references from this stack; provider plugins are not needed.

[Review](skills/review/SKILL.md) assesses a snapshot without fixes.
[Review Sweep](skills/review-sweep/SKILL.md) validates findings and implements
accepted fixes with the working model selection.
[Review Fix Loop](skills/review-fix-loop/SKILL.md) owns review coverage, reviewer
selection, harness review, optional skips, and fix rounds. It uses Orchestration's
model table and delegation rules. Enable the OpenCode Go subscription routes
named in that table for its OpenCode pool.
Substantial changes also receive a required adversarial assessment that tests
assumptions and failure paths. The loop records its coverage decision from the
change's behavior and consequences.

When migrating an installed setup, remove only the links and rank presets you
previously installed for the retired Gemini/OpenCode skills and Codex ranks;
keep unrelated provider settings and custom agents. These repository edits do
not update live skill folders or host configuration. Keep installed skill links
on a stable clone rather than a temporary worktree.

Sample requests and expected results:

- “Research these official docs”: the General research selection handles reading,
  comparison, and synthesis.
- “Research this YouTube video and X post”: `research` routes retrieval to Gemini
  and Grok respectively, then checks the source evidence before writing a cited note.
- “Implement this change”: the working policy supplies the model and options;
  parallel children have disjoint ownership in the same checkout.
- “Review and fix this shared-contract change”: primary, Ponytail, Thermo, and
  adversarial assessments and optional pool reviewers cover the same snapshot;
  accepted fixes use the working model.
- “Review this small fix”: one required primary assessment plus optional pool
  reviewers when full-review risk/contract triggers do not apply. An ordinary
  prose or wording-only edit with no procedure change uses parent review.
- When an additional reviewer is unavailable or fails, the loop records a skip
  and continues. Missing required coverage cannot produce a clean result.
- A substantive fix triggers a fresh round against the original base. A changed
  snapshot supersedes in-flight review; successful dispatch alone is not a pass.
- Ordinary delegation does not create goals or recurring schedules. Explicit
  goal or swarm work can use ordinary tasks; requested native tracking follows
  the host's available capabilities.

`pr` writes titles/bodies or brings a single PR to readiness; `merge` lands ready PRs or stacks and
finishes resolved GitHub issues through GitHub CLI. `merge` uses `gh-stack` for
stacks and `repo-cleanup` for completed task resources, including Mac development
apps, simulator/emulator test installs, and task-created temporary devices when
platform tooling is available.
`handoff` is manual-only: invoke it explicitly and supply the handoff note path
when resuming in a new session. A plain resume request does not load that skill.
`snip-snap` requires the `snipsnap` command on `PATH`; check `snipsnap --help`
for the commands you need.
Installing or copying only the GUI app does not expose the CLI automatically.
A Snip Snap Homebrew cask release that declares the bundled `snipsnap` binary does.

Use [Snipsnap Do Chores](skills/snipsnap-do-chores/SKILL.md) with "snipsnap do
chores" to tackle saved mechanical improvements through Snip Snap and Goal
Swarm. It leaves features and product decisions open and works without native
goal-state tools.

The [retro skill](skills/retro/SKILL.md) reviews a coding session for improvements
to the agent environment. Invoke it explicitly; it returns recommendations.
The [correct skill](skills/correct/SKILL.md) investigates repeated agent mistakes
in a repository and connects each live failure class to a structural repair or
enforceable guard. It supports planning and authorized implementation and stays
automatically discoverable. For example, “Find the mistakes agents keep repeating
in this repo and give me a prevention plan” returns cited occurrences, priorities,
repair choices, experiment results, and a migration and verification plan.

[Improve Codebase Architecture](skills/improve-codebase-architecture/SKILL.md)
remains manual-only. Its default is interactive candidate selection. For example,
“Use `$improve-codebase-architecture` to investigate autonomously and return a
plan backed by runnable experiments” returns checked design recommendations and
a migration plan. Technical experiments cover interfaces, callers, state, and
performance; [prototype](skills/prototype/SKILL.md) owns UI experiments. Both
planning workflows keep production implementation for the requested finish line.

[How](skills/how/SKILL.md), [Why](skills/why/SKILL.md), and
[Blast Radius](skills/blast-radius/SKILL.md) answer three different questions:
how the system works now, what decisions produced its shape, and what a proposed
change could break elsewhere. All three support automatic discovery and direct
invocation. For example, “How does our import retry flow work?” returns a traced
explanation with key code locations and gaps; historical motivation and proposed
redesign stay with their own workflows. How needs repository access; optional
runtime checks need the project's tools, and historical investigations may need
access to linked records.

If you linked `code-why` or `change-safety` from an earlier version, replace those
skill symlinks with `why` and `blast-radius` after updating your clone.

[Arena](skills/arena/SKILL.md) produces independent candidates for one task,
compares them against a shared rubric, and returns a recommendation or one
verified synthesis. For example, “Arena three approaches to our import pipeline;
compare caller simplicity, retry correctness, and migration cost” returns the
candidates, evidence, and chosen base, with any useful ideas adapted from the
other candidates when synthesis is requested.

[Architect](skills/architect/SKILL.md) carries a consequential design from
caller usage and competing type sketches through the requested finish line.
For example, “Architect a retryable importer and implement it; preserve existing
callers and prove recovery after interruption” returns the design rationale,
experiment evidence, and verified implementation. “Architect the importer,
design only” returns the checked design. Both skills support automatic discovery
and direct invocation. `prototype` keeps UI experiments on the target platform;
technical experiments test behavior and caller assumptions. Existing review
and verification skills assess the integrated result.

The [gauntlet-loop skill](skills/gauntlet-loop/SKILL.md) is also user-invoked:
use `$gauntlet-loop` in Codex or `/gauntlet-loop` in Claude Code with a goal and
optionally a specific reference. It returns a prompt for a builder-and-critic
loop. Writing the prompt needs no extra tools; running it needs independent
agents and access to the reference and generated output.
Domain skills use `GLOSSARY.md` for new layouts and preserve configured or
existing legacy `CONTEXT.md` glossary paths.

[Show, Don't Tell](skills/show-dont-tell/SKILL.md) is automatically discoverable
for code and documentation clarity passes and callable from other skills. Invoke
`$show-dont-tell` in Codex or `/show-dont-tell` in Claude Code with files or a
diff to reduce the explanations and reminders they need. It favors self-documenting
code, one home for each rule, and ADRs for consequential decisions. Documentation
earns its place by supplying necessary knowledge agents cannot cheaply and reliably
obtain elsewhere; legal notices remain protected. PR preparation invokes it
before the existing review; merge checks that current review includes the pass.

[SreeStack setup](skills/setup-sreestack/SKILL.md) is the manual
`setup-sreestack` entry point for project workflow conventions, glossary/ADR
paths, a verification foundation, and optional issue tracking and triage labels.
Full setup creates or reuses `docs/agents/verification/index.md`, or an equivalent
established location, records known setup facts and coverage gaps, and adds an
agent-instruction pointer. It links the project's existing checks and review
and PR conventions to the shared skills. Feature
recipes and live verification use `verify` when requested. Invoke setup with
“migrate glossary” to move existing domain `CONTEXT.md` / `CONTEXT-MAP.md` files
to `GLOSSARY.md` / `GLOSSARY-MAP.md` and update their consumers without repeating
other setup.

### Product verification

[verify](skills/verify/SKILL.md) tests real user workflows using a temporary plan
when no verification map exists. Once a map is set up, verification uses and
maintains its affected recipes. Maps use `docs/agents/verification/index.md`,
or an equivalent established location, and may start with shared facts alone.
Ask to set up verification to add and prove feature recipes; `features/` is
created with the first recipe. Commit the map in the product repo. The shared
skill supplies the procedure, so projects need no generated verification skill.
You can also request map maintenance or verification without updating docs.
For ambitious targets, consequential changes, or candidate comparisons, Verify
starts with the desired outcome, relevant constraints, and suitable evaluation
in the existing brief or task plan. Checks grow with discovered risks; detailed
comparison records are needed where a claim depends on them. Qualitative work
uses criteria and judgment. Product repositories supply the actual harnesses
and enforced delivery checks for runtime claims.
Authenticated checks reuse designated test accounts and their existing access
setup. Verify checks credential access and secure delivery before login, and
reports automatic login separately from checks performed after user sign-in.
Linking this skill does not install the product's browser, device, or terminal
harness.

[iOS verification](skills/verify/references/ios.md) covers interactive device
checks and repeatable regression suites. It preserves host device routing and
existing project harnesses, and prefers XCTest with XCUIAutomation for new iOS
UI workflow tests. New Swift unit tests use Swift Testing; performance tests use
XCTest. Project recipes link executable tests and their assertions; Verify judges
coverage and evidence, including checks outside the suite.

For example, “Model-check this retry race” uses Verify's
[formal-verification guidance](skills/verify/references/formal-verification.md)
to select a tool, tie the model to current code, challenge the property with a
broken variant, and explain counterexamples. “Refresh our model after this
refactor” checks drift from its last synchronized revision. These requests need
the project's verifier or an installable suitable tool; unavailable proof stays
blocked. The guidance adds no bundled model checker or statechart renderer.
Product acceptance still exercises the real workflow.

[showroom](skills/showroom/SKILL.md) helps you experience and judge results,
including during iteration. It chooses formats based on the work and available
tools: screenshots, collages, video, preview links, device installs, runnable
examples, or accessible files. It can combine demonstrations with hands-on
access and reuse current verification evidence. Website handoffs include a
checked PR preview or Tailscale URL when available.

Showroom is automatically discoverable. The shared completion instructions and
Orchestration call it for results you can inspect or try; project setup includes
the corresponding handoff pointer. The repository edits do not update installed
skills or live host instructions. Apply them through your stable clone and the
host setup below to activate those routes.

### Code quality tools

[Code Quality](skills/code-quality/SKILL.md) runs Crapper, Dryer, and Mutator and
returns their reports. Invoke it with `$code-quality` in Codex or `/code-quality`
in Claude Code. [Setup](skills/code-quality/references/setup.md) lives with the skill.

### Store screenshot design

The [koubou skill](skills/koubou/SKILL.md) designs and iterates on App Store
screenshots from real app captures. It includes style intake, narrative and
copy planning, device geometry, HTML/CSS composition, and visual verification.
Follow its [setup guide](skills/koubou/references/setup.md) for the CLI and HTML
renderer. App capture follows the project's run scripts and the host's device tooling.

### Agent login

The [agent-login skill](skills/agent-login/SKILL.md) owns application sign-in,
approved credential access, and private delivery. It stays automatically
discoverable; `verify` owns the product checks that follow. Its bundled command
supports 1Password credentials and existing local Chromium CDP tabs.

Follow [command setup](skills/agent-login/references/cli-setup.md) for installation,
private account mappings, provider prerequisites, and development checks.
[Account setup](skills/agent-login/references/setup.md) covers onboarding and
login readiness; [runtime provisioning](skills/agent-login/references/runtime-provisioning.md)
covers private environment files and host-specific access checks.

## Optional Codex host defaults

The files under [codex/](codex/) provide parent-session settings and shared host
instructions. They are separate from orchestration's delegated model policy.
Keeping them here does not change live Codex configuration. Keep the full
personal config local; it may contain machine paths, trusted projects, and
integration settings.

| Source | Destination | How to apply |
|---|---|---|
| [config.toml](codex/config.toml) | `~/.codex/config.toml` | Merge parent settings and the native concurrency ceiling |
| [global-instructions.md](codex/global-instructions.md) | `~/.codex/AGENTS.md` | Merge these shared instructions |
| [optional-instructions.md](codex/optional-instructions.md) | `~/.codex/AGENTS.md` | Merge only sections you want to enable |
| [optional.rules](codex/optional.rules) | `~/.codex/rules/default.rules` | Replace its path placeholder and merge selected rules |

Back up local files, preserve unrelated values/instructions, and check that
TOML parses after merging. If `~/.codex/AGENTS.override.md` exists, it takes
precedence over `AGENTS.md`; update the active file. Native child execution
uses explicit policy settings rather than named rank presets. Start a new task
after changing host settings and check its effective selection; active tasks
may retain earlier settings.

Local research notes under `docs/research/` are ignored by Git. Keep maintained
technical citations beside their guidance. Host setup follows OpenAI's
[config precedence](https://learn.chatgpt.com/docs/config-file/config-basic) and
[global instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

## Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for changes and checks, and
[AGENTS.md](AGENTS.md) for agent instructions.

## License

SreeStack’s original work uses the [MIT License](LICENSE).
Imported material keeps its own terms; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
Report security issues through the [private reporting channel](SECURITY.md).

## Credits and thanks

Thank you to the authors and contributors who shared the skills this collection
uses and adapts:

- [David Collado / Koubou](https://github.com/bitomule/Koubou) — App Store screenshot design workflow and supporting references.
- [Matt Pocock](https://github.com/mattpocock/skills) — engineering and productivity skills, including the Standards and Spec review rules.
- John Ousterhout — deep-module and design-it-twice concepts used in Codebase Design.
- David Khourshid — state-machine modeling and UI-independent logic informing Engineering Principles; no upstream prose or code copied.
- [Felix Rieseberg](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/) and [Ray Amjad](https://www.youtube.com/watch?v=RbfQayMNtJc) — outcome, depth, range, and verification ideas informing Reframe and goal execution; instructions are independently written.
- [Jay E / RoboNuggets](https://github.com/robonuggets/gauntlet-loop) — the adapted `gauntlet-loop` prompt-writing skill (CC BY 4.0), based on [Matt Shumer's technique](https://github.com/mshumer/Claude-of-Duty/blob/main/prompt.md). Local adaptations are recorded in [SOURCES.md](SOURCES.md#gauntlet-loop).
- [HumanLayer / Dex Horthy](https://github.com/humanlayer/skills) — visual explanation guidance credited by Matt Pocock's PR skill.
- [Emil Kowalski](https://github.com/emilkowalski/skills) — animation, motion and gesture behavior, typography and materials, interface access/input, and interface-review guidance.
- [Jakub Antalík’s transitions.dev](https://github.com/Jakubantalik/transitions.dev) — motion pattern references and tuning guidance used by `animate`.
- [Dietrich Gebert’s Ponytail](https://github.com/DietrichGebert/ponytail) — simplicity and code review rules.
- [Vox](https://x.com/Voxyz_ai/status/2115518965443076573) — review-noise ideas informing the shared bug-evidence and settlement rules; no upstream prose copied.
- [Cursor](https://github.com/cursor/plugins) — the Thermo Nuclear Code Quality Review.
- [OpenAI’s Codex plugin](https://github.com/openai/codex-plugin-cc) — adversarial review criteria.
- [OpenCode](https://github.com/anomalyco/opencode) — general review criteria used by OpenCode reviewers.
- [Gemini CLI’s code-review extension](https://github.com/gemini-cli-extensions/code-review) — review criteria used by Gemini reviewers.
- [Lauren Tan’s pstack](https://github.com/cursor/plugins/tree/main/pstack) — `arena`, `architect`, `how`, `show-dont-tell`, `correct`, `engineering-principles`, and ideas for `verify`, `blast-radius`, `why`, `codebase-design`, `diagnosing-bugs`, `pr`, `handoff`, `goal-swarm`, and `orchestration`.
- [Robert C. Martin’s ub-mode](https://github.com/unclebob/ub-mode) — simplicity, behavior verification, and assumption-checking ideas informing the shared global instructions; no upstream prose or code copied.
- [Robert C. Martin’s Crapper](https://github.com/unclebob/crapper), [Dryer](https://github.com/unclebob/dryer), and [Mutator](https://github.com/unclebob/mutator) — external tools used by `code-quality`.
- [Uzair Ansar’s p3-stack](https://github.com/uzairansaruzi/p3-stack) — T3 workflow comparison informing app/runtime boundaries, PR monitoring, and continuity; no upstream prose or code copied.
- [t3dotgg’s tstack](https://github.com/t3dotgg/tstack) — PR babysitting workflow comparison informing watcher ownership and handoff; no upstream prose or code copied.
- [Anthropic’s skills](https://github.com/anthropics/skills) — art-direction guidance used by `ui-design`.
- [Anthropic’s Claude Plugins Community](https://github.com/anthropics/claude-plugins-community) — the `eli5` skill.
- [GitHub’s gh-stack](https://github.com/github/gh-stack) — the stacked PR skill.
- [s0xDk](https://github.com/s0xDk/refactoring-ui-skill) — web-system guidance used by `ui-design`, based on Adam Wathan and Steve Schoger’s work.
- [Vojta Holik / good-css](https://github.com/vojtaholik/good-css) — modern CSS layout, content, interaction, and motion recipes adapted into `ui-design` and `animate`.
- [React Doctor](https://github.com/millionco/react-doctor) — the React diagnostics skill.
- [Vercel’s agent-skills](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices) — the React Best Practices skill, originally created by [Shu Ding](https://x.com/shuding).
- [Charles Wiltgen’s Axiom haptics guide](https://github.com/CharlesWiltgen/Axiom/blob/dd3334734ecd01afab28b0ac22c49d4b5b2e5857/.claude-plugin/plugins/axiom/skills/axiom-media/skills/haptics.md) — inspiration for our locally written iOS haptics skill; no upstream prose or code copied.
- [Rudrank Riyam’s App Store Connect CLI skills](https://github.com/rorkai/app-store-connect-cli-skills) — usage and workflow guides for our App Store Connect skill.
- [superagents-lab’s xcode27-skills](https://github.com/superagents-lab/xcode27-skills) — coverage input for independently written Xcode security and SwiftUI SDK 27 guidance; no upstream prose or code copied.
- [Snip Snap](https://github.com/sreejithraman/snip-snap) — the snip-snap skill and its CLI workflow.
- [OpenClaw](https://github.com/openclaw/openclaw/tree/main/skills/1password) — CLI authentication and secret-handling guidance adapted for agent-login’s 1Password references.

[SOURCES.md](SOURCES.md) records upstream paths, import revisions, and current
differences to preserve. Git records how the skills changed over time.
