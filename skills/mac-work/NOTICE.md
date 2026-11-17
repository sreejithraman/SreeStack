# Local queue modifications

Block's agent-task-queue at commit
`48d16da41f57801bbf9462ed2df923713978b6ae` is licensed under
[Apache-2.0](licenses/agent-task-queue.txt). Its package metadata credits
Matt McKenna and Block. No upstream NOTICE file exists in that archive.

SreeStack's local patch changes `queue_core.py`, `tq.py`, `task_queue.py` and
`pyproject.toml`, and adds `queue_lifecycle.py`. It serializes nondestructive
initialization, atomically records admission clocks, serializes cancellation with
gated launch, isolates gate imports, validates existing state, records launch
identities, consolidates lifecycle closure and
receipts, persists configuration, and retains unresolved admission rows. Modified
Python files carry a change notice. The added lifecycle module carries its own
Apache-2.0 SPDX/copyright notice. The runner revision adds atomic operation/task associations, one worker claim per
operation, and verified pre-launch abort closure. The built version is
`0.4.1+macwork.4`.

The patch retains the upstream SQLite/FIFO admission implementation. It does not
establish arbitrary detached-descendant containment or a production-ready shared
Mac command route. Keep this notice and the upstream license with redistributed
patches or built artifacts.
