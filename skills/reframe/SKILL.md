---
name: reframe
description: Use when asked to reframe a task, raise its ambition, improve a prompt, or define acceptance criteria, or when a workflow needs a brief.
---

# Reframe

Turn a request and its context into an execution-ready brief. Start from a user
request, prompt, or calling workflow's context. Leave a concise brief (or a
copyable prompt when prompt rewriting was asked) with preserved constraints and
evaluation criteria. You are done when the brief (or copyable prompt) is
returned to the caller with the required fields below.

Preserve explicit requirements while considering stronger ways to achieve the
outcome. Scale the pass to what is unsettled: a precise request may need only a
short confirmation.

## Find the better task

Read the request, settled decisions, and relevant project evidence. Separate the
desired result from the proposed means or artifact, and label alternatives beyond
authorized scope as proposals. Use
[acceptance guidance](references/acceptance.md) to resolve what context can
establish and ask for material user decisions.

Consider the dimensions that can improve this task:

- **Outcome:** who needs what change, and what decision or activity does the
  requested artifact serve? When useful, compare the artifact, the outcome it
  serves, and a lasting workflow that improves that outcome. Explore whether a
  substantially harder target is feasible; distinguish proposed stretch targets
  from the agreed finish line.
- **Depth:** which original inputs, expert methods, and instruments would make
  the work more rigorous? Test consequential assumptions against raw evidence.
  Consider what new finding could change the decision and how to test it;
  predictive claims need evaluation on unseen evidence. Name the method rather
  than an expert persona.
- **Range:** describe what the work must accomplish as activities, then ask which
  adjacent field handles them well. Choose a concrete technique and its tools.
- **Evaluation:** how and by whom should the result be judged, which constraints
  must hold, and what finish line was requested? Use the acceptance guidance to
  propose suitable checks or qualitative criteria, leaving uncertainty and
  missing prerequisites explicit.

Choose the strongest coherent framing rather than expanding every dimension;
extra deliverables must earn their place. Use [Research](../research/SKILL.md)
for factual uncertainty worth investigating, and run experiments to settle
empirical questions within requested scope. Keep ambitious targets distinct from
evidence that they have been achieved.

Name the data, tools, environments, and access needed to execute and evaluate the
chosen approach, separating available resources from missing setup. For a lasting
workflow, identify its signal, action, feedback, and owner; keep setup and
ongoing operation within the authorized scope, and treat a proposal alone as
authorizing neither automation nor recurring execution.

## Return the brief

State the outcome and target, the code it covers, preserved constraints, what is
out of scope, relevant methods, evaluation, requested finish line, material
assumptions and unknowns, and any meaningful framing changes. Proposed evaluation
is not evidence of achievement. Reuse the existing format and task record; a
clear request can be confirmed in a few sentences without a separate document.
When prompt rewriting is the requested product, return a copyable prompt with the
outcome, preserved constraints, methods, and evaluation.

When another workflow calls Reframe, return the brief to that owner without
starting another copy of its workflow. For a direct reframing request, return the
brief in chat unless another format or destination was requested; if the user
also requested execution, hand the brief to the authorized execution workflow.
Reframing alone authorizes no implementation, native goal, schedule, or external
action.
