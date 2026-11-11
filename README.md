# SreeStack

A collection of agent skills for planning, coding, review, research, and UI work,
with T3 Code orchestration and shared instructions for Codex and Claude Code.
It includes original workflows and adapted skills from the projects credited below.
Browse [skills/](skills/) and see [SOURCES.md](SOURCES.md) for upstream origins
and local differences to preserve during updates.

## Use

Clone the repo to a dedicated stable location, keep that clone on `main`, and
do task work in T3 worktrees. Then sync the clone into each host:

```bash
git clone https://github.com/sreejithraman/SreeStack.git
cd SreeStack
python3 -m venv --clear .venv                           # once
.venv/bin/python -m pip install -r scripts/requirements-sync.txt   # once
.venv/bin/python scripts/sync_hosts.py --check   # preview; changes no host files
.venv/bin/python scripts/sync_hosts.py           # link and merge host setup
```

The ignored `.venv` holds the pinned `tomlkit` package that keeps TOML comments
intact. Re-running setup rebuilds this dedicated environment. Without it, sync
still links skills and instructions, then reports the
settings as unmerged and prints this setup. Nothing installs packages for you.

Sync reads each host's manifest. It links every skill folder one by one, and
links each host's global instructions to [global/AGENTS.md](global/AGENTS.md):

| Host | Manifest | Skill links | Instructions link |
|---|---|---|---|
| Codex | [codex/setup.json](codex/setup.json) | `~/.agents/skills/<skill>` | `~/.codex/AGENTS.md` |
| Claude Code | [claude/setup.json](claude/setup.json) | `~/.claude/skills/<skill>` | `~/.claude/CLAUDE.md` |

Manifest paths are relative to home. New skills link to every host by default;
add a skill name to a manifest's `exclude` list to keep it out of that host.
Sync rejects unknown manifest keys and unknown skill names.

Sync is idempotent. It adds links for new skills and removes or repoints links
into this clone's `skills/` that no longer match a skill. It leaves every other
entry alone, including Claude's `synced/` account downloads and links into other
folders. It reports a conflict and leaves the path unchanged when it finds:

- a file, folder, or foreign link at a skill's name;
- instructions whose content differs from `global/AGENTS.md`; merge that guidance
  into `global/AGENTS.md` or move the file aside, then rerun;
- a skills folder linked to anything other than this clone's `skills/`.

Instructions with the same content are kept as `<name>.backup-<UTC time>` before
sync links the path. A link that already resolves to `global/AGENTS.md`, such as
`~/.codex-t3/AGENTS.md` pointing at `~/.codex/AGENTS.md`, stays as it is. A
skills folder linked as a whole to this clone's `skills/` becomes a real folder
of per-skill links. To undo that, move the folder aside and run
`ln -s "$PWD/skills" ~/.agents/skills`.

Sync and hook installation write only from the stable clone with `main` checked
out. They refuse linked worktrees, feature branches, and detached checkouts.
`--check` changes no host files; it may create a lock file in the repo's Git
directory. In a T3 worktree it checks the stable clone's setup, using that clone's
script, manifests, and `.venv`. It exits 0 only when host setup matches the
stable clone. Both modes
exit 1 on conflicts, and `--check` also exits 1 when changes are pending.
`--home DIR` configures another home directory.

The links point straight into the stable clone, so hosts read whatever that
clone's working tree holds. Editing files there, or checking out another branch,
changes what both hosts load. Work in T3 worktrees: they never change installed
links or the stable clone's files.

### Sync after updates

Install the Git hook once, from the stable clone:

```bash
.venv/bin/python scripts/sync_hosts.py --install-hooks
.venv/bin/python scripts/sync_hosts.py --check-hooks
```

This installs `.git/hooks/sreestack-host-sync` and links Git's
`reference-transaction` hook to it. It records the home directory in the repo's
local Git config as `sreestack.home`. Git runs the hook for ref updates in every
worktree. The handler checks in shell, before it reads any SreeStack file or
config, that the update was committed, touched `main` or `HEAD`, ran in the
stable clone, and left `main` checked out. Anything else exits quietly, so
worktrees keep working when the stable clone is on an older branch or `python3`
is missing.

Each sync refreshes an existing SreeStack-owned handler from `main` when it
changes. `--check-hooks` reports a missing or stale handler, unusable hook
integration, or home setting; it also works from T3 worktrees. Both check modes
fail when the stable clone is off `main`. Rerun `--install-hooks` to
repair those settings. `--check` checks links and settings separately and needs
`tomlkit`; `--check-hooks` and `--install-hooks` do not.

The hook syncs after each local update of `main`: commit, amend, merge, pull,
rebase, `reset --hard`, and switching back to `main`. A merge on GitHub changes
nothing until this clone's `main` is updated. Nothing polls or fetches in the
background. The handler runs the clone's `.venv/bin/python` when it exists and
`python3` from Git's `PATH` otherwise. It never installs packages or uses the
network. Tested with Git 2.54 and 2.56.

A failed hook sync prints its conflicts and says the Git operation was not
rolled back. Git ignores this hook's exit status after a commit, so the Git
command still exits 0. Watch for `sreestack:` warnings, or run
`.venv/bin/python scripts/sync_hosts.py --check` after updating; it exits 0 only
when host setup is current. To recover, fix the conflict and run
`.venv/bin/python scripts/sync_hosts.py`.

Install keeps your hooks. When `reference-transaction` already exists or
`core.hooksPath` is set, it still installs the handler and `sreestack.home`,
changes no hook, and prints the block to add immediately after the hook's
shebang, before any commands. The block preserves reference input byte for byte,
including empty input, for your existing hook. Rerun `--install-hooks` until it
recognizes the installed block, then run `--check-hooks`.

The block does nothing in repositories without the handler, so a shared hooks
directory can carry it.

To remove the hook:

```bash
rm .git/hooks/reference-transaction .git/hooks/sreestack-host-sync
git config --remove-section sreestack
```

If you chained the block into your own hook, remove that block instead of
deleting `reference-transaction`.

Read each skill before use. Delegation and review target T3 Code's orchestration
MCP tools and its configured provider runtimes. Other workflows may need goal
state tools, GitHub CLI, Claude artifact tools or the Sites plugin for command
center publication, optional Tailscale sharing, or
Apple development tools. Linking skills does not install provider executables,
authenticate accounts, or enable models.

### Claude Code

Claude Code loads personal skills from `~/.claude/skills`; see
[skill locations and symlink support](https://code.claude.com/docs/en/skills#choose-where-skills-load).
Sync links each skill there instead of linking the whole folder, because Claude
also stores account downloads in `synced/`. Those downloads stay out of
SreeStack and Codex.

Claude reads user instructions from `~/.claude/CLAUDE.md`, which sync links to
the same `global/AGENTS.md` as Codex. Claude Code v2.1.277 or later reads project
`AGENTS.md` by default when no project or ancestor `CLAUDE.md` or `CLAUDE.local.md`
exists; see [instruction discovery and exceptions](https://code.claude.com/docs/en/memory#agents-md).

Sync merges the keys from [claude/settings.json](claude/settings.json) into your
`~/.claude/settings.json`; see [Host defaults](#host-defaults).

The template's `cc-plugin-agents-md@builtin` configuration applies to Claude Code
v2.1.285 or later. It keeps reading `AGENTS.md` when a project also has Claude
instructions. This setting applies at user scope, not project/local scope.
Claude still reads the shared global `~/.claude/CLAUDE.md`. See
[instruction file selection](https://code.claude.com/docs/en/memory#choose-which-instruction-files-load).

The template also sets a personal 500k-token compaction budget: how much context
Claude Code keeps before it compacts the conversation. It does not change output
tokens or the model's maximum context, which the host model sets separately.
See [`autoCompactWindow`](https://code.claude.com/docs/en/settings-reference#autocompactwindow).

In a fresh T3 Claude session, check that `orchestration` is discoverable and
invoke `/reframe` to check direct invocation. Inspect `/skills` in Claude Code to
confirm which files load; personal skills can replace same-named bundled skills.
T3 must also have the provider enabled and authenticated. Test a small delegated
task to confirm execution. Local links configure Claude Code on this machine;
Cowork and cloud sessions have separate skill loading rules.

### How the skills fit together

T3 supplies the live model catalog, child-task lifecycle, thread history, PR
notifications, and collaborative browser and device controls. SreeStack supplies
model defaults, bounded assignments, review criteria, acceptance checks, and
handoff artifacts. Skills use those app capabilities through the host's current
instructions rather than maintaining another API manual.

| Task | Owner |
| --- | --- |
| Clarify requirements or architecture | `grilling`, `domain-modeling`, `codebase-design`; optional manual planning commands |
| Shape a rough idea into ready work | [shape](skills/shape/SKILL.md), started by you; chains `reframe`, `grilling`, `prototype`, `show-me`, and `to-spec` |
| Form or improve a task brief | `reframe`, requested directly or used by the responsible workflow |
| Write or maintain skills and agent instructions | [writing-for-agents](skills/writing-for-agents/SKILL.md) |
| Choose engineering approaches | `engineering-principles`; workflows retain their procedures and checks |
| Compare independent candidates and synthesize a result | `arena` |
| Understand current code, historical decisions, or change risks | `how`, `why`, and `blast-radius`, respectively |
| Explain simply, including for a PM or junior engineer | [explain](skills/explain/SKILL.md) |
| Design a consequential change and guide its implementation | `architect`, using `codebase-design`, `arena`, and experiments |
| Prevent recurring code mistakes | `correct`, using shared design principles and historical proof |
| Carry one outcome to its finish line | [implement](skills/implement/SKILL.md), using the relevant platform/domain methods |
| Carry several outcomes to their finish lines | [chief-of-staff](skills/chief-of-staff/SKILL.md), with one Implement owner per outcome |
| Diagnose or improve website search discoverability | [seo](skills/seo/SKILL.md), including deployed crawl verification |
| Run bounded parallel work | [swarm](skills/swarm/SKILL.md), returning results to its caller |
| Delegate and accept results | `orchestration` supplies shared mechanics; `research` owns cited investigations |
| Prove behavior | `verify` |
| Share disposable simulators across agents and projects | [simulator-lifecycle](skills/simulator-lifecycle/SKILL.md), using SimLock |
| Run complexity, duplication, or mutation tools | `code-quality` |
| Show results and make them available to try | `show-me` shows results in the thread and makes them easy to try |
| Sign in or use approved authentication credentials | `agent-login`; provider mechanics live in its references |
| Generate or edit images in any coding agent | [create-image](skills/create-image/SKILL.md), automatically discoverable; API first, then the host's subscription tool |
| Review and repair | `review-fix-loop` coordinates, `review` assesses, `review-sweep` settles and fixes |
| Publish and watch | `pr`; `gh-stack` manages dependent layers |
| Land and clean up | `merge`, then `repo-cleanup` |
| Transfer context or improve the environment | Explicit `handoff` or `retro` |
| Improve the stack's skills and checks from evidence | [tune-stack](skills/tune-stack/SKILL.md), started by you; chains `retro` and `correct`, and proves each change against the old version |

[SEO](skills/seo/SKILL.md) is automatically discoverable for website search work.
For example, “Find why our public product pages aren't indexed and fix it”
returns a diagnosis, supported fixes, and verification of deployed responses
when the changes are live. Search Console access improves the evidence but is
not required for repository and public-response checks.

Use only the skills triggered by the task. A small change needs no global mode,
mandatory design panel, or planning registry. Specialists retain their current
invocation choices; setup, planning commands, handoff, and retrospective remain
explicit where configured. Ordinary delegation creates no native goals,
schedules, or ordinary top-level conversations. Program execution, new sessions,
native tracking, and recurring work follow the user's request and host rules.

[Writing for Agents](skills/writing-for-agents/SKILL.md) sets the standard for
skills, `AGENTS.md`, `CLAUDE.md`, and agent docs: a line stays only if removing it
changes what an agent does. Root instruction files stay thin and map to the rest.
For example, “Correct this skill's command example” uses a focused check, and
“Rewrite this skill” starts fresh from its job and real requests. Context-savings
claims need measured trials with validated isolation.

[Reframe](skills/reframe/SKILL.md) forms a brief from the user's request and
context. It scales to what is unsettled: a precise request may need only a
concise confirmation. The calling workflow reuses the settled brief through
execution and revisits it when evidence or user direction changes. Material
scope or tradeoff changes need authorization; routine framing adds no approval
checkpoint.

You can also invoke `$reframe` in Codex or `/reframe` in Claude Code directly.
For example, “Be more ambitious about helping users recover from upload errors,
preserving existing upload behavior” returns a brief with a stronger outcome,
methods, needed setup, and suitable evaluation. It can propose harder targets or
a lasting workflow; execution follows the authorized scope. Ask to rewrite a
prompt to receive a copyable version of that brief.
It needs the task context and relevant evidence; investigation may need the
project's tools. Reframing alone ends with the brief. When another workflow
calls it, Reframe returns the brief to that owner, which continues execution.

[Shape](skills/shape/SKILL.md) turns a rough idea into ready work through
conversation. Start it with `/shape` in Claude Code or `$shape` in Codex. It keeps
one record, a draft outside the repo unless an existing spec or task record
fits, and uses Grilling for your decisions, Prototype and Show Me when seeing an
option would decide it, and To Spec when the idea holds several outcomes. It
ends with a settled brief or spec, or a dropped idea and the reason. If you
already asked to build, it hands the record to Implement or Chief of Staff;
otherwise it offers that step. It publishes to a tracker only when you ask.

[Implement](skills/implement/SKILL.md) carries one outcome, as one PR or a
planned stack, to its finish line and returns an owner report to whoever
started it. It picks **Land** for settled, reversible work and merges once
review, checks, and proof pass; otherwise it picks **Try**, proves and shows the
result, and stops before review for you to merge, change, or scrap it. It states
the pick up front so you can override it, and “open a PR” stops at the PR. It
also pursues measurable targets: “Reduce search p95 to 200 ms while preserving
results and resource limits” keeps a correct 300 ms improvement as progress and
continues toward 200 ms. Work outside the outcome becomes a follow-up with its
own finish line, or a snip when unrelated.

[Chief of Staff](skills/chief-of-staff/SKILL.md) carries several outcomes to
their finish lines. Its input is any set of work: a spec, a list in chat, saved
snips, follow-ups, or existing PRs. It splits the work into outcomes, starts or
adopts one Implement owner per outcome, starts only ready work, and keeps
blocked work moving on provisional bases or recommended options that can be
undone. It reads owner reports, watches pending PRs, and routes discoveries and
shared blockers. It settles reversible decisions that a recorded source or your
standing approval already answers, and you can reopen any of them; the rest come
to you, with judgment calls ahead of quick picks. Each outcome has its own
**Land**, **Try**, or PR finish line: an owner lands its accepted outcome once
the chief releases it, the chief lands only sets that span owners, and each
**Try** waits for your merge, changes, or scrap choice. Its command center shows
Needs you first and Work second, rendered from the program record's last
commit: each outcome with its finish line, results to open, layers, provisional
state, and what each decision blocks. Answers go back through chat. Existing
trackers stay authoritative. Claude chiefs publish a private Claude artifact;
Codex chiefs publish a private ChatGPT Site when the Sites plugin is available.
The chief reuses its backend target and republishes after each commit that
changes the page, and on resume or chief move. A backend change updates the
current page link after successful publication. Open Sites check for updates
every 20 seconds while visible and when you return, then reload matching new
content. Failed checks leave the page available. On reload,
the page restores your tab, open sections, selected decision, and scroll
position; local browser tests cover this. In Claude's web viewer, an open page
moved to a newly published version without a reload, kept its selected tab, and
loaded its icons. The iPhone app is unchecked.

[Swarm](skills/swarm/SKILL.md) is a bounded tool any session can use. For example,
“Swarm these three possible causes and return evidence” partitions the question
and returns one consolidated result with coverage gaps. It supports coverage,
races, and mixed assignments without taking over its caller's PR or program.

Implement and Swarm work on their own; Chief of Staff uses them as tools.
[Orchestration](skills/orchestration/SKILL.md) supplies the shared mechanics they
all use: model selection, briefs, decision requests, holds, and acceptance.

[Engineering Principles](skills/engineering-principles/SKILL.md) is automatically
discoverable. Its task-based index links to 24 reference files, one per principle,
for data and interface design, simplification, state and migration, evidence,
and execution. Specialist workflows point to useful guidance for design and
implementation.
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
[model-defaults table](skills/orchestration/references/models.md#model-defaults)
to change working/research/review models, source-retrieval routes, effort, and
additional-review pools.
The local concurrency ceiling is in Orchestration. This table is the one source
for skill model defaults; explicit user/project requirements are resolved by
[models](skills/orchestration/references/models.md).
[Who does the work](skills/orchestration/SKILL.md#who-does-the-work) says when a thread delegates.

[Models](skills/orchestration/references/models.md) defines UI operation, UI and implementation
tiers, document work, and raising a row;
[reuse and recovery](skills/orchestration/references/reuse-and-recovery.md) covers agent reuse,
owner replacement, and availability fallbacks. The existing agent handles routine UI operation,
with dedicated operators for substantial work, specialized capabilities, independent
verification, or repeated difficulty.

Enable and authenticate the providers named in that table in T3 Code. Routing
resolves their exact instance/model IDs and supported options from the live
catalog; an ambiguous match needs an explicit selection. Gemini's effort selection
is encoded in its model ID, while other providers may expose an option. Catalog availability does
not establish quota or successful access. T3's injected MCP tools or supported
ACP bridge must be reachable from the agent. OpenCode and Gemini reviewers read
their review references from this stack; provider plugins are not needed.

[Review](skills/review/SKILL.md) assesses a snapshot without fixes.
[Review Sweep](skills/review-sweep/SKILL.md) settles local findings, PR comments, and
failing checks the same way, by outcome, and sends accepted fixes through
[Orchestration](skills/orchestration/SKILL.md#who-does-the-work).
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
- “Implement this change”: the model table supplies the subagent's model and options;
  parallel children have disjoint ownership in the same checkout.
- “Review and fix this shared-contract change”: Primary, Ponytail, Thermo, and
  optional pool reviewers assess the initial snapshot. The parent settles scope
  and design, then Adversarial assesses the settled snapshot. Accepted fixes go
  back to the slice's owner.
- “Review this small fix”: one required Primary plus initial optional pool
  reviewers for contained ordinary work; contained risky work adds a fitting
  lens. An ordinary prose or wording-only edit with no procedure change uses
  parent review.
- When an additional reviewer is unavailable or fails, the loop records a skip
  and continues. Missing required coverage cannot produce a clean result.
- A substantive fix gets a new pass: new tasks on the original reviewers' models
  for the angles it touches, with the prior evidence. Each pass checks the current
  snapshot, bounded to affected behavior, prior findings, and relevant proof.
  Primary's integrated check covers cumulative repairs. Retain earlier coverage
  only where it still applies. Keep the original base for context.
  A changed snapshot supersedes in-flight review; dispatch alone is not a pass.
- Ordinary delegation does not create goals or recurring schedules. Explicit
  goal or swarm work can use ordinary tasks; requested native tracking follows
  the host's available capabilities.

`pr` writes titles and bodies, publishes one PR, and watches it to ready. `merge` lands a
finished change: it brings the PR to ready, stops only when a fix changes what you kept,
shows the result, and finishes resolved GitHub issues through GitHub CLI. `merge` uses
`gh-stack` for stacks and `repo-cleanup` for completed task resources, including Mac development
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
[Tune Stack](skills/tune-stack/SKILL.md) improves SreeStack's own skills and
checks from session logs, run metrics, or a new model release. Invoke it
explicitly. A retrospective request returns recommendations; otherwise it
picks one hypothesis, proves the candidate against the old version with
`writing-for-agents`' comparison runner on `claude plugin eval`, and builds it
through `implement` to Try.
It lands only when you say Land.
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
paths, verification maps, and optional issue tracking.
Full setup creates or reuses `docs/agents/verification/index.md`, or an equivalent
established location, records known setup facts and coverage gaps, and adds an
agent-instruction pointer. It links the project's existing checks and review
and PR conventions to the shared skills. Ask setup to add feature recipes, prove
them live, or maintain the map. Invoke setup with
“migrate glossary” to move existing domain `CONTEXT.md` / `CONTEXT-MAP.md` files
to `GLOSSARY.md` / `GLOSSARY-MAP.md` and update their consumers without repeating
other setup.

### Product verification

[verify](skills/verify/SKILL.md) proves a change through its real entry points.
It runs a read-only doctor before driving, reproduces the old result when a claim
needs one, and gives every assertion a verdict with evidence. It writes no docs in
any repo, except the records of formal checks when asked or when the task changes
code a check covers. With no verification map it uses a temporary plan. With a map it reads the
map and reports drift. Project repositories supply the harnesses, so linking this
skill doesn't install a browser, device, or terminal tool.

[Verification maps](skills/setup-sreestack/references/verification-map.md) are for
your own repos. `setup-sreestack` creates and maintains them when you ask. [Reframe](skills/reframe/SKILL.md) plans how a result will be judged,
including qualitative work and candidate comparisons.

Authenticated checks reuse designated test accounts and their existing access
setup. Verify checks credential access and secure delivery before login, and
reports automatic login separately from checks performed after user sign-in.

[iOS verification](skills/verify/references/ios.md) covers interactive
checks and repeatable regression suites. `simulator-lifecycle` owns how to reach a
device. Verification reuses existing project harnesses and prefers XCTest with XCUIAutomation for new iOS
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

[show-me](skills/show-me/SKILL.md) helps you experience and judge results,
including during iteration. It chooses formats based on the work and available
tools: screenshots, collages, video, preview links, device installs, runnable
examples, or accessible files. It can combine demonstrations with hands-on
access and reuse current verification evidence. Website handoffs include a
checked PR preview or Tailscale URL when available.

Show Me is automatically discoverable. The shared completion instructions and
Orchestration call it for results you can inspect or try; project setup includes
the corresponding handoff pointer. The repository edits do not update installed
skills or live host instructions. Apply them through your stable clone and the
host setup below to activate those routes.

### Shared simulators

[Simulator Lifecycle](skills/simulator-lifecycle/SKILL.md) routes disposable
agent devices through [SimLock](https://incubator.callstack.com/simlock/).
It reads the installed tool's rules instead of maintaining another lease system.
Verify uses that route for tests; Show Me records inspection lifetimes; Repo
Cleanup releases managed leases and handles proven task-owned host outputs.

Use its [setup and rollout guide](skills/simulator-lifecycle/references/setup.md)
to configure a bounded reusable pool and prove concurrent isolation, failure
cleanup and retained-device protection. Project adoption wires the normal test
command to [acquisition and teardown](skills/simulator-lifecycle/references/project-runners.md).
Linking the skill alone does not install SimLock or integrate project runners.
T3 interactive work requires its supported route to the same SimLock lease.
Retained app data stays outside the disposable pool; expiry can wipe pooled data.

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

### Product illustrations and demos

The [stageshow skill](skills/stageshow/SKILL.md) creates faux product UI stills,
animated cursor demos, and bento grids for marketing pages and docs. It includes
the upstream React/CSS kit, examples, playground, and capture tools unchanged.
Follow its [setup and usage guide](skills/stageshow/README.md) to run the examples.
When copying kit or example source into another project, include the
[Stageshow MIT notice](licenses/benjitaylor-stageshow.txt) and applicable
[asset notices](skills/stageshow/NOTICE.md).

### Agent login

The [agent-login skill](skills/agent-login/SKILL.md) owns application sign-in,
approved credential access, and private delivery. It stays automatically
discoverable; `verify` owns the product checks that follow. Its bundled command
supports 1Password credentials and existing local Chromium CDP tabs.

[Browser login](skills/agent-login/references/browser-login.md) covers
installation, account onboarding, private account mappings, and development
checks. [Machine setup](skills/agent-login/references/machine-setup.md) covers
the agent vault, service account, private environment files, and host-specific
access checks.

## Host defaults

The host settings templates below supply parent-session defaults, separate
from orchestration's delegated model policy. Sync and its Git hook merge them
into these private config files:

| Template | Destination | Keys |
|---|---|---|
| [config.toml](codex/config.toml) | `~/.codex/config.toml`, `~/.codex-t3/config.toml` | Parent settings and the native concurrency ceiling |
| [settings.json](claude/settings.json) | `~/.claude/settings.json` | Parent settings and instruction-file selection |

Shared instructions are not a template: sync links them, as described in [Use](#use).

The templates own the keys they set, and a local change to one of those keys is
replaced on the next sync. Every other key stays local and never reaches this
repo. Full configs stay regular files, because they may hold machine paths,
trusted projects, and integration settings. TOML comments are preserved. JSON is
reformatted only when a managed key changes. When nothing differs, sync leaves
the file untouched.

Before it replaces a config, sync writes an exact private copy beside it, named
`<file>.backup-<time>-<random>`, then renames a new file into place. Sync keeps
these backups; delete them when you no longer need them. New folders and files
are private (`0700` and `0600`). An existing file keeps its mode.

Sync refuses a config it cannot merge safely, leaves it unchanged, and continues
with the rest. It refuses malformed files, a table or list where the template
sets a value, a value where the template needs a table, JSON numbers that would
change if rewritten, symlinks, hard links, special files, a symlinked config
folder such as `~/.codex-t3 -> ~/.codex`, and any destination inside a checkout.
Each refusal names the file and managed key, never a config value.

Sync rereads a config just before replacing it and stops if it changed, but a
host can still write in the moment before the rename and lose that write. The
backup holds the version sync read. Quit hosts first when that matters.

If `~/.codex/AGENTS.override.md` exists, it takes precedence over
the linked `AGENTS.md`; merge its guidance into `global/AGENTS.md` or remove it.
Native child execution uses explicit policy settings rather than named rank
presets. Start a new task after changing host settings and check its effective
selection; active tasks may retain earlier settings.

Each template applies to its own host. T3 can override model and effort per
assignment. T3 thread selections and
Orchestration's delegated model defaults are separate from either host's
defaults. Sharing instructions does not change those selections. See Claude's
[user instruction location](https://code.claude.com/docs/en/memory#choose-where-to-put-claudemd-files).

Use [research](skills/research/SKILL.md) for cited investigations and session
notes. Keep maintained technical citations beside their guidance. Host setup
follows OpenAI's
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

- [DeepSeek Harness Team](https://github.com/deepseek-ai/dsh-superagent-prototype) — coordination, attention, handoff, and visual-comparison ideas; instructions are independently written.
- [Lucide Icons and Contributors](https://github.com/lucide-icons/lucide), with Feather-derived work by Cole Bemis — chief-of-staff dashboard icons.
- [Suraj Sharma](https://x.com/suraj_sharma14/status/2116062550416871512) and [Rakesh Patel](https://x.com/rakeshpatelco/status/2116065801279291422) — website SEO coverage and deployed crawl verification ideas; instructions are independently written.
- [David Collado / Koubou](https://github.com/bitomule/Koubou) — App Store screenshot design workflow and supporting references.
- [Benji Taylor / Stageshow](https://github.com/benjitaylor/skills) — product UI illustrations, animated demos, and the bundled React kit and examples.
- [Matt Pocock](https://github.com/mattpocock/skills) — engineering and productivity skills, including implementation, chief-of-staff coordination, and the Standards and Spec review rules.
- [Nico Bailon / skill-diet](https://github.com/nicobailon/skill-diet) — skill revision, tool-guidance auditing, call-format, and evaluation methods, including comparison rules, adapted into `writing-for-agents`.
- John Ousterhout — deep-module and design-it-twice concepts used in Codebase Design.
- David Khourshid — state-machine modeling and UI-independent logic informing Engineering Principles; no upstream prose or code copied.
- [Felix Rieseberg](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/) and [Ray Amjad](https://www.youtube.com/watch?v=RbfQayMNtJc) — outcome, depth, range, and verification ideas informing Reframe and goal execution; instructions are independently written.
- [Jay E / RoboNuggets](https://github.com/robonuggets/gauntlet-loop) — the adapted `gauntlet-loop` prompt-writing skill (CC BY 4.0), based on [Matt Shumer's technique](https://github.com/mshumer/Claude-of-Duty/blob/main/prompt.md), and [be-ambitious](https://github.com/robonuggets/be-ambitious), which informed independently written Reframe guidance. Source records are in [SOURCES.md](SOURCES.md).
- [HumanLayer / Dex Horthy](https://github.com/humanlayer/skills) — visual explanation guidance credited by Matt Pocock's PR skill.
- [Emil Kowalski](https://github.com/emilkowalski/skills) — animation, motion and gesture behavior, typography and materials, interface access/input, and interface-review guidance.
- [Jakub Antalík’s transitions.dev](https://github.com/Jakubantalik/transitions.dev) — motion pattern references and tuning guidance used by `animate`.
- [Dietrich Gebert’s Ponytail](https://github.com/DietrichGebert/ponytail) — simplicity and code review rules.
- [Vox](https://x.com/Voxyz_ai/status/2115518965443076573) — review-noise ideas informing the shared bug-evidence and settlement rules; no upstream prose copied.
- [Maze](https://x.com/mazeincoding/status/2115575731585507796) — architecture signals informing exploration and structural review; guidance is independently written.
- [Cursor](https://github.com/cursor/plugins) — the Thermo Nuclear Code Quality Review.
- [OpenAI’s Codex plugin](https://github.com/openai/codex-plugin-cc) — adversarial review criteria.
- [OpenCode](https://github.com/anomalyco/opencode) — general review criteria used by OpenCode reviewers.
- [Gemini CLI’s code-review extension](https://github.com/gemini-cli-extensions/code-review) — review criteria used by Gemini reviewers.
- [Lauren Tan’s pstack](https://github.com/cursor/plugins/tree/main/pstack) — `arena`, `architect`, `how`, `show-dont-tell`, `correct`, `engineering-principles`, and ideas for `explain`, `verify`, `blast-radius`, `why`, `codebase-design`, `diagnosing-bugs`, `pr`, `handoff`, `chief-of-staff`, `swarm`, and `orchestration`.
- [Robert C. Martin’s ub-mode](https://github.com/unclebob/ub-mode) — simplicity, behavior verification, and assumption-checking ideas informing the shared global instructions; no upstream prose or code copied.
- [Robert C. Martin’s Crapper](https://github.com/unclebob/crapper), [Dryer](https://github.com/unclebob/dryer), and [Mutator](https://github.com/unclebob/mutator) — external tools used by `code-quality`.
- [Uzair Ansar’s p3-stack](https://github.com/uzairansaruzi/p3-stack) — T3 workflow comparison informing app/runtime boundaries, PR monitoring, and continuity; no upstream prose or code copied.
- [t3dotgg’s tstack](https://github.com/t3dotgg/tstack) — PR babysitting workflow comparison informing watcher ownership and handoff; no upstream prose or code copied.
- [Callstack’s SimLock](https://github.com/callstackincubator/simlock) — adapted skill entrypoint in `simulator-lifecycle`; runtime instructions stay with the installed tool. [MIT notice](licenses/callstackincubator-simlock.txt).
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
