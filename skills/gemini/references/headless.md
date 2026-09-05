# Headless configuration

Use these options for the current prompt; keep saved settings unchanged.

```bash
agy --add-dir <absolute-workspace> --sandbox --effort high --output-format json --print '<prompt>'
```

- **Workspace:** pass its absolute path with `--add-dir` and in the prompt so
  agy uses the right checkout.
- **Model:** use the configured Gemini default or pass `--model <slug>` for the
  caller's choice. If the Gemini model is unknown, check `agy models` for a valid
  slug. Always use `--effort high`, the highest supported reasoning level.
- **Analysis or review:** add `--mode plan` and request an answer without project
  edits. `--sandbox` restricts terminal tools; it does not make files read-only.
- **Follow-up:** pass `--conversation <id>` from the earlier result. Omit it for
  an independent answer.
- **Timeout:** use `--print-timeout <duration>` when the task needs more time.

Pass prompt text as a literal argument with proper shell quoting or a process
argument array. Check the exit code, JSON status, response, and stderr; denied
tools can leave work incomplete even with exit code zero. Report these gaps.
If authentication needs the user, tell them what is needed before retrying.
Follow host approval rules.

See the official [headless mode docs](https://antigravity.google/docs/cli/headless/)
for current options and response fields.
