# Project delivery command

The checked-in command prefix from `.showroom.toml` implements protocol version 1. It runs without a shell.

## Describe

`<delivery> describe --json` must only inspect checked-in project facts. It returns the shape defined by [delivery-description.schema.json](delivery-description.schema.json). `start` and `verify` are argv suffixes. `required_arguments` names flags that Showroom must supply at start and save for later verification.

## Start and verify

Showroom runs the advertised suffix, adds each required `--name value`, then adds `--result-json <private-path>`. The command writes [delivery-result.schema.json](delivery-result.schema.json). It may also write evidence and logs inside the worktree or Showroom's private record folder.

A Device surface uses `manual` ownership and a 24-hour record. A TestFlight surface uses `provider` ownership and no guessed end time. A pending provider result may omit `provider_resource_id`; a passed result must return the provider's real ID.

`showroom stop` ends the record only. It never uninstalls an app or removes a provider build.

## Checks

Run `showroom doctor <project>`. It parses the TOML and runs only `describe`; it does not start delivery.
