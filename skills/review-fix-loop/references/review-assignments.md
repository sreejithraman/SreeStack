# Review assignments

Every reviewer reads the complete change using [Review](../../review/SKILL.md).
The assignment selects its criteria, not its files. The parent owns acceptance.

| Assignment | Criteria | Selection |
| --- | --- | --- |
| Primary | Correctness, regressions, security/data loss, test gaps; [Spec](../../review/references/spec.md) and [Standards](../../review/references/standards.md) | Primary review default |
| Ponytail | Proven simplification, deletion, reuse, and root-cause repairs using [Ponytail](../../review/references/ponytail.md) | Random alternate |
| Thermo | Structure, boundaries, abstractions, types, and concrete design improvements using [Thermo](../../review/references/thermo.md) | Another random alternate |

Primary owns Review's applicable indirect-consumer and React/Next checks,
including react-best-practices and React Doctor evidence. Keep those reports
and Spec/Standards separately labeled. All reviewers apply requirements, repo
rules, and evidence standards; report material issues noticed outside the lens.
For instructions, trace realistic requests and assess workflow complexity and
boundaries. For ordinary prose, use Review's documentation criteria.

Give reviewers their criteria, references, and the canonical
[review brief](../../review/references/review-brief.md). That brief owns snapshot
contents, first/later-round context, read-only limits, and peer isolation.
Keep the coordination rules below with the parent.

## Draw and retain the mapping

Use this draw only when Prepare selected the three-assessment round. Parent
review and a single-primary round need no alternate mapping.

Resolve the alternate rows in [model defaults](../../orchestration/references/agent-routing.md#model-defaults)
using agent routing. Record excluded targets and why. Fill up to two slots in
ascending alternate priority, randomly sampling within a tier when it has more
eligible candidates than open slots. Select different models/families; different
provider instances of one model are not diversity. Randomly assign the selected
pair to Ponytail and Thermo.

If only one alternate is eligible, randomly choose its lens; use a fresh
primary-review task for the other. If none are eligible,
use separate primary tasks for both lenses. This permitted fallback retains
all three assessments and discloses lost diversity. Explicit user model/diversity
requirements take precedence.

Record one mapping per loop. Retain it through fixes; replace only the affected
assignment when a target becomes unavailable, preserving its peer. A user
policy change can require reselection. Every round still uses fresh tasks.

## Replace a failed alternate

Follow agent routing's execution recovery: distinguish uncertain dispatch from
terminal failure, permit its bounded transient retry, and respect denials.
Recheck the snapshot before replacement; a moved snapshot needs a new round.
Retain useful findings and the failure cause.

After permitted recovery is exhausted, exclude the failed alternate for this
loop. Exclude its peer's model and prefer a different family. Draw from the
lowest-numbered remaining eligible priority tier, randomly within that tier.
If none remain, use a fresh primary task
for that lens. Preserve peer results only for the unchanged snapshot. Record
the replacement and new task IDs/keys. A failed required primary or fallback
assessment is blocked coverage; preserve that gap rather than reducing the trio.

## Resolve disagreement

Preserve assignment/model provenance when consolidating findings. No findings
with incomplete coverage is not a pass. Ponytail may remove a layer while Thermo
extracts a boundary; Sweep judges actual consumers, requirements, and benefit.
Use [Sweep classification](../../review-sweep/references/classification.md)
for the blocking bar and dispositions.
