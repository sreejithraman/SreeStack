---
name: handoff
description: Transfer or resume unfinished work through a compact handoff document.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Transfer operational state, not a transcript summary. If the user asks for a handoff, write a document in the OS temporary directory, outside the workspace. Tailor it to the next session the user describes.

Record the goal and definition of done; branch, worktree, and relevant commit or PR; what is complete and verified; what is pending or blocked; decisions that still constrain the work; exact artifact paths; and the first useful action on resume. Distinguish work saved on disk from an uncommitted or unpushed state. Include a short suggested-skills section only for skills the next agent will need. Point to specs, plans, ADRs, issues, diffs, and evidence rather than copying them. Redact secrets and personal data.

If the user asks you to resume from a handoff, read its linked artifacts and reconstruct the current branch, worktree, and external state before acting. Compare completed work with pending work and name the resume point. Treat the handoff as orientation: verify inherited claims that affect the next action against current code, artifacts, or remote state. Continue the requested work without redoing completed steps whose evidence still applies.

Creating a handoff does not itself authorize a commit, push, PR, or pause. Before finishing, check that the next agent can act from the note and its linked artifacts without this conversation. Report the document path and any state that could not safely be captured.
