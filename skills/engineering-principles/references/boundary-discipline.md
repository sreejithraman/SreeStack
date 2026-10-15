# Boundary Discipline

Parse external input into domain values where trust changes: requests, CLI
arguments, configuration, stored records, and third-party responses. Keep
transport, storage, and framework representations behind the interface. Prefer
pure domain logic with a thin effectful shell. Inside a validated trust domain,
use established invariants instead of scattering the same checks through callers.
Runtime authorization, changing state, and data arriving from untrusted code
still need checks at their actual enforcement point.
Enforce private implementation through language visibility, package exports, or
an import rule so callers cannot take a convenient bypass. Inject effectful
dependencies when real callers or tests need to substitute them.
