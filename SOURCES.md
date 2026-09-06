# Skill sources

Sources and revisions from Caddie’s manifest and lock, copied on 2026-09-04.
See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for bundled license notices
and unresolved license checks.

Recorded commits are import baselines; local files may differ. Local sources do
not establish original authorship. Unknown means Caddie did not record the fact.

Use one entry per skill and one bullet per source, including sources of its references. Record the commit or version
last imported; update it when pulling source changes. Add a brief note only to
explain adaptations, combined sources, or invocation changes from upstream.
Keep `disable-model-invocation` in `SKILL.md` and `allow_implicit_invocation`
in `agents/openai.yaml` aligned: `true`/`false` for manual-only skills;
`false`/`true` (or omit both) for automatic use.

## animate

- [emilkowalski/skills](https://github.com/emilkowalski/skills) — `skills/animate`; commit: unknown.

Adapted in SreeStack.

## codebase-design

- [mattpocock/skills / skills/engineering/codebase-design](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/codebase-design) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## design-eng

- [emilkowalski/skills](https://github.com/emilkowalski/skills) — `skills/emil-design-eng`; commit: unknown.
- [emilkowalski/skills](https://github.com/emilkowalski/skills) — `skills/apple-design`; commit: unknown.

Combines both sources in SreeStack.

Local: `disable-model-invocation: true` and `allow_implicit_invocation: false`.
Neither source has these restrictions on `main` as checked on 2026-09-04;
the imported revisions are unknown.

## diagnosing-bugs

- [mattpocock/skills / skills/engineering/diagnosing-bugs](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/diagnosing-bugs) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## domain-modeling

- [mattpocock/skills / skills/engineering/domain-modeling](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/domain-modeling) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## eli5

- [anthropics/claude-plugins-community / eli5/skills/eli5](https://github.com/anthropics/claude-plugins-community/tree/f4c9452f5ca091f1be7064d9faab1b001ea21645/eli5/skills/eli5) — commit `f4c9452f5ca091f1be7064d9faab1b001ea21645`.

## execute-goal

- Local: `skills/execute-goal` (SreeStack).

## gemini

- Local: `skills/gemini` (SreeStack), formerly `gemini-review`.
- [Antigravity CLI docs](https://antigravity.google/docs/cli/headless/) — checked 2026-09-05 against installed agy `1.1.26`; docs are unversioned.

Local: focus on self-contained headless prompts and assessing Gemini's answers.
Keep headless configuration and the installed agy review command in references.
Always request high reasoning.
Preserve caller scope and report incomplete reviews; no external skill text copied.

## gh-stack

- [github/gh-stack / skills/gh-stack](https://github.com/github/gh-stack/tree/14fc42ed9b6c376a53b2f999f138d3bd26dac546/skills/gh-stack) — commit `14fc42ed9b6c376a53b2f999f138d3bd26dac546`.

## goal-swarm

- Local: `skills/goal-swarm` (SreeStack).

## grill-me

- [mattpocock/skills / skills/productivity/grill-me](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/productivity/grill-me) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## grill-with-docs

- [mattpocock/skills / skills/engineering/grill-with-docs](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/grill-with-docs) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## grilling

- [mattpocock/skills / skills/productivity/grilling](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/productivity/grilling) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## handoff

- [mattpocock/skills / skills/productivity/handoff](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/productivity/handoff) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## implement

- [mattpocock/skills / skills/engineering/implement](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/implement) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

Local: use `review-fix-loop` to review, fix, and verify before committing.

## improve-codebase-architecture

- [mattpocock/skills / skills/engineering/improve-codebase-architecture](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/improve-codebase-architecture) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

Local: default to high-level findings, recommendations, and reasons in chat; create an HTML report only on request.

## ios-haptics

- Local: `skills/ios-haptics` (SreeStack).
- [CharlesWiltgen/Axiom / haptics](https://github.com/CharlesWiltgen/Axiom/blob/dd3334734ecd01afab28b0ac22c49d4b5b2e5857/.claude-plugin/plugins/axiom/skills/axiom-media/skills/haptics.md) — inspiration reviewed at commit `dd3334734ecd01afab28b0ac22c49d4b5b2e5857`; no imported baseline. Found through [MCP Market](https://mcpmarket.com/tools/skills/ios-haptics).
- [Apple: Practice audio haptic design](https://developer.apple.com/videos/play/wwdc2021/10278/) — WWDC21 session 10278.
- [Apple: Expanding the Sensory Experience with Core Haptics](https://developer.apple.com/videos/play/wwdc2019/223/) — WWDC19 session 223; design reference.
- [Apple: Sharpness](https://developer.apple.com/documentation/corehaptics/chhapticevent/parameterid/hapticsharpness), [parameter curves](https://developer.apple.com/documentation/corehaptics/chhapticparametercurve), and [AHAP format](https://developer.apple.com/documentation/corehaptics/representing-haptic-patterns-in-ahap-files) — design and Core Haptics references; unversioned docs, checked 2026-09-05.
- [Apple: SensoryFeedback](https://developer.apple.com/documentation/swiftui/sensoryfeedback) and [trigger modifier](https://developer.apple.com/documentation/swiftui/view/sensoryfeedback(_:trigger:)) — unversioned docs, checked 2026-09-05.
- [Apple: prepare()](https://developer.apple.com/documentation/uikit/uifeedbackgenerator/prepare()) — unversioned docs, checked 2026-09-05.
- [Apple: Feedback selection](https://developer.apple.com/documentation/swiftui/view/sensoryfeedback(trigger:_:)) and [view-associated impact generator](https://developer.apple.com/documentation/uikit/uiimpactfeedbackgenerator/init(style:view:)) — sources for `references/swiftui-feedback.md`; unversioned docs, checked 2026-09-05.
- [Apple: Engine setup and recovery](https://developer.apple.com/documentation/corehaptics/preparing-your-app-to-play-haptics), [pattern players](https://developer.apple.com/documentation/corehaptics/chhapticpatternplayer), and [audio scheduling](https://developer.apple.com/documentation/avfaudio/avaudioplayer/play(attime:)) — sources for `references/core-haptics.md`; unversioned docs, checked 2026-09-05.

Written locally for SwiftUI apps targeting iOS 26+; no upstream prose or code
copied. Starts with event meaning and design, then SwiftUI state-driven feedback
or authored Core Haptics playback. Direct UIKit emission serves control and timing
needs, with no older-platform path. References connect worked designs, state and
playback ownership, sound, motion, and device tuning. Example values are local
proposals, not Apple presets. Automatic invocation uses the host defaults.

## launch-swarm

- Local: `skills/launch-swarm` (SreeStack).

## liquid-glass

- [haider-nawaz/liquid-glass-skill / plugins/liquid-glass/skills/liquid-glass](https://github.com/haider-nawaz/liquid-glass-skill/tree/2c1b2789c30dc2c9208f3b9a3811d42480714577/plugins/liquid-glass/skills/liquid-glass) — commit `2c1b2789c30dc2c9208f3b9a3811d42480714577`.

Local: added `disable-model-invocation: true` and
`allow_implicit_invocation: false`; upstream has neither setting.

## manual-verify

- Local: `skills/manual-verify` (SreeStack).

Focuses on audience and affected user workflows; uses a browser for web apps
and Simulator for iOS. Asks for user help with login or other user-only steps.

## post-merge-cleanup

- Local: `~/.agents/skills/post-merge-cleanup`.

Local: removed `disable-model-invocation: true` and set
`allow_implicit_invocation: true` so `pr-prep` can invoke cleanup after merging.
Accepts that handoff as authorization for task-owned cleanup.

## prototype

- [mattpocock/skills / skills/engineering/prototype](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/prototype) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

Adapted for UI prototypes across web, mobile, and desktop. Removed the logic
prototype path and combined the UI workflow into `SKILL.md`.

## react-doctor

- [millionco/react-doctor / skills/react-doctor](https://github.com/millionco/react-doctor/tree/79d80072817eb86c74f3dd42ce91c8104f448810/skills/react-doctor) — commit `79d80072817eb86c74f3dd42ce91c8104f448810`.

## refactoring-ui-skill

- [s0xDk/refactoring-ui-skill / SKILL.md](https://github.com/s0xDk/refactoring-ui-skill/blob/main/SKILL.md) — imported revision: unknown.

Source confirmed by Sree.

## research

- [mattpocock/skills / skills/engineering/research](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/research) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## resolving-merge-conflicts

- [mattpocock/skills / skills/engineering/resolving-merge-conflicts](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/resolving-merge-conflicts) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## review-fix-loop

- Local: `skills/review-fix-loop` (SreeStack).

Reviewer references:

- `references/standards.md` and `references/spec.md`: [mattpocock/skills / skills/engineering/code-review](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/code-review) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.
- `references/thermo.md`: [cursor/plugins / cursor-team-kit/skills/thermo-nuclear-code-quality-review](https://github.com/cursor/plugins/tree/a29f5a8ca161b1de4ffc5484454958bebc04eaa5/cursor-team-kit/skills/thermo-nuclear-code-quality-review) — commit `a29f5a8ca161b1de4ffc5484454958bebc04eaa5`.
- `references/ponytail.md`: combines these sources from `DietrichGebert/ponytail`
  at commit `974d940a1c5344210874150b98ff0d2c861fab6a`:
  - [ponytail](https://github.com/DietrichGebert/ponytail/tree/974d940a1c5344210874150b98ff0d2c861fab6a/skills/ponytail) — core language, ladder, and safety limits.
  - [ponytail-review](https://github.com/DietrichGebert/ponytail/tree/974d940a1c5344210874150b98ff0d2c861fab6a/skills/ponytail-review) — tags, examples, and review boundaries.
  - [ponytail-audit](https://github.com/DietrichGebert/ponytail/tree/974d940a1c5344210874150b98ff0d2c861fab6a/skills/ponytail-audit) — bloat targets and cut ranking.
  - [ponytail-debt](https://github.com/DietrichGebert/ponytail/tree/974d940a1c5344210874150b98ff0d2c861fab6a/skills/ponytail-debt) — shortcut ceilings and upgrade triggers.
  - [ponytail-gain](https://github.com/DietrichGebert/ponytail/tree/974d940a1c5344210874150b98ff0d2c861fab6a/skills/ponytail-gain) — limits on savings claims.

Local: Standards and Spec retain upstream’s reviewer briefs, 400-word limits,
smell baseline, and separation examples. The parent supplies scope and sources
and owns triage and fixes; references add evidence and coverage reporting.

Local: Ponytail keeps the supplied diff scope and read-only parent contract.
Retains repo reuse, proof for cuts, and coverage reporting. Omits persistent
modes, installation steps, benchmark displays, and whole-repo debt scans.

Local: folded the three former review skills into four read-only reviewer briefs.
Split Matt’s Standards and Spec rules, moved dispatch and scope to the parent,
and kept Thermo’s upstream language with a read-only, parent-scoped review contract.
References have no invocation settings. Code and mixed changes use the full loop:
Thermo runs on every pass, Gemini runs directly, and the parent sweeps findings,
fixes accepted issues, and verifies the result. Any fix in that loop starts another
full pass; completion requires a pass with no fixes needed. The model decides when
manual verification adds useful confidence based on behavior, risk, and test coverage.

Docs and skill instructions alone use one focused parent review, accepted fixes,
and targeted verification. Style preferences are optional; explicit writing rules
still apply. Executable skill scripts use the code loop. An explicit user request
for repeated full reviews overrides the focused path. Invocation choices stay unchanged.

## pr-prep

- Local: `skills/pr-prep` (SreeStack).

Renamed from `review-push-and-watch`; keeps publishing, CI, and feedback
references. Optional `yolo` authorizes merging this PR once requirements pass.
CI and feedback fixes return to publishing, without repeating the local review loop.
Runs `post-merge-cleanup` after a confirmed merge.

## review-sweep

- Local: `skills/review-sweep` (SreeStack).

## setup-matt-pocock-skills

- [mattpocock/skills / skills/engineering/setup-matt-pocock-skills](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/setup-matt-pocock-skills) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## showroom

- Local: `skills/showroom` (SreeStack).

## tdd

- [mattpocock/skills / skills/engineering/tdd](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/tdd) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

Local: point the review stage to `review-fix-loop`.

## teach

- [mattpocock/skills / skills/productivity/teach](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/productivity/teach) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## to-questionnaire

- [mattpocock/skills / skills/productivity/to-questionnaire](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/productivity/to-questionnaire) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## to-spec

- [mattpocock/skills / skills/engineering/to-spec](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/to-spec) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## to-tickets

- [mattpocock/skills / skills/engineering/to-tickets](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/to-tickets) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## triage

- [mattpocock/skills / skills/engineering/triage](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/triage) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## ui-component-inspiration

- Local: `skills/ui-component-inspiration` (SreeStack).
- [Kinetics](https://github.com/ckissi/kinetics) — motion examples and source search guidance.
- [Forever Components](https://forevercomponents.com/infinite/) — component manifest and source search guidance.
- [React Bits](https://reactbits.dev) — component catalog.
- [Magic UI](https://magicui.design/docs/components) — component catalog and Shimmer Button retrieval example, checked 2026-09-02.
- [Lightswind UI](https://lightswind.com/components) — component catalog.
- [Aceternity UI](https://ui.aceternity.com/components) — component catalog.
- [Hover.dev](https://www.hover.dev/components) — component catalog.
- [Motion](https://motion.dev/docs/react) — animation tool reference.
- [Superdesign](https://superdesign.dev) — design tool reference.

Sources are live references; no component code or catalog snapshot is bundled.
Local: manual-only in both hosts, with `disable-model-invocation: true` and
`allow_implicit_invocation: false`.

## wait-what

- [mattpocock/skills / skills/productivity/wait-what](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/productivity/wait-what) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## wayfinder

- [mattpocock/skills / skills/engineering/wayfinder](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/wayfinder) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## wizard

- [mattpocock/skills / skills/engineering/wizard](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/wizard) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

Local: added `disable-model-invocation: true` and
`allow_implicit_invocation: false` to make this skill manual-only.

## writing-for-agents

- [mattpocock/skills / skills/productivity/writing-for-agents](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/productivity/writing-for-agents) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.
