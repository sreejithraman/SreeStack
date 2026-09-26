---
name: code-why
description: Investigate code history to explain a design decision's rationale, when and why a regression was introduced, or whether an old constraint still applies. Use diagnosing-bugs for an active defect.
---

# Code Why

Answer historical intent from records, not from a plausible reading of today's code. Keep observed behavior and motivation separate.

If the requested outcome is to diagnose or repair a current failure, use `diagnosing-bugs` for that work. Use this skill for a separate question about the failure's history.

1. **Anchor the question.** Identify the exact code, symbol, behavior, or decision in question. Read enough current code to understand what it does, then inspect its blame and history, following renames where relevant.
2. **Follow the decision trail.** Read the introducing or changing commits and substantive PR discussion. Follow linked issues, design documents, incidents, or other available records when they could explain the decision. Search proportionally to the question; do not fan out across every connector by default. Record which promising sources were searched, empty, or unavailable.
   For a question about when a regression began, distinguish the commit that changed code from the first revision where the symptom occurred. Compare passing and failing revisions with an existing test, replay, bisect, or dated incident evidence when feasible; run revision checks in an isolated checkout. Without that evidence, call a commit a candidate and leave symptom onset unknown.
3. **Grade each explanation.** Distinguish an explicit contemporary statement of rationale, several independent records that support an explanation, an inference from context, a plausible guess, and an unknown. Code shape alone proves behavior, not author intent. Surface conflicting accounts and whether a documented constraint still holds; do not select the tidier story without evidence.
4. **Answer and apply.** Cite the record beside each historical claim. State what the code does now, why the record says it was shaped that way, what remains uncertain, and any current constraint a proposed change should preserve or revisit. If no rationale survives the search, say so and name the search coverage.

This is a read-only investigation unless the user also asks for a code or documentation change. Keep private records within the audience authorized to see them.
