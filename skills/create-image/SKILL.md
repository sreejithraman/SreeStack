---
name: create-image
description: Use first whenever a task needs a generated or edited raster image, including photos, illustrations, textures, or local image edits. Excludes charts, screenshots, and graphics built directly in code.
---

# Create Image

Make the requested image through the OpenAI Images API, and use the host's
subscription image tool when the API cannot deliver. The user has approved that
fallback in advance, so use it without asking.

- **Input:** a prompt, any local images, and an optional model preference.
- **Output:** saved image files.
- **Done:** every file exists at its reported path, you opened it and checked it
  against the request, and your report names the route, the model, and any
  disclosure below.

## Choose the model

Flare is the default. Pick the flags from what the user said:

| The user says | Flags |
| --- | --- |
| Nothing about the model | None |
| Sunburst, or very detailed visual work | `--model sunburst` |
| A model ID | `--model <id>` |
| Only that model, or the exact model matters | Add `--require-model` |

The native tool cannot select a model. A plain preference permits the fallback, and
a required model forbids it.

## Run the API route

Use the CLI in this skill's `scripts/` folder. If a higher-priority host
instruction forbids the API or the network, skip the CLI and go to
[Fall back](#fall-back).

```bash
python3 <skill-folder>/scripts/openai_images.py generate --prompt "..." --out assets/hero.png
python3 <skill-folder>/scripts/openai_images.py edit --image photo.png --prompt "..." --out photo-edited.png
```

Use `--help` for size, quality, mask, reference, and count flags. Add `--dry-run`
to validate a command with no key, no request, and no file written. Pass long
prompts through `--prompt-file -` on stdin. The `--out` extension sets the format,
and the path must be new. Pick another name instead of removing a file.

Give the shell call at least 60 seconds more than the CLI's `--timeout`, which limits
the whole API exchange and defaults to 300 seconds. If the host kills the run anyway,
act as on exit 3, or exit 5 when the model is required, and report a possible charge.

## Act on the exit code

The CLI prints one JSON object. Read `reason`, `message`, `outputs`,
`fallback_allowed`, and `api`, which holds the API's own `message` and
`may_have_charged`.

| Exit | Meaning | Do this |
| --- | --- | --- |
| 0 | Saved, or dry run passed | Check each file in `outputs` |
| 2 | Bad argument, file, or output path. Nothing was sent | Fix it and rerun |
| 3 | The API could not deliver, and a fallback is allowed | [Fall back](#fall-back) |
| 4 | Request stopped, or a file could not be saved | Stop, and report `message` and any `outputs`. The flag rule below is the one exception |
| 5 | The API could not deliver, and the model is required | Stop and report `message` |
| 1 | CLI bug | Stop and report `message` |

Follow these limits on every path:

- **Respect a refusal.** After `refused` or `user_error`, leave the prompt and inputs
  to the user. Another route, model, or reworded prompt must not get around it.
- **Fix your own flag once.** After `invalid_request`, rerun once if `message` names a
  flag you chose. Keep the prompt and `--model`. Otherwise stop.
- **Avoid double billing.** When `api.may_have_charged` is true, rerun the same
  request only if the user asks. The CLI already retried the failures that are safe
  to retry.
- **Protect the key.** The CLI reads `OPENAI_API_KEY` from the environment. Never
  print it, pass it as an argument, or write it to a file. Stay out of secret stores
  unless the user asks. Then use [agent-login](../agent-login/SKILL.md).
- **Name the Codex setting.** On Codex, whenever `reason` is `network_error`, tell the
  user the API route needs network access, which
  [`sandbox_workspace_write.network_access = true`](https://learn.chatgpt.com/docs/config-file/config-reference)
  gives the `workspace-write` sandbox. Leave the config for the user to change.
- **Keep Codex out of the API route.** Never run `codex exec` for an image, and never
  sign Codex in with an API key. Monthly Pro API credits
  [cover the Images API but not Codex through API keys](https://developers.openai.com/api/docs/guides/chatgpt-api-credits).

Those credits apply only to a project key from the API organization linked to the
plan. Free credits are spent before purchased ones. No API reports the balance or
limits a call to free credits. Send balance questions to the API Platform billing
settings.

## Fall back

If the user required a model, stop and report why the API route failed. The native
tool cannot honor that.

Otherwise use only an image tool the current session lists, such as Codex's
`image_gen`. Follow its schema. It does not run through this CLI, and
[it uses `gpt-image-2` and counts against Codex usage limits](https://learn.chatgpt.com/docs/image-generation).

1. Make any local input visible to the tool. In Codex, load it with `view_image`.
2. Call the tool once per requested image.
3. Copy each result to the requested path without replacing a file, then check it.

When the tool refuses, fails, or returns an unusable image, stop and report that with
the CLI's `message`.

If the session has no such tool, report that exactly: this host has no subscription
image tool, plus the CLI's `message`. Leave the image unmade rather than swap in
another provider, an SVG, or a placeholder.

Tell the user, after any fallback:

- That the fallback ran, why, and that the model was `gpt-image-2` rather than the
  one requested.
- Any CLI `message` about a possible charge, so they know an image may be billed
  even though none came back.
- Each requested setting the tool could not honor, such as a mask, size, or format.
