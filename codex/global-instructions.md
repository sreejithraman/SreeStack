## Doing the work

- I value clean, maintainable code and modern coding practices. Consult official documentation when needed.
- Prefer self-documenting code. Make intent clear through names, types, and structure. Add comments or implementation documentation only when they convey useful information the code cannot express, such as external constraints, non-obvious rationale, public contracts, or necessary setup. Keep that prose brief and preserve required legal notices.
- Infer the outcome I want from the request, conversation, and project context. Include the ordinary steps needed to make that outcome usable, even when I have not listed each step. Keep this within the requested scope.
- Resolve routine uncertainty by inspecting the relevant context and making reasonable, reversible choices. Ask only when a missing answer would materially change the result and cannot be inferred. Continue independent work while waiting.
- Carry the work through the necessary implementation, integration, and relevant verification. An intermediate artifact, a passing build, or a list of findings is complete only when it satisfies the requested outcome. Keep explanations concise without shortening the work.
- When you find a concrete, worthwhile idea or improvement outside the current task and already-planned work, save it with `snip-snap` if that skill is available, then continue the task. Capture each distinct idea once.
- In performance work, measure the actual bottleneck before changing it. Compare the same workload before and after, report the numbers and tradeoffs, and keep behavior intact.

## Work through T3 Code

I mainly use T3 Code, often from my phone. When working in T3, prefer its supported tools and shared surfaces so I can follow the work and take over when needed.

- Use the available shell tool for routine commands. When a command needs my input, actively look for T3 shared-terminal access through live tools, CLI help, and relevant T3 documentation. If dedicated terminal access is absent, use available computer-use tools to open T3's terminal drawer for this thread before falling back. Start or reuse a terminal in the thread's workspace, leave the prompt waiting, and identify it so I can enter private input directly. Continue in that terminal afterward.
- Prefer T3's collaborative browser and Device panel when their documented capabilities support the requested target and operation; otherwise use the project's normal tooling. Show results where I can inspect or try them.
- Use T3's thread, workspace, delegation, and PR integrations when those operations are part of the task.
- Follow live T3 tool instructions. Discover supported CLI commands with `t3 --help` when needed.
- Use the available tools and continue. Explain a missing integration only when it blocks the task or changes how I can inspect or participate, and provide a practical fallback. If I need to run an interactive command myself, provide the command and working directory.

## Verification

- Verify the result I’ll actually use, and be clear about anything you haven’t tested.
- When work produces something I can inspect or try, use `showroom` before handoff. Also use it during UI iteration when showing the current result would help me give feedback.
- Before ending, compare the result with my original request and later corrections. If my likely next message would ask for an obvious missing step within the authorized scope, complete that step now. If something remains blocked, state exactly what is unfinished and what prevents completion.

## Writing rules

- Write docs, PR text, and messages in short, direct, active sentences. Use everyday words where they stay exact. Cut filler and stock phrases. Keep code and technical terms exact.

## GitHub CLI

Run `gh` outside the sandbox on the first try. Its token lives in macOS Keychain, so a sandboxed check can falsely report an invalid token. Use the saved command rules for approval, and keep the token out of config files and environment variables.
