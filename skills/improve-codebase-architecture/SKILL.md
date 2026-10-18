---
name: improve-codebase-architecture
description: Find structural improvements, compare designs, and produce evidence-backed architecture recommendations or migration plans. HTML reports are optional.
disable-model-invocation: true
---

# Improve Codebase Architecture

Resolve project, legacy, or custom glossary paths with [glossary paths](../domain-modeling/references/glossary-paths.md) before reading or writing the domain vocabulary.

Surface architectural friction and propose **deepening opportunities**: refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

Own structural improvement. [Correct](../correct/SKILL.md) owns mining repeated
agent mistakes and proving their prevention. Use its findings as inputs when
the requested architecture work addresses an evidenced failure class.

Use [Redesign From First Principles](../engineering-principles/references/redesign-from-first-principles.md)
when shaping a candidate,
[Model the Domain](../engineering-principles/references/model-the-domain.md)
when ownership changes, and
[Migrate Callers Then Delete Legacy APIs](../engineering-principles/references/migrate-callers-then-delete-legacy-apis.md)
when moving callers. Codebase Design supplies the module vocabulary and interface
techniques used below.

## Choose the finish line

Default to interactive exploration: present candidates, let the user select one,
then explore its design together. When the user requests an autonomous
investigation or a plan backed by experiments, carry promising candidates
through design and technical checks before returning the recommendation.
Resolve routine technical questions from the repository and experiments. Ask
only when a missing product choice, access, or scope decision changes the result.
Both paths produce recommendations; a planning request does not authorize
production refactoring.

This command is _informed_ by the project's domain model and built on a shared design vocabulary:

- Apply the skill "codebase-design" for the architecture vocabulary (**module**, **interface**, **depth**, **seam**, **adapter**, **leverage**, **locality**) and its principles (the deletion test, "the interface is the test surface", "one adapter = hypothetical seam, two = real"). Use these terms exactly in every suggestion, and don't drift into "component," "service," "API," or "boundary."
- The domain language in `GLOSSARY.md` gives names to good seams; ADRs in `docs/adr/` record decisions this command should not re-litigate.

## Process

### 1. Explore

**Scope before you scan: YAGNI.** Deepening a module pays off by making future changes to it easier, so put extra weight on the parts of the codebase that have recently changed. Decide *where* to look before you look:

- If the user named a direction (a module, a subsystem, a pain point), take it, and skip the inference below.
- Otherwise, walk back a good stretch of the commit history (`git log --oneline`) to find the codebase's hot spots, the files and areas that keep coming up, and let those paths pull your attention first. If the changes are scattered with no clear hot spot, widen the net.

Read the project's domain glossary (`GLOSSARY.md`) and any ADRs in the area you're touching first.

Then use [orchestration](../orchestration/SKILL.md) to assign a read-only
exploration of that scope, with paths, domain vocabulary, ADRs, and an
evidence-backed findings report as its completion criterion. Give the child these
friction questions and ask it to explore organically:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow**, with an interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their current interface?

Have the child also apply Codebase Design's
[ownership and enforcement checks](../codebase-design/references/preventing-mistakes.md)
to evidenced friction in this scope. The child returns recommendations without
implementing them.

Include the **deletion test** in the brief: would deleting a suspected shallow
module concentrate complexity, or just move it? A "yes, concentrates" is the
signal to investigate. Accept the child's findings against the assigned scope
and evidence before making recommendations.

### 2. Share findings and recommendations

Default to a concise, high-level response in chat. Lead with the change you
recommend first and why it matters. For each worthwhile candidate, explain:

- **Finding** — where the current design causes friction, with a brief example
  or file link that supports it.
- **Recommendation** — what should change, in plain language.
- **Why** — the expected benefit, key tradeoffs, and why it is worth doing.
- **Confidence** — `Strong`, `Worth exploring`, or `Speculative`.

Use the project's domain terms and the `/codebase-design` vocabulary. Keep
implementation detail for the follow-up discussion. If no change is worth
recommending, say so and explain why.

If a candidate conflicts with an ADR, explain why the observed friction warrants
revisiting that decision. Only include conflicts worth reopening.

Create an HTML report only when the user asks for one. For that path, read
[HTML-REPORT.md](HTML-REPORT.md) for the format and diagrams. Write it to
`<tmpdir>/architecture-review-<timestamp>.html`, using `$TMPDIR` or `/tmp`
(`%TEMP%` on Windows). Open it with the platform's file opener and share its
absolute path. Include the high-level recommendation in chat too.

For interactive exploration, ask which candidate the user wants to explore
before designing interfaces. For an autonomous investigation, select the
strongest candidate or compare candidates when the evidence leaves a real
tradeoff, then continue below.

### 3. Explore the design

For interactive exploration, apply "grilling" after the user picks a candidate:
constraints, dependencies, the shape of the deepened module, what sits behind
the seam, and what tests survive. For autonomous investigation, work through
those questions from the code, ADRs, and evidence; bring back only questions
that require the user's judgment or unavailable access.

When a decision rests on an untested technical assumption, run a focused
[architecture experiment](references/experiments.md). Compare actual caller
requirements, migration cost, and enforceable invariants. Use the shared
measurement guidance linked there for performance claims. Return commands,
observations, and limits; keep unrun proposals distinct from checked designs.

During interactive design, apply "domain-modeling" as decisions crystallize:

- **Naming a deepened module after a concept not in `GLOSSARY.md`?** Add the term to `GLOSSARY.md`. Create the file lazily if it doesn't exist.
- **Sharpening a fuzzy term during the conversation?** Update `GLOSSARY.md` right there.
- **User rejects the candidate with a load-bearing reason?** Offer an ADR, framed as: _"Want me to record this as an ADR so future architecture reviews don't re-suggest it?"_ Only offer when the reason would actually be needed by a future explorer to avoid re-suggesting the same thing; skip ephemeral reasons ("not worth it right now") and self-evident ones.

For autonomous planning, record proposed glossary and ADR changes in the plan
for review. When exploring alternative interfaces, use Codebase Design's
[design-it-twice guidance](../codebase-design/DESIGN-IT-TWICE.md) to compare
structurally distinct designs through arena; check technical assumptions with
experiments where proposals alone cannot distinguish the options.

### 4. Return a usable plan

When a migration plan is requested, connect the finding to the recommended
interface and owner, affected callers and compatibility paths, migration order,
enforcement, and verification. Explain tradeoffs and rejected alternatives using
the evidence actually gathered. Include experiment artifacts and commands, and
label checks still proposed. State any ADR or domain vocabulary changes needed.

Interactive findings are complete when worthwhile candidates have evidence,
reasons, and confidence. A requested design or plan is complete when its
technical uncertainties have been checked or have explicit evidence gaps and
next checks, and the migration and proof are concrete enough to review.
Production implementation follows only within the user's requested scope and
uses the existing implementation, review, and verification workflows. Use
[architect](../architect/SKILL.md) when the selected design needs to guide
implementation; carry forward the findings and experiments already checked.
