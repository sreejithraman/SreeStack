# Evidence

## Read logs safely

Read structure, field names, and the records you need. Never print secrets:
session bodies can hold tokens, keys, env files, and pasted credentials. Quote
only what a finding needs, and redact anything that looks like a secret.

A skill named in a message was not used. A skill read was not applied. Count a
use only from an observed load and the behavior that follows it. Keep a missing
value unknown, never zero. Resumed, forked, and subagent sessions repeat
history: join them by stable IDs and lineage before counting.

## Sources

- **T3 Code:** use `t3_thread_search` and `t3_thread_read` first. Reads are
  paginated and carry run identity, model, status, and timestamps; they don't
  establish complete token or cost telemetry. Its SQLite state under
  `~/.t3/userdata/` is a read-only fallback for discovery, not a stable
  contract.
- **Claude Code:** `~/.claude/projects/<project>/<session>.jsonl`. Records carry
  UUIDs, parent links, timestamps, model, effort, tool blocks, and per-message
  usage, plus API-request records, cumulative `cost-state` snapshots,
  compaction, and PR links. Don't sum cumulative cost snapshots, and don't count
  an API record and its assistant message as two requests.
- **Codex:** `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`. Records carry
  session metadata, turn context, function calls and results joined by call ID,
  token usage, compaction, and inter-agent metadata. The path date is the
  session's start, not the window you observed. Usage has input, cached input,
  cache-write input, output, reasoning output, and total. Check whether each
  record is cumulative or per response before adding, and don't add reasoning
  twice. Code-mode nested calls and inherited histories need explicit handling.

## Metrics

| Metric | Definition |
| --- | --- |
| Review cost per accepted issue | Reviewer cost over a scoped PR window, zero-yield rounds included, divided by distinct accepted in-scope issues. Use reported cost; label an estimate with its rate date and cache treatment. Zero accepted issues gives no ratio: report total spend. Report the owner's repair cost separately, and rejected, duplicate, and optional findings apart. |
| Review rounds per PR | Distinct assessment rounds on identified snapshots, joined across delegates, with accepted issues per round. Retries and parallel reviewers are not new rounds by themselves. |
| Try stopping before review | Real Try outcomes with no request for review or a PR, checked in ordered activity for review or publication before handback. A quiet final message is not enough. |
| TDD batch size | New test behaviors between meaningful red and green runs, from file diffs and test executions. Report the test-count proxy apart from the behavior count; bulk-edit call counts mislead. |
| Trial versus real mismatch | A frozen expectation joined to a later comparable real outcome, with the assertion it violated. Without a comparable real run, it is unobserved. |
| Skill firing | Eligible requests against observed loads, plus near misses. Label eligibility without seeing whether it fired. A prompt that names the skill measures adherence, not discovery. |

Start with a bounded recent sample of SreeStack PRs and every real Try and TDD
example in the same window.
