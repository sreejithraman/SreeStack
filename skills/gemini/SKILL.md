---
name: gemini
description: Prompt Gemini headlessly for a second opinion, research, analysis, or code review.
---

# Gemini

Give Gemini a self-contained task: the question, relevant context, scope,
constraints, and the kind of answer you need. It cannot see this conversation.
Include the facts it needs without steering it toward your preferred conclusion.
For an independent opinion, leave out earlier reviewers' conclusions.

Send the prompt headlessly through agy and wait for the answer. Use
[headless.md](references/headless.md) for headless configuration. Start fresh for a
new task; keep the same conversation when asking a follow-up.

For code or docs review, use [review.md](references/review.md). Code and mixed
changes use agy's native code-review skill with the complete evidence packet,
caller's exact scope, and read-only repository inspection. Documentation-only
changes use a plain review prompt with the evidence packet. Keep analysis
read-only unless the caller asks for changes.

Assess the answer against the task and available evidence. Follow up when a
material gap needs clarification. Tell the caller what Gemini found, what you
recommend and why, and any limits or disagreements. An incomplete run is not
an answer.
