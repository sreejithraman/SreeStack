# iOS Verification

Use a Simulator that supports the app's deployment target. Identify the project
or workspace, scheme, build configuration, Simulator model, and runtime used for
the check. Choose the shortest available path that can observe the required
result: Xcode's MCP tools can build, run, interact with the Simulator, and capture
screenshots; `xcodebuild` and `xcrun simctl` cover build, install, and launch;
Simulator or computer-use tools can provide the remaining interaction. Check
the connected tool's capabilities before relying on it. Xcode 27 adds Simulator
interaction to its MCP server ([Xcode 27 release notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes)); external agents connect through
[`xcrun mcpbridge`](https://developer.apple.com/documentation/xcode/giving-external-agents-access-to-xcode).
Before using those MCP tools, open the target project or workspace in Xcode. If
Xcode's headless MCP server is enabled, `xcrun mcp-server open <project-or-workspace>`
can open it instead; check `xcrun mcp-server status` when discovery fails.

## Build and launch

- Build and run the intended scheme. If the build fails, preserve the failure and
  determine whether it comes from the product or verification environment. Report
  it as the workflow result. Fix code only when the active task includes fixing
  failures, then restart verification against the changed revision.
- After launch, confirm that the expected app and screen are visible. Capture a
  screenshot and inspect the accessibility hierarchy when the available tooling
  exposes it.
- Preserve the workflow's data assumptions. Reset, reinstall, seed, or relaunch
  only when the required starting state calls for it, and report material setup.

## Observe and interact

- Target controls by accessibility identifier or label when supported. When the
  available tooling exposes only rendered state, interact from the current view,
  recapture after every action, and report semantic or accessibility coverage as
  untested. Derive coordinate targets from current hierarchy or bounds when they
  are available rather than from a stale screenshot.
- Recapture the hierarchy after navigation, presentation, rotation, animation, or
  any interaction that may move the target.
- Exercise text input, gestures, scrolling, orientation, permissions, and
  background or foreground transitions when they belong to the selected workflow.
- When a save or update should persist, verify it through a fresh read path by
  relaunching and refetching, inspecting the stored value through an independent
  interface, or reopening through a path known to create a new model and reload
  durable storage. Record the persisted value observed.
- Check both function and presentation: hit targets, clipping, Dynamic Type where
  relevant, safe areas, keyboard avoidance, and expected system dialogs.
- Capture application logs when the app crashes, exits, hangs, or behaves
  differently from the visible state. Use the process and bundle identifier to
  separate app output from unrelated Simulator noise.

Keep an explicitly requested Simulator check in Simulator. Exercise the portions
the Simulator supports and name the exact device-only step that remains unverified.
Use a physical device when the request includes device verification and suitable
hardware is available.

## Evidence

Record the scheme, Simulator model and runtime, workflow states, and relevant
screenshots or logs. A successful build proves that the app compiled; the
interaction and resulting state prove whether the workflow worked.
