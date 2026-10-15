# Migrate Callers Then Delete Legacy APIs

For an internal interface the project can migrate together, inventory its callers,
move them to the supported route, update examples and tests, and remove the obsolete
route in the same refactor wave. Leaving both available creates competing examples
for the next contributor. Preserve distinct adapters and externally required
compatibility paths. Where deployment or external consumers require staged support,
name its owner, removal condition, and verification rather than breaking them for
local simplicity.
