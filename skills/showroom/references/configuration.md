# Project configuration

Use `.showroom.toml` when automatic discovery cannot select one project. Version 1 has one table per named project:

```toml
version = 1

[deal]
project = "ios/Deal/Deal.xcodeproj"
scheme = "Deal"
delivery = ["node", "scripts/deal-delivery.mjs"]
```

Each project accepts only `project`, `scheme`, and `delivery`. `project` must name an existing `.xcodeproj` inside the worktree. `delivery` must be an argv array. Keep signing data, accounts, device names and IDs, build numbers, keys, host names, and generated state out of this file.

With this entry, `showroom start deal` starts the Simulator. `device` and `testflight` come from the delivery command description, not extra TOML tables.
