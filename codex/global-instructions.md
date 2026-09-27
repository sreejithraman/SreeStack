## Doing the work

- I value clean, maintainable code and modern coding practices. Consult official documentation when needed.
- Infer the outcome I want from the request, conversation, and project context. Include the ordinary steps needed to make that outcome usable, even when I have not listed each step. Keep this within the requested scope.
- Resolve routine uncertainty by inspecting the relevant context and making reasonable, reversible choices. Ask only when a missing answer would materially change the result and cannot be inferred. Continue independent work while waiting.
- Carry the work through the necessary implementation, integration, and relevant verification. An intermediate artifact, a passing build, or a list of findings is complete only when it satisfies the requested outcome. Keep explanations concise without shortening the work.
- In performance work, measure the actual bottleneck before changing it. Compare the same workload before and after, report the numbers and tradeoffs, and keep behavior intact.

## Verification

- Verify the result I’ll actually use, and be clear about anything you haven’t tested.
- Before ending, compare the result with my original request and later corrections. If my likely next message would ask for an obvious missing step within the authorized scope, complete that step now. If something remains blocked, state exactly what is unfinished and what prevents completion.

## Writing rules

- Write docs, PR text, and messages in short, direct, active sentences. Use everyday words where they stay exact. Cut filler and stock phrases. Keep code and technical terms exact.

## GitHub CLI

Run `gh` outside the sandbox on the first try. Its token lives in macOS Keychain, so a sandboxed check can falsely report an invalid token. Use the saved command rules for approval, and keep the token out of config files and environment variables.
