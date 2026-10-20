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
| Choose engineering approaches | `engineering-principles`; workflows retain their procedures and checks |
| Compare independent candidates and synthesize a result | `arena` |
| Design a consequential change and guide its implementation | `architect`, using `codebase-design`, `arena`, and experiments |
| Prevent recurring code mistakes | `correct`, using shared design principles and historical proof |
| Implement or diagnose | The relevant platform/domain skill, using orchestration's working model |
| Delegate independent work | `orchestration`; `research` owns cited investigations |
| Prove behavior | `verify` |
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
conversations. Explicit goal-backed work uses `goal-swarm` and the host's goal tools.

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
to change implementation/review models, effort, and alternate-review priorities.
The local concurrency ceiling is in that same reference. This is the one source
for skill model defaults; explicit user/project requirements are resolved by
[agent routing](skills/orchestration/references/agent-routing.md).

Enable and authenticate the providers named in that table in T3 Code. Routing
resolves their exact instance/model IDs and supported options from the live
catalog; an ambiguous match needs an explicit selection. Gemini's high selection
is encoded in its model ID, while other providers may expose an option. Catalog availability does
not establish quota or successful access. T3's injected MCP tools or supported
ACP bridge must be reachable from the agent. Provider-specific review plugins
and standalone headless execution skills are not needed for this shared review
procedure.

Alternate reviews prefer the free OpenCode DeepSeek and GLM routes in the table,
then Gemini, then fresh primary-model tasks for any remaining review lenses.

[Review](skills/review/SKILL.md) assesses a snapshot without fixes.
[Review Sweep](skills/review-sweep/SKILL.md) validates findings and implements
accepted fixes with the working model selection.
[Review Fix Loop](skills/review-fix-loop/SKILL.md) coordinates primary Spec +
Standards assessment and, for a full round, randomly assigned Ponytail and
Thermo reviews from the alternate pool. It retains the mapping through fix
rounds, uses fresh T3 children, and reports any lost model diversity.

When migrating an installed setup, remove only the links and rank presets you
previously installed for the retired Gemini/OpenCode skills and Codex ranks;
keep unrelated provider settings and custom agents. These repository edits do
not update live skill folders or host configuration. Keep installed skill links
on a stable clone rather than a temporary worktree.

Sample requests and expected results:

- “Implement this change”: the working policy supplies the model and options;
  parallel children have disjoint ownership in the same checkout.
- “Review and fix this shared-contract change”: primary, Ponytail, and Thermo
  assessments cover the same snapshot; accepted fixes use the working model.
- “Review this small fix”: one independent primary assessment when full-review
  risk/contract triggers do not apply; an ordinary prose or wording-only edit
  with no procedure change uses parent review.
- When the alternate pool cannot fill a slot, a fresh primary-model task covers
  that lens, retaining coverage and disclosing reduced diversity. Missing required
  coverage cannot produce a clean result.
- A substantive fix triggers a fresh round against the original base. A changed
  snapshot supersedes in-flight review; successful dispatch alone is not a pass.
- Ordinary delegation does not create goals or recurring schedules. Explicit
  goal-backed work still needs the host's goal-state tools.

`pr` writes titles/bodies or brings a single PR to readiness; `merge` lands ready PRs or stacks and
finishes resolved GitHub issues through GitHub CLI. `merge` uses `gh-stack` for
stacks and `repo-cleanup` for completed task resources, including simulator and
emulator test installs when platform tooling is available.
`handoff` is manual-only: invoke it explicitly and supply the handoff note path
when resuming in a new session. A plain resume request does not load that skill.
`snip-snap` requires the `snipsnap` command on `PATH`; check `snipsnap --help`
for the commands you need.
Installing or copying only the GUI app does not expose the CLI automatically.
A Snip Snap Homebrew cask release that declares the bundled `snipsnap` binary does.

Use [Snipsnap Do Chores](skills/snipsnap-do-chores/SKILL.md) with "snipsnap do
chores" to tackle saved mechanical improvements through Snip Snap and Goal
Swarm. It leaves features and product decisions open and requires the host's
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

[no-comments](skills/no-comments/SKILL.md) is manual-only. Invoke
`$no-comments` in Codex or `/no-comments` in Claude Code with files or a diff
to audit redundant comments and fix the code they explain. It uses T3's
independent auditing and keeps legal headers, public API contracts, and proven
external constraints. For example, “Use `$no-comments` on this diff” returns
comment deletions, scoped repairs, constraint encodings, and verification.

[SreeStack setup](skills/setup-sreestack/SKILL.md) is the manual
`setup-sreestack` entry point for project workflow conventions, glossary/ADR
paths, and optional issue tracking and triage labels. It links the project's
existing checks, review and PR conventions, and verification knowledge to the
shared skills. An explicit verification-setup request uses `verify` to build
and prove a reusable map. Invoke setup with “migrate glossary” to move existing
domain `CONTEXT.md` / `CONTEXT-MAP.md` files to `GLOSSARY.md` / `GLOSSARY-MAP.md`
and update their consumers without repeating other setup.

### Product verification

[verify](skills/verify/SKILL.md) tests real user workflows using a temporary plan
when no verification map exists. Once a map is set up, verification uses and
maintains its affected recipes. Ask to set up verification to create reusable
docs in `docs/agents/verification/index.md` and `features/`, or an equivalent
established project location. Commit the map in the product repo. The shared
skill supplies the procedure, so projects need no generated verification skill.
You can also request map maintenance or verification without updating docs.
Authenticated checks reuse designated test accounts and their existing access
setup. Verify checks credential access and secure delivery before login, and
reports automatic login separately from checks performed after user sign-in.
Linking this skill does not install the product's browser, device, or terminal
harness.

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

### Store screenshot design

The [koubou skill](skills/koubou/SKILL.md) designs and iterates on App Store
screenshots from real app captures. It includes style intake, narrative and
copy planning, device geometry, HTML/CSS composition, and visual verification.
Linking it makes the workflow available to agents; it does not install Koubou.
Use a working `kou` CLI with HTML rendering support (`kou setup-html`). App
capture follows the project's run scripts and the host's device tooling.

### Agent login

The [agent-login skill](skills/agent-login/SKILL.md) owns application sign-in,
approved credential access, and private delivery. It stays automatically
discoverable; `verify` owns the product checks that follow. For account
onboarding, follow [account setup](skills/agent-login/references/setup.md).

1Password is a provider reference within this skill. Its
[access and setup guide](skills/agent-login/references/1password.md) covers scoped
provider access, item management, and command/API secrets. It requires `op` on
`PATH`, a dedicated agent vault, a scoped service account, runtime token
provisioning, and an approved credential mapping. Linking the skill does not
configure 1Password or restrict shell access.

Codex runtimes on one Mac can share a private environment file while keeping
separate Codex homes. A general file such as `~/.config/agents/shared.env` can hold
1Password variables alongside other credentials and configuration intended for
both runtimes. The [runtime setup](skills/agent-login/references/runtime-provisioning.md)
covers that option and host-specific verification.

The bundled `agent-login` command currently supports only 1Password credentials
and existing local Chromium tabs exposed through a loopback CDP endpoint.
Both Codex and T3 agents can invoke the same
installed command and private account mappings. Native T3/Codex browser adapters
and simulator delivery remain separate work; their tab IDs cannot be passed to
this adapter. The command disconnects after filling, leaving the tab with its
original owner for verification. It does not redact browser snapshots.

Install with Node 22 or newer and npm from this repository's root:

```sh
npm install --global --install-links ./skills/agent-login/scripts
agent-login --help
```

`--install-links` installs a copy that survives worktree removal. The package
uses `playwright-core` without installing a browser. Use a host-supported CDP
endpoint or a dedicated Chromium automation profile; recent Chrome requires a
nondefault data directory for remote debugging.
([Chrome debugging profiles](https://developer.chrome.com/blog/remote-debugging-port),
[Playwright CDP](https://playwright.dev/docs/api/class-browsertype#browser-type-connect-over-cdp))

Keep user-specific aliases in `~/.config/agents/accounts.json`, owned by the user
with mode `0600` inside a `0700` directory. Store only references, never passwords
or the service-account token. Preserve other accounts when adding an alias:

```json
{
  "version": 1,
  "serviceAccountId": "<confirmed service-account ID>",
  "accounts": {
    "staging-buyer": {
      "origin": "https://staging.example.com",
      "allowedOrigins": ["https://auth.example.com"],
      "username": "op://<vault ID>/<item ID>/username",
      "password": "op://<vault ID>/<item ID>/password",
      "selectors": {
        "username": "input[autocomplete='username']",
        "password": "input[autocomplete='current-password']",
        "submit": "button[type='submit']"
      },
      "purpose": "Test login and dashboard verification",
      "role": "BUYER"
    }
  }
}
```

Replace placeholders with confirmed 26-character IDs and selectors for the
approved form. The login origin is always allowed; `allowedOrigins` adds exact
origins needed during credential entry and submission, including redirects and
identity providers. Remote origins require HTTPS; explicitly approved loopback
test origins can use HTTP. Input fields must be empty, unique, and in the main
document. See the [browser procedure](skills/agent-login/references/browser-login.md)
for selecting a target, checking outcomes, and recovering from errors.

For development, install dependencies with `npm ci --prefix skills/agent-login/scripts`
and run `TEST_BROWSER_EXECUTABLE=/path/to/chromium npm test --prefix skills/agent-login/scripts`.
Tests use dummy credentials and a dedicated temporary browser profile.

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
- [Jay E / RoboNuggets](https://github.com/robonuggets/gauntlet-loop) — the adapted `gauntlet-loop` prompt-writing skill (CC BY 4.0), based on [Matt Shumer's technique](https://github.com/mshumer/Claude-of-Duty/blob/main/prompt.md). Local adaptations are recorded in [SOURCES.md](SOURCES.md#gauntlet-loop).
- [HumanLayer / Dex Horthy](https://github.com/humanlayer/skills) — visual explanation guidance credited by Matt Pocock's PR skill.
- [Emil Kowalski](https://github.com/emilkowalski/skills) — animation, motion and gesture behavior, typography and materials, interface access/input, and interface-review guidance.
- [Jakub Antalík’s transitions.dev](https://github.com/Jakubantalik/transitions.dev) — motion pattern references and tuning guidance used by `animate`.
- [Dietrich Gebert’s Ponytail](https://github.com/DietrichGebert/ponytail) — simplicity and code review rules.
- [Cursor](https://github.com/cursor/plugins) — the Thermo Nuclear Code Quality Review.
- [Lauren Tan’s pstack](https://github.com/cursor/plugins/tree/main/pstack) — `arena`, `architect`, `no-comments`, `correct`, `engineering-principles`, and ideas for `verify`, `change-safety`, `code-why`, `codebase-design`, `diagnosing-bugs`, `pr`, `handoff`, `goal-swarm`, and `orchestration`.
- [Uzair Ansar’s p3-stack](https://github.com/uzairansaruzi/p3-stack) — T3 workflow comparison informing app/runtime boundaries, PR monitoring, and continuity; no upstream prose or code copied.
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
