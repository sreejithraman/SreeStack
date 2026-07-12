# Goal Prompts

Use this template for the parent goal and for each shard `/goal` prompt.

```text
/goal

Objective:
<single concrete outcome>

Success:
- <observable proof>
- <expected return format>

Scope:
- Own: <files, modules, questions, docs, tests, workflows, or artifact>
- Do not touch: <reserved files, responsibilities, or non-goals>

Inputs:
- <paths, commands, URLs, screenshots, prior findings, issue links>

Constraints:
- <style, budget, network, side effects, compatibility, time limits>
- Shared-codebase rule: preserve user and agent work, adapting to concurrent edits.

Validation:
- <commands, checks, review criteria, manual verification surface>

Return:
- <findings, patch summary, changed files, commands run, blockers, residual risks>
```
