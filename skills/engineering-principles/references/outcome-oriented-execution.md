# Outcome-Oriented Execution

For a planned rewrite, define the target behavior and explicit verification
boundaries. Converge on that target instead of accumulating temporary compatibility
machinery solely to preserve every private intermediate state. Temporary breakage
belongs only inside a scoped, reversible development phase; keep delivered commits,
PR layers, shared branches, and rollout stages coherent under their own checks.
Use [Sequence work into verifiable units](sequence-work-into-verifiable-units.md) to choose
those boundaries and prove the complete target before declaring completion.
