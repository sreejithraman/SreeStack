# Code review

Run from the workspace, replacing the placeholders with the caller's scope:

```bash
agy --add-dir <absolute-workspace> --sandbox --mode plan --effort high --output-format json --print '/code-review Workspace: <absolute-workspace>. Set command working directory to that exact path. Review changes against <resolved-base-commit>, including committed, staged, unstaged, and untracked changes within <file-scope>. This scope overrides origin/HEAD. Requirements and standards: <context>. Report findings with file locations, evidence, suggested fixes, and coverage gaps. Review only; do not edit files, commit, or post comments.'
```

This uses agy's installed `code-review` skill and configured Gemini model with
highest reasoning. Keep the code stable during review. Check the result as
described in [headless.md](headless.md); confirm coverage matches the requested
scope before sending findings to the caller for triage.
