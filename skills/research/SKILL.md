---
name: research
description: Investigate a question against primary sources and record cited findings. Use when research, documentation or API facts, or background reading are requested.
---

# Research

Own a question and the evidence needed to answer it. Resolve the decision,
scope, and an output path using the repo's research-note convention. Apply
[agent routing](../orchestration/references/agent-routing.md#model-defaults)
before investigating, including when working directly.

When independent reading helps another owner continue useful work, use
[orchestration](../orchestration/SKILL.md) to delegate a bounded question with
that path. When dispatched as the researcher, do the research directly;
assign additional children only when the brief permits it.

1. Follow factual claims to primary sources: official documentation, source
   code, specifications, datasets, or first-party APIs. Record the revision/date
   and limits of the evidence; distinguish findings from inference.
2. Write one Markdown note with a direct answer, claim-level citations,
   unresolved gaps, and implications for the requested decision.
3. Inspect the note and sources before accepting it. Finish when the question
   is answered with the required evidence, or report exactly what remains
   unsupported and what would resolve it. Return the note path and conclusion.
