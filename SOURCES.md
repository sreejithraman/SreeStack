# Upstream sources and local differences

Use this file when updating imported skills. Each entry records the upstream
material, the revision last imported, and current local differences.
Source mappings also cover imported references inside locally written skills.
See [AGENTS.md](AGENTS.md) for maintenance rules and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for license notices and gaps.

Commits are import baselines, not the latest versions checked. Unknown means the
baseline was not recorded. A local source path does not prove original authorship.
An entry without a difference note does not prove that its files match upstream.

Keep one entry per skill and one bullet per imported source, followed by plain
descriptions of current local differences, including invocation choices.
Local-only skills need just an origin note.

## animate

- [emilkowalski/skills](https://github.com/emilkowalski/skills) — `skills/animate`; commit: unknown.

Local differences are not recorded.

## app-store-connect

- [rorkai/app-store-connect-cli-skills](https://github.com/rorkai/app-store-connect-cli-skills/tree/9813732f640495bdb7bd1f894f5df499c76cfbcf) — `skills/`; commit `9813732f640495bdb7bd1f894f5df499c76cfbcf`, imported 2026-09-08. Author: Rudrank Riyam; MIT notice in `licenses/rudrankriyam-app-store-connect-cli-skills.txt`.

- One discoverable skill: upstream `skills/asc-cli-usage/SKILL.md` supplies the
  entrypoint; the other `skills/<name>/SKILL.md` files map to local
  `references/<name>/guide.md`. Guides retain supporting paths and local links
  and omit skill frontmatter. The skill omits upstream scripts and app settings.
- Guide selection by task, checks against the installed CLI, and IDs and release
  rules from the project. API key creation requires a setup request. Apple Ads
  detail lives in its guide only.
- Screenshot cleanup uses working copies; associative-array examples require
  Bash 4. The guides qualify unsupported ranking claims and distinguish App Store
  description, promotional text, and release-note guidance.

## codebase-design

- [mattpocock/skills / skills/engineering/codebase-design](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/codebase-design) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## design-eng

- [emilkowalski/skills](https://github.com/emilkowalski/skills) — `skills/emil-design-eng`; commit: unknown.
- [emilkowalski/skills](https://github.com/emilkowalski/skills) — `skills/apple-design`; commit: unknown.

Combines both upstream sources in one skill. Invocation is
manual-only: `disable-model-invocation: true` and
`allow_implicit_invocation: false`.

## diagnosing-bugs

- [mattpocock/skills / skills/engineering/diagnosing-bugs](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/diagnosing-bugs) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## domain-modeling

- [mattpocock/skills / skills/engineering/domain-modeling](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/domain-modeling) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## eli5

- [anthropics/claude-plugins-community / eli5/skills/eli5](https://github.com/anthropics/claude-plugins-community/tree/f4c9452f5ca091f1be7064d9faab1b001ea21645/eli5/skills/eli5) — commit `f4c9452f5ca091f1be7064d9faab1b001ea21645`.

## frontend-web-design

- [anthropics/skills / skills/frontend-design](https://github.com/anthropics/skills/tree/34040c9c568585f6929bedeaad110ad08f079624/skills/frontend-design) — commit `34040c9c568585f6929bedeaad110ad08f079624`.

Renamed to `frontend-web-design`, with a web-only description. Removes the
AI-default calibration list and guidance tied to it, while keeping the rule to
follow the brief. Omits the license frontmatter field and license file. The rest
of the upstream wording remains. Automatic discovery stays enabled.

## goal-bee

- Local: `skills/goal-bee` (SreeStack).

## gemini

- Local: `skills/gemini` (SreeStack).

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

Uses `review-fix-loop` to review, fix, and verify before committing.

## improve-codebase-architecture

- [mattpocock/skills / skills/engineering/improve-codebase-architecture](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/improve-codebase-architecture) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

Returns findings, recommendations, and reasons in chat; creates an HTML report
only on request.

## ios-haptics

- Local: `skills/ios-haptics` (SreeStack).

## swarm-and-push

- Local: `skills/swarm-and-push` (SreeStack).

## liquid-glass

- [haider-nawaz/liquid-glass-skill / plugins/liquid-glass/skills/liquid-glass](https://github.com/haider-nawaz/liquid-glass-skill/tree/2c1b2789c30dc2c9208f3b9a3811d42480714577/plugins/liquid-glass/skills/liquid-glass) — commit `2c1b2789c30dc2c9208f3b9a3811d42480714577`.

Manual-only invocation: `disable-model-invocation: true` and
`allow_implicit_invocation: false`; upstream has neither setting.

## manual-verify

- Local: `skills/manual-verify` (SreeStack).

## post-merge-cleanup

- Local source: `~/.agents/skills/post-merge-cleanup`; upstream origin unrecorded.

## prototype

- [mattpocock/skills / skills/engineering/prototype](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/prototype) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

UI prototypes for web, mobile, and desktop; no logic-prototype mode.

## react-doctor

- [millionco/react-doctor / skills/react-doctor](https://github.com/millionco/react-doctor/tree/79d80072817eb86c74f3dd42ce91c8104f448810/skills/react-doctor) — commit `79d80072817eb86c74f3dd42ce91c8104f448810`.

## refactoring-ui-skill

- [s0xDk/refactoring-ui-skill / SKILL.md](https://github.com/s0xDk/refactoring-ui-skill/blob/main/SKILL.md) — imported revision: unknown.

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

- Imported material stays in read-only reference briefs. The local parent skill
  supplies scope and owns dispatch, triage, fixes, and acceptance.
- Standards and Spec remain separate checks and labeled reports, with their
  upstream smell baseline, requirements checks, and 400-word limits.
- Thermo keeps its structural review criteria within the parent's supplied scope.
  Structural suggestions require evidence and a concrete benefit; the parent
  decides which fixes to accept.
- Ponytail keeps reuse, evidence for cuts, and coverage reporting within the
  supplied diff. Persistent modes, install steps, benchmark displays, and the
  upstream debt skill's whole-repo ledger are excluded. The brief limits savings
  claims to observed local evidence.

## pr-prep

- Local: `skills/pr-prep` (SreeStack).

## review-sweep

- Local: `skills/review-sweep` (SreeStack).

## setup-matt-pocock-skills

- [mattpocock/skills / skills/engineering/setup-matt-pocock-skills](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/setup-matt-pocock-skills) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## showroom

- Local: `skills/showroom` (SreeStack).

## tdd

- [mattpocock/skills / skills/engineering/tdd](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/tdd) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

The review stage uses `review-fix-loop`.

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

## wait-what

- [mattpocock/skills / skills/productivity/wait-what](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/productivity/wait-what) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## wayfinder

- [mattpocock/skills / skills/engineering/wayfinder](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/wayfinder) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

## wizard

- [mattpocock/skills / skills/engineering/wizard](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/engineering/wizard) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.

Manual-only invocation: `disable-model-invocation: true` and
`allow_implicit_invocation: false`.

## writing-for-agents

- [mattpocock/skills / skills/productivity/writing-for-agents](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/productivity/writing-for-agents) — v1.2.3, commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.
