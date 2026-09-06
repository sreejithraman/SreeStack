# SreeStack

The source of truth for Sree’s user skills. Browse [skills/](skills/) for the
collection and edit skills here.

## Use

Clone this repo, then symlink its `skills/` directory to `~/.agents/skills`.
Move any existing `~/.agents/skills` folder aside first.

```bash
mkdir -p ~/.agents
ln -s /absolute/path/to/SreeStack/skills ~/.agents/skills
```

Edit skills in this repo. See [AGENTS.md](AGENTS.md) for how to add and update them.

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
