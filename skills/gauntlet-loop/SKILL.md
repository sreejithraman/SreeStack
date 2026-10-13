---
name: gauntlet-loop
description: Turn a goal into a short, paste-ready prompt for a builder-and-critic loop against a real quality bar.
disable-model-invocation: true
---

# Gauntlet Loop

Write one short prompt the user can paste into a fresh agent session. The prompt
directs builders and independent critics to improve the work until it wins a
blind comparison against a real reference. Creating the prompt is the task;
execute it only when the user asks to run it.

## Choose the bar

Read the goal and any constraints. Use the user's supplied reference when it
passes all three checks:

- **Named:** a specific artifact, such as a particular pricing page or published
  article, rather than a category such as “award-winning sites.”
- **Fetchable:** the executing agent can obtain the actual page, text, repo,
  binary, or footage. An inaccessible reference needs a supplied copy or a
  replacement; a description of it cannot stand in for the artifact.
- **Comparable:** the reference and the output can be judged side by side under
  equivalent conditions, with a clear choice between them.

If the reference is missing or unsuitable, offer two or three concrete candidate
bars, one line each, and wait for the user's choice before writing the prompt.
Prefer demanding references the executing agent can actually reach. Resolve
general names to specific artifacts; verify current pages or publications when
needed rather than inventing a title or URL.

| Goal | Suitable reference and comparison |
| --- | --- |
| Website, app, UI | A specific product page or screen at the same viewport |
| Game, 3D, visual | Footage or screenshots from a named shipped title |
| Writing | A particular published piece with comparable length, audience, and format |
| Code, tooling | A named repo's implementation plus relevant tests or benchmarks |
| Research, analysis | A particular report or methods section, judged for rigor and coverage |
| Deck, document | A real artifact with comparable format and page count |

Where the goal has measurable requirements, include them alongside the reference:
for example, load time, benchmark score, word count, or pass rate. A favorable
taste judgment does not replace those requirements.

## Write the prompt

Return one fenced, paste-ready block without a preamble, headings inside the
prompt, or a narrated explanation. Aim for 120–180 words in plain sentences.
Adapt this template to the goal and selected bar:

```text
Build [GOAL].

The bar is [SPECIFIC REFERENCE]. Obtain the real artifact first and compare directly against it under equivalent conditions.

Break the work into the smallest pieces that can be improved and judged independently. For each piece, use a builder and a separate critic with fresh context; run independent pieces in parallel. Give the critic the actual output and reference without builder commentary. Strip identifying labels and randomize A/B order where possible. If identity remains recognizable, disclose that limit.

The critic must be harsh: pick the better artifact and name the single biggest remaining gap. Send that gap back to the builder and repeat until ours wins and measurable requirements pass. Finish with a comparison of the integrated result against the full bar. Stop if I stop the run; report a blocked comparison instead of declaring a win when the reference or independent critic is unavailable.

Keep a live progress page I can inspect as the work evolves.
```

Keep the prompt focused on the goal, bar, independent evaluation, and completion
criterion. Add a budget or cost ceiling only when the user supplied one. Include
tools, architecture, stack, file layout, or other implementation choices only
when the goal requires them or the user specified them. Let the executing agent
choose the decomposition. Winning the comparison is the quality exit; an
arbitrary round count is not.

Use portable instructions for iteration and parallel subagents. Include
host-specific commands only when their availability and behavior are verified
for the intended host. Prompt generation needs no subagent or scheduler tools;
running the loop requires independent agents and access to the reference and
actual output. A request to run the prompt authorizes its builder/critic workflow,
subject to the user's scope and the host's permissions.

After the block, add only: “I can run this here.” If the user asks to run it,
become the lead agent and follow the generated prompt with the available tools.
Report missing execution capabilities before starting dependent work. Keep the
progress page within the task's authorized workspace; publishing it requires
the user's requested publication scope.
