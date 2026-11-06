# Issue tracker: GitLab

Issues and specs for this repo live as GitLab issues. Use the [`glab`](https://gitlab.com/gitlab-org/cli) CLI for all operations.

## Conventions

- **Create an issue**: `glab issue create --title "..." --description "..."`. Use a heredoc for multi-line descriptions. Pass `--description -` to open an editor.
- **Read an issue**: `glab issue view <number> --comments`. Use `-F json` for machine-readable output.
- **List issues**: `glab issue list -F json`
- **Comment on an issue**: `glab issue note <number> --message "..."`. GitLab calls comments "notes".
- **Close**: `glab issue close <number>`. `glab issue close` does not accept a closing comment, so post the explanation first with `glab issue note <number> --message "..."`, then close.

Infer the repo from `git remote -v`; `glab` does this automatically when run inside a clone.

## When a skill says "publish to the issue tracker"

Create a GitLab issue.

## Blocking and claiming

- **Blocking**: GitLab's **native blocking link**, the canonical, UI-visible representation. Add it with the `/blocked_by #<n>` quick action, posted as a note (`glab issue note <ticket> --message "/blocked_by #<blocker>"`). Read links with `glab api projects/:id/issues/:iid/links`. Native blocking links are a Premium/Ultimate feature; on the free tier (or where unavailable) fall back to a `Blocked by: #<n>, #<n>` line at the top of the description.
- **Claim**: Run `glab issue update <n> --assignee @me` as the session's first write. If you chose the ticket yourself, re-read it first, and leave it if it has an assignee, even your own account, if a blocker is open, or if it isn't ready under the Ready rule in the `to-tasks` skill. If someone gave you a ticket another account holds, ask them before you claim it.
