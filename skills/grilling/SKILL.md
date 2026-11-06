---
name: grilling
description: Use when the user asks to grill or stress-test a plan, decision, or idea.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask _now_ without guessing at answers you haven't heard yet.

Ask a frontier decision only when it would change the outcome and you can't tell what the user would choose. Always ask one that risks data loss, exposes private data, weakens security, or can't be undone. Put the rest in one **Assuming** block after the questions, one line each. Ask the questions in one round, highest stakes first: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Each question should be formatted like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Each round the user answers reshapes the tree — settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent to find it — don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report — ask the rest of the frontier now.

The session is done when no open decision would change the result and nothing is left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.
