# Terminal and Service Verification

Exercise the public command, terminal interface, or API used by the product's
users. Identify the executable or server revision and the working directory,
configuration, fixture, and account state that affect the result. Reuse the
project's existing harness when it drives that entry point.

## CLI and TUI

- For a short-lived command, build or prepare the executable once, then run each
  workflow in its own disposable working directory and configuration or data
  profile where supported. Set up each command's required starting state; a
  multi-command workflow can retain its own state between steps.
- Use ordinary process execution for noninteractive commands. Use an available
  PTY or terminal harness for prompts, key input, and TUIs whose behavior depends
  on a terminal. Test redirected input separately when that is part of the
  command's contract; piping answers does not exercise terminal interaction.
- Capture arguments and input without secrets, stdout, stderr, and exit status.
  For interactive flows, record the prompt or screen before input and the
  resulting state. Target current prompt text or semantic handles when available.
- Bound terminal waits by the expected prompt, output, or completion deadline;
  retain timeout transcripts and follow the main recovery rules.
- Verify relevant failure behavior: invalid input, cancellation, or unavailable
  prerequisites should produce the expected message, status, and side effects.
  A zero exit code alone does not prove the requested output is correct.

## Services

- Exercise the public protocol with the expected authentication and request data.
  Capture the method, route, non-sensitive inputs, response status, headers, and
  body relevant to each assertion. A health endpoint proves readiness, not the
  feature's behavior.
- For asynchronous operations, wait for the documented observable completion
  within a bounded deadline. An accepted request does not establish completion.
- Read persisted changes through a separate request or fresh process, or inspect
  the resulting artifact independently. Check material side effects on failures
  as well as successes.
