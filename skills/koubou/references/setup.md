# Setup

Reuse the project's working Koubou installation, including its virtual
environment. Check `kou --version` or the project's documented equivalent.
A missing executable on PATH alone does not establish that Koubou is absent.
Keep the resolved executable consistent across commands.

Prepare HTML support before rendering:

```bash
kou setup-html
```

Use this supported setup command instead of installing Playwright directly.
Leave a working Koubou installation in place. If setup fails, inspect and
report the exact failure; do not claim that rendering is ready.

## When Koubou is absent

Use the project's documented dependency setup. If it has none, a local virtual
environment keeps Python packages separate from system Python:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install koubou
.venv/bin/kou --version
.venv/bin/kou setup-html
```

Use `.venv/bin/kou` for subsequent commands. Keep the environment in ignored
local state according to the repo's rules. Pin the version in the project's
dependency mechanism when repeatable exports are required.

Homebrew is another supported option for macOS:

```bash
brew install bitomule/tap/koubou
```

Verify the installed CLI supports the commands used in the skill with its
`--help` output. HTML templates need Koubou's Playwright Chromium runtime.
Device frame inspection or rendering may download missing frame assets;
network access and their license terms apply.

The [Koubou documentation](https://github.com/bitomule/Koubou#installation)
describes supported setup and rendering commands.
