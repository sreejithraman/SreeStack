# Shared Apple signing

Use one machine profile for every repository and worktree that declares Apple credentials in its delivery description.

## One-time setup

Prepare an App Store Connect `.p8` key and one or more password-protected `.p12` files. Use an Apple Distribution identity for TestFlight and add an Apple Development identity when Device builds must also work without the login keychain.

```sh
showroom apple setup \
  --profile personal \
  --default \
  --team-id <team-id> \
  --key-id <key-id> \
  --issuer-id <issuer-id> \
  --api-key /path/to/AuthKey_<key-id>.p8 \
  --certificate /path/to/distribution.p12 \
  --certificate /path/to/development.p12
```

Showroom asks for a new signing-session password and lets macOS ask for each `.p12` password. It imports private keys as non-extractable, limits them to Apple signing tools, and writes the API-key bytes straight from memory into the dedicated keychain through macOS's Security framework. The JSON profile contains only non-secret metadata and uses user-only permissions.

Keep one encrypted offline backup of each source `.p12` and its password. Remove ordinary local copies after `showroom apple status --json` reports the profile ready. Apple allows a `.p8` download only once, so keep its encrypted backup too.

## Each login or work period

```sh
showroom apple unlock --profile personal --hours 8
showroom apple status --profile personal --json
```

The unlock password is sent only to the macOS `security` process and is not written to Showroom state, environment variables, delivery logs, or repositories. It appears in that short-lived process's arguments because Apple's command requires it; Showroom clears its own reference as soon as the command ends. The keychain locks at the timeout, system sleep, logout, reboot, or this command:

```sh
showroom apple lock --profile personal
```

While unlocked, Showroom serializes Apple delivery across worktrees, adds the dedicated keychain to the user search list for the run, creates a private temporary `.p8`, passes its path through private process environment, then removes the file and restores the prior search list.

## Delivery contract

A repository asks for the profile without naming it or storing account data:

```json
{
  "start_credentials": ["apple"],
  "verify_credentials": ["apple"]
}
```

The default profile applies across repositories. `SHOWROOM_APPLE_PROFILE` can choose another global profile for one run. Showroom fails before the repository command when a required profile is absent or locked.

The repository command receives `SHOWROOM_APPLE_TEAM_ID`, `SHOWROOM_APPLE_KEY_ID`, `SHOWROOM_APPLE_ISSUER_ID`, `SHOWROOM_APPLE_KEY_PATH`, and `SHOWROOM_APPLE_KEYCHAIN_PATH`. Treat them as run-only inputs and redact them from results and logs.

For automatic TestFlight numbering, the delivery surface declares Apple start credentials. Showroom reads the selected scheme's bundle ID, app version, and platform, checks App Store Connect, and reserves the next positive integer build number in machine state before it runs the repository command. The counter is scoped to the bundle ID and app version, so a new app version starts at `1`. The machine reservation keeps automatic starts distinct while Apple processes a prior upload. Keep the app version in Xcode and build numbers out of `.showroom.toml`.

`--build-number` remains a manual override for a release process that owns its own number. It skips the App Store Connect check and Showroom's reservation.
