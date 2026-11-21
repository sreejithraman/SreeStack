# Models

These defaults apply to new launches and availability recovery; they never replace a running agent
or override the model the user picked for a thread.

## Model defaults

### Work and coordination
- **Coordinator:** Claude Opus 5.5 High → Devin Opus 5.5 Medium → Antigravity Gemini 4 Neon High → Codex GPT-6.2 Sol High
- **UI implementation and fixes:** Claude Opus 5.5 High → Devin Opus 5.5 Medium → Devin Gemini 4 Neon High → Codex GPT-6.2 Sol High
- **Simple implementation and fixes:** Devin Opus 5.5 Medium → Codex GPT-6.2 Sol Medium
- **Standard implementation and fixes:** Codex GPT-6.2 Sol High → Claude Opus 5.5 High → Devin Gemini 4 Neon High → Antigravity Gemini 4 Neon High
- **Hardest implementation and fixes:** Claude Fable 5.2 X-High → Codex GPT-6.2 Astra X-High
- **Document writing and revision:** Antigravity Gemini 4 Neon High → Devin Gemini 4 Neon High → Claude Opus 5.5 Medium → Devin Opus 5.5 Medium → Antigravity Opus 5.5 Medium → Codex GPT-6.2 Sol Medium
- **UI operation:** Codex GPT-6.1 Terra High *(Medium for simple linear flows; X-High for complex edge cases or costly false passes)*

### Research and retrieval
- **General research:** Codex GPT-6.2 Sol Medium
- **YouTube retrieval:** Antigravity Gemini 4 Hydrogen High
- **X retrieval:** Grok 4.7 High

### Reviews
- **Primary review:** Antigravity Gemini 4 Neon High → Devin Gemini 4 Neon High → Codex GPT-6.2 Sol High
- **Ponytail review:** Claude Opus 5.5 High → Devin Opus 5.5 Medium → Antigravity Opus 5.5 High → Codex GPT-6.2 Sol High
- **Thermo review:** Codex GPT-6.2 Sol High
- **Adversarial review:** Claude Opus 5.5 High → Devin Opus 5.5 Medium → Antigravity Opus 5.5 High → Codex GPT-6.2 Sol High

This list is the source of truth for availability fallbacks: try a job's listed entries left to
right on quota or unavailability; never invent an unlisted substitute. Match only the exact
standalone model (not a hybrid like Devin `Fusion`), resolving exact model IDs and effort options
from live host capabilities (some providers encode effort in the model ID or expose a separate
thought-level option). A caller or project choice settles multiple model-ID matches; otherwise
report the ambiguity. Pass the effort option only when live host capabilities advertise one for that
model; leave other options (like Devin's `mode` and `speed`) at host defaults unless the user sets
them.

## Choose a model

Use the job's named default above, applying these boundaries:

- **Building or changing UI (any size):** `UI implementation and fixes` — never `Simple` or
  `Hardest` (reviewing or researching UI still uses its review or research default).
- **Prose only (skills, agent instructions, READMEs, docs):** `Document writing and revision`. Mixed
  prose and code keeps one owner on the code default; executable scripts and tests are code.
- **Unnamed source review (second opinions, ad-hoc audits):** `Primary review`.
- **Other code, diagnosis, design, tests, config, or non-interactive verification:** `Standard` by
  default (choose it whenever `Simple` is in doubt). Use `Simple` only for small, mechanical tasks
  with an obvious check (typo, rename, formatting). Use `Hardest` only when evidence shows
  `Standard` is insufficient (unresolved architectural tradeoffs, subtle state or concurrency
  invariants, or repeated failed approaches).

**Raise the difficulty** one tier (or straight to `Hardest`) for the next launch when evidence shows
the work is harder; a running owner stays unless replaced. A product failure is a finding to
diagnose or fix, not a reason to raise difficulty. Raised difficulty holds for the work and its
fixes unless `UI implementation` applies; high-stakes prose raises to `Standard` or `Hardest` only
after repeated failed attempts.

## Operate a UI

Drive a browser, desktop app, or device UI yourself when your tools reach it. Delegate a **UI
operation** child only for lengthy or difficult flows, tools you lack, required independent
verification, or repeated operational difficulty (tool failures, state mismatches, or inconsistent
judgments) — never for product bugs (send those to the implementer). The caller keeps assertions
and verdicts, and delegating or raising effort never grants extra permissions or authorization; pass
expected vs. observed state, captured evidence, unresolved checks, and session/tool references in
the handoff.
