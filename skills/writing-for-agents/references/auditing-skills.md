# Auditing skills

Use an audit to ask: would we write this skill this way today? For a repo-wide
audit, rank skills by `SKILL.md` size and by lines added against lines removed in
`git log --numstat`. Audit one skill at a time, largest problem first.

Work on a draft outside the skill folder. Unless the request also asks for the
rewrite, end with the report and let the user decide.

1. **Record what must survive.** List the skill's invocation choice, required
   legal notices, the anchors and paths other files link to, its consumers, and
   decisions the user has already made. Read its project record, such as its
   entry in `SOURCES.md`, for context. Any other recorded behavior is a rule to
   test, not an automatic keep. Follow
   [revising skills](revising-skills.md#establish-the-baseline). Done: the
   original can be recovered and the list is complete.

2. **State the job.** Write one sentence for what the skill does. Collect real
   requests from its description, consumers, and session history. Add the rare
   cases its rules name. Done: each branch has at least one request.

3. **Draft fresh.** Write the skill from the job, the requests, and the survival
   list, using [the writing rules](../SKILL.md). Keep the old text closed. Done: a
   full draft that handles every request.

4. **Test the draft.** Run the requests against the old and new text in fresh
   sessions, on each model that uses the skill. Repeat uncertain cases. Done: both
   versions have results for every request.

5. **Compare.** Open the old text and list each rule the draft lacks or states
   more weakly. Group equivalent rules. Check `git log -S` or use
   [Why](../../why/SKILL.md) for any rule whose reason is not obvious. Then settle
   each group in this order:

   1. **Restore** a rule on the survival list. Also restore a guardrail against data
      loss, a security failure, unauthorized or irreversible action, a false pass,
      lost review independence, or colliding writers. Skip it only if you can cite a
      draft line that states it at equal strength, before the action it constrains.
   2. **Drop** a no-op, a duplicate, a fact the environment holds, or a rule whose
      reason is obsolete. Name the surviving line or the evidence. A weaker version
      is not a duplicate. A no-op needs a passing run on each model that uses the
      skill.
   3. **Restore** a rule when a request failed without it, or when you can name the
      failure it still prevents.
   4. **Restore a rule with an unknown reason** only if it fits a plausible failure,
      and add a request that exercises it.
   5. **Drop** the rest. If you suspect a no-op or duplicate but lack the evidence in
      item 2, get it or restore the rule.

   Write restored rules in the draft's voice, and rerun the affected and added
   requests. Done: every group has a decision and a reason, and every request has a
   result against the final draft and the old text.

6. **Report.** Give the size before and after, each dropped group and why, rules
   kept with an unknown reason, each request's result against the final draft, and
   remaining gaps. If the draft replaces the skill, update its project record and
   follow [check and accept](revising-skills.md#check-and-accept).
