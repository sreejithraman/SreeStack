"""Host adapters for compare.py: one isolated, non-interactive session per call.

Each adapter loads exactly the given skill tree, hides installed skills, plugins,
and user instructions, keeps the user's login untouched, and keeps raw output in
the cell's evidence folder. Flags were checked against `claude --help` 2.1.318 and
`codex exec --help` 0.166.0.
"""

from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path
import re
import shutil
import subprocess


@dataclass
class RunResult:
    status: str = "ok"  # ok, error, or timeout
    error: str | None = None
    answer: str = ""
    calls: list | None = None  # [{"name", "path"?, "command"?, "skill"?}]
    tokens: dict | None = None
    cost_usd: float | None = None
    turns: int | None = None
    model: str | None = None
    loaded_skills: list | None = None
    wall_seconds: float = 0.0
    checks: list = field(default_factory=list)

    def read_skill(self, name: str) -> bool:
        marker = f"{name}/SKILL.md"
        return any(call.get("skill") == name or marker in (call.get("path") or "")
                   or marker in (call.get("command") or "") for call in self.calls or [])

    def save(self, out: Path, extra=None) -> None:
        (out / "answer.txt").write_text(self.answer)
        (out / "result.json").write_text(json.dumps({**(extra or {}), **asdict(self)}, indent=2))


def frontmatter(skill: Path) -> str:
    text = (skill / "SKILL.md").read_text()
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return match.group(1) if match else ""


def model_invocable(tree: Path) -> list:
    return sorted(skill.name for skill in tree.iterdir() if (skill / "SKILL.md").exists()
                  and not re.search(r"^disable-model-invocation:\s*true\s*$", frontmatter(skill), re.M))


def skill_names(*directories: Path) -> set:
    return {entry.name for directory in directories if directory.is_dir()
            for entry in directory.iterdir() if not entry.name.startswith(".")}


def execute(command, *, cwd, env, out: Path, timeout) -> tuple:
    """Run a host CLI, keeping its raw stdout and stderr. Returns (returncode or None on timeout, stdout)."""
    with open(out / "raw.jsonl", "w") as stdout, open(out / "stderr.log", "w") as stderr:
        try:
            done = subprocess.run(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                  stdout=stdout, stderr=stderr, timeout=timeout)
            code = done.returncode
        except subprocess.TimeoutExpired:
            code = None
    return code, (out / "raw.jsonl").read_text(errors="replace")


def events(raw: str):
    for line in raw.splitlines():
        try:
            yield json.loads(line)
        except ValueError:
            continue


class Claude:
    """`claude -p` with stream-json output, project settings only, and the tree as a project skill set."""

    # Claude Code bundles a skill under this installed name, so the leak probe can't tell them apart.
    bundled_names = {"verify"}
    telemetry_notes = ("cost_usd is total_cost_usd as Claude Code reports it. tokens.input excludes cache reads "
                       "and cache writes, which are listed separately; price each at its own rate, never summed.")

    def version(self) -> str:
        return subprocess.check_output(["claude", "--version"], text=True).strip()

    def installed_skill_names(self) -> set:
        return skill_names(Path.home() / ".claude/skills") - self.bundled_names

    def run(self, *, skills, prompt, work, out, settings, scratch, variant) -> RunResult:
        command = ["claude", "-p", "--output-format", "stream-json", "--verbose",
                   "--setting-sources", "project", "--strict-mcp-config", "--no-session-persistence",
                   "--model", settings["model"], "--permission-mode", settings.get("permission_mode", "acceptEdits"),
                   "--allowedTools", *settings.get("allowed_tools", ["Bash", "Read", "Skill"])]
        if settings.get("effort"):
            command += ["--effort", settings["effort"]]
        if settings.get("max_budget_usd"):
            command += ["--max-budget-usd", str(settings["max_budget_usd"])]
        if skills is not None:
            shutil.copytree(skills, work / ".claude/skills", symlinks=True, dirs_exist_ok=True)
        code, raw = execute([*command, "--", prompt], cwd=work, env=dict(os.environ), out=out,
                            timeout=settings.get("timeout_seconds", 600))
        result = RunResult(calls=[])
        final = None
        for event in events(raw):
            if event.get("type") == "system" and event.get("subtype") == "init":
                result.loaded_skills, result.model = event.get("skills"), event.get("model")
            elif event.get("type") == "assistant":
                for block in event["message"].get("content", []):
                    if block.get("type") == "tool_use":
                        given = block.get("input") or {}
                        result.calls.append({"name": block["name"], "path": given.get("file_path"),
                                             "command": given.get("command"), "skill": given.get("skill"),
                                             "nested": bool(event.get("parent_tool_use_id"))})
            elif event.get("type") == "result":
                final = event
        if final:
            usage = final.get("usage") or {}
            result.answer = final.get("result") or ""
            result.cost_usd = final.get("total_cost_usd")
            result.turns = final.get("num_turns")
            result.tokens = {"input": usage.get("input_tokens"), "cache_read": usage.get("cache_read_input_tokens"),
                             "cache_write": usage.get("cache_creation_input_tokens"),
                             "output": usage.get("output_tokens")}
        if code is None:
            result.status, result.error = "timeout", "the session hit timeout_seconds"
        elif code != 0 or not final or final.get("is_error"):
            result.status = "error"
            result.error = f"claude exited {code}" + (f": {final.get('subtype')}" if final else "; no result event")
        return result


class Codex:
    """`codex exec --json` with a disposable HOME and CODEX_HOME that links only the login."""

    telemetry_notes = ("Codex reports no cost. tokens.* sum turn.completed usage: input_tokens includes "
                       "cached_input_tokens and output_tokens includes reasoning_output_tokens, as in the "
                       "Responses API, so never add the parts; price cached input at its own rate.")

    def version(self) -> str:
        return subprocess.check_output(["codex", "--version"], text=True).strip()

    def codex_home(self) -> Path:
        return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))

    def installed_skill_names(self) -> set:
        return skill_names(Path.home() / ".agents/skills", self.codex_home() / "skills")

    def run(self, *, skills, prompt, work, out, settings, scratch, variant) -> RunResult:
        home, codex_home = scratch / "home", scratch / "codex-home"
        codex_home.mkdir(parents=True)
        (home / ".agents/skills").mkdir(parents=True)
        # Links, not copies: a token refresh then writes through to the real login.
        for name in ("auth.json", "auth.lock"):
            if (self.codex_home() / name).exists():
                (codex_home / name).symlink_to(self.codex_home() / name)
        if skills is not None:
            shutil.copytree(skills, home / ".agents/skills", symlinks=True, dirs_exist_ok=True)
        command = ["codex", "exec", "--json", "--ephemeral", "--skip-git-repo-check", "--ignore-rules",
                   "--disable", "plugins", "--disable", "apps", "--disable", "hooks",
                   "-s", settings.get("sandbox", "workspace-write"), "-m", settings["model"], "-C", str(work)]
        if settings.get("effort"):
            command += ["-c", f'model_reasoning_effort="{settings["effort"]}"']
        env = {**os.environ, "HOME": str(home), "CODEX_HOME": str(codex_home)}
        code, raw = execute([*command, "--", prompt], cwd=work, env=env, out=out,
                            timeout=settings.get("timeout_seconds", 600))
        result = RunResult(calls=[], model=settings["model"])
        usage, failure = {}, None
        for event in events(raw):
            item = event.get("item") or {}
            if event.get("type") == "item.completed":
                kind = item.get("type")
                if kind == "agent_message":
                    result.answer = item.get("text", "")
                elif kind == "command_execution":
                    result.calls.append({"name": "shell", "command": item.get("command")})
                elif kind == "file_change":
                    result.calls += [{"name": "file_change", "path": c.get("path")} for c in item.get("changes", [])]
                elif kind == "mcp_tool_call":
                    result.calls.append({"name": f"mcp:{item.get('server')}.{item.get('tool')}"})
                elif kind not in ("reasoning", "todo_list"):
                    result.calls.append({"name": kind})
            elif event.get("type") == "turn.completed":
                for key, value in (event.get("usage") or {}).items():
                    usage[key] = usage.get(key, 0) + value
            elif event.get("type") in ("turn.failed", "error"):
                failure = json.dumps(event)[:500]
        result.tokens = usage or None
        result.turns = None  # Codex exec reports no model-request count.
        for name in ("auth.json", "auth.lock"):
            link = codex_home / name
            if link.exists() and not link.is_symlink():
                failure = (failure or "") + f" Codex replaced the {name} link, so the real login may need `codex login`."
                link.unlink()
        if code is None:
            result.status, result.error = "timeout", "the session hit timeout_seconds"
        elif code != 0 or failure or not usage:
            result.status, result.error = "error", f"codex exited {code}" + (f": {failure}" if failure else "")
        return result


ADAPTERS = {"claude": Claude, "codex": Codex}
