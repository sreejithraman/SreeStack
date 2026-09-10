# SreeStack

A collection of agent skills for planning, coding, review, research, and UI work,
with a small set of shared Codex defaults.
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

Read each skill before use. Some workflows need host tools for goals, agents,
or browser control; others need GitHub CLI, Antigravity CLI, Tailscale, or Apple
development tools. Available tools and invocation settings vary by host.
This collection has no single runtime that supports every skill.

## Codex defaults

The files under [codex/](codex/) define shared defaults. Keeping them here does
not change the live Codex config or global instructions. Keep the full personal
config local. It can contain machine paths, trusted projects, and integration
settings.

| Source | Destination | How to apply |
|---|---|---|
| [config.toml](codex/config.toml) | `~/.codex/config.toml` | Merge the listed keys into the existing file and `[agents]` table |
| [global-instructions.md](codex/global-instructions.md) | `~/.codex/AGENTS.md` | Add this section to the existing instructions |
| [reviewer.toml](codex/agents/reviewer.toml) | `~/.codex/agents/reviewer.toml` | Copy this role file |
| [hard_worker.toml](codex/agents/hard_worker.toml) | `~/.codex/agents/hard_worker.toml` | Copy this role file |

To apply these defaults, back up the local files, merge or copy only these parts, and
check that the TOML parses. Keep unrelated values and existing instructions.
If `~/.codex/AGENTS.override.md` exists, Codex reads it instead of `AGENTS.md`;
merge the section into that active file, or deliberately retire the override
before using `AGENTS.md`.
If a destination role already exists, review its differences before replacing
it. No install script or whole-config symlink is needed for this first version.

The global instructions expect [goal-swarm](skills/goal-swarm/SKILL.md) and
[review-fix-loop](skills/review-fix-loop/SKILL.md), plus their referenced skills,
to be installed from this repo. The
[routing reference](skills/goal-swarm/references/agent-routing.md) explains role
selection and the host's spawn rules. Model and effort values live in config
and agent files; the skills own delegation, review coverage, and rounds.

These are defaults for local tasks using the same Codex home. Project config,
explicit model choices, and custom roles can override them. Defining roles makes
them available; the global and skill instructions request their use. Start a
new task after applying the files and check the effective settings. Existing
tasks may retain their selections. Keep any installed links on a stable clone,
not a temporary worktree.

Sample checks after installation:

- A small behavior change uses one reviewer; substantial changes, multiple
  behaviors, shared contracts, risky logic, or work from several agents use two.
  Each reviewer reads the whole diff in every round.
- A complete clean review can finish after one round. Accepted code fixes
  trigger another full review against the original base.
- Ordinary docs use parent review. Docs that change agent behavior use one
  independent reviewer, with another full review after substantive fixes.
- Independent work can use agents without creating goals unless the user asks
  for goal-backed work. A difficult cohesive task can keep one owner.

Local research notes under `docs/research/` are ignored by Git. Keep maintained
technical citations beside the guidance they support. The setup above follows
OpenAI's [config precedence](https://learn.chatgpt.com/docs/config-file/config-basic),
[custom agent format](https://learn.chatgpt.com/docs/agent-configuration/subagents),
and [global instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

## Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for changes and checks, and
[AGENTS.md](AGENTS.md) for agent instructions.

## License

SreeStack’s original work uses the [MIT License](LICENSE).
Imported material keeps its own terms; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
See [release notes](OPEN_SOURCE_READINESS.md) for the checks and repository settings.
Report security issues through the [private reporting channel](SECURITY.md).

## Credits and thanks

Thank you to the authors and contributors who shared the skills this collection
uses and adapts:

- [Matt Pocock](https://github.com/mattpocock/skills) — engineering and productivity skills, including the Standards and Spec review rules.
- [Emil Kowalski](https://github.com/emilkowalski/skills) — animation and design engineering skills.
- [Dietrich Gebert’s Ponytail](https://github.com/DietrichGebert/ponytail) — simplicity and code review rules.
- [Cursor](https://github.com/cursor/plugins) — the Thermo Nuclear Code Quality Review.
- [Anthropic’s Claude Plugins Community](https://github.com/anthropics/claude-plugins-community) — the `eli5` skill.
- [GitHub’s gh-stack](https://github.com/github/gh-stack) — the stacked PR skill.
- [haider-nawaz](https://github.com/haider-nawaz/liquid-glass-skill) — the Liquid Glass skill.
- [s0xDk](https://github.com/s0xDk/refactoring-ui-skill) — the Refactoring UI skill, based on Adam Wathan and Steve Schoger’s work.
- [React Doctor](https://github.com/millionco/react-doctor) — the React diagnostics skill.
- [Charles Wiltgen’s Axiom haptics guide](https://github.com/CharlesWiltgen/Axiom/blob/dd3334734ecd01afab28b0ac22c49d4b5b2e5857/.claude-plugin/plugins/axiom/skills/axiom-media/skills/haptics.md) — inspiration for our locally written iOS haptics skill; no upstream prose or code copied.
- [Rudrank Riyam’s App Store Connect CLI skills](https://github.com/rorkai/app-store-connect-cli-skills) — usage and workflow guides for our App Store Connect skill.

[SOURCES.md](SOURCES.md) records upstream paths, import revisions, and current
differences to preserve. Git records how the skills changed over time.
