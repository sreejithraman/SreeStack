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
that path. Include any permitted source delegation and its bounds in the brief.
When dispatched as the researcher, own the investigation and synthesis;
assign additional children only when the brief permits it.

## Source routing

Define the evidence needed and identify source access prerequisites. Prefer
suitable direct retrieval. When required evidence needs tools unavailable to
the current agent, resolve the configured source preferences in
[agent routing](../orchestration/references/agent-routing.md#model-defaults),
preserving user overrides. Use orchestration to dispatch bounded retrieval to
an available agent with suitable tools. A tool fetch error alone does not
establish a permission or policy denial; distinguish retrieval limits from
access restrictions before using another permitted route. Follow the
[denial and recovery policy](../orchestration/references/agent-routing.md#recover-work);
report a gap when no permitted route can supply the evidence.

Request original source content or grounded extracts/paraphrases, canonical
URLs, relevant dates/timestamps, retrieval provenance and modality (actual
video, captions, metadata, native source tools), and precise access gaps.
Inspect returned evidence against the requested claims before synthesis.
A child summary or claimed model capability alone does not prove retrieval;
captions or metadata support only claims grounded in that modality.

## Findings and acceptance

1. Follow factual claims to primary sources: official documentation, source
   code, specifications, datasets, or first-party APIs. Record the revision/date
   and limits of the evidence; distinguish findings from inference.
2. Write one Markdown note with a direct answer, claim-level citations,
   unresolved gaps, and implications for the requested decision.
3. Inspect the note and sources before accepting it. Finish when the question
   is answered with the required evidence, or report exactly what remains
   unsupported and what would resolve it. Return the note path and conclusion.
