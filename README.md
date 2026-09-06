# SreeStack

A collection of agent skills for planning, coding, review, research, and UI work.
It includes original workflows and adapted skills from the projects credited below.
Browse [skills/](skills/) and see [SOURCES.md](SOURCES.md) for each skill’s history.

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

## Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for changes and checks, and
[AGENTS.md](AGENTS.md) for agent instructions.

## Release status and licenses

Open-source preparation is in progress. A root license is still pending.
Imported material keeps its own terms; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
[OPEN_SOURCE_READINESS.md](OPEN_SOURCE_READINESS.md) tracks unresolved release work.

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
- [Charles Wiltgen’s Axiom](https://github.com/CharlesWiltgen/Axiom) — inspiration for our iOS haptics skill.

[SOURCES.md](SOURCES.md) records per-skill sources, imported revisions, local
changes, and gaps in the source history.
